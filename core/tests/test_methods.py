from django.test import TestCase
from core.models import *
from core.analyzer import AnalysisEvent
from datetime import datetime


class AnalysTestCase(TestCase):
    fixtures = ["events.yaml"]

    def setUp(self):
        self.analys = AnalysisEvent(1)

    def test_correctness_get_num_v(self):
        self.assertTrue(self.analys.get_num_visitors() == 7)

    def test_correctness_get_num_v_by_type(self):
        res = [{'type__name': 'Тип 1', 'dcount': 3}, {
            'type__name': 'Тип 2', 'dcount': 2}, {'type__name': 'Тип 3', 'dcount': 2}]
        print(self.analys.get_num_visitors_by_type())
        self.assertTrue(list(self.analys.get_num_visitors_by_type()) == res)

    def test_correctness_get_mean_time(self):
        self.assertTrue(self.analys.get_mean_time() ==
                        datetime(2021, 10, 1, 17, 21, 25, 714286))

    def test_correctness_get_max_time(self):
        self.assertTrue(self.analys.get_max_time() ==
                        datetime(2021, 10, 1, 17, 51))

    def test_correctness_get_min_time(self):
        self.assertTrue(self.analys.get_min_time() ==
                        datetime(2021, 10, 1, 17, 0))

    def test_correctness_get_median_time(self):
        self.assertTrue(self.analys.get_median_time() ==
                        datetime(2021, 10, 1, 17, 11))

    def test_correctness_get_q1_time(self):
        self.assertTrue(self.analys.get_q1_time() ==
                        datetime(2021, 10, 1, 17, 8, 30))

    def test_correctness_get_q3_time(self):
        self.assertTrue(self.analys.get_q3_time() ==
                        datetime(2021, 10, 1, 17, 35, 30))
