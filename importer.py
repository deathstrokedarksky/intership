from calendar import month
import os
from nbformat import read
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    fcolumns[1],fcolumns[2] = fcolumns[2], fcolumns[1]
    fdata = fdata[10:]
    data = []
    for x in fdata:
        if not x:
            break
        part = x.split(';')
        data.append(part)
    df = pd.DataFrame(np.array(data[:-1]), columns = fcolumns)
    df.iloc[:, [1]],df.iloc[:, [2]] = df.iloc[:, [2]], df.iloc[: ,[1]]
    return df

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

#fig, ax = plt.subplots()
#ax.plot(lcr_data.index, lcr_data['var1'], color = 'red')
#ax2 = ax.twinx()
#ax2.plot(lcr_data.index, lcr_data['var2'], color = 'blue')
#plt.show()


fluke_data = readTemp(Fluke_path)

def optimTemp (df, col):

  samp_col = [1,2]
  max_col = [4,5]
  min_col = [7,8]
  findf = list()

  if col == 'Sample':
    n = samp_col
  elif col == 'Max':
    n = max_col
  else:
    n = min_col

  for x in range(len(df.index)):
    temp = df.iloc[x, n[1]]
    if x==0 or x ==len(df.index):
      findf.append(list(df.iloc[x, n]))
    else:
      if temp != df.iloc[x-1, n[1]] or temp!= df.iloc[x+1, n[1]]:
        findf.append(list(df.iloc[x, n]))

  d = pd.DataFrame(findf, columns=(df.columns[n[0]], df.columns[n[1]]))
  return d


samples = optimTemp(fluke_data, 'Sample')
maxes = optimTemp(fluke_data, 'Max')
#mins = optimTemp(fluke_data, 'Min')

fig, ax = plt.subplots()

ax.plot(samples['Start Time'], samples['Sample'], color = 'red')
ax2 = ax.twinx()
ax2.plot(maxes['Max time'], maxes['Max'], color = 'blue')
#ax3 = ax.twinx()
#ax3.plot(newdf['Start time'], newdf['Min'], color = 'green')
plt.show()

LAI24_data = readLAI(LAI24_path)

Press_data = readPress(Press_path)