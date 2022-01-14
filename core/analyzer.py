from django.db.models.fields import TimeField
from django.db.models import Aggregate

from django.db.models.query import QuerySet

from django.db.models import Count
from django.db.models import Avg
from django.db.models import Max
from django.db.models import Min
from django.db.models import F
from datetime import datetime

from django.db.models.query_utils import Q

from .models import *

from abc import ABC, abstractmethod

from typing import Dict


class Median(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = TimeField()
    template = '%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)'


class Q1(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = TimeField()
    template = '%(function)s(0.25) WITHIN GROUP (ORDER BY %(expressions)s)'


class Q3(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = TimeField()
    template = '%(function)s(0.75) WITHIN GROUP (ORDER BY %(expressions)s)'


class Analysis(ABC):
    def __init__(self):
        self.resource: Dict = dict()
        self.data: Dict = dict()

    @abstractmethod
    def set_resource(self):
        pass

    @abstractmethod
    def calc_data(self):
        pass


class AnalysisEvents(Analysis):
    def set_resource(self):
        self.resource['visitors'] = Visitor.objects.all()
        self.resource['events'] = Event.objects.all()

    def calc_data(self):
        self.data['num_visitors'] = self.resource['visitors'].count()
        self.data['num_visitors_by_type'] = self.resource['visitors'].values(
            'type__name').annotate(dcount=Count('type'))

        self.data['last_event'] = self.resource['events'].first()
        query_result = self.resource['visitors'].values(
            'event__id').annotate(dcount=Count('event'))
        if query_result:
            maxval = max(query_result, key=lambda x: x['dcount'])
            self.data['maxv_event'] = Event.objects.get(id=maxval['event__id'])
        else:
            self.data['maxv_event'] = None


class AnalysisEvent(Analysis):
    def set_resource(self, index):
        self.resource['visitors'] = Visitor.objects.filter(event__id=index)
        self.resource['count'] = self.resource['visitors'].count()

    def calc_data(self):
        self.data['num_visitors'] = self.resource['visitors'].count()
        self.data['num_visitors_by_type'] = self.resource['visitors'].values(
            'type__name').annotate(dcount=Count('type'))
        self.data['mean_time'] = TimeContext(
            TimeStrategyMean(), self.resource['visitors']).make_strategy()
        self.data['max_time'] = TimeContext(
            TimeStrategyMax(), self.resource['visitors']).make_strategy()
        self.data['min_time'] = TimeContext(
            TimeStrategyMin(), self.resource['visitors']).make_strategy()
        self.data['median_time'] = TimeContext(
            TimeStrategyMedian(), self.resource['visitors']).make_strategy()
        self.data['q1_time'] = TimeContext(
            TimeStrategyQ1(), self.resource['visitors']).make_strategy()
        self.data['q3_time'] = TimeContext(
            TimeStrategyQ3(), self.resource['visitors']).make_strategy()


class Analyzer(ABC):
    @abstractmethod
    def create_analysis(self):
        pass

    def get_analysis(self) -> Dict:
        data: Dict = self.create_analysis().data
        return data


class AnalyzerEvents(Analyzer):
    def create_analysis(self) -> Analysis:
        analysis = AnalysisEvents()
        analysis.set_resource()
        analysis.calc_data()
        return analysis


class AnalyzerEvent(Analyzer):
    def create_analysis(self, index) -> Analysis:
        analysis = AnalysisEvent()
        analysis.set_resource(index)
        analysis.calc_data()
        return analysis

    def get_analysis(self, index) -> Dict:
        data: Dict = self.create_analysis(index).data
        return data


class TimeStrategy(ABC):
    @abstractmethod
    def do_algorithm(self, visitors: QuerySet):
        pass


class TimeStrategyMedian(TimeStrategy):
    def do_algorithm(self, visitors: QuerySet) -> datetime:
        if visitors.count() > 0:
            mediandata = visitors.aggregate(median_difference=Median(
                F('arrivalDate')-datetime(1970, 1, 1)))['median_difference']
            return datetime(1970, 1, 1)+mediandata
        else:
            return None


class TimeStrategyQ1(TimeStrategy):
    def do_algorithm(self, visitors: QuerySet) -> datetime:
        if visitors.count() > 0:
            q1data = visitors.aggregate(q1_difference=Q1(
                F('arrivalDate')-datetime(1970, 1, 1)))['q1_difference']
            return datetime(1970, 1, 1)+q1data
        else:
            return None


class TimeStrategyQ3(TimeStrategy):
    def do_algorithm(self, visitors: QuerySet) -> datetime:
        if visitors.count() > 0:
            q3data = visitors.aggregate(q3_difference=Q3(
                F('arrivalDate')-datetime(1970, 1, 1)))['q3_difference']
            return datetime(1970, 1, 1)+q3data
        else:
            return None


class TimeStrategyMax(TimeStrategy):
    def do_algorithm(self, visitors: QuerySet) -> datetime:
        if visitors.count() > 0:
            return visitors.aggregate(Max('arrivalDate'))['arrivalDate__max']
        else:
            return None


class TimeStrategyMin(TimeStrategy):
    def do_algorithm(self, visitors: QuerySet) -> datetime:
        if visitors.count() > 0:
            return visitors.aggregate(Min('arrivalDate'))[
                'arrivalDate__min']
        else:
            return None


class TimeStrategyMean(TimeStrategy):
    def do_algorithm(self, visitors: QuerySet) -> datetime:
        if visitors.count() > 0:
            meandata = visitors.aggregate(average_difference=Avg(
                F('arrivalDate')-datetime(1970, 1, 1)))['average_difference']
            return datetime(1970, 1, 1)+meandata
        else:
            return None


class TimeContext():
    def __init__(self, strategy: TimeStrategy, visitors: QuerySet) -> None:
        self.strategy = strategy
        self.visitors = visitors

    def make_strategy(self) -> datetime:
        return self.strategy.do_algorithm(self.visitors)
