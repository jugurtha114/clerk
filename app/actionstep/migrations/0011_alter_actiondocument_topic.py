# Generated by Django 3.2.10 on 2022-01-11 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actionstep', '0010_alter_actiondocument_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actiondocument',
            name='topic',
            field=models.CharField(choices=[('REPAIRS', 'Repairs'), ('BONDS', 'Bonds'), ('RENT_REDUCTION', 'Rent reduction'), ('EVICTION', 'Eviction'), ('OTHER', 'Other')], max_length=32),
        ),
    ]
