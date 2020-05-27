import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.response import Response
from model_mommy import mommy
from . import models

User = get_user_model()


class TestCreateTask(APITestCase):
    def setUp(self):
        self.task_poster = User.objects.create_user(
            username="thomas11", email="thomas@thomas.com", password="123456qqq"
        )
        self.tasker = User.objects.create_user(
            username="thomas12", email="thomas12@thomas.com", password="123456qqq"
        )
        self.task = mommy.make(
            models.Task, client=self.task_poster, title="task created"
        )
        self.category = mommy.make(models.Category, name="cleaning")
        self.deal = mommy.make(models.TaskDeal, task=self.task, tasker=self.tasker)
        # self.email_address = EmailAddress.objects.create(
        #     user=self.user, email=self.user.email, verified=True, primary=True
        # )
        # self.email_address = EmailAddress.objects.create(
        #     user=self.user, email=self.user.email, verified=True, primary=True
        # )

    def test_models(self):
        self.assertEqual(self.category.__str__(), self.category.name)
        self.assertEqual(self.task.__str__(), self.task.title)
        self.assertEqual(self.deal.__str__(), f"Deal ({self.deal.id})")        

    def test_create_task(self):
        url = reverse("deals-list")
        self.client.force_authenticate(user=self.task_poster)
        data = {
            "tasker": self.tasker.id,
            "task": {
                "location": {
                    "city": "mt",
                    "street": "st",
                    "district": "ds",
                    "building_number": 2,
                    "apartment": 1,
                    "floor": 2,
                },
                "title": "task new",
                "description": "new",
                "transportation": "b",
                "size": "m",
                "duration_time": 4,
                "status": "p",
                "start_time": "2020-05-27T10:17:38Z",
                "phone_number": "01234343234",
                "category": self.category.id,
            },
        }
        response = self.client.post(url, data)
        self.assertEqual(response.data['detail'], "Task posted successfully, waiting tasker for accept task.")

