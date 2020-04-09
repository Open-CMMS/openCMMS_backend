from django.db import models
from django.contrib.auth.models import Group,Permission, AbstractUser

# Create your models here.

class UserProfile(AbstractUser):
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
    perms = models.ManyToManyField(Permission,
        verbose_name='Team Type permissions',
        blank=True,
        help_text='Specific permissions for this team type.',
        related_name="teamType_set",
        related_query_name="teamType")

    def __str__(self):
        return self.name

    def apply(self):
        teams_with_this_teamtype = Team.objects.filter(team_type=self)
        for team in teams_with_this_teamtype:
            team.permissions.set(list(self.perms.all()))
            # for perm in self.perms.all():’
            #     team.permissions.add(perm)



class Team(Group):
    team_type = models.ForeignKey(TeamType,
        verbose_name="Team Type",
        on_delete=models.SET_NULL,
        null=True,
        help_text='Group of users, extends the auth.models.Group model',
        related_name="team_set",
        related_query_name="team")