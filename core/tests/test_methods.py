from django.test import TestCase
from core.models import *
from core.analyzer import AnalysisEvent


class AnalysTestCase(TestCase):
    def setUp(self):
        etype1 = TypeEvent.objects.create(name="Тип 1")
        vtype1 = TypeVisitor.objects.create(name="Тип 1")
        vtype2 = TypeVisitor.objects.create(name="Тип 2")
        vtype3 = TypeVisitor.objects.create(name="Тип 3")

        event = Event.objects.create(name="Мероприятие 1", address="Адрес 1",
                                     type=etype1, description="Описание")

        Visitor.objects.create(event=event, fullName="Всеволод 1",
                               type=vtype1)
        Visitor.objects.create(event=event, fullName="Всеволод 1",
                               type=vtype1)
        Visitor.objects.create(event=event, fullName="Всеволод 1",
                               type=vtype1)
        Visitor.objects.create(event=event, fullName="Всеволод 1",
                               type=vtype1)
        Visitor.objects.create(event=event, fullName="Всеволод 1",
                               type=vtype1)
        Visitor.objects.create(event=event, fullName="Всеволод 1",
                               type=vtype1)
        Visitor.objects.create(event=event, fullName="Всеволод 1",
                               type=vtype1)
        self.idevent = event.id

    def test_correctness_types(self):
        analys = AnalysisEvent(self.idevent)
        self.assertTrue(analys.get_num_visitors() == 7)
