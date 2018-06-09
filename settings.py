import os
from os import environ

import dj_database_url
from boto.mturk import qualification

import otree.settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SENTRY_DSN = 'http://2d6137799b914e1693146c5011f39030:46838e8caa374937a91b14b59ebbe164@sentry.otree.org/36'
# the environment variable OTREE_PRODUCTION controls whether Django runs in
# DEBUG mode. If OTREE_PRODUCTION==1, then DEBUG=False
if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = False
else:
    DEBUG = True

ADMIN_USERNAME = 'admin'

# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

# don't share this with anybody.
SECRET_KEY = '+-74_d1!1go3erg2g1*=pgennj#xgtn^yrq=bn165e!%4q7htl'

DATABASES = {
    'default': dj_database_url.config(
        # Rather than hardcoding the DB parameters here,
        # it's recommended to set the DATABASE_URL environment variable.
        # This will allow you to use SQLite locally, and postgres/mysql
        # on the server
        # Examples:
        # export DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
        # export DATABASE_URL=mysql://USER:PASSWORD@HOST:PORT/NAME

        # fall back to SQLite if the DATABASE_URL env var is missing
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    )
}

# AUTH_LEVEL:
# If you are launching a study and want visitors to only be able to
# play your app if you provided them with a start link, set the
# environment variable OTREE_AUTH_LEVEL to STUDY.
# If you would like to put your site online in public demo mode where
# anybody can play a demo version of your game, set OTREE_AUTH_LEVEL
# to DEMO. This will allow people to play in demo mode, but not access
# the full admin interface.

AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')

# setting for integration with AWS Mturk
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')

# e.g. EUR, CAD, GBP, CHF, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
POINTS_DECIMAL_PLACES = 0

# e.g. en, de, fr, it, ja, zh-hans
# see: https://docs.djangoproject.com/en/1.9/topics/i18n/#term-language-code
LANGUAGE_CODE = 'en'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

# SENTRY_DSN = ''

DEMO_PAGE_INTRO_TEXT = """
oTree games
"""

# from here on are qualifications requirements for workers
# see description for requirements on Amazon Mechanical Turk website:
# http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html
# and also in docs for boto:
# https://boto.readthedocs.org/en/latest/ref/mturk.html?highlight=mturk#module-boto.mturk.qualification

mturk_hit_settings = {
    'keywords': ['survey'],
    'title': 'Academic Experiment & Survey, earn between $7 and $31',
    'description': 'Participate in 30 minute experiment & survey',
    'frame_height': 800,
    'preview_template': 'global/MTurkPreview.html',
    'minutes_allotted_per_assignment': 180,
    'expiration_hours': 24,  # 7 days
    'grant_qualification_id': '38XLDN1M8EIWZ7B4AOVS2TS9EP6D3B',  # to prevent retakes
    'qualification_requirements': [
        {
            'QualificationTypeId': "00000000000000000071",
            'Comparator': "EqualTo",
            'LocaleValues': [{
                'Country': "US",
            }]
        },
        {
            'QualificationTypeId': "000000000000000000L0",
            'Comparator': "GreaterThanOrEqualTo",
            "IntegerValues": [90],
        },
        {
            'QualificationTypeId': "00000000000000000040",
            'Comparator': "GreaterThanOrEqualTo",
            "IntegerValues": [100],
        },
        {
            'QualificationTypeId': "38XLDN1M8EIWZ7B4AOVS2TS9EP6D3B",
            'Comparator': "DoesNotExist",
        },
    ],

    #     [
    #     qualification.LocaleRequirement("EqualTo", "US"),
    #     qualification.PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", 90),
    #     qualification.NumberHitsApprovedRequirement("GreaterThanOrEqualTo", 100),
    #     # qualification.Requirement('YOUR_QUALIFICATION_ID_HERE', 'DoesNotExist')
    # ]
}

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']


real_world_currency_per_point = 0.01
participation_fee = 7.0

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': real_world_currency_per_point,
    # 'participation_fee_in_points': participation_fee_in_points,
    'participation_fee': participation_fee,
    'doc': "",
    'mturk_hit_settings': mturk_hit_settings,
}

SESSION_CONFIGS = [

    {
        'name': 'kelsey_random',
        'display_name': 'random (T0, T1)',
        'num_demo_participants': 1,
        'app_sequence': ['kelsey'],
        'treatment_order': 'random'

    },
    {
        'name': 'kelseyT0T1',
        'display_name': 'T0-T1',
        'num_demo_participants': 1,
        'app_sequence': ['kelsey'],
        'treatments': ['T0', 'T1']
    },
    {
        'name': 'kelseyT1T0',
        'display_name': 'T1-T0',
        'num_demo_participants': 1,
        'app_sequence': ['kelsey'],
        'treatments': ['T1', 'T0']
    },
    {
        'name': 'T1T2random',
        'display_name': 'Random (T1, T2)',
        'num_demo_participants': 1,
        'app_sequence': ['kelsey'],
        'treatments': ['T1', 'T2'],
        'treatment_order': 'random',
    },

]

# anything you put after the below line will override
# oTree's default settings. Use with caution.
otree.settings.augment_settings(globals())
