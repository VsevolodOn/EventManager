from django.test import TestCase
from core.models import *
from core.analyzer import *
from datetime import datetime
from unittest.mock import patch


class AnalysTestCase(TestCase):
    fixtures = ["events.yaml"]

    def setUp(self):
        self.visitors = Visitor.objects.filter(event__id=1)
        self.visitors_none = Visitor.objects.filter(event__id=2)

    def test_correctness_strategy_mean_time(self):
        res = TimeStrategyMean().do_algorithm(self.visitors)
        self.assertTrue(res == datetime(2021, 10, 1, 17, 21, 25, 714286))

        res = TimeStrategyMean().do_algorithm(self.visitors_none)
        self.assertTrue(res == None)

    def test_correctness_strategy_max_time(self):
        res = TimeStrategyMax().do_algorithm(self.visitors)
        self.assertTrue(res == datetime(2021, 10, 1, 17, 51))

        res = TimeStrategyMean().do_algorithm(self.visitors_none)
        self.assertTrue(res == None)

    def test_correctness_strategy_min_time(self):
        res = TimeStrategyMin().do_algorithm(self.visitors)
        self.assertTrue(res == datetime(2021, 10, 1, 17, 0))

        res = TimeStrategyMin().do_algorithm(self.visitors_none)
        self.assertTrue(res == None)

    def test_correctness_strategy_median_time(self):
        res = TimeStrategyMedian().do_algorithm(self.visitors)
        self.assertTrue(res == datetime(2021, 10, 1, 17, 11))

        res = TimeStrategyMedian().do_algorithm(self.visitors_none)
        self.assertTrue(res == None)

    def test_correctness_strategy_q1_time(self):
        res = TimeStrategyQ1().do_algorithm(self.visitors)
        self.assertTrue(res == datetime(2021, 10, 1, 17, 8, 30))

        res = TimeStrategyQ1().do_algorithm(self.visitors_none)
        self.assertTrue(res == None)

    def test_correctness_strategy_q3_time(self):
        res = TimeStrategyQ3().do_algorithm(self.visitors)
        self.assertTrue(res == datetime(2021, 10, 1, 17, 35, 30))

        res = TimeStrategyQ3().do_algorithm(self.visitors_none)
        self.assertTrue(res == None)

    def test_correctness_strategy_last_event(self):
        res = EventStrategyLast().do_algorithm()
        data = {'id': 2, 'name': 'Мероприятие 2',
                'startDate': datetime(2021, 10, 3, 17, 0)}
        self.assertTrue(res == data)

    def test_correctness_strategy_max_event(self):
        res = EventStrategyMax().do_algorithm()
        data = {'id': 1, 'name': 'Мероприятие 1',
                'startDate': datetime(2021, 10, 1, 17, 0)}
        self.assertTrue(res == data)

    @patch("core.analyzer.TimeContext.make_strategy", return_value=datetime(2021, 10, 1, 17, 0))
    def test_correctness_analysis_event_calc(self, mocked):
        analysis = AnalysisEvent()
        analysis.resource['visitors'] = self.visitors
        analysis.resource['count'] = self.visitors.count()
        analysis.calc_data()
        data = {'num_visitors': 7,
                'num_visitors_by_type': [{'type__name': 'Тип 1', 'dcount': 3}, {'type__name': 'Тип 2', 'dcount': 2}, {'type__name': 'Тип 3', 'dcount': 2}]}
        self.assertTrue(analysis.data['num_visitors'] == data['num_visitors'])
        self.assertTrue(
            analysis.data['num_visitors_by_type'] == data['num_visitors_by_type'])

    @patch("core.analyzer.EventContext.make_strategy", return_value=None)
    def test_correctness_analysis_events_calc(self, mocked):
        analysis = AnalysisEvents()
        analysis.resource['visitors'] = self.visitors

        analysis.calc_data()
        data = {'num_visitors': 7,
                'num_visitors_by_type': [{'type__name': 'Тип 1', 'dcount': 3}, {'type__name': 'Тип 2', 'dcount': 2}, {'type__name': 'Тип 3', 'dcount': 2}]}
        self.assertTrue(analysis.data['num_visitors'] == data['num_visitors'])
        print(analysis.data)
        self.assertTrue(
            analysis.data['num_visitors_by_type'] == data['num_visitors_by_type'])
