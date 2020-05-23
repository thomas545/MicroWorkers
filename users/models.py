from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxLengthValidator
from base.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from base import choices
from tasks.models import Category


User = get_user_model()


def id_image_path(instance, filename):
    return f"ID_images/{instance.national_id}/{filename}"


def profile_image_path(instance, filename):
    return f"profile/{instance.user.username}/{filename}"


class Address(TimeStampedModel):
    country = models.CharField(max_length=200, default="Egypt")
    city = models.CharField(
        max_length=2, choices=choices.GOVERNORATE_CHOICES, blank=True
    )
    street = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    building_number = models.PositiveIntegerField(blank=True, null=True)
    apartment = models.PositiveIntegerField(blank=True, null=True)
    floor = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"Address ({self.id})"


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    address = models.ForeignKey(
        Address, related_name="address", on_delete=models.CASCADE, blank=True, null=True
    )
    phone_number = PhoneNumberField(
        unique=True,
        error_messages={"unique": _("A phone number already exists.")},
        blank=True,
        null=True,
    )
    picture = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=choices.GENDER_CHOICES, blank=True, null=True
    )
    transportation = models.CharField(
        max_length=1, choices=choices.TRANSPORTATION_CHOICES, blank=True, null=True
    )
    birth_date = models.DateTimeField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    national_id = models.IntegerField(
        validators=[MaxLengthValidator(14, _("National ID is 14 number only."))],
        blank=True,
        null=True,
    )
    id_front_image = models.ImageField(upload_to=id_image_path, blank=True, null=True)
    id_back_image = models.ImageField(upload_to=id_image_path, blank=True, null=True)
    accept_terms = models.BooleanField(default=False)
    is_tasker = models.BooleanField(default=False)
    # skills = models.ManyToManyField(Category)
    # elite = models.BooleanField(default=False)
    # great = models.BooleanField(default=False)
    # our_fees = models.IntegerField(default=15)


    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)
