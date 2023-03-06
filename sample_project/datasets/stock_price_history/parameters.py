from typing import Callable
from functions import *
import squirrels as sq


# Define options for Date Range parameter
class TimeUnitParameterOption(sq.ParameterOption):
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
class NumPeriodsParameter(sq.NumberParameter):
    def __init__(self, name: str, label: str, time_unit_name: str):
        super().__init__(name, label, 1, 1, 1, 1) # most parameters taken care of in refresh method
        self.parent = time_unit_name
    
    def refresh(self, all_parameters: sq.ParameterSet):
        super().refresh(all_parameters)
        time_unit: sq.SingleSelectParameter = all_parameters.get_parent_parameter(self.name)
        selected_time_unit: TimeUnitParameterOption = time_unit.get_selected()
        self.max_value = selected_time_unit.max_num_periods
        self.selected_value = selected_time_unit.default_num_periods


# Define data source for Ticker parameter
ticker_data_source = sq.OptionsDataSource('lu_tickers', 'ticker_id', 'ticker', 'ticker_order')


# Define options for time_of_year
time_of_year_options = [
    sq.ParameterOption('0', 'No Options', '0'),
    sq.ParameterOption('1', 'No Options', '1'),
    sq.ParameterOption('2', 'January', '2'),
    sq.ParameterOption('3', 'February', '2'),
    sq.ParameterOption('4', 'March', '2', True),
    sq.ParameterOption('5', 'April', '2'),
    sq.ParameterOption('14', 'Q1', '3'),
    sq.ParameterOption('15', 'Q2', '3'),
    sq.ParameterOption('16', 'Q3', '3', True),
    sq.ParameterOption('17', 'Q4', '3'),
    sq.ParameterOption('18', 'No Options', '4')
]


# Define parameters
sq.add_parameters([
    sq.DateParameter('reference_date', 'Reference Date', get_today()),
    sq.SingleSelectParameter('time_unit', 'Time Unit', time_unit_options, trigger_refresh=True),
    NumPeriodsParameter('num_periods', 'Number of Time Units', 'time_unit'),
    sq.MultiSelectParameter('time_of_year', 'Time of Year', time_of_year_options, parent='time_unit'),
    sq.DataSourceParameter(sq.WidgetType.MultiSelect, 'ticker', 'Ticker', ticker_data_source)
])

