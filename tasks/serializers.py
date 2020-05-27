from rest_framework import serializers
from base.serializers import WritableNestedModelSerializer
from . import models
from users.models import Address


class ChildCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        exclude = ("parent",)


class CategorySerializer(serializers.ModelSerializer):
    children = ChildCategorySerializer(source="childrens", many=True)

    class Meta:
        model = models.Category
        exclude = ("parent",)


class TaskDealMiniSerializer(WritableNestedModelSerializer):
    class Meta:
        model = models.TaskDeal
        fields = "__all__"


class TaskLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ("country",)


class TaskSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    size_value = serializers.SerializerMethodField(read_only=True, required=False)
    status_value = serializers.SerializerMethodField(read_only=True, required=False)
    location = TaskLocationSerializer(read_only=True, required=False)
    deals = TaskDealMiniSerializer(source='task_deal',read_only=True, required=False, many=True)

    def get_size_value(self, obj):
        return obj.get_size_display()

    def get_status_value(self, obj):
        return obj.get_status_display()

    class Meta:
        model = models.Task
        fields = "__all__"


class TaskMiniSerializer(WritableNestedModelSerializer):
    location = TaskLocationSerializer()
    client = serializers.PrimaryKeyRelatedField(read_only=True, required=False)

    class Meta:
        model = models.Task
        fields = "__all__"

    def save(self):
        request = self.context.get("request")
        self.validated_data["client"] = request.user
        return super(TaskMiniSerializer, self).save()


class TaskDealSerializer(WritableNestedModelSerializer):
    task = TaskMiniSerializer()

    class Meta:
        model = models.TaskDeal
        fields = (
            "id",
            "tasker",
            "task",
        )


class UpdateDealSerializer(serializers.ModelSerializer):
    is_accepted = serializers.BooleanField(required=True)

    class Meta:
        model = models.TaskDeal
        fields = (
            "is_accepted",
            "reason",
        )
