# Generated by Django 3.0.4 on 2020-05-04 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maintenancemanagement', '0005_auto_20200504_1216'),
    ]

    operations = [
        migrations.RenameField(
            model_name='files',
            old_name='is_notice',
            new_name='is_manual',
        ),
    ]
