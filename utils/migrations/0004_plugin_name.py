# Generated by Django 3.1.1 on 2020-11-03 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0003_auto_20201103_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
