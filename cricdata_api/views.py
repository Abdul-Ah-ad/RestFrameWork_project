from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cricdata_api.utils import load_json_file, sync_teams_and_players_from_json


class SyncTeamsAndPlayersView(APIView):
    """
    API endpoint to import or update teams and players from combined_stats.json.
    Access restricted to admin users only.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        json_data, error = load_json_file()

        if error:
            return Response(
                {'error': f'❌ Failed to load JSON: {error}'},
                status=status.HTTP_404_NOT_FOUND
            )

        updated = sync_teams_and_players_from_json(json_data)

        return Response(
            {
                'message': (
                    '✅ Data imported or updated successfully.'
                    if updated else
                    '🟢 No changes detected. Data is already up-to-date.'
                )
            },
            status=status.HTTP_201_CREATED if updated else status.HTTP_200_OK
        )


