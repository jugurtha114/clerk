# Generated by Django 3.1.4 on 2020-12-04 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caller', '0002_auto_20201111_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='topic',
            field=models.CharField(choices=[('REPAIRS', 'REPAIRS'), ('RENT_REDUCTION', 'RENT_REDUCTION'), ('OTHER', 'OTHER')], max_length=32),
        ),
    ]