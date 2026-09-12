from django.urls import path

from . import views

urlpatterns = [
    path("", views.builder, name="builder"),
    path("projects/<slug:slug>/", views.dashboard, name="dashboard"),
    path("projects/<slug:slug>/tasks/", views.dashboard_tasks_partial, name="dashboard_tasks"),
]
