from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from usersmanagement.serializers import TeamSerializer
from usersmanagement.models import Team, UserProfile


User = settings.AUTH_USER_MODEL


@api_view(['GET', 'POST'])
def team_list(request):
    """
        List all teams or create a new one
    """

    user = authenticate(username='user', password='pass')
    login(request, user)

    if request.user.has_perm("usersmanagement.view_team"):
        if request.method == 'GET':
            teams = Team.objects.all()
            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)

    if request.user.has_perm("usersmanagement.add_team"):
        if request.method == 'POST' :
            serializer = TeamSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)




@api_view(['GET', 'PUT', 'DELETE'])
def team_detail(request, pk):
    """
        Retrieve, update or delete a team
    """

    user = authenticate(username='user', password='pass')
    login(request, user)

    try:
        team = Team.objects.get(pk=pk)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.has_perm("usersmanagement.view_team"):
            serializer = TeamSerializer(team)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        if request.user.has_perm("usersmanagement.change_team"):
            serializer = TeamSerializer(team, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.user.has_perm("usersmanagement.delete_team"):
            team.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)




@api_view(['POST', 'PUT'])
def add_user_to_team(request):
    """
        Add and remove users from teams
    """

    user = authenticate(username='user', password='pass')
    login(request, user)

    if request.user.has_perm("usersmanagement.change_team"):
        if request.method == 'POST':
            user = UserProfile.objects.get(pk=request.data["id_user"])
            team = Team.objects.get(pk=request.data["id_team"])
            team.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)


        elif request.method == 'PUT':
            user = UserProfile.objects.get(pk=request.data["id_user"])
            team = Team.objects.get(pk=request.data["id_team"])
            team.user_set.remove(user)
            return Response(status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_401_UNAUTHORIZED)



def belongs_to_team(user, team):
    return user.groups.filter(id=team.id).exists()
