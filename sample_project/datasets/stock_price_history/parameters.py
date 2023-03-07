from typing import Callable
from functions import *
import squirrels as sq


# Define options for Date Range parameter
class TimeUnitParameterOption(sq.ParameterOption):
    def __init__(self, identifier: str, label: str, get_start_date: Callable[[str, str], str], date_bucket_column: str, 
                 min_num_periods: int, max_num_periods: int, default_num_periods: int, num_periods_increment: int = 1):
        super().__init__(identifier, label)
        self.get_start_date = get_start_date
        self.date_bucket_column = date_bucket_column
        self.min_num_periods = min_num_periods
        self.max_num_periods = max_num_periods
        self.default_num_periods = default_num_periods
        self.num_periods_increment = num_periods_increment

time_unit_options = [
    TimeUnitParameterOption('0', 'Days', get_start_of_days, 'trading_date', 7, 364, 28, 7),
    TimeUnitParameterOption('1', 'Weeks', get_start_of_weeks, 'week_value', 1, 260, 52),
    TimeUnitParameterOption('2', 'Months', get_start_of_months, 'month_value', 1, 120, 12),
    TimeUnitParameterOption('3', 'Quarters', get_start_of_quarters, 'quarter_value', 1, 40, 8),
    TimeUnitParameterOption('4', 'Years', get_start_of_years, 'year_value', 1, 10, 5)
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
        self.min_value = selected_time_unit.min_num_periods
        self.max_value = selected_time_unit.max_num_periods
        self.increment = selected_time_unit.num_periods_increment
        self.default_value = selected_time_unit.default_num_periods
        self.selected_value = self.default_value


# Define data source for Ticker parameter
ticker_data_source = sq.OptionsDataSource('lu_tickers', 'ticker_id', 'ticker', 'ticker_order')


# Define options for time_of_year
time_of_year_options = [
    sq.ParameterOption('1', 'January', '2'),
    sq.ParameterOption('2', 'February', '2'),
    sq.ParameterOption('3', 'March', '2'),
    sq.ParameterOption('4', 'April', '2'),
    sq.ParameterOption('5', 'May', '2'),
    sq.ParameterOption('6', 'June', '2'),
    sq.ParameterOption('7', 'July', '2'),
    sq.ParameterOption('8', 'August', '2'),
    sq.ParameterOption('9', 'September', '2'),
    sq.ParameterOption('10', 'October', '2'),
    sq.ParameterOption('11', 'November', '2'),
    sq.ParameterOption('12', 'December', '2'),
    sq.ParameterOption('13', 'Q1', '3'),
    sq.ParameterOption('14', 'Q2', '3'),
    sq.ParameterOption('15', 'Q3', '3'),
    sq.ParameterOption('16', 'Q4', '3')
]


# Define parameters
sq.add_parameters([
    sq.DateParameter('reference_date', 'Reference Date', get_today()),
    sq.SingleSelectParameter('time_unit', 'Time Unit', time_unit_options, trigger_refresh=True),
    NumPeriodsParameter('num_periods', 'Number of Time Units', 'time_unit'),
    sq.MultiSelectParameter('time_of_year', 'Time of Year', time_of_year_options, parent='time_unit'),
    sq.DataSourceParameter(sq.WidgetType.MultiSelect, 'ticker', 'Ticker', ticker_data_source)
])

