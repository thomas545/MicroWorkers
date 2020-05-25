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
    http_method_names = ["get", "put", "patch", "head", "options"]
    queryset = models.Task.objects.select_related("task_poster", "category", "location")

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
        if request.user not in [instance.task_deal.tasker, instance.task_poster]:
            raise PermissionDenied(_("You don't own task."))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def validation(self, task, request):
        if task.task_deal.tasker != request.user:
            raise PermissionDenied(_("Tasker only can finish the task"))
        if datetime.now(timezone.utc) < task.end_time:
            raise NotAcceptable(_("You can't finish the task before task end."))
        if task.status == "c":
            raise NotAcceptable(_("Task canceled."))
        if task.status == "f":
            raise NotAcceptable(_("You already finished the task."))

    def update(self, request, *args, **kwargs):
        """
         used to finish the task
        """
        task = self.get_object()
        self.validation(task, request)
        task.status = "f"
        task.save()
        # TODO send notification
        return Response({"detail": _("Task finished successfully!")})


class TaskDealViewSet(ModelViewSet):
    serializer_class = serializers.TaskDealSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    queryset = models.TaskDeal.objects.select_related("task", "tasker")

    def create(self, request, *args, **kwargs):
        """
        create a task 
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # TODO send notificationto tasker to accept/reject task 
        return Response(
            {"detail": _("Task posted successfully, waiting tasker for accept task.")}
        )

    def update(self, request, *args, **kwargs):
        """
        For tasker to accept or reject task
        """
        deal = self.get_object()
        if deal.tasker != request.user:
            raise PermissionDenied(_("This task doesn't belong to you"))
        if deal.is_accepted == True:
            raise NotAcceptable(_("You already accepted the task."))
        if deal.is_accepted == False:
            raise NotAcceptable(_("You already Rejected the task."))
        if deal.expired:
            raise PermissionDenied(_("Deal expired."))
        message = ''
        serializer = serializers.UpdateDealSerializer(deal, data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('is_accepted') == True:
            # TODO create transaction and send notification congrats
            message = "Deal Accepted"
        
        if serializer.validated_data.get('is_accepted') == False:
            # TODO send notification rejected
            message = "Deal Rejected"
        
        serializer.save()
        return Response({"detail": _(str(message))})

