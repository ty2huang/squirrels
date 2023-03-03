import time, json
from squirrels import constants as c

start = time.time()
import jinja2 as j2
c.timer.add_activity_time(c.IMPORT_JINJA, start)

start = time.time()
parms = None


def list_to_dict(key, the_list):
    return {x[key]: x for x in the_list}
    

def initialize(manifest_path):
    global parms
    if parms is None:
        with open(manifest_path, 'r') as f:
            content = f.read()
        proj_vars = json.loads(content).get(c.PROJ_VARS_KEY, dict())
        template = j2.Environment().from_string(content)
        rendered = template.render(**proj_vars)
        parms = json.loads(rendered)
        
        parms[c.DATASETS_KEY] = list_to_dict(c.DATASET_NAME_KEY, parms[c.DATASETS_KEY])


try:
    initialize(c.MANIFEST_FILE)
except FileNotFoundError:
    pass

c.timer.add_activity_time('initialize context', start)
