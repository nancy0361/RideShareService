# Generated by Django 2.1.5 on 2019-01-27 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideService', '0006_auto_20190127_0430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
