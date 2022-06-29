from calendar import month
import os
from nbformat import read
import pandas as pd
import numpy as np

#functions to work with diffirerent types of files

#read binary files
def readBytes(filename):
    with open(filename, 'rb') as file:
        b = file.read()       
    return b

def readEmission(filename):
    dataframe = pd.DataFrame(np.reshape( (np.array(np.fromfile(filename, dtype='uint16'))), (-1,6144)))
    dataframe.drop(dataframe.columns[3072:],axis=1)
    dataframe['time'] = dataframe.iloc[:,3] + dataframe.iloc[:,4] * 65536

    dataframe['temp'] = dataframe.iloc[:,8] * 1000000 + dataframe.iloc[:,9] * 1000 + dataframe.iloc[:,10]
    dataframe['date'] = 0
    delta_time = dataframe.iloc[0, -3]
    begin_date = dataframe.iloc[0, -2]

    for d in range(len(dataframe['time'])):
      dataframe.iloc[d, -3] = (dataframe.iloc[d, -3]-delta_time)

    for d in range(len(dataframe['time'])):
      dataframe.iloc[d, -1] = (dataframe.iloc[d, -3]/1000 + begin_date)    
    
    for d in range(len(dataframe['date'])):
      dataframe.iloc[d, -1] = datetime.fromtimestamp(dataframe.iloc[d, -1])

    dataframe = dataframe.drop(dataframe.iloc[:, :12], axis=1)
    dataframe = dataframe.drop(dataframe[['temp', 'time']], axis=1)
    return dataframe

def readLCR(filename):
    with open(filename, 'r') as file:
        data = ' '.join(file.read().split())
    months = {"Jan":'1', "Feb":'2', "Mar":'3', "Apt":'4', "May":'5', "Jun":'6', "Jul":'7', "Aug":'8', "Sep":'9', "Oct":'10', "Nov":'11', "Dec":'12'}  
    
    temparray = np.reshape((np.array(data.split())), (-1, 10)) 
    file = pd.DataFrame(temparray)
    file = file.iloc[:, [0, 4, 6, 7, 8, 9]]

    file.iloc[:, 2] = file.iloc[:, 2].replace(months)
    file['datetime'] = pd.to_datetime(file.iloc[:, 5]+' '+ file.iloc[:, 2]+' '+ file.iloc[:, 3]+' '+ file.iloc[:, 4])
    file = file.iloc[:, [0,1,-1]]
    file.columns=['var1', 'var2', 'datetime']
    return file

def readTemp(filename):
    with open(filename, 'rb') as file:
        tempdata = file.read().decode('unicode_escape').replace('\r', '')
    fdata =  tempdata.replace(' °C', '').split('\n')
    fcolumns = fdata[9].split(';')
    fdata = fdata[10:]
    data = []
    for x in fdata:
        if not x:
            break
        part = x.split(';')
        data.append(part)
    return pd.DataFrame(np.array(data), columns = fcolumns)

def readLAI(filename):
    with open(filename, 'r') as file:
        fdata = file.read().split('\n') 
    temp_list = list()
    for x in fdata:
        temp = x.split('\t')
        temp_list.append(temp[:-1])
    frame = pd.DataFrame(temp_list, columns = ['var1', 'var2', 'var3'] )
    return frame

def readPress(filename):
    with open(filename, 'r') as file:
        fdata = file.read()
    tempdata = fdata.split('\n')
    data = list()
    
    temparray = list()

    for x in tempdata:
      if x:
        temparray.append(x)

    beg = 0
    end = 0
    data = list()
    for i in range(len(temparray)):
      if 'Start' in temparray[i]:
        beg = i
      if 'Stop' in temparray[i]:
        data.extend(temparray[beg:i+1])
    return data
#steps and frequency

months = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}
LCRvalues = ["var1", "var2", "var3", "var4", "var5", "month", "day", "time", "year"]

current_path = os.path.join((os.path.dirname(__file__)), 'Исходные данные', 'Пресс' )

#pathes for the files
emission_path = os.path.join(current_path, 'AE_DEF', '010622.001')
lcr_path = os.path.join(current_path, 'AKTAKOM', 'AM3001-100.txt')
Fluke_path =os.path.join(current_path, 'Temperature 01.06.22.csv')
LAI24_path = os.path.join(current_path, 'La_i_24', '01.06.2022 13.59.12. 6.25Hz. Channels = 4.txt')
Press_path = os.path.join(current_path, 'log.log')

#retriving files
#data reading and cleaning up
emission_data = pd.DataFrame(np.array(np.fromfile(emission_path, dtype='uint16')))


lcr_data = readLCR(lcr_path)
lcr_data.head()

fluke_data = readTemp(Fluke_path)

LAI24_data = readLAI(LAI24_path)

Press_data = readPress(Press_path)