from rest_framework import serializers

from cricdata_api.models import Player, Team
from cricdata_api.utils import save_or_update_all_players


class PlayerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Player model.

    Automatically serializes all fields except the 'id' field.
    """
    class Meta:
        model = Player
        exclude = ['id']


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Team model.

    Allows nested player data via a writable ListField (`players`) during create/update.
    On create/update, it syncs associated players using `save_or_update_all_players`.
    """
    players = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Team
        fields = [
            'external_team_id','full_team_name','team_abbreviation','country_name','players']

    def create(self, validated_data):
        """
        Creates or updates a Team instance based on external_team_id.
        Also syncs any provided player data.
        """
        players_data = validated_data.pop('players', [])
        team, _ = Team.objects.update_or_create(
            external_team_id=validated_data['external_team_id'],
            defaults=validated_data
        )
        if players_data:
            save_or_update_all_players(players_data, team)
        return team

    def update(self, instance, validated_data):
        """
        Updates a Team instance with new data.
        Also updates associated player records if provided.
        """
        players_data = validated_data.pop('players', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if players_data:
            save_or_update_all_players(players_data, instance)
        return instance

