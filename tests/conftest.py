import sys, os
from squirrels import context, profile_manager as pm, constants as c


def pytest_sessionstart(session):
    sys.path.append('sample_project')
    context.initialize('sample_project/manifest.json')
    database_path = os.path.abspath('./data/test.db')
    pm.Profile(context.parms[c.DB_PROFILE_KEY]).set('sqlite', f'/{database_path}', '', '')
