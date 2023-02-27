from squirrels.db_conn import DbConnection
from squirrels import constants as c
import time

start = time.time()
import pandas as pd
c.timer.add_activity_time(c.IMPORT_PANDAS, start)


def test_get_dataframe_from_query():
    conn = DbConnection()
    df = conn.get_dataframe_from_query('SELECT 1 as col1, 2 as col2')
    df_expected = pd.DataFrame({'col1': [1], 'col2': [2]})
    assert(df.equals(df_expected))
