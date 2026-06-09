from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("service/", views.service, name="service"),
    path("stop/", views.stop, name="stop"),
    path("logs/", views.get_logs, name="logs"),
    path("howtowork/", views.howtowork, name="howtowork"),
]