from __future__ import annotations
from dataclasses import dataclass
from collections import OrderedDict
from typing import List, Dict, OrderedDict, Optional, Union, Type
from datetime import datetime
from enum import Enum
from decimal import Decimal
from squirrels import constants as c
from squirrels.db_conn import DbConnection
import time

start = time.time()
import pandas as pd
c.timer.add_activity_time(c.IMPORT_PANDAS, start)

class WidgetType(Enum):
    SingleSelect = 1
    MultiSelect = 2
    DateField = 3
    NumberField = 4
    RangeField = 5


def raiseParameterError(param_name: str, remaining_message: str, errorClass: Type[Exception] = RuntimeError):
    message = f'For parameter "{param_name}", {remaining_message}'
    raise errorClass(message)


@dataclass
class DataSource:
    table_or_query: str

    def get_query(self):
        if self.table_or_query.startswith('SELECT '):
            query = self.table_or_query
        else:
            query = f'SELECT * FROM {self.table_or_query}'
        return query


@dataclass
class OptionsDataSource(DataSource):
    id_col: str
    options_col: str
    order_by_col: Optional[str]
    is_default_col: Optional[str]
    parent_id_col: Optional[str]

    def __init__(self, table_or_query: str, id_col: str, options_col: str, order_by_col: Optional[str] = None, 
                is_default_col: Optional[str] = None, parent_id_col: Optional[str] = None):
        super().__init__(table_or_query)
        self.id_col = id_col 
        self.options_col = options_col
        self.order_by_col = id_col if order_by_col is None else order_by_col
        self.is_default_col = is_default_col
        self.parent_id_col = parent_id_col


@dataclass
class _NumericDataSource(DataSource):
    min_value_col: str
    max_value_col: str
    increment_col: str

@dataclass
class NumberDataSource(_NumericDataSource):
    default_value_col: str

@dataclass
class RangeDataSource(_NumericDataSource):
    default_min_value_col: str
    default_max_value_col: str


@dataclass
class DateDataSource(DataSource):
    default_date_col: str


@dataclass
class ParameterOption:
    identifier: str
    label: str
    parent_id: Optional[str] = None

    def to_dict(self):
        return {'id': self.identifier, 'label': self.label}


@dataclass
class _Parameter:
    widget_type: WidgetType
    name: str
    label: str

    def refresh(self):
        pass # intentional, empty definition unless overwritten

    def set_selection(self, _: str):
        raise RuntimeError('Must override "set_selection" method in all classes that override the "_Parameter" class')

    def to_dict(self):
        return {
            'widget_type': self.widget_type.name,
            'name': self.name,
            'label': self.label
        }


@dataclass
class _SelectionParameter(_Parameter):
    options: List[ParameterOption]
    trigger_refresh: bool
    parent: Optional[str]

    def __post_init__(self):
        self.all_options = list(self.options)

    def get_selected_ids_as_list(self):
        return []

    def refresh(self):
        super().refresh()
        if self.parent is not None:
            parent_param = parameters.get_parent_parameter(self.name)
            selected_ids = set(parent_param.get_selected_ids_as_list())
            self.options = [x for x in self.all_options if x.parent_id in selected_ids]
        return self
    
    def verify_selected_id_in_options(self, selected_id):
        if selected_id not in [x.identifier for x in self.options]:
            raise raiseParameterError(self.name, f'the selected id "{selection}" is not selectable from options')

    def to_dict(self):
        output = super().to_dict()
        output['options'] = [x.to_dict() for x in self.options]
        output['trigger_refresh'] = self.trigger_refresh
        return output


@dataclass
class SingleSelectParameter(_SelectionParameter):
    selected_id: str

    def __init__(self, name: str, label: str, options: List[ParameterOption], selected_id: Optional[str] = None, 
                 trigger_refresh: bool = False, parent: Optional[str] = None):
        super().__init__(WidgetType.SingleSelect, name, label, options, trigger_refresh, parent)
        selected_id_default = options[0].identifier if options else None
        identifiers = [x.identifier for x in self.options]
        self.selected_id = selected_id if selected_id in identifiers else selected_id_default
    
    def set_selection(self, selection: str):
        self.selected_id = selection
        self.verify_selected_id_in_options(self.selected_id)

    def get_selected(self) -> ParameterOption:
        return next((x for x in self.options if x.identifier == self.selected_id), None)
    
    def get_selected_id(self) -> str:
        return self.get_selected().identifier
    
    def get_selected_label(self) -> str:
        return self.get_selected().label
    
    # Overriding for refresh method
    def get_selected_ids_as_list(self) -> List[str]:
        return [self.get_selected_id()]

    def to_dict(self):
        output = super().to_dict()
        output['selected_id'] = self.selected_id
        return output


@dataclass
class MultiSelectParameter(_SelectionParameter):
    selected_ids: List[str]
    include_all: bool

    def __init__(self, name: str, label: str, options: List[ParameterOption], selected_ids: List[str] = [], 
                 trigger_refresh: bool = False, parent: Optional[str] = None, include_all: bool = True):
        super().__init__(WidgetType.MultiSelect, name, label, options, trigger_refresh, parent)
        self.selected_ids = selected_ids
        self.include_all = include_all

    def set_selection(self, selection: str):
        self.selected_ids = selection.split(',')
        for selected_id in self.selected_ids:
            self.verify_selected_id_in_options(selected_id)

    def get_selected_list(self) -> List[ParameterOption]:
        if len(self.selected_ids) == 0 and self.include_all:
            result = self.options
        else:
            result = [x for x in self.options if x.identifier in self.selected_ids]
        return result
    
    def get_selected_ids_as_list(self) -> List[str]:
        return [x.identifier for x in self.get_selected_list()]
    
    def get_selected_labels_as_list(self) -> List[str]:
        return [x.label for x in self.get_selected_list()]
    
    def get_selected_ids(self) -> str:
        return ', '.join(self.get_selected_ids_as_list())
    
    def get_selected_labels_quoted(self) -> str:
        return ', '.join("'" + x + "'" for x in self.get_selected_labels_as_list())

    def to_dict(self):
        output = super().to_dict()
        output['selected_ids'] = self.selected_ids
        output['include_all'] = self.include_all
        return output


@dataclass
class DateParameter(_Parameter):
    selected_date: datetime
    format: str

    def __init__(self, name: str, label: str, selected_date: str, format: str = '%Y-%m-%d'):
        super().__init__(WidgetType.DateField, name, label)
        self.format = format
        try:
            self.selected_date = datetime.strptime(selected_date, format)
        except ValueError:
            raiseParameterError(name, f'the selected value "{selected_date}" could not be converted to a date')
    
    def set_selection(self, selection: str):
        self.selected_date = datetime.strptime(selection, self.format)

    def get_selected_date(self) -> str:
        return self.selected_date.strftime(self.format)

    def get_selected_date_quoted(self) -> str:
        return "'" + self.get_selected_date() + "'"
    
    def to_dict(self):
        output = super().to_dict()
        output['selected_date'] = self.get_selected_date()
        return output


@dataclass
class _NumericParameter(_Parameter):
    min_value: Decimal
    max_value: Decimal
    increment: Decimal

    def __post_init__(self):
        self.min_value = Decimal(self.min_value)
        self.max_value = Decimal(self.max_value)
        self.increment = Decimal(self.increment)
        if self.min_value > self.max_value:
            raiseParameterError(self.name, f'the min_value "{self.min_value}" must be less than the max_value "{self.max_value}"', ValueError)
        if (self.max_value - self.min_value) % self.increment != 0:
            raiseParameterError(self.name, f'the increment "{self.increment}" must fit evenly between the min_value "{self.min_value}" and max_value "{self.max_value}"', ValueError)

    def validate_value(self, value):
        if value < self.min_value or value > self.max_value:
            raiseParameterError(self.name, f'the selected value "{value}" is out of bounds', ValueError)
        if (value - self.min_value) % self.increment != 0:
            raiseParameterError(self.name, f'the difference between selected value "{value}" and min_value "{self.min_value}" must be a multiple of increment "{self.increment}"', ValueError)

    def to_dict(self):
        output = super().to_dict()
        output['min_value'] = str(self.min_value)
        output['max_value'] = str(self.max_value)
        output['increment'] = str(self.increment)
        return output


@dataclass
class NumberParameter(_NumericParameter):
    selected_value: Decimal

    def __init__(self, name: str, label: str, min_value: Union[Decimal, int, str], max_value: Union[Decimal, int, str], 
                 increment: Union[Decimal, int, str], selected_value: Union[Decimal, int, str]):
        super().__init__(WidgetType.NumberField, name, label, min_value, max_value, increment)
        self.selected_value = Decimal(selected_value)
        self.validate_value(selected_value)
    
    def set_selection(self, selection: str):
        self.selected_value = Decimal(selection)

    def get_selected_value(self) -> str:
        return str(self.selected_value)
        
    def to_dict(self):
        output = super().to_dict()
        output['selected_value'] = self.get_selected_value()
        return output


@dataclass
class RangeParameter(_NumericParameter):
    selected_lower_value: Decimal
    selected_upper_value: Decimal

    def __init__(self, name: str, label: str, min_value: Union[Decimal, int, str], max_value: Union[Decimal, int, str], increment: Union[Decimal, int, str], 
                 selected_lower_value: Union[Decimal, int, str], selected_upper_value: Union[Decimal, int, str]):
        super().__init__(WidgetType.RangeField, name, label, min_value, max_value, increment)
        self.selected_lower_value = Decimal(selected_lower_value)
        self.selected_upper_value = Decimal(selected_upper_value)
        self.validate_value(selected_lower_value)
        self.validate_value(selected_upper_value)
    
    def set_selection(self, selection: str):
        lower, upper = selection.split(',')
        self.selected_lower_value = Decimal(lower)
        self.selected_upper_value = Decimal(upper)

    def get_selected_lower_value(self) -> str:
        return str(self.selected_lower_value)

    def get_selected_upper_value(self) -> str:
        return str(self.selected_upper_value)

    def to_dict(self):
        output = super().to_dict()
        output['selected_lower_value'] = self.get_selected_lower_value()
        output['selected_upper_value'] = self.get_selected_upper_value()
        return output


@dataclass
class DataSourceParameter(_Parameter):
    data_source: OptionsDataSource
    trigger_refresh: bool = False
    parent: Optional[str] = None
    
    def get_data_source(self) -> OptionsDataSource:
        return self.data_source

    def convert(self, df: pd.DataFrame = None) -> _Parameter:
        from_sample = (df is not None)
        if not from_sample:
            conn = DbConnection()
            df = conn.get_dataframe_from_query(self.data_source.get_query())
        
        new_param = None
        if self.widget_type == WidgetType.SingleSelect or self.widget_type == WidgetType.MultiSelect:
            id_col = 'id' if from_sample else self.data_source.id_col
            options_col = 'options' if from_sample else self.data_source.options_col
            order_by_col = 'ordering' if from_sample else self.data_source.order_by_col
            default_col = 'default' if from_sample else self.data_source.is_default_col
            parent_id_col = 'parent_id' if from_sample else self.data_source.parent_id_col
            def get_parent_id(row):
                if parent_id_col is not None and not pd.isnull(row[parent_id_col]):
                    return str(row[parent_id_col])
                else:
                    return None
            
            df.sort_values(order_by_col, inplace=True)
            options = [ParameterOption(str(row[id_col]), str(row[options_col]), get_parent_id(row)) for _, row in df.iterrows()]
            
            selected_ids = []
            if default_col is not None:
                df_filtered = df.query(f'{default_col} == 1')
                selected_ids = [str(x) for x in df_filtered[id_col].values.tolist()]
            
            if self.widget_type == WidgetType.SingleSelect:
                selected_id = selected_id[0] if len(selected_ids) > 0 else None
                new_param = SingleSelectParameter(self.name, self.label, options, selected_id, self.trigger_refresh, self.parent)
            else:
                new_param = MultiSelectParameter(self.name, self.label, options, selected_ids, self.trigger_refresh, self.parent)
        elif self.widget_type in [WidgetType.DateField, WidgetType.NumberField, WidgetType.RangeField]:
            raiseParameterError(self.name, f'the widget type "{self.widget_type}" is not supported yet')
        else:
            raiseParameterError(self.name, f'no such widget type "{self.widget_type}"') 
        
        return new_param
    
    def to_dict(self):
        output = super().to_dict()
        output['data_source'] = self.data_source.__dict__
        return output


class _ParameterSet:
    def __init__(self):
        self.parameters_dict: OrderedDict[str, _Parameter] = OrderedDict()
        self.data_source_params: OrderedDict[str, DataSourceParameter] = OrderedDict()

    def add(self, parameters: List[_Parameter]):
        for param in parameters:
            self.parameters_dict[param.name] = param
            if isinstance(param, DataSourceParameter):
                self.data_source_params[param.name] = param
            param.refresh()

    def get_parameter(self, param_name):
        if param_name in self.parameters_dict:
            return self.parameters_dict[param_name]
        else:
            raise KeyError(f'No such parameter exists called "{param_name}"')
    
    def get_parent_parameter(self, param_name) -> _SelectionParameter:
        param = self.get_parameter(param_name)
        if hasattr(param, 'parent') and param.parent is not None:
            parent_param_name = param.parent
        else:
            raiseParameterError(param_name, 'it does not have a non-null "parent" attribute... cannot use "get_parent_parameter"')
        
        try:
            return self.get_parameter(parent_param_name)
        except KeyError:
            message = f'the options depend on parameter "{parent_param_name}"... so "{parent_param_name}" must be defined beforehand'
            raiseParameterError(param_name, message)

    def convert_datasource_params(self, test_file: str = None):
        df_all = pd.read_csv(test_file) if test_file is not None else None
        for key, ds_param in self.data_source_params.items():
            df = df_all.query(f'parameter == "{key}"') if df_all is not None else None
            new_param = ds_param.convert(df)
            self.parameters_dict[key] = new_param
            new_param.refresh()
        self.data_source_params.clear()
    
    def to_dict(self):
        output = {'parameters': [x.to_dict() for x in self.parameters_dict.values()]}
        return output


parameters = _ParameterSet()
