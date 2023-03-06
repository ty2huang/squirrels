import time, yaml
from typing import Dict, Any
from squirrels import constants as c

start = time.time()
import jinja2 as j2
c.timer.add_activity_time(c.IMPORT_JINJA, start)

parms = None


def list_to_dict(key, the_list):
    return {x[key]: x for x in the_list}
    

def initialize(manifest_path):
    global parms
    if parms is None:
        with open(manifest_path, 'r') as f:
            content = f.read()
        proj_vars = yaml.safe_load(content).get(c.PROJ_VARS_KEY, dict())
        template = j2.Environment().from_string(content)
        rendered = template.render(**proj_vars)
        parms = yaml.safe_load(rendered)
        

def get_dataset_parms(dataset: str) -> Dict[str, Any]:
    return parms[c.DATASETS_KEY][dataset]

def get_setting(key: str, default: Any):
    settings: Dict[str, str] = parms.get(c.SETTINGS_KEY, {})
    return settings.get(key, default)