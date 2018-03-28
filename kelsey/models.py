from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
from math import ceil
from itertools import product
import csv
from collections import OrderedDict
from django import forms as djforms
import json

author = 'Philipp Chapkovski, UZH'

doc = """
Kelsey-Oliva lottery game
"""


class Constants(BaseConstants):
    name_in_url = 'kelsey'
    players_per_group = None
    num_rounds = 2
    # till what round we play T0 and then change to whatever treatment
    # we have?::
    first_half = 1
    second_half = first_half + 1
    assert first_half <= num_rounds, "SOMETHING WRONG WITH NUMBER OF ROUNDS!"
    p = 0.5  # probability of low payoff
    initial_cost = 25
    final_cost = 45
    treatments = ['T1', 'T2']
    lottery_choices = sorted(list(range(0, 101, 10)) + [5, 25, 75, 95])
    len_lottery = len(lottery_choices[1:-1])
    lotteryA = c(2.50)
    lotteryB = {'low': c(2), 'high': c(4)}
    first_decision_labels = {
        'T0': """Do you want to pay an initial investment cost of {}  with the final
    investment cost determined based on what value payoff
    is drawn?""".format(c(initial_cost)),
        'T1': """Do you want to pay an initial investment cost of {} to
    take this contract?""".format(c(initial_cost)),
        'T2': """Do you want to pay an initial investment cost of {} and a final investment
     cost of {} to release the randomly determined payoff?""".format(c(initial_cost), c(final_cost)),
    }
    wallet = c(1000)  # initial wallet
    low_payoff_set = [0, 18, 36]
    high_payoff_set = [90, 108, 126]
    payoffs_sets = list(product(low_payoff_set, high_payoff_set))
    # values for control questions:
    q_parameters = {'initial_cost': initial_cost,
                    'final_cost': final_cost,
                    'high_payoff': 90,
                    'low_payoff': 0,
                    'PT0ExampleHigh': 20,
                    'PT0ExampleLow': -16,
                    }
    for key, value in q_parameters.items():
        q_parameters[key] = c(value)
    with open('kelsey/qs_to_add.csv') as f:
        questions = list(csv.DictReader(f))
    for q in questions:
        q['verbose'] = q['verbose'].format(
            initial=q_parameters['initial_cost'],
            final=q_parameters['final_cost'],
            hpayoff=q_parameters['high_payoff'],
            lpayoff=q_parameters['low_payoff'],
        )
        # a = dict(questions)
        # questions = OrderedDict(sorted(questions.items(), key=lambda item: item['number']))


def weighted_choice(a, b):
    assert 0 <= Constants.p <= 1, 'SOMETHING WRONG WITH PROBABILITIES, DUDE'
    selector = random.random()
    if selector <= Constants.p:
        return a
    return b


class Subsession(BaseSubsession):
    def before_session_starts(self):
        first_half = self.session.config.get('first_half', 'T0')
        random_treatment = self.session.config.get('second_half') == 'random'
        second_half = self.session.config.get('second_half', 'T0')
        for p in self.session.get_participants():
            if random_treatment:
                p.vars.setdefault('treatment', random.choice(Constants.treatments))
        for p in self.get_players():
            curpayoffset = (Constants.payoffs_sets.copy())
            random.shuffle(curpayoffset)
            p.participant.vars.setdefault('payoffsets', curpayoffset)
            i = p.round_number % Constants.first_half - 1
            p.low_payoff = p.participant.vars['payoffsets'][i][0]
            p.high_payoff = p.participant.vars['payoffsets'][i][1]
            p.investment_payoff = weighted_choice(p.low_payoff, p.high_payoff)
            if p.round_number <= Constants.first_half:
                p.treatment = first_half
            else:
                if random_treatment:
                    p.treatment = p.participant.vars.get('treatment')
                else:
                    p.treatment = second_half


class Group(BaseGroup):
    pass


CONFIDENT_CHOICES = ['Very Confident',
                     'Confident',
                     'Somewhat Unconfident',
                     'Unconfident',
                     ]


class Player(BasePlayer):
    game_payoff=models.CurrencyField(doc='for ingame payoffs only')
    vars_dump = models.TextField(doc='to store participant vars')
    consent = models.BooleanField(widget=djforms.CheckboxInput,
                                  initial=False
                                  )
    treatment = models.CharField()
    investment_payoff = models.IntegerField()
    low_payoff = models.IntegerField()
    high_payoff = models.IntegerField()
    first_decision = models.BooleanField()
    second_decision = models.BooleanField(
        verbose_name="""Do you want to pay the final
        investment cost of ${} to
         release this payoff?""".format(Constants.final_cost)
    )

    round_to_pay_part1 = models.IntegerField(min=1, max=Constants.first_half,
                                             doc='Random number defining payoff for the first part of the game')
    round_to_pay_part2 = models.IntegerField(min=Constants.second_half, max=Constants.num_rounds,
                                             doc='Random number defining payoff for the second part of the game')
    # set of control questions for each treatment

    for i in Constants.questions:
        locals()[i['qname']] = models.CharField(verbose_name=i['verbose'],
                                                widget=widgets.RadioSelectHorizontal(),
                                                choices=[i['option1'], i['option2']])

        # filtered_dict = {k:v for (k,v) in d.items() if filter_string in k}

        #  END OF set of control questions for each treatment

    def set_payoffs(self):
        if self.treatment == 'T0':
            self.payoff = self.first_decision * (-Constants.initial_cost +
                                                 max(self.investment_payoff - Constants.final_cost, 0))
        if self.treatment == 'T1':
            self.payoff = self.first_decision * (-Constants.initial_cost +
                                                 (self.investment_payoff - Constants.final_cost) *
                                                 self.second_decision)
        if self.treatment == 'T2':
            self.payoff = self.first_decision * (
                - Constants.initial_cost + self.investment_payoff - Constants.final_cost)
        # to store the game_payoffs only
        self.game_payoff = self.payoff

    def set_lottery_payoffs(self):

        random_lottery = random.randint(1, Constants.len_lottery)
        self.stage3_chosen_lottery = random_lottery
        stage3decision = json.loads(str(self.stage3decision))
        lottery_decision = stage3decision[str(random_lottery)]
        if lottery_decision == 'A':
            self.stage3_payoff = Constants.lotteryA
        else:
            ranges = Constants.lottery_choices[1:-1]
            lottery_outcome = random.randint(1, 100)
            self.stage3_picked_number = lottery_outcome
            if lottery_outcome <= ranges[random_lottery]:
                self.stage3_payoff = Constants.lotteryB['low']
            else:
                self.stage3_payoff = Constants.lotteryB['high']

    def set_final_payoff(self):
        # TODO: include wallet calculations here
        self.set_lottery_payoffs()
        self.payoff += self.stage3_payoff
        self.payoff += Constants.wallet

    # block of survey questions:

    gender = models.CharField(verbose_name='Gender', choices=['Male', 'Female', 'Other'],
                              widget=widgets.RadioSelectHorizontal, )
    nationality = models.CharField(verbose_name='Nationality', choices=['US', 'Other'],
                                   widget=widgets.RadioSelectHorizontal, )
    nationality_other = models.CharField(verbose_name='', blank=True)
    race_ethnicity = models.CharField(verbose_name='Race/Ethnicity',
                                      choices=['African American/African/Black/Caribbean',
                                               'Asian/Pacific Islander',
                                               'Caucasian',
                                               'Hispanic/Latino',
                                               'Native American',
                                               'Other',
                                               'Prefer not to answer '
                                               ],
                                      widget=widgets.RadioSelect, )
    race_ethnicity_other = models.CharField(verbose_name='', blank=True)
    major = models.CharField(verbose_name='Major', blank=True)
    year_in_college = models.CharField(verbose_name='If you are currently in school, what year are you in?', choices=[
        'Freshman/First-Year ',
        'Sophomore',
        'Junior',
        'Senior',
        'Graduate Student',
        'Other'
    ],
                                       blank=True)
    year_in_college_other = models.CharField(verbose_name='', )

    stock_market_experience = models.CharField(verbose_name='Do you have any experience with the stock market?',
                                               widget=widgets.RadioSelectHorizontal,
                                               choices=['Yes', 'No'])

    stock_market_explain = models.CharField(verbose_name='', )

    instructions = models.CharField(verbose_name='Were the instructions clear?',
                                    choices=['Yes', 'No'],
                                    widget=widgets.RadioSelect, )
    recommendations = models.CharField(verbose_name='Do you have any recommendations for improvements?',
                                       blank=True)

    random_contract = models.CharField(
        verbose_name='How confident were you that the experimenters truly randomized the payoff of each contract based on the stated probabilities?',
        choices=CONFIDENT_CHOICES,
        widget=widgets.RadioSelectHorizontal, )

    random_round = models.CharField(
        verbose_name='How confident were you that the experimenters truly chose the rounds for payments randomly?',
        choices=CONFIDENT_CHOICES,
        widget=widgets.RadioSelectHorizontal, )
    easiest = models.CharField(verbose_name='Which Part of the experiment did you find was easiest to think through?',
                               choices=['Part 1', 'Part 2'],
                               widget=widgets.RadioSelectHorizontal, )

    end_beginning = models.CharField(
        verbose_name='Do you think you made better decisions at the end of each Part or at the beginning of each Part?',
        choices=['Beginning', 'End'],
        widget=widgets.RadioSelectHorizontal, )
    pleasant = models.CharField(
        verbose_name='Would you say that you found being in this study a pleasant or unpleasant experience?',
        choices=['Extremely Pleasant',
                 'Pleasant',
                 'Somewhat Pleasant',
                 'Neither',
                 'Somewhat Unpleasant',
                 'Unpleasant',
                 'Extremely Unpleasant', ],
        widget=widgets.RadioSelectHorizontal, )

    thinking = models.TextField(
        verbose_name="""Please try to describe what you were thinking when you were making decisions 
        during the study.  What factors entered your decisions? And why did you make the choices you did?""",
        blank=True)
    stage3decision = models.CharField(doc='to store Stage 3 decision in a form of ordered dictionary')
    stage3_chosen_lottery = models.IntegerField()
    stage3_picked_number = models.IntegerField()
    stage3_payoff = models.CurrencyField(doc='field to store Stage 3 payoff')
    general_comments = models.TextField(doc='general comments about the study - mostly for pilot',
                                        verbose_name='Please share with us any comments or '
                                                     'questions you have in a course of the study',
                                        blank=True, null=True)
