
from django.db import models


class EventTeam(models.Model):
    name = models.CharField(max_length=100)


class Event(models.Model):
    team1 = models.ForeignKey(EventTeam, null=True, related_name='opponent1')
    team2 = models.ForeignKey(EventTeam, null=True, related_name='opponent2')
    start_at = models.DateTimeField(null=True, blank=True)
    day = models.ForeignKey('ChampionshipDay', related_name='events', null=True)


class ChampionshipDay(models.Model):
    day = models.PositiveIntegerField()
    championship = models.ForeignKey('Championship', related_name='days')


class Championship(models.Model):
    name = models.CharField(max_length=100)
