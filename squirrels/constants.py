# Squirrels CLI commands
GET_PROFILES_CMD = 'get-all-profiles'
SET_PROFILE_CMD = 'set-profile'
DELETE_PROFILE_CMD = 'delete-profile'
INIT_CMD = 'init'
LOAD_MODULES_CMD = 'load-modules'
TEST_CMD = 'test'
RUN_CMD = 'run'

# Manifest file keys
DB_PROFILE_KEY = 'db_profile'
PROJ_VARS_KEY = 'project_variables'
MODULES_KEY = 'modules'
DATASET_LABEL_KEY = 'label'
DATASETS_KEY = 'datasets'
HEADERS_KEY = 'headers'
DATABASE_VIEWS_KEY = 'database_views'
DB_VIEW_NAME_KEY = 'name'
DB_VIEW_FILE_KEY = 'file'
FINAL_VIEW_KEY = 'final_view'
BASE_PATH_KEY = 'base_path'
SETTINGS_KEY = 'settings'

# Database profile keys
DIALECT = 'dialect'
CONN_URL = 'conn_url'
USERNAME = 'username'
PASSWORD = 'password'

# Folder/File names
MANIFEST_FILE = 'manifest.yaml'
OUTPUTS_FOLDER = 'outputs'
MODULES_FOLDER = 'modules'
DATASETS_FOLDER = 'datasets'
PARAMETERS_MODULE = 'parameters'
PARAMETERS_OUTPUT = 'parameters.json'
FINAL_VIEW_NAME = 'final_view'

# Dataset setting names
PARAMETERS_CACHESIZE_SETTING = 'parameters.cachesize'
RESULTS_CACHESIZE_SETTING = 'results.cachesize'

# Activities to time
IMPORT_JINJA = 'import jinja'
IMPORT_SQLALCHEMY = 'import sqlalchemy'
IMPORT_PANDAS = 'import pandas'

# Selection cfg sections
PARAMETERS_SECTION = 'parameters'
HEADERS_SECTION = 'headers'

# Global utilities
import time

class Timer:
    def __init__(self):
        self.times = {}
    
    def add_activity_time(self, activity, my_start):
        self.times[activity] = self.times.get(activity, 0) + (time.time()-my_start) * 10**3
    
    def report_times(self, verbose):
        if verbose:
            for activity, time in self.times.items():
                print(f'The time of execution of "{activity}" is:', time, "ms")

timer = Timer()
