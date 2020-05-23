from django.db import models
from django.utils.translation import activate, ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from base.models import TimeStampedModel
from base.choices import TRANSPORTATION_CHOICES

User = get_user_model()


def category_image_path(instance, filename):
    return f"categories/{instance.name}/{filename}"


class CategoryManager(models.Manager):
    pass


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    description_for_skill = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=category_image_path, blank=True, null=True)
    parent = models.ForeignKey(
        "self", related_name="children", on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_children(self):
        return self.parent.all()


class Task(TimeStampedModel):
    TASK_STATUS = (
        ("p", _("Pending")),
        ("a", _("active")),
        ("f", _("Finished")),
    )

    SIZE_CHOICES = (
        ("s", _("Small")),
        ("m", _("Medium")),
        ("l", _("Large")),
    )

    task_poster = models.ForeignKey(
        User, related_name="client", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category, related_name="category", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    transportation = models.CharField(
        max_length=1, choices=TRANSPORTATION_CHOICES, blank=True, null=True
    )
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default="s")
    duration_time = models.IntegerField(validators=[MaxValueValidator(8)])
    status = models.CharField(max_length=1, choices=TASK_STATUS, default="p")
    start_time = models.DateTimeField(blank=True, null=True)
    finished_time = models.DateTimeField(
        blank=True, null=True
    )  # determine when tasker finish task
    phone_number = PhoneNumberField(blank=True, null=True)
    location = models.ForeignKey(
        "users.Address",
        related_name="location",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title


class TaskDeal(TimeStampedModel):
    task = models.ForeignKey(Task, related_name="task", on_delete=models.CASCADE)
    tasker = models.ForeignKey(User, related_name="tasker", on_delete=models.CASCADE)
    is_accepted = models.NullBooleanField()
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Deal ({self.id})"
