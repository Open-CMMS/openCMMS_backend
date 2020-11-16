"""This file contain the model for the usermanagement app."""
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class UserProfile(AbstractUser):
    """
    Define a user.

    Here, we use heritage of abstract user and addition of the field nb_tries
    to detect if the user use a false password to login.
    """

    nb_tries = models.IntegerField(default=0)
    USERNAME_FIELD = 'username'

    class Meta:
        """Add metadata on the class."""

        ordering = ('pk',)

    def deactivate_user(self):
        """Deactivate a user."""
        self.is_active = False

    def reactivate_user(self):
        """Reactivate a user if it was deactivated, else, do nothing."""
        if not self.is_active:
            self.is_active = True

    def __repr__(self):
        """Define formal representation of a user."""
        return "<User: {id} {name}>".format(id=self.id, name=self.username)


class TeamType(models.Model):
    """
    Define a team type.

    It inherits of Model class and redefine _apply_ and __str__ methods.
    """

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
        """Return the name of the teamtype."""
        return self.name

    def __repr__(self):
        """Define formal representation of a team type."""
        return "<TeamType: {id} {name}>".format(id=self.id, name=self.name)

    def _apply_(self):
        teams_with_this_teamtype = self.team_set.all()
        for team in teams_with_this_teamtype:
            # team.permissions.set()
            team.permissions.set(list(self.perms.all()))


class Team(Group):
    """
    Define a team.

    It inherits of Group class and define set_team_type.
    """

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
        """Assign the team type to the team."""
        self.team_type = new_team_type
        self.save()
        new_team_type._apply_()

    def __repr__(self):
        """Define formal representation of a team."""
        return "<Team: {id} {name}>".format(id=self.id, name=self.team_type)
