import sys, os
from squirrels import context, profile_manager as pm, constants as c


def pytest_sessionstart(session):
    sys.path.append('sample_project')
    context.initialize('sample_project/manifest.yaml')
    database_path = os.path.abspath('./data/test.db')
    pm.Profile('product_profile').set('sqlite', f'/{database_path}', '', '')
