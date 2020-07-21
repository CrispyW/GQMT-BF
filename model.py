import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from connect_data import *

register_matplotlib_converters()

def read_time_series(): # 要加try except防止报错
	# nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	te = datetime.datetime.now()
	ts = te - datetime.timedelta(hours=8)

	cursor = sqlserver_conn(db="Runtime", usr="sa", pwd="123QWE!@#", addr="10.20.0.21", port="1433")
	query = "SELECT DateTime, TagName, Value FROM Runtime.dbo.AnalogHistory WHERE TagName='CC.GF.mq_lyl' AND DateTime between '%s' and '%s'"%(ts, te)
	cursor.execute(query)
	name = [i[0] for i in cursor.description]
	raw_data = pd.DataFrame.from_records(cursor.fetchall(),columns=name)
	raw_data = raw_data.drop_duplicates('DateTime').set_index('DateTime')
	raw_data.index = pd.to_datetime(raw_data.index) 
	# raw_data = raw_data.set_index('DateTime')
	cursor.close()
	return(raw_data[['Value']])

def model_output(data):
	return(data['Value'].mean())
