from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("knowledge/", views.knowledge_list, name="knowledge_list"),
    path("knowledge/<str:slug>/", views.knowledge_detail, name="knowledge_detail"),
    path("wellness/", views.wellness_home, name="wellness_home"),
    path("wellness/assessments/", views.assessment_list, name="assessment_list"),
    path("wellness/assessments/history/", views.assessment_history, name="assessment_history"),
    path(
        "wellness/assessments/<str:slug>/result/<int:submission_id>/",
        views.assessment_result,
        name="assessment_result",
    ),
    path("wellness/assessments/<str:slug>/", views.assessment_detail, name="assessment_detail"),
    path("wellness/services/", views.service_directory, name="service_directory"),
    path("wellness/relaxation/", views.relaxation_center, name="relaxation_center"),
    path("consult/", views.consult_create, name="consult"),
    path("consult/thanks/", views.consult_thanks, name="consult_thanks"),
    path("account/register/", views.register, name="register"),
    path("account/login/", views.login, name="login"),
    path("account/logout/", views.logout, name="logout"),
    path("account/tickets/", views.my_tickets, name="my_tickets"),
    path("manage/tickets/", views.manage_ticket_list, name="manage_ticket_list"),
    path("manage/tickets/<int:ticket_id>/", views.manage_ticket_detail, name="manage_ticket_detail"),
    path("api/chat/", views.api_chat, name="api_chat"),
]
