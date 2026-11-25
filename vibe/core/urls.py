from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("topics/", views.topics, name="topics"),
    path("quiz/<int:topic_id>/", views.quiz, name="quiz"),
    path("result/", views.result, name="result"),
    path("my-results/", views.my_results, name="my_results"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "accounts/login/",
        LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        LogoutView.as_view(next_page="/"),
        name="logout",
    ),
]
