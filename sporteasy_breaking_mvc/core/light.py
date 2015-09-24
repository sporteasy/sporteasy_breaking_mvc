

class LightEvent(object):
    def __init__(self, model_instance):
        self.id = model_instance.id

        self.team1_name = model_instance.team1.name
        self.team2_name = model_instance.team2.name

        self.team1_id = model_instance.team1.id
        self.team2_id = model_instance.team2.id

        self.start_at = model_instance.start_at

        self.description = u"{} - {}".format(self.team1_name, self.team2_name)


class LightDay(object):
    def __init__(self, model_instance):
        self.id = model_instance.id
        self.day_number = model_instance.day
        self.events = [LightEvent(item) for item in model_instance.events.all()]


class LightChampionship(object):
    def __init__(self, model_instance):
        self.id = model_instance.id
        self.name = model_instance.name
        self.days = [LightDay(item) for item in model_instance.days.all()]
