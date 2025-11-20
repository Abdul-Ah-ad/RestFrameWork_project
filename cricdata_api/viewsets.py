import json

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from cricdata_api.constants import MatchFormat
from cricdata_api.models import Player, Team
from cricdata_api.permission import AdminPostPermissionMixin
from cricdata_api.serializers import PlayerSerializer, TeamSerializer
from cricdata_api.utils import (get_best_eleven_players,sync_teams_and_players_from_json)


class TeamViewSet(AdminPostPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for performing CRUD operations on Team model.
    
    - Allows all users to perform GET (list/retrieve).
    - Allows only admins to perform POST.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PlayerViewSet(AdminPostPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for performing CRUD operations on Player model.
    
    - Allows all users to perform GET (list/retrieve).
    - Allows only admins to perform POST.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class InjectDataViewSet(viewsets.ViewSet):
    """
    Admin-only ViewSet to upload and import team/player data from a JSON file.

    Endpoint:
        - POST /api/inject-teams-data/upload/
          Accepts form-data file field named 'file'.
    """

    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'], url_path='upload', parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        Uploads a JSON file and syncs data with the database.

        Request:
            - form-data with field name: 'file'

        Returns:
            - 201 CREATED if data is imported or updated.
            - 200 OK if no changes were needed.
            - 400 BAD REQUEST if file is invalid or missing.
        """
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            json_data = json.load(uploaded_file)
        except json.JSONDecodeError as e:
            return Response({'error': f'Invalid JSON format: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        updated = sync_teams_and_players_from_json(json_data)

        if updated:
            return Response(
                {'message': '✅ Data imported or updated successfully.'},status=status.HTTP_201_CREATED)
        return Response(
            {'message': '🟢 No changes detected. Data is already up-to-date.'},status=status.HTTP_200_OK)


class TeamAnalysisViewSet(viewsets.ViewSet):
    """
    ViewSet that provides analysis functionality for teams.

    Includes:
        - Best XI player selection based on team name and match category.
    
    Permissions:
        - Public access (AllowAny).
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='best')
    def validating_fetch_request(self, request):
        """
        Query Parameters:
            - team (str): Name of the team (required).
            - category (str): Match category like 'odi', 'test', etc. (optional).

        Returns:
            - 400 BAD REQUEST if 'team' is missing.
            - 200 OK with best XI data if successful.
        """
        team_name = request.query_params.get('team')
        match_category = request.query_params.get('category', MatchFormat.DEFAULT).strip().lower()

        if not team_name:
            return Response(
                {'error': 'Query parameter team is required.'},status=status.HTTP_400_BAD_REQUEST)

        result = get_best_eleven_players(team_name, match_category)
        return Response(result, status=status.HTTP_200_OK)

