from django.utils.translation import ugettext_lazy as _
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import LoginSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions
from base.base64fields import Base64ImageField
from base.serializers import WritableNestedModelSerializer
from rest_auth.serializers import LoginSerializer
from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists
from allauth.account.adapter import get_adapter
from phonenumber_field.serializerfields import PhoneNumberField
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from . import models
from base import choices

User = get_user_model()


class UserRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = PhoneNumberField(required=True, write_only=True, 
                            validators=[UniqueValidator(models.Profile.objects.all(), 
                            message=_("Phone number already exist."))])
    accept_terms = serializers.BooleanField(required=True, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("E-mail address is taken.")
                )
        return email

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return data

    def create_profile_data(self, user):
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        user.save()
        user.profile.phone_number = self.validated_data.get('phone_number')
        user.profile.accept_terms = self.validated_data.get('accept_terms')
        user.profile.save()

    def custom_signup(self, request, user):
        self.create_profile_data(user)


class UserLoginSerializer(LoginSerializer):
    email = None

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        user = None

        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.EMAIL
            ):
                user = self._validate_email(email, password)

            # Authentication through username
            elif (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.USERNAME
            ):
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = User.objects.get(email__iexact=email).get_username()
                except User.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, "", password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _("User account is banned by admin.")
                raise exceptions.ValidationError(msg)
        else:
            msg = _("Wrong username or password.")
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if "rest_auth.registration" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            if (
                app_settings.EMAIL_VERIFICATION
                == app_settings.EmailVerificationMethod.MANDATORY
            ):
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_("E-mail is not verified."))

        attrs["user"] = user
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        exclude = ("created","modified",)


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer include endpoint `/user/` include (GET, PUT) methods  
    we will user this for Become a tasker and update profile
    if become a tasker send is_tasker = True 
    if update profile, fields you will update only (first name , last name, email)
    """
    
    phone_number = PhoneNumberField(required=False, source='profile.phone_number',)
    picture = Base64ImageField(required=False, source='profile.picture')
    about = serializers.CharField(required=False, source='profile.about')
    address = AddressSerializer(required=False, many=True)
    birth_date = serializers.DateField(source='profile.birth_date', required=False)
    transportation = serializers.ChoiceField(choices=choices.TRANSPORTATION_CHOICES, source='profile.transportation', required=False)
    gender = serializers.ChoiceField(choices=choices.GENDER_CHOICES, source='profile.gender', required=False)
    national_id = serializers.IntegerField(source='profile.national_id', required=False)
    id_front_image = Base64ImageField(required=False, source='profile.id_front_image')
    id_back_image = Base64ImageField(required=False, source='profile.id_back_image')
    accept_terms = serializers.BooleanField(source='profile.accept_terms', required=False)
    is_tasker = serializers.BooleanField(source='profile.is_tasker', required=False)

    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'username', 'email', 'phone_number', 
                    'picture', 'about', 'address', 'birth_date', 'transportation', 
                    'gender', 'national_id', 'id_front_image', 'id_back_image', 
                    'accept_terms', 'is_tasker',)
        read_only_fields = ('username',)

    def validate(self, data):
        if models.Profile.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError(
                _("Phone Number already used before.")
            )
        return data


    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        phone_number = profile_data.pop('phone_number', None)
        profile_picture = profile_data.get('picture', None)
        about = profile_data.get('about', None)
        address = profile_data.get('address', None)
        birth_date = profile_data.get('birth_date', None)
        transportation = profile_data.get('transportation', None)
        gender = profile_data.get('gender', None)
        id_number = profile_data.get('id_number', None)
        is_tasker = profile_data.get('is_tasker', None)
        new_email = validated_data.pop('email', None)


        user = super(UserSerializer, self).update(instance, validated_data)

        if new_email:
            if EmailAddress.objects.filter(user=user, email=new_email, verified=False).exists():
                raise exceptions.ValidationError(_("Email confirmation has been sent"))
            
            if not EmailAddress.objects.filter(user=user, email=new_email, verified=False).exists():
                email_address = EmailAddress.objects.add_email(self.context.get('request'), user, new_email)
                confirmation = EmailConfirmationHMAC(email_address)
                print("confirmation key ->", confirmation.key)
                # TODO send mail to confirmation


        profile = user.profile
        if profile_data:
            if phone_number:
                profile.phone_number = phone_number
            if profile_picture:
                profile.picture = profile_picture
            if about:
                profile.about = about
            if address:
                profile.address = address
            if birth_date:
                profile.birth_date = birth_date
            if transportation:
                profile.transportation = transportation
            if gender:
                profile.gender = gender
            if id_number:
                profile.id_number = id_number
            if is_tasker:
                profile.is_tasker = is_tasker
        profile.save()
        return instance

    # def to_representation(self, instance):
    #     data = super(UserSerializer, self).to_representation(instance)
    #     print(instance.profile.address)
    #     data['address'] = AddressSerializer(instance=instance.profile.address).data
    #     return data
    
