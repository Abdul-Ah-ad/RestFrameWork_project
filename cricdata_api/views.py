import json
import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from cricdata_api.models import Team
from cricdata_api.serializers import TeamSerializer
from cricdata_api.utils import sync_teams_and_players_from_json

logger = logging.getLogger(__name__)


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Team model.

    Provides CRUD operations for teams and supports a custom
    endpoint for uploading team/player data via JSON file.

    Admins can:
    - GET: list or retrieve teams
    - POST: upload JSON file to bulk sync teams and players
    """

    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="upload",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_team_data(self, request):
        """
        Upload a `.json` file and synchronize team/player data.

        Request:
            - form-data with field: `file` (.json file)

        Returns:
            - 201 CREATED: If any new data is imported or existing data is updated.
            - 200 OK: If no changes were needed.
            - 400 BAD REQUEST: If file is missing or invalid.
        """
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "❌ No file was provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not uploaded_file.name.endswith(".json"):
            return Response(
                {"error": "❌ Only .json files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_data = uploaded_file.read().decode("utf-8")
            parsed_data = json.loads(file_data)
        except (UnicodeDecodeError, json.JSONDecodeError) as decode_err:
            logger.error(f"Failed to parse uploaded file: {decode_err}")
            return Response(
                {"error": f"❌ Failed to parse JSON: {str(decode_err)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception("Unexpected error during file upload.")
            return Response(
                {"error": f"❌ Unexpected error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = sync_teams_and_players_from_json(parsed_data)

        if updated:
            return Response(
                {"message": "✅ Data imported or updated successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"message": "🟢 No changes detected. Data is already up-to-date."},
            status=status.HTTP_200_OK,
        )
