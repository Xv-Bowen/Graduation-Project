import json
import re

from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .ai import AIServiceError
from .forms import (
    ArticleSearchForm,
    ConsultationNoteForm,
    ConsultationTicketForm,
    LoginForm,
    RegisterForm,
    RelaxationLogForm,
    RelaxationReminderForm,
    TicketStatusForm,
)
from .services.ai_chat import (
    AIChatPayload,
    build_messages,
    contains_risk,
    generate_ai_reply,
    log_chat,
    parse_ai_payload,
)
from .services.assessment_scoring import score_assessment
from .pagination import paginate_queryset
from .models import (
    Article,
    Assessment,
    AssessmentAnswer,
    AssessmentSubmission,
    Category,
    ConsultationNote,
    ConsultationTicket,
    Hotline,
    Institution,
    RelaxationLog,
    RelaxationMethod,
    RelaxationReminder,
)
from django.utils import timezone


@ensure_csrf_cookie
def home(request):
    categories = Category.objects.order_by("name")[:6]
    articles = (
        Article.objects.filter(is_published=True)
        .select_related("category")
        .order_by("-created_at")[:6]
    )
    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "articles": articles,
        },
    )


@login_required
def knowledge_list(request):
    form = ArticleSearchForm(request.GET or None)
    articles = Article.objects.filter(is_published=True).select_related("category")
    selected_category = None
    if form.is_valid():
        raw_query = (form.cleaned_data.get("query") or "").strip()
        category_slug = (form.cleaned_data.get("category") or "").strip()

        # 允许用户用空格/逗号/顿号等分隔多个关键词，避免“睡眠、焦虑”搜不到的误解。
        tokens = [t for t in re.split(r"[\s,，、;；]+", raw_query) if t]
        if tokens:
            query_filter = Q()
            for token in tokens:
                query_filter |= (
                    Q(title__icontains=token)
                    | Q(summary__icontains=token)
                    | Q(tags__icontains=token)
                )
            articles = articles.filter(query_filter)

        if category_slug:
            articles = articles.filter(category__slug=category_slug)
            selected_category = Category.objects.filter(slug=category_slug).first()
    articles = articles.order_by("-created_at")
    page_obj, querystring = paginate_queryset(
        request, articles, settings.PAGINATION_PAGE_SIZE
    )
    return render(
        request,
        "knowledge_list.html",
        {
            "form": form,
            "page_obj": page_obj,
            "querystring": querystring,
            "categories": Category.objects.order_by("name"),
            "selected_category": selected_category,
        },
    )


@login_required
def knowledge_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "knowledge_detail.html", {"article": article})


def consult_create(request):
    if request.method == "POST":
        form = ConsultationTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            if request.user.is_authenticated:
                ticket.user = request.user
            ticket.save()
            return redirect("consult_thanks")
    else:
        form = ConsultationTicketForm()
    return render(request, "consult_form.html", {"form": form})


def consult_thanks(request):
    return render(request, "consult_thanks.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "account/register.html", {"form": form})


def login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("home")
        django_messages.error(request, "用户名或密码不正确。")
    else:
        form = LoginForm(request)
    return render(request, "account/login.html", {"form": form})


def logout(request):
    auth_logout(request)
    return redirect("home")


@login_required
def my_tickets(request):
    tickets = (
        ConsultationTicket.objects.filter(user=request.user)
        .select_related("assigned_to")
        .order_by("-created_at")
    )
    page_obj, querystring = paginate_queryset(
        request, tickets, settings.PAGINATION_PAGE_SIZE
    )
    return render(
        request,
        "account/tickets.html",
        {"page_obj": page_obj, "querystring": querystring},
    )


@staff_member_required
def manage_ticket_list(request):
    tickets = (
        ConsultationTicket.objects.all()
        .select_related("user", "assigned_to")
        .order_by("-created_at")
    )
    page_obj, querystring = paginate_queryset(
        request, tickets, settings.PAGINATION_PAGE_SIZE
    )
    return render(
        request,
        "manage/tickets.html",
        {"page_obj": page_obj, "querystring": querystring},
    )


@staff_member_required
def manage_ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        ConsultationTicket.objects.select_related("user", "assigned_to").prefetch_related(
            "notes__author"
        ),
        id=ticket_id,
    )
    status_form = TicketStatusForm(request.POST or None, instance=ticket)
    note_form = ConsultationNoteForm(request.POST or None)
    if request.method == "POST":
        if "update_status" in request.POST and status_form.is_valid():
            status_form.save()
            django_messages.success(request, "咨询状态已更新。")
            return redirect("manage_ticket_detail", ticket_id=ticket.id)
        if "add_note" in request.POST and note_form.is_valid():
            ConsultationNote.objects.create(
                ticket=ticket,
                author=request.user,
                note=note_form.cleaned_data["note"],
                is_internal=note_form.cleaned_data.get("is_internal", True),
            )
            django_messages.success(request, "处理记录已添加。")
            return redirect("manage_ticket_detail", ticket_id=ticket.id)
    return render(
        request,
        "manage/ticket_detail.html",
        {"ticket": ticket, "status_form": status_form, "note_form": note_form},
    )


@login_required
def wellness_home(request):
    assessment_count = Assessment.objects.filter(is_published=True).count()
    method_count = RelaxationMethod.objects.filter(is_active=True).count()
    institution_count = Institution.objects.count()
    hotline_count = Hotline.objects.count()
    return render(
        request,
        "wellness/home.html",
        {
            "assessment_count": assessment_count,
            "method_count": method_count,
            "institution_count": institution_count,
            "hotline_count": hotline_count,
        },
    )


@login_required
def assessment_list(request):
    query = (request.GET.get("query") or "").strip()
    category = (request.GET.get("category") or "").strip()
    assessments = Assessment.objects.filter(is_published=True).annotate(
        question_count=Count("questions")
    )
    if query:
        assessments = assessments.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__icontains=query)
        )
    if category:
        assessments = assessments.filter(category=category)
    assessments = assessments.order_by("name")
    page_obj, querystring = paginate_queryset(
        request, assessments, settings.PAGINATION_PAGE_SIZE
    )
    categories = (
        Assessment.objects.filter(is_published=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
    )
    return render(
        request,
        "wellness/assessments.html",
        {
            "page_obj": page_obj,
            "querystring": querystring,
            "categories": categories,
            "query": query,
            "category": category,
        },
    )


@login_required
def assessment_detail(request, slug):
    assessment = get_object_or_404(Assessment, slug=slug, is_published=True)
    questions = assessment.questions.prefetch_related("options")
    if request.method == "POST":
        selected = {}
        missing = []
        for question in questions:
            option_id = request.POST.get(f"question_{question.id}")
            if not option_id:
                missing.append(question)
                continue
            selected[str(question.id)] = option_id
        if missing:
            django_messages.error(request, "请完成全部题目后再提交。")
        else:
            try:
                result_data = score_assessment(assessment, selected)
            except ValueError:
                django_messages.error(request, "提交包含无效选项，请重新作答。")
                return render(
                    request,
                    "wellness/assessment_detail.html",
                    {"assessment": assessment, "questions": questions},
                )
            submission = AssessmentSubmission.objects.create(
                assessment=assessment,
                user=request.user,
                total_score=result_data.total_score,
                result_title=result_data.result_title,
                result_summary=result_data.result_summary,
                result_advice=result_data.result_advice,
            )
            answer_rows = []
            for question in questions:
                option = result_data.option_map.get(int(selected[str(question.id)]))
                answer_rows.append(
                    AssessmentAnswer(
                        submission=submission,
                        question=question,
                        option=option,
                        score=option.score if option else 0,
                    )
                )
            AssessmentAnswer.objects.bulk_create(answer_rows)
            return redirect("assessment_result", slug=assessment.slug, submission_id=submission.id)
    return render(
        request,
        "wellness/assessment_detail.html",
        {"assessment": assessment, "questions": questions},
    )


@login_required
def assessment_result(request, slug, submission_id):
    submission = get_object_or_404(
        AssessmentSubmission,
        id=submission_id,
        assessment__slug=slug,
        user=request.user,
    )
    return render(
        request,
        "wellness/assessment_result.html",
        {"submission": submission},
    )


@login_required
def assessment_history(request):
    submissions = (
        AssessmentSubmission.objects.filter(user=request.user)
        .select_related("assessment")
        .order_by("-created_at")
    )
    page_obj, querystring = paginate_queryset(
        request, submissions, settings.PAGINATION_PAGE_SIZE
    )
    return render(
        request,
        "wellness/assessment_history.html",
        {"page_obj": page_obj, "querystring": querystring},
    )


@login_required
def service_directory(request):
    query = (request.GET.get("query") or "").strip()
    region = (request.GET.get("region") or "local").strip()
    if region not in {"local", "province", "national"}:
        region = "local"

    institutions = Institution.objects.filter(region_type=region)
    hotlines = Hotline.objects.filter(region_type=region)

    if query:
        institutions = institutions.filter(
            Q(name__icontains=query)
            | Q(address__icontains=query)
            | Q(description__icontains=query)
            | Q(phone__icontains=query)
        )
        hotlines = hotlines.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(phone__icontains=query)
        )

    emergency_hotlines = hotlines.filter(is_emergency=True)
    service_hotlines = hotlines.filter(is_emergency=False)

    return render(
        request,
        "wellness/institutions.html",
        {
            "institutions": institutions,
            "emergency_hotlines": emergency_hotlines,
            "service_hotlines": service_hotlines,
            "query": query,
            "region": region,
            "local_city": settings.LOCAL_CITY,
            "local_province": settings.LOCAL_PROVINCE,
        },
    )


@login_required
def relaxation_center(request):
    methods = RelaxationMethod.objects.filter(is_active=True)
    reminders = RelaxationReminder.objects.filter(user=request.user).select_related("method")
    logs = (
        RelaxationLog.objects.filter(user=request.user)
        .select_related("method", "reminder")
        .order_by("-practiced_at")[:10]
    )

    reminder_form = RelaxationReminderForm(user=request.user)
    log_form = RelaxationLogForm(
        user=request.user,
        initial={"practiced_at": timezone.localtime()},
    )

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "reminder":
            reminder_form = RelaxationReminderForm(request.POST, user=request.user)
            if reminder_form.is_valid():
                reminder_form.save()
                django_messages.success(request, "已保存放松提醒。")
                return redirect("relaxation_center")
        elif form_type == "log":
            log_form = RelaxationLogForm(request.POST, user=request.user)
            if log_form.is_valid():
                log = log_form.save(commit=False)
                log.user = request.user
                log.save()
                django_messages.success(request, "已记录本次练习。")
                return redirect("relaxation_center")

    return render(
        request,
        "wellness/relaxation.html",
        {
            "methods": methods,
            "reminders": reminders,
            "logs": logs,
            "reminder_form": reminder_form,
            "log_form": log_form,
        },
    )


@require_POST
def api_chat(request):
    if not request.user.is_authenticated:
        return JsonResponse({"reply": "请先登录后再使用 AI 咨询。", "risk": False}, status=401)
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"reply": "请求格式不正确，请刷新后再试。", "risk": False}, status=400)

    provider = payload.get("provider") or "deepseek"
    try:
        parsed: AIChatPayload = parse_ai_payload(payload)
    except ValueError as exc:
        message = "内容过长，请精简后再试。" if "内容过长" in str(exc) else "消息格式不正确，请刷新后再试。"
        return JsonResponse({"reply": message, "risk": False}, status=400)

    latest_text = " ".join(
        str(msg.get("content", ""))
        for msg in parsed.messages
        if msg.get("role") == "user"
    )
    if contains_risk(latest_text):
        response_text = (
            "我很在意你的安全。如果你正在经历强烈的痛苦或有伤害自己的想法，请立刻寻求帮助。"
            "你可以联系身边可信任的人，或拨打当地紧急电话寻求支持。"
            "如果愿意，也可以提交人工咨询，我们会尽快跟进。"
        )
        log_chat(parsed.provider, request.user if request.user.is_authenticated else None, parsed.messages, response_text, True)
        return JsonResponse({"reply": response_text, "risk": True})

    try:
        reply = generate_ai_reply(parsed)
        log_chat(parsed.provider, request.user if request.user.is_authenticated else None, parsed.messages, reply, False)
        return JsonResponse({"reply": reply, "risk": False})
    except AIServiceError as exc:
        return JsonResponse({"reply": str(exc), "risk": False}, status=200)
    except Exception:
        return JsonResponse(
            {"reply": "AI 服务暂时不可用，请稍后再试。", "risk": False},
            status=200,
        )
