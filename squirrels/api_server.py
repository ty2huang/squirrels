import json, os
from typing import Dict, List, FrozenSet, Tuple
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from cachetools.func import ttl_cache

from squirrels import major_verion, constants as c, context
from squirrels.renderer import Renderer
from squirrels.parameter_configs import ParameterSet


def normalize_name(name: str):
    return name.replace('-', '_')

def normalize_name_for_api(name: str):
    return name.replace('_', '-')


def load_selected_parameters(renderer: Renderer, query_params: FrozenSet[Tuple[str, str]]) -> ParameterSet:
    parameters = renderer.parameters
    query_params_dict = dict(query_params)
    for name, parameter in parameters.parameters_dict.items():
        parameter.refresh(parameters)
        selected_value = query_params_dict.get(name)
        if selected_value is not None:
            parameter.set_selection(selected_value)
    return parameters


def load_dataframe(renderer: Renderer):
    sql_by_view_name = renderer.get_rendered_sql_by_view()
    
    dataset_context = context.get_dataset_parms(renderer.dataset)
    final_view_name = dataset_context[c.FINAL_VIEW_KEY]
    final_view_sql_str = renderer.get_final_view_sql_str(final_view_name, sql_by_view_name)
    
    _, df = renderer.get_all_results(sql_by_view_name, final_view_name, final_view_sql_str)
    return df


def template_function(dataset: str, request: Request, helper_func):
    dataset = normalize_name(dataset)
    query_params = frozenset((normalize_name(key), val) for key, val in request.query_params.items())
    return helper_func(dataset, query_params)


# Helper functions for "parameters" api
def get_parameters_helper(dataset: str, query_params: FrozenSet[Tuple[str, str]]):
    renderer = Renderer(dataset)
    parameters = load_selected_parameters(renderer, query_params)
    return parameters.to_dict()
    

# Helper functions for "get_results" api
def get_results_helper(dataset: str, query_params: FrozenSet[Tuple[str, str]]):
    renderer = Renderer(dataset)
    load_selected_parameters(renderer, query_params)
    df = load_dataframe(renderer)
    return json.loads(df.to_json(orient='table', index=False))
        
        
def run(no_cache: bool, uvicorn_args: List[str]):
    app = FastAPI()
    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), 'templates'))

    context.initialize(c.MANIFEST_FILE)
    squirrels_version_path = f'/squirrels{major_verion}'
    config_base_path = normalize_name_for_api(context.parms[c.BASE_PATH_KEY])
    base_path = squirrels_version_path + config_base_path

    # Parameters API
    parameters_path = '/{dataset}/parameters'
    # TODO: create setting for ttl cache time seconds

    @ttl_cache(maxsize=context.get_setting(c.PARAMETERS_CACHESIZE_SETTING, 1024))
    def get_parameters_cachable(dataset: str, query_params: FrozenSet[Tuple[str, str]]):
        return get_parameters_helper(dataset, query_params)
    
    @app.get(base_path + parameters_path, response_class=JSONResponse)
    async def get_parameters(dataset: str, request: Request):
        helper_func = get_parameters_helper if no_cache else get_parameters_cachable
        return template_function(dataset, request, helper_func)

    # Results API
    results_path = '/{dataset}'

    @ttl_cache(maxsize=context.get_setting(c.RESULTS_CACHESIZE_SETTING, 128))
    def get_results_cachable(dataset: str, query_params: FrozenSet[Tuple[str, str]]):
        return get_results_helper(dataset, query_params)
    
    @app.get(base_path + results_path, response_class=JSONResponse)
    async def get_results(dataset: str, request: Request):
        helper_func = get_results_helper if no_cache else get_results_cachable
        return template_function(dataset, request, helper_func)
    
    # Catalog API
    @app.get(squirrels_version_path, response_class=JSONResponse)
    async def get_catalog():
        all_dataset_contexts: Dict = context.parms[c.DATASETS_KEY]
        datasets = []
        for dataset, dataset_context in all_dataset_contexts.items():
            dataset_normalized = normalize_name_for_api(dataset)
            datasets.append({
                'dataset': dataset,
                'label': dataset_context[c.DATASET_LABEL_KEY],
                'parameters': base_path + parameters_path.format(dataset=dataset_normalized),
                'result': base_path + results_path.format(dataset=dataset_normalized)
            })
        return {'project_variables': context.parms[c.PROJ_VARS_KEY], 'resource_paths': datasets}
    
    # Squirrels UI
    @app.get('/', response_class=HTMLResponse)
    async def get_ui(request: Request):
        return templates.TemplateResponse('index.html', {'request': request})

    
    # Run API server
    import uvicorn
    uvicorn.run(app, host=uvicorn_args.host, port=uvicorn_args.port)
