# Generated by Django 3.0.5 on 2020-04-30 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_submission_num_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='is_alert_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='is_data_sent',
            field=models.BooleanField(default=False),
        ),
    ]
