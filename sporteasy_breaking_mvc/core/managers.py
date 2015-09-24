from django.db.models import Q
from .models import EventTeam, Event, ChampionshipDay, Championship
from .light import LightDay, LightChampionship


class ChampionshipManager(object):

    def __init__(self, champ_id):
        self._champ = Championship.objects.get(id=champ_id)
        self._matches = []

    def get_info(self):
        return LightChampionship(self._champ)

    def add_match(self, team1, team2, start_at, day, **kwargs):

        team1 = EventTeam.objects.get(id=team1)
        team2 = EventTeam.objects.get(id=team2)

        try:
            champ_day = ChampionshipDay.objects.get(day=day)
        except ChampionshipDay.DoesNotExist:
            champ_day = ChampionshipDay()
            champ_day.day = day
            champ_day.championship = self._champ
            champ_day.save()

        event = Event()
        event.team1 = team1
        event.team2 = team2
        event.start_at = start_at
        event.day = champ_day
        event.save()

        self._matches.append(champ_day)

        return LightDay(champ_day)

    def invite_players(self):
        return True


class TeamManager(object):

    def get_championship_team_list(self, champ_id):
        teams = EventTeam.objects.filter(
            Q(opponent1__day__championship__id=champ_id) | Q(opponent2__day__championship__id=champ_id)
        ).order_by('name')

        # DISTINCT ON fields is not supported by this database backend:
        team_list = []
        for team in teams:
            tup = (team.id, team.name)
            if not tup in team_list:
                team_list.append(tup)
        return team_list
