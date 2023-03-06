import time
from squirrels import profile_manager as pm, constants as c
from squirrels import context as context

start = time.time()
from sqlalchemy import create_engine, text
c.timer.add_activity_time(c.IMPORT_SQLALCHEMY, start)

start = time.time()
import pandas as pd
c.timer.add_activity_time(c.IMPORT_PANDAS, start)


class DbConnection:
    def __init__(self, in_memory = False):
        context.initialize(c.MANIFEST_FILE)
        if in_memory:
            self.engine = create_engine('sqlite:///:memory:')
        else:
            profile_name = context.parms[c.DB_PROFILE_KEY]
            profile = pm.Profile(profile_name).get()
            self.engine = create_engine(f'{profile[c.DIALECT]}://{profile[c.USERNAME]}:{profile[c.PASSWORD]}@{profile[c.CONN_URL]}')

    
    def get_dataframe_from_query(self, query: str):
        """
        Executes a SQL query and returns the results as a pandas DataFrame.

        Args:
            query (str): The SQL query to execute.

        Returns:
            A pandas DataFrame containing the results of the query.
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        return df

        