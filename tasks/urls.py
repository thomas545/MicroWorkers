from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"tasks", views.TaskViewSet, basename='tasks')
router.register(r"deals", views.TaskDealViewSet, basename='deals')
router.register(r"category", views.CategoryView, basename='categories')

urlpatterns = [
    path('', include(router.urls)),
]