from django.urls import path
from .views import views_user;
from .views import views_team;
from .views import views_perms;
from .views import views_grouptypes;


urlpatterns = [
]


urlpatterns_users = [
    path('users/', views_user.user_list, name='user-list'),
    path('users/<int:pk>/', views_user.user_detail, name='user-detail'),
    path('users/is_first_user', views_user.is_first_user, name='is_first_user'),
    path('users/username_suffix', views_user.username_suffix, name='username_suffix'),
    path('login', views_user.sign_in, name="sign_in"),
    path('logout', views_user.sign_out, name="sign_out"),
]


urlpatterns_perms = [
    path('perms/', views_perms.perms_list, name='perms-list'),
    path('perms/<int:pk>/', views_perms.perm_detail, name='perm-detail')
]


urlpatterns_teams = [
    path('add_user_to_team', views_team.add_user_to_team, name="add_user_to_team"),
    path('teams/', views_team.team_list, name='team-list'),
    path('teams/<int:pk>', views_team.team_detail, name='team-detail'),
]

url_patterns_grouptypes = [
    path('grouptypes/', views_grouptypes.grouptypes_list, name='grouptypes-list'),
    path('grouptypes/<int:pk>/', views_grouptypes.grouptypes_detail, name='grouptypes-detail')
]


urlpatterns += urlpatterns_users
urlpatterns += urlpatterns_perms
urlpatterns += urlpatterns_teams
urlpatterns += url_patterns_grouptypes