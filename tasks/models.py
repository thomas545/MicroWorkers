from django.db import models
from django.utils.translation import activate


def category_image_path(instance, filename):
    return f"categories/{instance.name}/{filename}"


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to=category_image_path)
    parent = models.ForeignKey(
        "self", related_name="children", on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_children(self):
        return self.parent.all()