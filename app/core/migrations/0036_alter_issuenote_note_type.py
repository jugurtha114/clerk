# Generated by Django 3.2.6 on 2021-08-29 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_stage_and_outcome_mapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuenote',
            name='note_type',
            field=models.CharField(choices=[('PARALEGAL', 'File note'), ('REVIEW', 'Case review'), ('PERFORMANCE', 'Paralegal performance review'), ('EVENT', 'System generated event'), ('EMAIL', 'Email')], max_length=32),
        ),
    ]
