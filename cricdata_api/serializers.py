from rest_framework import serializers

from cricdata_api.models import Player, Team
from cricdata_api.utils import save_or_update_all_players
from cricdata_api.constants import PLAYER_FORMATS


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        exclude = ['id']


class TeamSerializer(serializers.ModelSerializer):
    players = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Team
        fields = ['external_team_id', 'full_team_name', 'team_abbreviation', 'country_name', 'players']

    def create(self, validated_data):
        players_data = validated_data.pop('players', [])
        team, _ = Team.objects.update_or_create(
            external_team_id=validated_data['external_team_id'],
            defaults=validated_data
        )
        save_or_update_all_players(players_data, team)
        return team

    def update(self, instance, validated_data):
        players_data = validated_data.pop('players', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        save_or_update_all_players(players_data, instance)
        return instance
    
