# Generated by Django 3.0.4 on 2020-04-29 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usersmanagement', '0002_auto_20200409_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='team_type',
            field=models.ForeignKey(help_text='Group of users, extends the auth.models.Group model', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_set', related_query_name='team', to='usersmanagement.TeamType', verbose_name='Team Type'),
        ),
    ]
