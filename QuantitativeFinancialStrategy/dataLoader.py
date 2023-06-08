import tushare as ts
import sqlite3
import pandas as pd
import logging

class DataLoader:

    def __init__(self, code, start_date, end_date, ktype='D', autype='qfq'):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.ktype = ktype
        self.autype = autype
        self.conn = None

    def __enter__(self):
        try:
            # get data
            df = ts.get_k_data(self.code, start = self.start_date, end = self.end_date, ktype = self.ktype, autype = self.autype)
            # save data to 数据库
            self.conn = sqlite3.connect(":memory:")
            df.to_sql('k_data', self.conn, if_exists = 'replace')
            return self
        except Exception as e:
            logging.error(f"Error retrieving stock data: {str(e)}" )
            self.conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def get_data(self):
        # read data
        df = pd.read_sql('select * from k_data', self.conn, index_col='date')
        print("finish data reading")
        return df