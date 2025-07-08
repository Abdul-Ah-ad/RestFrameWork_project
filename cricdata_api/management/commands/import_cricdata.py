import os
import json

from django.core.management.base import BaseCommand, CommandError
from cricdata_api.utils import sync_teams_and_players_from_json


class Command(BaseCommand):
    help = 'Import cricket teams and players from a specified JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('json_file_path', type=str, help='Path to the JSON file to import.')

    def handle(self, *args, **options):
        json_file_path = options['json_file_path']

        if not os.path.exists(json_file_path):
            raise CommandError(f"❌ File does not exist: {json_file_path}")

        self.stdout.write(f"📂 Loading file: {json_file_path}")
        
        try:
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f"❌ JSON decode error: {e}")

        updated = sync_teams_and_players_from_json(json_data)

        if updated:
            self.stdout.write(self.style.SUCCESS("✅ Data imported or updated successfully."))
        else:
            self.stdout.write(self.style.WARNING("🟢 No changes detected. Data is already up-to-date."))
