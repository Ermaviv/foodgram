# Generated by Django 4.2.20 on 2025-03-19 20:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_rename_subscribes_subscribe_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='title',
            new_name='name',
        ),
    ]
