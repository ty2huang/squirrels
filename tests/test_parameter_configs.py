from squirrels.parameter_configs import *
import importlib

importlib.import_module("datasets.stock_price_history.parameters")


def test_parameters_to_dict():
    parameters = ParameterSet()

    reference_date_dict = {
        'widget_type': 'DateField',
        'name': 'reference_date',
        'label': 'Reference Date',
        'selected_date': '2023-01-31'
    }
    assert(parameters.get_parameter('reference_date').to_dict() == reference_date_dict)

    time_unit_dict = {
        'widget_type': 'SingleSelect',
        'name': 'time_unit',
        'label': 'Time Unit',
        'options': [
            {'id': '0', 'label': 'Days'}, 
            {'id': '1', 'label': 'Weeks'}, 
            {'id': '2', 'label': 'Months'}, 
            {'id': '3', 'label': 'Quarters'}, 
            {'id': '4', 'label': 'Years'}
        ],
        'selected_id': '0',
        'trigger_refresh': True
    }
    assert(parameters.get_parameter('time_unit').to_dict() == time_unit_dict)
    
    num_periods_dict = {
        'widget_type': 'NumberField',
        'name': 'num_periods',
        'label': 'Number of Time Units',
        'min_value': '1',
        'max_value': '365',
        'increment': '1',
        'selected_value': '30'
    }
    assert(parameters.get_parameter('num_periods').to_dict() == num_periods_dict)

    time_of_year_dict = {
        'widget_type': 'MultiSelect',
        'name': 'time_of_year',
        'label': 'Time of Year',
        'options': [
            {'id': '0', 'label': 'No Options'}
        ],
        'selected_ids': [],
        'trigger_refresh': False,
        'include_all': True,
        'order_matters': False
    }
    assert(parameters.get_parameter('time_of_year').to_dict() == time_of_year_dict)

    ticker_dict = {
        'widget_type': 'MultiSelect',
        'name': 'ticker',
        'label': 'Ticker',
        'data_source': {
            'table_or_query': 'lu_tickers',
            'id_col': 'ticker_id',
            'options_col': 'ticker',
            'order_by_col': 'ticker_order',
            'is_default_col': None,
            'parent_id_col': None,
            'is_cond_default_col': None
        }
    }
    assert(parameters.get_parameter('ticker').to_dict() == ticker_dict)

    parameters_dict = { 'parameters': [
        reference_date_dict, time_unit_dict, num_periods_dict, time_of_year_dict, ticker_dict
    ] }
    assert(parameters.to_dict() == parameters_dict)


def test_convert_datasource_params():
    parameters = ParameterSet()
    parameters.convert_datasource_params()

    ticker_dict = {
        'widget_type': 'MultiSelect',
        'name': 'ticker',
        'label': 'Ticker',
        'options': [
            {'id': '0', 'label': 'AAPL'}, 
            {'id': '1', 'label': 'AMZN'}, 
            {'id': '2', 'label': 'GOOG'}, 
            {'id': '3', 'label': 'MSFT'}
        ],
        'selected_ids': [],
        'trigger_refresh': False,
        'include_all': True,
        'order_matters': False
    }
    assert(parameters.get_parameter('ticker').to_dict() == ticker_dict)


def test_refresh():
    parameters = ParameterSet()
    parent_parm: SingleSelectParameter = parameters.get_parameter('time_unit')
    parent_parm.set_selection('3')
    time_of_year_parm: MultiSelectParameter = parameters.get_parameter('time_of_year')
    time_of_year_parm.refresh(parameters)
    expected_time_of_year_options =  [
        ParameterOption('14', 'Q1'),
        ParameterOption('15', 'Q2'),
        ParameterOption('16', 'Q3'),
        ParameterOption('17', 'Q4')
    ]
    assert([x.to_dict() for x in time_of_year_parm.options] == [x.to_dict() for x in expected_time_of_year_options])
    assert(time_of_year_parm.get_selected_ids() == '16')
    