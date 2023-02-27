DEBUG = True

# Manifest file keys
DB_PROFILE = 'db_profile'
PROJ_VARS = 'project_variables'
NAME_KEY = 'name'
DATASETS_KEY = 'datasets'
HEADERS_KEY = 'headers'
DATABASE_VIEWS_KEY = 'database_views'
FINAL_VIEW_KEY = 'final_view'

# Database profile keys
DIALECT = 'dialect'
CONN_URL = 'conn_url'
USERNAME = 'username'
PASSWORD = 'password'

# Folder/File names
MANIFEST_FILE = 'manifest.json'
OUTPUTS_FOLDER = 'outputs'
DATASETS_FOLDER = 'datasets'
PARAMETERS_MODULE = 'parameters'
PARAMETERS_OUTPUT = 'parameters.json'
FINAL_VIEW_NAME = 'final_view'

# Activities to time
IMPORT_JINJA = 'import jinja'
IMPORT_SQLALCHEMY = 'import sqlalchemy'
IMPORT_PANDAS = 'import pandas'

# Selection cfg sections
DATES_SECTION = 'dates'
NUMBERS_SECTION = 'numbers'
RANGES_SECTION = 'ranges'
SINGLE_SELECT_SECTION = 'singleselect'
MULTI_SELECT_SECTION = 'multiselect'
HEADERS_SECTION = 'headers'

# Global utilities
import time

class Timer:
    def __init__(self):
        self.times = {}
    
    def add_activity_time(self, activity, start):
        self.times[activity] = self.times.get(activity, 0) + (time.time()-start) * 10**3
    
    def report_times(self):
        if DEBUG:
            for activity, time in self.times.items():
                print(f'The time of execution of "{activity}" is:', time, "ms")

timer = Timer()
