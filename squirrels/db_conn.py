import time
from squirrels import profile_manager as pm, constants as c

start = time.time()
from sqlalchemy import create_engine, text
c.timer.add_activity_time(c.IMPORT_SQLALCHEMY, start)

start = time.time()
import pandas as pd
c.timer.add_activity_time(c.IMPORT_PANDAS, start)


class DbConnection:
    def __init__(self, profile_name: str):
        if profile_name is not None and profile_name != '':
            profile = pm.Profile(profile_name).get()
            self.engine = create_engine(f'{profile[c.DIALECT]}://{profile[c.USERNAME]}:{profile[c.PASSWORD]}@{profile[c.CONN_URL]}')
        else:
            self.engine = None

    
    def get_dataframe_from_query(self, query: str):
        """
        Executes a SQL query and returns the results as a pandas DataFrame.

        Args:
            query (str): The SQL query to execute.

        Returns:
            A pandas DataFrame containing the results of the query.
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
        except AttributeError as e:
            raise ValueError('A profile name must be specified for database views that use sql')

        return df

        