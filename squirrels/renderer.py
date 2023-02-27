import os, json, time
import concurrent.futures
from typing import Dict, Tuple
from importlib.machinery import SourceFileLoader
from configparser import ConfigParser
from squirrels import constants as c, parameter_configs, context as ct
from squirrels.db_conn import DbConnection

start = time.time()
import jinja2 as j2
c.timer.add_activity_time(c.IMPORT_JINJA, start)

start = time.time()
from pandas import DataFrame
from pandasql import sqldf
c.timer.add_activity_time(c.IMPORT_PANDAS, start)


class Renderer:
    def __init__(self, dataset, selection_cfg: str = None, lu_data: str = None) -> None:
        self.dataset = dataset
        self.input_folder = os.path.join(c.DATASETS_FOLDER, dataset)
        self.selection_cfg = os.path.join(self.input_folder, selection_cfg) if selection_cfg is not None else None
        if self.selection_cfg is not None and not os.path.exists(self.selection_cfg):
            raise FileNotFoundError(f'The selection cfg file "{self.selection_cfg}" could not be found relative to the "datasets/[dataset]" folder')
        self.lu_data = lu_data

        
    def load_parameters(self) -> parameter_configs._ParameterSet:
        module_path = os.path.join(self.input_folder, c.PARAMETERS_MODULE+'.py')
        SourceFileLoader(c.PARAMETERS_MODULE, module_path).load_module()
        return parameter_configs.parameters
    
    
    def run_final_view_in_python(self, py_file: str, database_views: Dict[str, DataFrame]) -> DataFrame:
        module_path = os.path.join(self.input_folder, py_file)
        module = SourceFileLoader(c.PARAMETERS_MODULE, module_path).load_module()
        return module.main(database_views)

    
    def render_view(self, view_file: str) -> str:
        parms_dict = parameter_configs.parameters.parameters_dict
        env = j2.Environment(loader=j2.FileSystemLoader('.'))
        template = env.get_template(view_file.replace('\\', '/'))
        return template.render(parms_dict)
    

    def get_rendered_sql_by_view(self) -> Dict[str, str]:
        dataset_parms = ct.parms[c.DATASETS_KEY][self.dataset]
        bigdata_sql = dataset_parms[c.DATABASE_VIEWS_KEY]
        
        output = {}
        for view_name, view_file in bigdata_sql.items():
            input_path = os.path.join(self.input_folder, view_file)
            output[view_name] = self.render_view(input_path)
        return output


    def get_all_results(self, sql_by_view_name: str, final_view_name: str, final_view_sql_str: str = None) -> Tuple[Dict[str, DataFrame], DataFrame]:
        conn = DbConnection()
        def run_single_query(item) -> Dict[str, DataFrame]:
            view_name, query = item
            return view_name, conn.get_dataframe_from_query(query)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            df_by_view_name = dict(executor.map(run_single_query, sql_by_view_name.items()))
        
        if final_view_name in sql_by_view_name:
            final_df = df_by_view_name[final_view_name]
        elif final_view_name.endswith('.py'):
            final_df = self.run_final_view_in_python(final_view_name, df_by_view_name)
        else:
            final_df = sqldf(final_view_sql_str, env=df_by_view_name)
        
        return df_by_view_name, final_df
    

    def write_outputs(self, runquery: bool):
        # Dynamically import the parameters.py configuration file
        start = time.time()
        parms = self.load_parameters()
        c.timer.add_activity_time('dynamic import', start)

        # Convert all datasources parameters to widget parameters
        start = time.time()
        parms.convert_datasource_params(self.lu_data)
        c.timer.add_activity_time('convert datasources', start)

        # Apply selections from selections.cfg
        start = time.time()
        if self.selection_cfg is not None:
            parms_dict = parms.parameters_dict
            config = ConfigParser()
            config.read(self.selection_cfg)
            parameters_sections = [c.DATES_SECTION, c.NUMBERS_SECTION, c.RANGES_SECTION, c.SINGLE_SELECT_SECTION, c.MULTI_SELECT_SECTION]
            for section in parameters_sections:
                if config.has_section(section):
                    for key, selection in config.items(section):
                        parameter = parms_dict[key]
                        parameter.refresh()
                        parameter.set_selection(selection)
        c.timer.add_activity_time('apply selections', start)

        # Clear output folder contents and write the parameters metadata to file
        start = time.time()
        output_folder = os.path.join(c.OUTPUTS_FOLDER, self.dataset)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        files = os.listdir(output_folder)
        for file in files:
            file_path = os.path.join(output_folder, file)
            os.remove(file_path)
        
        parameters_outfile = os.path.join(output_folder, c.PARAMETERS_OUTPUT)
        with open(parameters_outfile, 'w') as f:
            json.dump(parms.to_dict(), f, indent=4)
        c.timer.add_activity_time('write parameters', start)
        
        # Render and write the sql queries
        start = time.time()
        dataset_parms = ct.parms[c.DATASETS_KEY][self.dataset]
        
        def write_sql_file(view_name, sql_str):
            sql_file = os.path.join(output_folder, view_name+'.sql')
            with open(sql_file, 'w') as f:
                f.write(sql_str)
        
        sql_by_view_name = self.get_rendered_sql_by_view()
        for view_name, final_view_sql_str in sql_by_view_name.items():
            write_sql_file(view_name, final_view_sql_str)

        final_view_name = dataset_parms[c.FINAL_VIEW_KEY]
        final_view_sql_str = None
        if final_view_name not in sql_by_view_name and not final_view_name.endswith('.py'):
            final_view_path = os.path.join(self.input_folder, final_view_name)
            final_view_sql_str = self.render_view(final_view_path)
            write_sql_file(c.FINAL_VIEW_NAME, final_view_sql_str)
        c.timer.add_activity_time('write sql files', start)

        # Run the sql queries and write output
        if runquery:
            start = time.time()
            df_by_view_name, final_df = self.get_all_results(sql_by_view_name, final_view_name, final_view_sql_str)
            
            for view_name, df in df_by_view_name.items():
                csv_file = os.path.join(output_folder, view_name+'.csv')
                df.to_csv(csv_file, index=False)
            
            final_csv_path = os.path.join(output_folder, c.FINAL_VIEW_NAME+'.csv')
            final_df.to_csv(final_csv_path, index=False)
            c.timer.add_activity_time('query and write results', start)

        # Print status
        print(f'Outputs written! See the "{output_folder}" folder for output files')
