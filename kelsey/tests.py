from otree.api import Currency as c, currency_range, Submission
from . import views
from ._builtin import Bot
from .models import Constants, CONFIDENT_CHOICES
import random
from .views import *


class PlayerBot(Bot):
    def play_round(self):
        print('IM IN ROUND {}, TREATMENT:: {}'.format(self.round_number, self.player.treatment))
        if self.round_number == 1:
            yield (Consent, {'consent': True})
            yield Instr1
            yield Instr2
        if self.round_number == 1 or self.round_number == Constants.second_half:
            yield Instr3
            yield Example
            qs = [(i['qname'], i['option1'], i['option2']) for i in Constants.questions
                  if i['treatment'] == self.player.treatment]
            answers = {i[0]: random.choice([i[1], i[2]])
                       for i in qs}
            print('ANSWERS', answers)
            yield Q, answers
            yield QResults
            yield Separ
        yield InitialInvestment, {'first_decision': random.choice([True, False])}
        if self.player.treatment == 'T1' and self.player.first_decision:
            yield FinalInvestment, {'second_decision': random.choice([True, False])}
        yield Results

        if self.round_number == Constants.num_rounds:
            survey_data = {
                'gender': random.choice(['Male', 'Female', 'Other']),
                'nationality': random.choice(['US', 'Other']),
                'race_ethnicity': 'Caucasian',
                'stock_market_experience': random.choice(['Yes', 'No']),
                'instructions': random.choice(['Yes', 'No']),
                'random_contract': random.choice(CONFIDENT_CHOICES),
                'easiest': random.choice(['Part 1', 'Part 2']),
                'end_beginning': random.choice(['Beginning', 'End']),
                'pleasant': random.choice(['Extremely Pleasant',
                                           'Pleasant',
                                           'Somewhat Pleasant',
                                           'Neither',
                                           'Somewhat Unpleasant',
                                           'Unpleasant',
                                           'Extremely Unpleasant', ]),
            }
            yield Survey, survey_data
            risk_data = {'lottery_{}'.format(i): random.choice(['B', 'A']) for i in range(1, 14)}
            yield Submission(views.Task3, risk_data, check_html=False)
            yield ShowPayoff
