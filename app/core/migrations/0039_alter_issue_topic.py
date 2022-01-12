# Generated by Django 3.2.10 on 2022-01-10 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_alter_issuenote_note_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='topic',
            field=models.CharField(choices=[('REPAIRS', 'Repairs'), ('BONDS', 'Bonds'), ('RENT_REDUCTION', 'Rent reduction'), ('EVICTION', 'Eviction'), ('OTHER', 'Other')], max_length=32),
        ),
    ]