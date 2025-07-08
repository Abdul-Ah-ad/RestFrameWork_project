from django.db import models
from cricdata_api.constants import (
    MATCH_FORMAT_CHOICES, FORMAT_UNKNOWN, PLAYER_ROLE_CHOICES
)


class Team(models.Model):
    external_team_id = models.IntegerField(
        unique=True, verbose_name='External Team ID'
    )
    full_team_name = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='Full Team Name'
    )
    team_abbreviation = models.CharField(
        max_length=20, null=True, blank=True, verbose_name='Team Abbreviation'
    )
    country_name = models.CharField(max_length=100, verbose_name='Country Name')
    last_fetched_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Last Time Fetched'
    )

    def __str__(self):
        return self.full_team_name or f"Team {self.external_team_id}"


class Player(models.Model):
    external_player_id = models.IntegerField(verbose_name='External Player ID')

    player_full_name = models.CharField(max_length=100, verbose_name='Player Full Name')
    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Associated Team'
    )

    format_category = models.CharField(
        max_length=10, choices=MATCH_FORMAT_CHOICES, default=FORMAT_UNKNOWN,
        verbose_name='Match Format'
    )

    player_role_type = models.PositiveSmallIntegerField(
        choices=PLAYER_ROLE_CHOICES, verbose_name='Player Role'
    )

    is_active_player = models.BooleanField(
        default=True, verbose_name='Is Currently Active?'
    )

    batting_style_description = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='Batting Style left/right handed'
    )
    bowling_style_description = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='Bowling Style left/right handed'
    )

    # Batting Stats
    total_matches_played = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Matches Played'
    )
    total_innings_batted = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Innings Batted'
    )
    total_runs_scored = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Total Runs Scored'
    )
    career_batting_average = models.FloatField(
        null=True, blank=True, verbose_name='Batting Average'
    )
    career_strike_rate = models.FloatField(
        null=True, blank=True, verbose_name='Strike Rate'
    )
    number_of_fifties = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Fifties Scored'
    )
    number_of_hundreds = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Hundreds Scored'
    )

    # Bowling Stats
    total_overs_bowled = models.FloatField(
        null=True, blank=True, verbose_name='Overs Bowled'
    )
    total_wickets_taken = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Wickets Taken'
    )
    bowling_economy_rate = models.FloatField(
        null=True, blank=True, verbose_name='Bowling Economy'
    )
    bowling_average_score = models.FloatField(
        null=True, blank=True, verbose_name='Bowling Average'
    )
    number_of_five_wicket_hauls = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='5-Wicket Hauls'
    )

    class Meta:
        unique_together = ('external_player_id', 'format_category')

    def __str__(self):
        return f"{self.player_full_name} ({self.get_format_category_display()})"
