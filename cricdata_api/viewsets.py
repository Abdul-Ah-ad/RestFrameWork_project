from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from cricdata_api.models import Player, Team
from cricdata_api.serializers import \
    TeamWithPlayersSerializer  # ✅ Add this import
from cricdata_api.serializers import PlayerSerializer, TeamSerializer
from cricdata_api.utils import (get_best_xi, import_team_and_players,
                                load_json_file)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]


class ImportDataViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["post"])
    def import_data(self, request):
        data, error = load_json_file()
        if error:
            return Response({'error': f'❌ {error}'}, status=status.HTTP_404_NOT_FOUND)

        updated = import_team_and_players(data)
        if updated:
            return Response({'message': '✅ Data imported or updated successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': '🟢 No changes detected. Data is up-to-date.'}, status=status.HTTP_200_OK)


class TeamAnalysisViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @action(detail=False, methods=['get'], url_path='best')
    def best_xi(self, request):
        team_name = request.query_params.get('team')
        match_category = request.query_params.get('category', 'odi').strip().lower()

        if not team_name:
            return Response({'error': 'Query parameter "team" is required.'}, status=status.HTTP_400_BAD_REQUEST)

        result = get_best_xi(team_name, match_category)
        return Response(result, status=status.HTTP_200_OK)

