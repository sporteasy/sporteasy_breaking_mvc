from django.http import HttpResponseRedirect
from django.views.generic import FormView, TemplateView
from sporteasy_breaking_mvc.utils.proxy import service
from .forms import MatchForm


class ChampionshipView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self):
        return {
            'championship': service.championship.get_info(1),
        }


class ChampionshipAddMatchView(FormView):

    template_name = 'add_match.html'
    form_class = MatchForm

    def get(self, request, *args, **kwargs):
        self.champ_id = kwargs['champ_id']
        return super(ChampionshipAddMatchView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.champ_id = kwargs['champ_id']
        return super(ChampionshipAddMatchView, self).post(request, *args, **kwargs)

    def get_context_data(self, form):
        return {
            'championship': service.championship.get_info(self.champ_id),
            'form': form,
        }

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(ChampionshipAddMatchView, self).get_form_kwargs()
        kwargs['champ_id'] = self.champ_id
        return kwargs

    def form_valid(self, form):
        service.championship.add_match(
            self.champ_id,
            **form.cleaned_data
        )
        return HttpResponseRedirect('/')


index = ChampionshipView.as_view()
add_match = ChampionshipAddMatchView.as_view()
