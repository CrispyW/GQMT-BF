import pandas as pd 
import datetime
import pymssql # mysql
import psycopg2 # postgre


## 连接sqlserver数据库
def sqlserver_conn(db, usr, pwd, addr, port):
    try:
        conn = pymssql.connect(database=db, user=usr, password=pwd, host=addr, port=port)
        cursor = conn.cursor()
    except Exception as err:
        print("CONNECT ERROR: Failed to connect to Sqlserver Database!")
    else:
        return cursor


# #### 读取铁水化验数据
# def get_sample_test_data(table_name,iron_column,iron_ids):
#     cursor=sqlserver_conn(db="dpm", usr="sa", pwd="P@ssw0rd", addr="192.168.100.26")
#     sql = "select * from %s where %s in (%s)"
#     try:
#         iron_ids = "'"+"','".join(iron_ids)+"'"
# #         print(sql % (table_name,iron_column,iron_ids))
#         cursor.execute(sql % (table_name,iron_column,iron_ids))
#         name = [i[0] for i in cursor.description]
#         raw_data =  pd.DataFrame.from_records(cursor.fetchall(),columns=name)
#         raw_data.drop_duplicates(subset=[iron_column],keep = 'last',inplace=True)
#         cursor.close()
#     except:
#         print("Failed to load table:",table_name)
#         raise
#     else:
#         return raw_data