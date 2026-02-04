from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, allow_unicode=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    tags = models.CharField(max_length=200, blank=True, help_text="Use commas to separate tags.")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"], name="submission_user_created_idx"),
        ]
        indexes = [
            models.Index(fields=["user", "created_at"], name="chatlog_user_created_idx"),
            models.Index(fields=["provider", "created_at"], name="chatlog_provider_created_idx"),
        ]
        indexes = [
            models.Index(fields=["is_published", "created_at"], name="article_pub_created_idx"),
            models.Index(fields=["category", "is_published"], name="article_cat_pub_idx"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ConsultationTicket(models.Model):
    STATUS_NEW = "new"
    STATUS_ASSIGNED = "assigned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_NEW, "新建"),
        (STATUS_ASSIGNED, "已分配"),
        (STATUS_IN_PROGRESS, "处理中"),
        (STATUS_RESOLVED, "已解决"),
        (STATUS_CLOSED, "已关闭"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultation_tickets",
    )
    title = models.CharField(max_length=120)
    message = models.TextField()
    contact_name = models.CharField(max_length=50, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"], name="ticket_user_created_idx"),
            models.Index(fields=["status", "created_at"], name="ticket_status_created_idx"),
            models.Index(fields=["assigned_to", "status"], name="ticket_assigned_status_idx"),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ConsultationNote(models.Model):
    ticket = models.ForeignKey(ConsultationTicket, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    is_internal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for {self.ticket_id}"


class ChatLog(models.Model):
    PROVIDER_DEEPSEEK = "deepseek"

    provider = models.CharField(max_length=20)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_logs",
    )
    messages_json = models.JSONField()
    response_text = models.TextField()
    risk_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider} chat at {self.created_at:%Y-%m-%d %H:%M}"


class UserProfile(models.Model):
    GENDER_UNKNOWN = "unknown"
    GENDER_MALE = "male"
    GENDER_FEMALE = "female"

    GENDER_CHOICES = [
        (GENDER_UNKNOWN, "未说明"),
        (GENDER_MALE, "男"),
        (GENDER_FEMALE, "女"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    province = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    chronic_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user}"


class Assessment(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True, allow_unicode=True)
    category = models.CharField(max_length=60, blank=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_published", "category"], name="assessment_pub_cat_idx"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AssessmentQuestion(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="questions"
    )
    order = models.PositiveIntegerField(default=0)
    text = models.TextField()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.assessment.name} Q{self.order}"


class AssessmentOption(models.Model):
    question = models.ForeignKey(
        AssessmentQuestion, on_delete=models.CASCADE, related_name="options"
    )
    order = models.PositiveIntegerField(default=0)
    text = models.CharField(max_length=120)
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.question.assessment.name} - {self.text}"


class AssessmentResult(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="results"
    )
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    title = models.CharField(max_length=120)
    summary = models.TextField()
    advice = models.TextField(blank=True)

    class Meta:
        ordering = ["min_score"]

    def __str__(self):
        return f"{self.assessment.name}: {self.title}"


class AssessmentSubmission(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="submissions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessment_submissions"
    )
    total_score = models.IntegerField(default=0)
    result_title = models.CharField(max_length=120, blank=True)
    result_summary = models.TextField(blank=True)
    result_advice = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.assessment.name}"


class AssessmentAnswer(models.Model):
    submission = models.ForeignKey(
        AssessmentSubmission, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        AssessmentQuestion, on_delete=models.CASCADE, related_name="answers"
    )
    option = models.ForeignKey(
        AssessmentOption, on_delete=models.SET_NULL, null=True, related_name="answers"
    )
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer {self.submission_id} - {self.question_id}"


class Institution(models.Model):
    REGION_LOCAL = "local"
    REGION_PROVINCE = "province"
    REGION_NATIONAL = "national"

    REGION_CHOICES = [
        (REGION_LOCAL, "本地"),
        (REGION_PROVINCE, "本省"),
        (REGION_NATIONAL, "全国"),
    ]

    name = models.CharField(max_length=160)
    region_type = models.CharField(max_length=20, choices=REGION_CHOICES)
    province = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    service_hours = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["region_type", "name"]
        indexes = [
            models.Index(fields=["region_type"], name="institution_region_idx"),
            models.Index(fields=["province", "city"], name="institution_location_idx"),
        ]

    def __str__(self):
        return self.name


class Hotline(models.Model):
    REGION_LOCAL = "local"
    REGION_PROVINCE = "province"
    REGION_NATIONAL = "national"

    REGION_CHOICES = [
        (REGION_LOCAL, "本地"),
        (REGION_PROVINCE, "本省"),
        (REGION_NATIONAL, "全国"),
    ]

    name = models.CharField(max_length=160)
    region_type = models.CharField(max_length=20, choices=REGION_CHOICES)
    province = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=60)
    is_24h = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["region_type", "-is_emergency", "name"]
        indexes = [
            models.Index(fields=["region_type", "is_emergency"], name="hotline_region_emerg_idx"),
        ]

    def __str__(self):
        return self.name


class RelaxationMethod(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True, allow_unicode=True)
    description = models.TextField(blank=True)
    steps = models.TextField(blank=True)
    suggested_minutes = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RelaxationReminder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="relaxation_reminders"
    )
    method = models.ForeignKey(
        RelaxationMethod, on_delete=models.CASCADE, related_name="reminders"
    )
    reminder_time = models.TimeField()
    reminder_days = models.CharField(max_length=40, blank=True)
    target_minutes = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"], name="reminder_user_active_idx"),
        ]

    def __str__(self):
        return f"{self.user} - {self.method}"

    def reminder_days_display(self) -> str:
        if not self.reminder_days:
            return "每天"
        day_map = {
            "1": "周一",
            "2": "周二",
            "3": "周三",
            "4": "周四",
            "5": "周五",
            "6": "周六",
            "7": "周日",
        }
        parts = [day_map.get(day, day) for day in self.reminder_days.split(",") if day]
        return "、".join(parts) if parts else "每天"


class RelaxationLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="relaxation_logs"
    )
    method = models.ForeignKey(
        RelaxationMethod, on_delete=models.CASCADE, related_name="logs"
    )
    reminder = models.ForeignKey(
        RelaxationReminder, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs"
    )
    practiced_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=10)
    effect_rating = models.PositiveIntegerField(default=3)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-practiced_at"]
        indexes = [
            models.Index(fields=["user", "practiced_at"], name="relaxlog_user_time_idx"),
        ]

    def __str__(self):
        return f"{self.user} - {self.method} ({self.practiced_at:%Y-%m-%d})"
