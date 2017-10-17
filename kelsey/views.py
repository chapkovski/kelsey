from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from collections import OrderedDict
import random
import json


class MyPage(Page):
    ...
    # timeout_seconds = 60


def vars_for_all_templates(self):
    p_1 = int(round(1 - Constants.p, 1) * 100)
    p = int(round(Constants.p, 1) * 100)
    if self.round_number <= Constants.first_half:
        part_round_number = self.round_number
    else:
        part_round_number = self.round_number - Constants.first_half
    part_number = int(self.round_number > Constants.first_half) + 1
    max_rounds = Constants.first_half if \
        self.round_number <= Constants.first_half \
        else Constants.second_half - 1
    return {'p_1': p_1,
            'p': p,
            'part_round_number': part_round_number,
            'part_number': part_number,
            'max_rounds': max_rounds, }


def what_to_highlight(p):
    return {
        'highlighted_high': p.investment_payoff == p.high_payoff,
        'highlighted_low': p.investment_payoff == p.low_payoff,
        'prob_realized': True,
        'modal_shown': True,
    }


class LastPage(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class InstrPage(MyPage):
    def is_displayed(self):
        return self.extra_displayed and (self.round_number == 1 or
                                         self.round_number ==
                                         Constants.second_half)

    def extra_displayed(self):
        return True


class InitialInvestment(MyPage):
    form_model = models.Player
    form_fields = ['first_decision']

    def vars_for_template(self):
        curlab = Constants.first_decision_labels[self.player.treatment]
        return {
            'first_decision_label': curlab,
        }


class FinalInvestment(MyPage):
    form_model = models.Player
    form_fields = ['second_decision']

    def is_displayed(self):
        return self.player.treatment == 'T1' and self.player.first_decision

    def vars_for_template(self):
        return what_to_highlight(self.player)


class Results(MyPage):
    def is_displayed(self):
        self.player.set_payoffs()
        return True

    def vars_for_template(self):
        if self.player.first_decision:
            dict_to_return = what_to_highlight(self.player)
            if self.player.treatment == 'T2':
                dict_to_return['show_final_investment_block'] = True
            if (self.player.treatment == 'T0' and
                        self.player.investment_payoff >= Constants.final_cost):
                dict_to_return['show_final_investment_block'] = True
            if (self.player.treatment == 'T1' and
                    self.player.second_decision):
                dict_to_return['show_final_investment_block'] = True
            if self.player.treatment == 'T1':
                dict_to_return['modal_shown'] = False
            return dict_to_return


# INSTRUCTIONS AND QS BLOCK

class FirstRoundPage(MyPage):
    def is_displayed(self):
        return self.round_number == 1


class Consent(FirstRoundPage):
    form_model = models.Player
    form_fields = ['consent']

    def consent_error_message(self, value):
        if not value:
            return 'You must accept the consent form'


class Instr1(FirstRoundPage):
    ...


class Instr2(FirstRoundPage):
    ...


class Instr3(InstrPage):
    pass


class Instr4(InstrPage):
    pass


class Example(InstrPage):
    ...


class Separ(InstrPage):
    ...


class Q(InstrPage):
    form_model = models.Player

    def get_form_fields(self):
        return [i['qname'] for i in Constants.questions
                if i['treatment'] == self.player.treatment]


class QResults(InstrPage):
    def vars_for_template(self):
        fields_to_get = [i['qname'] for i in Constants.questions
                         if i['treatment'] == self.player.treatment]
        results = [getattr(self.player, f) for f in fields_to_get]
        qtexts = [i['verbose'] for i in Constants.questions
                  if i['treatment'] == self.player.treatment]
        qsolutions = [i['correct'] for i in Constants.questions
                      if i['treatment'] == self.player.treatment]
        is_correct = [True if i[0] == i[1] else False for i in zip(results, qsolutions)]
        data = zip(qtexts, results, qsolutions, is_correct)
        return {'data': data}


class Survey(LastPage):
    form_model = models.Player
    form_fields = [
        'gender',
        'nationality',
        'nationality_other',
        'race_ethnicity',
        'race_ethnicity_other',
        'major',
        'year_in_college',

        'stock_market_experience',
        'instructions',
        'recommendations',
        'random_contract',
        'random_round',
        'easiest',
        'end_beginning',
        'pleasant',
        'thinking',
    ]


class BeforeTask3(LastPage):
    ...


class Task3(LastPage):
    def vars_for_template(self):
        up = sorted(list(range(0, 101, 10)) + [5, 25, 75, 95])
        down = list(reversed(up))
        decisions = [None] + list(range(1, len(up[1:-1]) + 1)) + [None]
        names = list(range(len(up)))
        values = ['B'] + [None for i in range(len(up[1:-1]))] + ['A']
        data = zip(decisions, names, up, down, values, )
        return {'data': data}

    def before_next_page(self):

        lottery_choices = {}
        for k, v in self.request.POST.items():
            if k[:8] == 'lottery_':
                lottery_choices[int(k[8:])] = v
        self.player.stage3decision = json.dumps(dict(OrderedDict(lottery_choices)))
        self.player.set_final_payoff()


class ShowPayoff(LastPage):
    def vars_for_template(self):
        payoff_for_game = self.player.in_round(self.player.round_to_pay).temporary_payoff
        stage3decision = json.loads(str(self.player.stage3decision))
        return {'lottery_decision': stage3decision[str(self.player.stage3_chosen_lottery)],
                'payoff_for_game': payoff_for_game}


page_sequence = [
    Consent,
    Instr1,
    Instr2,
    Instr3,
    Example,
    Q,
    QResults,
    Separ,
    InitialInvestment,
    FinalInvestment,
    Results,
    Survey,
    BeforeTask3,
    Task3,
    ShowPayoff,
]
