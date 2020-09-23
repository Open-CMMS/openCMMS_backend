from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class UserProfile(AbstractUser):
    """
    Define a user. Heritage of abstract user and addition of the field nb_tries to detect if the user use a false password to login.
    """
    nb_tries = models.IntegerField(default=0)
    USERNAME_FIELD = 'username'

    class Meta:
        ordering = ('pk',)

    def deactivate_user(self):
        """
            Deactivate a user.
        """
        self.is_active = False

    def reactivate_user(self):
        """
            Reactivate a user if it was deactivated, else, do nothing.
        """
        if not self.is_active:
            self.is_active = True


class TeamType(models.Model):
    name = models.CharField(max_length=200)
    perms = models.ManyToManyField(
        Permission,
        verbose_name='Team Type permissions',
        blank=True,
        help_text='Specific permissions for this team type.',
        related_name="teamType_set",
        related_query_name="teamType"
    )

    def __str__(self):
        return self.name

    def _apply_(self):
        teams_with_this_teamtype = self.team_set.all()
        for team in teams_with_this_teamtype:
            #team.permissions.set()
            team.permissions.set(list(self.perms.all()))


class Team(Group):
    team_type = models.ForeignKey(
        TeamType,
        verbose_name="Team Type",
        on_delete=models.CASCADE,
        help_text='Group of users, extends the auth.models.Group model',
        related_name="team_set",
        related_query_name="team",
        blank=False,
        null=True
    )

    def set_team_type(self, new_team_type):
        self.team_type = new_team_type
        self.save()
        new_team_type._apply_()
