# Generated by Django 3.1.4 on 2021-03-25 02:00

from django.db import migrations


def migrate_client_employment_data(apps, schema_editor):
    Client = apps.get_model("core", "Client")
    for client in Client.objects.all():
        if client.employment_status:
            client.employment_status_new = [client.employment_status]
        else:
            client.employment_status_new = []

        client.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_auto_20210325_1259"),
    ]

    operations = [
        migrations.RunPython(migrate_client_employment_data),
    ]