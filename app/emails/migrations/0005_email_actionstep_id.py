# Generated by Django 3.2.7 on 2021-09-07 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0004_auto_20210903_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='actionstep_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]