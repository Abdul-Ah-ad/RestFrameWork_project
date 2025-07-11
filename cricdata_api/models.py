from django.db import models

from cricdata_api.constants import MatchFormat, PlayerRole


class Team(models.Model):
    """
    Represents a cricket team.

    Attributes:
        external_team_id (int): Unique identifier from external source.
        full_team_name (str): Full name of the team.
        team_abbreviation (str): Abbreviation or short code for the team.
        country_name (str): Country the team represents.
        last_fetched_at (datetime): Timestamp when the team data was last updated.
    """
    external_team_id = models.IntegerField(unique=True, verbose_name='External Team ID')
    full_team_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Full Team Name')
    team_abbreviation = models.CharField(max_length=20, null=True, blank=True, verbose_name='Team Abbreviation')
    country_name = models.CharField(max_length=100, verbose_name='Country Name')
    last_fetched_at = models.DateTimeField(null=True, blank=True, verbose_name='Last Time Fetched')

    def __str__(self):
        """
        Returns a human-readable name for the team.
        """
        return self.full_team_name or f'Team {self.external_team_id}'


class Player(models.Model):
    """
    Represents a cricket player and their statistical data.

    Attributes:
        external_player_id (int): Unique player ID from external source.
        player_full_name (str): Full name of the player.
        team (Team): Foreign key to the associated team.
        format_category (str): Match format category (e.g., ODI, Test).
        player_role_type (int): Player role (e.g., batsman, bowler).
        is_active_player (bool): Whether the player is currently active.
        batting_style_description (str): Batting hand/style description.
        bowling_style_description (str): Bowling hand/style description.
        total_matches_played (int): Number of matches played.
        total_innings_batted (int): Number of innings batted.
        total_runs_scored (int): Total runs scored in career.
        career_batting_average (float): Batting average.
        career_strike_rate (float): Batting strike rate.
        number_of_fifties (int): Number of 50s scored.
        number_of_hundreds (int): Number of 100s scored.
        total_overs_bowled (float): Total overs bowled in career.
        total_wickets_taken (int): Number of wickets taken.
        bowling_economy_rate (float): Economy rate in bowling.
        bowling_average_score (float): Bowling average.
        number_of_five_wicket_hauls (int): Number of 5-wicket hauls.

    Meta:
        Ensures uniqueness of a player per format using external_player_id and format_category.
    """

    external_player_id = models.IntegerField(verbose_name='External Player ID')
    player_full_name = models.CharField(max_length=100, verbose_name='Player Full Name')
    player_associated_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='players', verbose_name='Associated Team')
    format_category = models.IntegerField(choices=MatchFormat.INTEGER_CHOICES,default=MatchFormat.UNKNOWN,verbose_name='Match Format')    
    player_role_type = models.PositiveSmallIntegerField(choices=PlayerRole.CHOICES, verbose_name='Player Role')
    is_active_player = models.BooleanField(default=True, verbose_name='Is Currently Active?')

    batting_style_description = models.CharField(max_length=100, null=True, blank=True, verbose_name='Batting Style (L/R)')
    bowling_style_description = models.CharField(max_length=100, null=True, blank=True, verbose_name='Bowling Style (L/R)')

    total_matches_played = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Matches Played')
    total_innings_batted = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Innings Batted')
    total_runs_scored = models.PositiveIntegerField(null=True, blank=True, verbose_name='Total Runs Scored')
    career_batting_average = models.FloatField(null=True, blank=True, verbose_name='Batting Average')
    career_strike_rate = models.FloatField(null=True, blank=True, verbose_name='Strike Rate')
    number_of_fifties = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Fifties Scored')
    number_of_hundreds = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Hundreds Scored')

    total_overs_bowled = models.FloatField(null=True, blank=True, verbose_name='Overs Bowled')
    total_wickets_taken = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Wickets Taken')
    bowling_economy_rate = models.FloatField(null=True, blank=True, verbose_name='Bowling Economy')
    bowling_average_score = models.FloatField(null=True, blank=True, verbose_name='Bowling Average')
    number_of_five_wicket_hauls = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='5-Wicket Hauls')

    class Meta:
        """
        Ensures each player is unique per match format based on external_player_id and format_category.
        """
        unique_together = ('external_player_id', 'format_category')

    def __str__(self):
        """
        Returns a string representation of the player along with their match format.
        """
        return f'{self.player_full_name} ({self.get_format_category_display()})'

