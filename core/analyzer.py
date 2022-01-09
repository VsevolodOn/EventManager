from django.db.models.fields import TimeField
from django.db.models import Aggregate

from django.db.models.query import QuerySet

from django.db.models import Count
from django.db.models import Avg
from django.db.models import Max
from django.db.models import Min
from django.db.models import F
from datetime import datetime

from .models import *


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


class AnalysisEvent():
    def __init__(self, index) -> None:
        self.visitors = Visitor.objects.filter(event__id=index)

    def get_num_visitors(self) -> int:
        return self.visitors.count()

    def get_num_visitors_by_type(self) -> QuerySet:
        return self.visitors.values('type__name').annotate(dcount=Count('type'))

    def get_median_time(self) -> datetime:
        mediandata = self.visitors.aggregate(median_difference=Median(
            F('arrivalDate')-datetime(1970, 1, 1)))['median_difference']
        return datetime(1970, 1, 1)+mediandata

    def get_q1_time(self) -> datetime:
        q1data = self.visitors.aggregate(q1_difference=Q1(
            F('arrivalDate')-datetime(1970, 1, 1)))['q1_difference']
        return datetime(1970, 1, 1)+q1data

    def get_q3_time(self) -> datetime:
        q3data = self.visitors.aggregate(q3_difference=Q3(
            F('arrivalDate')-datetime(1970, 1, 1)))['q3_difference']
        return datetime(1970, 1, 1)+q3data

    def get_max_time(self) -> datetime:
        return self.visitors.aggregate(Max('arrivalDate'))

    def get_min_time(self) -> datetime:
        return self.visitors.aggregate(Min('arrivalDate'))

    def get_mean_time(self) -> datetime:
        meandata = self.visitors.aggregate(average_difference=Avg(
            F('arrivalDate')-datetime(1970, 1, 1)))['average_difference']
        return datetime(1970, 1, 1)+meandata
