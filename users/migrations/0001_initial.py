# Generated by Django 3.0.6 on 2020-05-16 12:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('country', models.CharField(default='Egypt', max_length=200)),
                ('city', models.CharField(blank=True, choices=[('mt', 'Matruh'), ('al', 'Alexandria'), ('bh', 'Beheira'), ('ks', 'Kafr El Sheikh'), ('dk', 'Dakahlia'), ('da', 'Damietta'), ('ps', 'Port Said'), ('ns', 'North Sinai'), ('gr', 'Gharbia'), ('mo', 'Monufia'), ('qa', 'Qalyubia'), ('sh', 'Sharqia'), ('is', 'Ismailia'), ('gi', 'Giza'), ('fa', 'Faiyum'), ('ca', 'Cairo'), ('su', 'Suez'), ('ss', 'South Sinai'), ('bs', 'Beni Suef'), ('mi', 'Minya'), ('wa', 'El Wadi El Gedid'), ('as', 'Asyut'), ('rs', 'Red Sea'), ('so', 'Sohag'), ('qn', 'Qena'), ('lx', 'Luxor'), ('sw', 'Aswan')], max_length=2)),
                ('street', models.CharField(blank=True, max_length=200)),
                ('district', models.CharField(blank=True, max_length=200, null=True)),
                ('building_number', models.PositiveIntegerField(blank=True, null=True)),
                ('apartment', models.PositiveIntegerField(blank=True, null=True)),
                ('floor', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, error_messages={'unique': 'A phone number already exists.'}, max_length=128, null=True, region=None, unique=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=users.models.profile_image_path)),
                ('gender', models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other Gender')], max_length=1, null=True)),
                ('transportation', models.CharField(blank=True, choices=[('b', 'Bicycle'), ('m', 'Motorcycle'), ('c', 'Car'), ('v', 'Van'), ('t', 'Truck')], max_length=1, null=True)),
                ('birth_date', models.DateTimeField(blank=True, null=True)),
                ('about', models.TextField(blank=True, null=True)),
                ('national_id', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(14, 'National ID is 14 number only.')])),
                ('id_front_image', models.ImageField(blank=True, null=True, upload_to=users.models.id_image_path)),
                ('id_back_image', models.ImageField(blank=True, null=True, upload_to=users.models.id_image_path)),
                ('accept_terms', models.BooleanField(default=False)),
                ('is_tasker', models.BooleanField(default=False)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='address', to='users.Address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]