# Generated by Django 3.1.1 on 2020-10-13 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenancemanagement', '0014_auto_20201013_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='over',
            field=models.NullBooleanField(default=False),
        ),
    ]