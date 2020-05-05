from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from usersmanagement.serializers import TeamSerializer
from usersmanagement.models import Team, UserProfile

@api_view(['GET', 'POST'])
def team_list(request):
    """
        \n# List all the teams or create a new one

        Parameter :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        GET request : list all teams and return the data
        POST request :
        - create a new team, send HTTP 201.  If the request is not valid, send HTTP 400.
        - If the user doesn't have the permissions, it will send HTTP 401.
        - The request must contain name (the name of the team, string) and team_type (the id of the team_type, int), can contain user_set (the users' id list, [])
    """
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
        \n# Retrieve, update or delete a team

        Parameters :
        request (HttpRequest) : the request coming from the front-end
        pk (int) : the id of the team

        Return :
        response (Response) : the response.

        GET request : return the team's data.
        PUT request : change the team with the data on the request or if the data isn't well formed, send HTTP 400.
        DELETE request: delete the team type and send HTTP 204.

        If the user doesn't have the permissions, it will send HTTP 401.
        If the id doesn't exist, it will send HTTP 404.

        The PUT request can contain one or more of the following fields :
            - name (string) : the name of the team
            - team_type (int) : the id of the team_type
            - user_set ([]): the users' id
    """
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
        \n# Add and remove users from team

        Parameters :
        request (HttpRequest) : the request coming from the front-end

        Return :
        response (Response) : the response.

        POST request : add a user to a team and send HTTP 201, must contain id_user (the id of the user to add, int) and id_team (the id of the team where the user will be add, int)
        PUT request : remove a user from a team and send HTTP 201, must contain id_user (the id of the user to remove, int) and id_team (the id of the team where the user will be remove, int)

        If the user doesn't have the permissions, it will send HTTP 401.
    """
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
    """
        \n# Check if a user belong to the team

        Parameters :
        user (UserProfile) : the user to check
        team (Team) : the team to check

        Return :
        boolean : True if the user belongs to team, else False
    """
    return user.groups.filter(id=team.id).exists()
