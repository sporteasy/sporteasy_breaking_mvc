from sporteasy_breaking_mvc.utils.service_endpoint import ServiceEndpoint
from ..managers import ChampionshipManager, TeamManager


class ChampionshipServiceEndpoint(ServiceEndpoint):

    def get_info(self, champ_id):
        manager = ChampionshipManager(champ_id)
        return manager.get_info()

    def add_match(self, champ_id, **match_data):
        manager = ChampionshipManager(champ_id)
        if manager.add_match(**match_data):
            manager.invite_players()
            return True
        return False

    def get_team_list(self, champ_id):
        return TeamManager().get_championship_team_list(champ_id)
