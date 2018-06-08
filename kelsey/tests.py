from otree.api import Currency as c, currency_range, Submission
from . import views
from ._builtin import Bot
from .models import Constants
import random


class PlayerBot(Bot):
    def play_round(self):
        # yield (views.MyPage)
        # yield (views.Results)



        if self.round_number == Constants.num_rounds:
            fulfill_dict = dict()
            for i in range(1, 14):
                fulfill_dict['lottery_{}'.format(i)] = random.choice(['B', 'A'])
            print(fulfill_dict)
            yield Submission(views.Task3, fulfill_dict, check_html=False)
