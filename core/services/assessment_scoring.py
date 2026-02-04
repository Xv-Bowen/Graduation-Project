from __future__ import annotations

from dataclasses import dataclass

from django.db.models import QuerySet

from core.models import Assessment, AssessmentOption, AssessmentResult


@dataclass
class AssessmentScoreResult:
    total_score: int
    result_title: str
    result_summary: str
    result_advice: str
    option_map: dict[int, AssessmentOption]


def score_assessment(assessment: Assessment, selected: dict[str, str]) -> AssessmentScoreResult:
    option_ids = list(selected.values())
    options = {
        option.id: option
        for option in AssessmentOption.objects.filter(
            id__in=option_ids, question__assessment=assessment
        ).select_related("question")
    }
    if len(options) != len(option_ids):
        raise ValueError("提交包含无效选项")

    total_score = 0
    for question in assessment.questions.all():
        option_id = selected.get(str(question.id))
        option = options.get(int(option_id)) if option_id else None
        if not option or option.question_id != question.id:
            raise ValueError("提交包含无效选项")
        total_score += option.score

    result = (
        AssessmentResult.objects.filter(
            assessment=assessment, min_score__lte=total_score, max_score__gte=total_score
        )
        .order_by("min_score")
        .first()
    )
    result_title = result.title if result else "评估结果"
    result_summary = result.summary if result else "请结合自身情况，选择合适的放松与支持方式。"
    result_advice = result.advice if result else ""

    return AssessmentScoreResult(
        total_score=total_score,
        result_title=result_title,
        result_summary=result_summary,
        result_advice=result_advice,
        option_map=options,
    )
