# python -m pip install requests
import requests
# library?
import pandas as pd
import matplotlib.pyplot as plt

URL = "https://eps-datalogger.herokuapp.com/api/data/all"

#result = requests.get(url=URL)
#print("status code:", result.status_code)
#print("headers:", result.headers)

#json = result.json()
df = pd.read_json(URL)
print("dataframe columns")
print(df.columns)
#print(df)

# find missing data
#print("missing battery data")
#print(df['battery'].isnull())

# replace missing data with 0
# df.fillna(method='pad'), df.fillna(method='bfill')
#print("replace missing data")
#print(df.fillna(0))

# drop missing data
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dropna.html
#print("drop missing data")
#print(df.dropna())
# drop rows that are missing battery,humidity,temperature,string1 data
df = df.dropna(subset=['battery','humidity','temperature','string1'])
#print(df)

# panads .loc()
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.loc.html
#print("reading specific rows and columns")
#print(df.loc[:,['battery','humidity', 'temperature', 'string1']])



print("queried df")
#df2 = df.query("area == '3d-printer' and temperature >= 22.0 and string1.str.contains('2022-06-21')")
# query: 3dprinter, temp >= 22.0, date range
df2 = df.query("area == '3d-printer' and device_id == 'feather2'\
    and string1 >= '2022-06-21 00:00:00.000' and string1 <= '2022-06-22 00:00:00.000'")
    # and not string1.str.contains('MDT')")
print("feather2 data")
print(df2.loc[:,['light', 'water_level', 'humidity', 'temperature', 'sound', 'string1']])

feather1_df = df.query("area == '3d-printer' and device_id == 'feather1'\
    and string1 >= '2022-06-21 00:00:00.000' and string1 <= '2022-06-22 00:00:00.000'")
    # and not string1.str.contains('MDT')")
print("feather1 data:")
print(feather1_df.loc[:,['light', 'water_level', 'humidity', 'temperature', 'sound', 'string1']])

def draw_multiple_graphs(num_rows):

    # multiple graphs
    # figsize in inches
    figure, axis = plt.subplots(2,3, figsize=(20,7))

    # plot temp
    range = num_rows
    # x_plot = df2.loc[:range,'string1']
    # y_plot = df2.loc[:range,'temperature']
    x_temp = df2.iloc[:range,14]
    y_temp = df2.iloc[:range,9]
    x1_temp = feather1_df.iloc[:range,14]
    y1_temp = feather1_df.iloc[:range,9]
    axis[0,0].set_title("temperature over time")
    axis[0,0].plot(x_temp,y_temp, label="feather2")
    axis[0,0].plot(x1_temp,y1_temp, label="feather1")
    plt.legend()

    # plot humidity
    # x_hum = df2.loc[:range,'string1']
    # y_hum = df2.loc[:range,'humidity']
    x_hum = df2.iloc[:range,14]
    y_hum = df2.iloc[:range,8]
    axis[0,1].set_title("humidity over time")
    axis[0,1].plot(x_hum,y_hum)

    # plot light
    x_light = df2.iloc[:range,14]
    y_light = df2.iloc[:range,6]
    axis[0,2].set_title("light over time")
    axis[0,2].plot(x_light,y_light)

    # plot water
    x_water = df2.iloc[:range,14]
    y_water = df2.iloc[:range,7]
    axis[1,0].set_title("water level over time")
    axis[1,0].plot(x_water,y_water)

    # plot sound
    x_sound = df2.iloc[:range,14]
    y_sound = df2.iloc[:range,11]
    axis[1,1].set_title("sound over time")
    axis[1,1].plot(x_sound,y_sound)

    #plt.tight_layout()
    plt.show()

draw_multiple_graphs(5)