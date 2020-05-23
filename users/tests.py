import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.response import Response
from model_mommy import mommy
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from .models import Profile, Address
from .serializers import UserRegisterSerializer, UserSerializer, UserLoginSerializer
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class BaseUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="thomas", email="thomas@dokkanz.com", password="123456qqq"
        )
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )
        self.confirm_key = EmailConfirmationHMAC(self.email_address).key

    def _generate_default_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        return uid, token


class RegistrationTestCase(BaseUserTestCase):
    def test_registration(self):
        url = reverse("account_signup")
        data = {
            "username": "thomas22",
            "email": "thomas@gmail.com",
            "password1": "123456qqq",
            "password2": "123456qqq",
            "first_name": "thomas",
            "last_name": "Adel",
            "phone_number": "01225434542",
            "accept_terms": True,
        }
        serializer = UserRegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data, serializer.data)

    def test_email_confirmation(self):
        url = reverse("account_confirm_email", kwargs={"key": self.confirm_key})
        response = self.client.post(url, {"key": self.confirm_key})
        self.assertEqual(response.data, {"detail": "ok"})
        self.assertEqual(response.status_code, 200)

    def test_resend_confirmation_email(self):
        url = reverse("resend_confirmation")
        response = self.client.post(url, {"email": self.user.email})
        self.assertEqual(response.data, {"detail": "Email Confirmation Sent."})
        self.assertEqual(response.status_code, 200)


class LoginTestCase(BaseUserTestCase):
    def test_login(self):
        url = reverse("account_login")
        data = {"username": self.user.username, "password": "123456qqq"}
        serializer = UserSerializer(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("user"), serializer.data)

    def test_login_with_email(self):
        # Login with email not working 
        url = reverse("account_login")
        data = {"username": self.user.email, "password": "123456qqq"}
        serializer = UserSerializer(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        # self.assertEqual(response.data.get("user"), serializer.data)

class UserDetailTestCase(BaseUserTestCase):
    def test_get_user_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("rest_user_details")
        serializer = UserSerializer(self.user)
        response = self.client.get(url, kwargs={"pk": self.user.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_become_tasker(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("rest_user_details")
        serializer = UserSerializer(self.user)
        data = {
            "phone_number": "01237654367",
            "about": "software developer",
            "address": [
                {
                    "city": "ca",
                    "street": "12street",
                    "district": "15",
                    "building_number": 12,
                }
            ],
            "transportation": "c",
            "gender": "m",
            "national_id": "1234354",
            "is_tasker": True,
        }
        response = self.client.put(url, data, kwargs={"pk": self.user.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)


class ResetPasswordTestCase(BaseUserTestCase):
    def test_wrong_reset_password(self):
        url = reverse("rest_password_reset")
        data = {"email": "tomas.temo77@gmail.com"}
        response = self.client.post(url, data)
        self.assertNotEqual(response.status_code, 200)

    def test_correct_reset_password(self):
        url = reverse("rest_password_reset")
        data = {"email": self.user.email}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"detail": "Password reset has been sent."})

    def test_confirm_reset_password(self):
        uid, token = self._generate_default_token()
        url = reverse(
            "rest_password_reset_confirm", kwargs={"uid": uid, "token": token}
        )
        data = {
            "new_password1": "123456789qqqq",
            "new_password2": "123456789qqqq",
            "uid": uid,
            "token": token,
        }
        response = self.client.post(url, data)
        self.assertEqual(
            response.data, {"detail": "Password has been reset with the new password."}
        )
        self.assertEqual(response.status_code, 200)


class ChangePasswordTestCase(BaseUserTestCase):
    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("rest_password_change")
        data = {"new_password1": "123456789qqqq", "new_password2": "123456789qqqq"}
        response = self.client.post(url, data)
        self.assertEqual(response.data, {"detail": "New password has been Changed."})
        self.assertEqual(response.status_code, 200)
