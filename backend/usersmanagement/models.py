from django.db import models
from django.contrib.auth.models import Group,Permission, AbstractUser

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



class GroupType(models.Model):
    name = models.CharField(max_length=200)
    perms = models.ManyToManyField(Permission,
        verbose_name='Group Type permissions',
        blank=True,
        help_text='Specific permissions for this group type.',
        related_name="groupType_set",
        related_query_name="groupType")

    def __str__(self):
        return self.name



class Team(Group):
    group_type = models.ForeignKey(GroupType,
        verbose_name="Group Type",
        on_delete=models.SET_NULL,
        null=True,
        help_text='Group of users, extends the auth.models.Group model',
        related_name="group_set",
        related_query_name="group")
