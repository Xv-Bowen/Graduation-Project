from django.test import TestCase

from core.models import Assessment, AssessmentOption, AssessmentQuestion
from core.services.assessment_scoring import score_assessment


class AssessmentScoringTests(TestCase):
    def setUp(self):
        self.assessment = Assessment.objects.create(name="测试量表", is_published=True)
        self.q1 = AssessmentQuestion.objects.create(assessment=self.assessment, order=1, text="Q1")
        self.q2 = AssessmentQuestion.objects.create(assessment=self.assessment, order=2, text="Q2")
        self.o11 = AssessmentOption.objects.create(question=self.q1, order=1, text="A", score=1)
        self.o12 = AssessmentOption.objects.create(question=self.q1, order=2, text="B", score=2)
        self.o21 = AssessmentOption.objects.create(question=self.q2, order=1, text="A", score=1)

    def test_score_success(self):
        selected = {str(self.q1.id): str(self.o12.id), str(self.q2.id): str(self.o21.id)}
        result = score_assessment(self.assessment, selected)
        self.assertEqual(result.total_score, 3)
        self.assertIn(self.o12.id, result.option_map)

    def test_score_rejects_invalid_option(self):
        other_assessment = Assessment.objects.create(name="其他量表", is_published=True)
        other_q = AssessmentQuestion.objects.create(assessment=other_assessment, order=1, text="QX")
        other_o = AssessmentOption.objects.create(question=other_q, order=1, text="X", score=9)
        selected = {str(self.q1.id): str(other_o.id), str(self.q2.id): str(self.o21.id)}
        with self.assertRaises(ValueError):
            score_assessment(self.assessment, selected)
