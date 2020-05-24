from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, permissions, generics, views
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, PermissionDenied, ValidationError
from . import serializers, models


class CategoryView(ModelViewSet):
    serializer_class = serializers.CategorySerializer
    http_method_names = ["get", "head", "options"]
    queryset = models.Category.objects.roots().select_related("parent")



class TaskViewSet(ModelViewSet):
    serializer_class = serializers.TaskSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get", "post", "put", "patch", "head", "options", "trace"]
    queryset = models.Task.objects

    def get_queryset(self):
        """
        Get all tasks
        """
        return models.Task.objects.filter(task_poster=self.request.user).select_related(
            "task_poster", "category", "location"
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Get a task 
        """
        instance = self.get_object()
        if instance.task_poster != request.user:
            raise PermissionDenied(_("You don't own task."))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        create a task 
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_poster=request.user)
        return Response({"detail": _("Task posted successfully, complete process.")})

    def validation(self, task, request):
        if task.task_poster != request.user:
            raise PermissionDenied(_("You don't own task"))
        if request.data.get("status") == "a":
            raise PermissionDenied(_("You can't change task status."))
        if task.status == 'a' and request.data.get("status") != "f":
            raise NotAcceptable(_("task is active"))
        if request.data.get("status") == "f" and datetime.now(timezone.utc) < task.end_time:
            raise NotAcceptable(_("You can't finish the task before task time end."))
        if task.status == "c":
            raise NotAcceptable(_("You already canceled the task."))
        if task.status == "f":
            raise NotAcceptable(_("You already finished the task."))

    def update(self, request, *args, **kwargs):
        """
         update status to (finish or cancel). 
        """
        task = self.get_object()
        self.validation(task, request)
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Task updated.")})

