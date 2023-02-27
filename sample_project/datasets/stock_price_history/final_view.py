from pandas import DataFrame
from typing import Dict

def main(database_views: Dict[str, DataFrame]) -> DataFrame:
    return database_views['ticker_history']
