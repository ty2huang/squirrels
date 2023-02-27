from typing import Callable
from squirrels import parameter_configs as pc
from functions import *


# Define options for Date Range parameter
class TimeUnitParameterOption(pc.ParameterOption):
    def __init__(self, identifier: str, label: str, get_start_date: Callable[[str, str], str], 
                 date_bucket_column: str, max_num_periods: int, default_num_periods: int):
        super().__init__(identifier, label)
        self.get_start_date = get_start_date
        self.date_bucket_column = date_bucket_column
        self.max_num_periods = max_num_periods
        self.default_num_periods = default_num_periods

time_unit_options = [
    TimeUnitParameterOption('0', 'Days', get_start_of_days, 'trading_date', 365, 30),
    TimeUnitParameterOption('1', 'Weeks', get_start_of_weeks, 'week_value', 52, 4),
    TimeUnitParameterOption('2', 'Months', get_start_of_months, 'month_value', 60, 12),
    TimeUnitParameterOption('3', 'Quarters', get_start_of_quarters, 'quarter_value', 20, 4),
    TimeUnitParameterOption('4', 'Years', get_start_of_years, 'year_value', 50, 5)
]


# Define number of periods
class NumPeriodsParameter(pc.NumberParameter):
    def __init__(self, name: str, label: str, time_unit_name: str):
        super().__init__(name, label, 1, 1, 1, 1) # most parameters taken care of in refresh method
        self.parent = time_unit_name
    
    def refresh(self):
        super().refresh()
        time_unit = pc.parameters.get_parent_parameter(self.name)
        self.max_value = time_unit.get_selected().max_num_periods
        self.selected_value = time_unit.get_selected().default_num_periods


# Define data source for Ticker parameter
ticker_data_source = pc.OptionsDataSource('lu_tickers', 'ticker_id', 'ticker', 'ticker_order')


# Define parameters
pc.parameters.add([
    pc.DateParameter('reference_date', 'Reference Date', get_today()),
    pc.SingleSelectParameter('time_unit', 'Time Unit', time_unit_options, trigger_refresh=True),
    NumPeriodsParameter('num_periods', 'Number of Time Units', 'time_unit'),
    pc.DataSourceParameter(pc.WidgetType.MultiSelect, 'ticker', 'Ticker', ticker_data_source)
])

