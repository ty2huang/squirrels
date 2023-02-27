from squirrels.parameter_configs import parameters as parms
import importlib

importlib.import_module("datasets.stock_price_history.parameters")


def test_parameters_to_dict():
    reference_date_dict = {
        'widget_type': 'DateField',
        'name': 'reference_date',
        'label': 'Reference Date',
        'selected_date': '2023-01-31'
    }
    assert(parms.get_parameter('reference_date').to_dict() == reference_date_dict)

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
    assert(parms.get_parameter('time_unit').to_dict() == time_unit_dict)
    
    num_periods_dict = {
        'widget_type': 'NumberField',
        'name': 'num_periods',
        'label': 'Number of Time Units',
        'min_value': '1',
        'max_value': '365',
        'increment': '1',
        'selected_value': '30'
    }
    assert(parms.get_parameter('num_periods').to_dict() == num_periods_dict)

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
            'parent_id_col': None
        }
    }
    assert(parms.get_parameter('ticker').to_dict() == ticker_dict)

    parameters_dict = { 'parameters': [reference_date_dict, time_unit_dict, num_periods_dict, ticker_dict] }
    assert(parms.to_dict() == parameters_dict)


def test_convert_datasource_params():
    parms.convert_datasource_params()
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
        'include_all': True
    }
    assert(parms.get_parameter('ticker').to_dict() == ticker_dict)