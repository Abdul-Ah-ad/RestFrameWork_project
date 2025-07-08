from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cricdata_api.utils import import_team_and_players, load_json_file


class FetchTeamsPlayersView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data, error = load_json_file()
        if error:
            return Response({'error': f'❌ {error}'}, status=status.HTTP_404_NOT_FOUND)

        updated = import_team_and_players(data)
        if updated:
            return Response({'message': '✅ Data imported or updated successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': '🟢 No changes detected. Data is up-to-date.'}, status=status.HTTP_200_OK)
