from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import RelaxationLog, RelaxationMethod, RelaxationReminder, ConsultationTicket


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="用户名")


class ConsultationTicketForm(forms.ModelForm):
    class Meta:
        model = ConsultationTicket
        fields = ("title", "message", "contact_name", "contact_phone", "contact_email")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }


class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = ConsultationTicket
        fields = ("status", "assigned_to")


class ConsultationNoteForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="处理记录")
    is_internal = forms.BooleanField(required=False, initial=True, label="仅内部可见")


class ArticleSearchForm(forms.Form):
    query = forms.CharField(required=False, label="搜索关键词")
    category = forms.CharField(required=False, label="分类")


class RelaxationReminderForm(forms.ModelForm):
    DAY_CHOICES = [
        ("1", "周一"),
        ("2", "周二"),
        ("3", "周三"),
        ("4", "周四"),
        ("5", "周五"),
        ("6", "周六"),
        ("7", "周日"),
    ]

    reminder_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="提醒日期",
    )

    class Meta:
        model = RelaxationReminder
        fields = ("method", "reminder_time", "reminder_days", "target_minutes", "is_active")
        widgets = {
            "reminder_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["method"].queryset = RelaxationMethod.objects.filter(is_active=True)
        if self.instance and self.instance.reminder_days:
            self.initial["reminder_days"] = self.instance.reminder_days.split(",")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        days = self.cleaned_data.get("reminder_days") or []
        instance.reminder_days = ",".join(days)
        if commit:
            instance.save()
        return instance


class RelaxationLogForm(forms.ModelForm):
    EFFECT_CHOICES = [
        (1, "效果不明显"),
        (2, "略有好转"),
        (3, "感觉还可以"),
        (4, "明显放松"),
        (5, "非常有帮助"),
    ]

    effect_rating = forms.TypedChoiceField(
        choices=EFFECT_CHOICES,
        coerce=int,
        label="效果感受",
    )
    practiced_at = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="练习时间",
    )

    class Meta:
        model = RelaxationLog
        fields = ("method", "reminder", "practiced_at", "duration_minutes", "effect_rating", "notes")
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["method"].queryset = RelaxationMethod.objects.filter(is_active=True)
        if self.user:
            self.fields["reminder"].queryset = RelaxationReminder.objects.filter(user=self.user)
