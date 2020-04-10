# Generated by Django 3.0.4 on 2020-04-09 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('usersmanagement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('perms', models.ManyToManyField(blank=True, help_text='Specific permissions for this team type.', related_name='teamType_set', related_query_name='teamType', to='auth.Permission', verbose_name='Team Type permissions')),
            ],
        ),
        migrations.RemoveField(
            model_name='team',
            name='group_type',
        ),
        migrations.DeleteModel(
            name='GroupType',
        ),
        migrations.AddField(
            model_name='team',
            name='team_type',
            field=models.ForeignKey(help_text='Group of users, extends the auth.models.Group model', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_set', related_query_name='team', to='usersmanagement.TeamType', verbose_name='Team Type'),
        ),
    ]