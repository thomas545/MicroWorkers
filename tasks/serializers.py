from rest_framework import serializers
from . import models


class ChildCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        exclude = ("parent",)


class CategorySerializer(serializers.ModelSerializer):
    children = ChildCategorySerializer(source="childrens", many=True)

    class Meta:
        model = models.Category
        exclude = ("parent",)
        


class TaskSerializer(serializers.ModelSerializer):
    task_poster = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    size_value = serializers.SerializerMethodField(read_only=True, required=False)
    status_value = serializers.SerializerMethodField(read_only=True, required=False)

    def get_size_value(self, obj):
        return obj.get_size_display()

    def get_status_value(self, obj):
        return obj.get_status_display()

    class Meta:
        model = models.Task
        fields = "__all__"
