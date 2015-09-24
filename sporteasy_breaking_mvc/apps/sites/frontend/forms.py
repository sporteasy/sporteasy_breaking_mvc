from django import forms
from sporteasy_breaking_mvc.utils.proxy import service


class MatchForm(forms.Form):
    team1 = forms.ChoiceField(choices=[])
    team2 = forms.ChoiceField(choices=[])
    start_at = forms.DateTimeField()
    day = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        champ_id = kwargs.pop('champ_id')
        super(MatchForm, self).__init__(*args, **kwargs)
        teams = service.championship.get_team_list(champ_id=champ_id)
        self.fields['team1'].choices = teams
        self.fields['team2'].choices = teams
