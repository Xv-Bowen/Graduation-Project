from django.contrib import admin

from .models import (
    Article,
    Assessment,
    AssessmentAnswer,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentSubmission,
    Category,
    ChatLog,
    ConsultationNote,
    ConsultationTicket,
    Hotline,
    Institution,
    RelaxationLog,
    RelaxationMethod,
    RelaxationReminder,
    UserProfile,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("is_published", "category")
    search_fields = ("title", "summary", "content", "tags")
    prepopulated_fields = {"slug": ("title",)}


class ConsultationNoteInline(admin.TabularInline):
    model = ConsultationNote
    extra = 0


@admin.register(ConsultationTicket)
class ConsultationTicketAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "assigned_to", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "message", "contact_name", "contact_phone", "contact_email")
    inlines = [ConsultationNoteInline]


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ("provider", "user", "risk_flag", "created_at")
    list_filter = ("provider", "risk_flag")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "gender", "province", "city")
    search_fields = ("user__username", "province", "city")


class AssessmentOptionInline(admin.TabularInline):
    model = AssessmentOption
    extra = 0


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ("assessment", "order", "text")
    list_filter = ("assessment",)
    search_fields = ("text",)
    inlines = [AssessmentOptionInline]


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ("assessment", "min_score", "max_score", "title")
    list_filter = ("assessment",)


@admin.register(AssessmentSubmission)
class AssessmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("assessment", "user", "total_score", "created_at")
    list_filter = ("assessment",)


@admin.register(AssessmentAnswer)
class AssessmentAnswerAdmin(admin.ModelAdmin):
    list_display = ("submission", "question", "score")
    list_filter = ("submission",)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "region_type", "province", "city", "phone")
    list_filter = ("region_type", "province")
    search_fields = ("name", "address", "phone")


@admin.register(Hotline)
class HotlineAdmin(admin.ModelAdmin):
    list_display = ("name", "region_type", "phone", "is_24h", "is_emergency")
    list_filter = ("region_type", "is_24h", "is_emergency")
    search_fields = ("name", "phone", "description")


@admin.register(RelaxationMethod)
class RelaxationMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "suggested_minutes", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(RelaxationReminder)
class RelaxationReminderAdmin(admin.ModelAdmin):
    list_display = ("user", "method", "reminder_time", "target_minutes", "is_active")
    list_filter = ("is_active",)


@admin.register(RelaxationLog)
class RelaxationLogAdmin(admin.ModelAdmin):
    list_display = ("user", "method", "practiced_at", "duration_minutes", "effect_rating")
    list_filter = ("method",)
