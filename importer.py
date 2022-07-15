import os
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import (MaxNLocator, AutoMinorLocator)

#functions to read files and all data in it
def readEmission(filename):
  df = pd.DataFrame(np.reshape( (np.array(np.fromfile(filename, dtype='uint16'))), (-1,6144)))
  df.drop(df.columns[3072:],axis=1)

  time = list(df.iloc[:,3] + df.iloc[:,4] * 65536)
  
  delta_time = time[0]
  begin_date = df.iloc[0,8] * 1000000 + df.iloc[0,9] * 1000 + df.iloc[0,10]

  final_list = list()
  for d in range(len(df)):
    final_list.append(datetime.datetime.fromtimestamp(((time[d] -delta_time)/1000 + begin_date)).strftime('%d.%m.%Y %H:%M:%S.%f'))
  
  df['datetime'] = pd.to_datetime(final_list, format='%d.%m.%Y %H:%M:%S.%f')

  df = df.drop(df.iloc[:, :12], axis=1)
 
  df['step'] = range(1, len(df) + 1)
  
  df.set_index('datetime')
  return df

def readLCR(filename):
  with open(filename, 'r') as file:
      data = ' '.join(file.read().split())
  months = {"Jan":'1', "Feb":'2', "Mar":'3', "Apt":'4', "May":'5', "Jun":'6',
            "Jul":'7', "Aug":'8', "Sep":'9', "Oct":'10', "Nov":'11', "Dec":'12'}  
  
  temparray_x = np.reshape((np.array(data.split())), (-1, 10)) 
  df = pd.DataFrame(temparray_x)
  df = df.iloc[:, [0, 4, 6, 7, 8, 9]]

  df.iloc[:, 2] = df.iloc[:, 2].replace(months)
  
  df['datetime'] = df.iloc[:, 5]+' '+ df.iloc[:, 2]+' '+ df.iloc[:, 3]+' '+ df.iloc[:, 4]+'.0'
  df = df.iloc[:, [0,1,-1]]
  df.columns=['var1', 'var2', 'datetime']
  
  df['datetime'] = pd.to_datetime(df['datetime'], format='%Y %m %d %H:%M:%S.%f')
  df['var1'] = df['var1'].astype(np.float64)
  df['var2'] = df['var2'].astype(np.float64)
  #df[['var1', 'var2']] = df[['var1', 'var2']].apply(pd.to_numeric)
  
  return df

def readTemp(filename):
  with open(filename, 'rb') as df:
    tempdata = df.read().decode('unicode_escape').replace('\r', '')
  fdata =  tempdata.replace(' °C', '').split('\n')
  col_temp = fdata[9].split(';')
  fcolumns = col_temp[1:2]
  fcolumns.append('datetime')
  fdata = fdata[10:]
  datas = []

  for x in fdata:
    if not x:
      break
    part = x.split(';')
    datas.append(part[1:3])
  data = np.array(datas)
  
  temp = list()
  for x in range(len(data)):
    temp_t = data[x, 0]
    if x==0 or x == len(data)-1:
      temp.append((data[x]))
    else:
      if temp_t != data[x-1, 0] or temp_t!= data[x+1, 0]:
        temp.append((data[x]))
  
  df = pd.DataFrame(temp, columns=fcolumns)
  df['Sample'] = pd.to_numeric(df['Sample'])
  df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%y %H:%M:%S.%f')
  
  return df

def readLAI(filename):
  with open(filename, 'r') as df:
      fdata = df.read().split('\n') 
  temp_list = list()
  for x in fdata:
    if x:
      temp = x.split('\t')
      temp_list.append(temp[:-1])
  df = pd.DataFrame(temp_list, columns = ['var1', 'var2', 'var3'] )
  
  d_temp = (filename.split('\\')[-1]).split(' ')
  date_part = d_temp[0]
  time_part = d_temp[1] + '0'
  dttm = date_part + ' ' + time_part
  start_datetime = datetime.datetime.strptime(dttm, '%d.%m.%Y %H.%M.%S.%f')

  tt = list()

  for x in range (len(df)):
    tt.append( (start_datetime + x * datetime.timedelta(milliseconds=160)) )

  df['datetime'] = tt
  #df[['var1', 'var2', 'var3']] = df[['var1', 'var2', 'var3']].apply(pd.to_numeric)
  df['var1'] = df['var1'].astype(np.float64)
  df['var3'] = df['var3'].astype(np.float64)
  df['var2'] = df['var2'].astype(np.float64)
  return df

def readPress(filename):
  with open(filename, 'r') as df:
      fdata = df.read()
  tempdata = fdata.split('\n')
    
  temparray_x = list()

  for x in tempdata:
    if x:
      temparray_x.append(x)

  beg = 0
  data = list()
  for i in range(len(temparray_x)):
    if 'Start' in temparray_x[i]:
      beg = i
    if 'Stop' in temparray_x[i]:
      data.extend(temparray_x[beg:i+1])
  return data
  #data not used yet

def readSiglent(filename):
  with open(filename, 'r') as df:
    tempdata = df.read().split('\n')
  
  date_data = list()
  on_data = list()
  tempd = str()
  
  for x in range(len(tempdata)):
    dt_data = tempdata[x].split(' ')
    if tempdata[x][-2:]=='on':
      tempd = (dt_data[0] + ' ' + dt_data[1] + '.0')
    if tempdata[x][-2:]=='ff':
      if on_data == [] and not tempd:
        continue
      else:
        date_data.extend([tempd, (dt_data[0] + ' ' + dt_data[1] + '.0')])
        on_data.extend([1, 0])
  df = pd.DataFrame({'datetime': date_data, 'Power':on_data})
  
  df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M:%S.%f')
  return df
#end of functions

#section for sample data
current_path = os.path.join((os.path.dirname(__file__)), 'Исходные данные', 'Пресс' )

  #pathes for the files
emission_path = os.path.join(current_path, 'AE_DEF', '010622.001')
lcr_path = os.path.join(current_path, 'AKTAKOM', 'AM3001-100.txt')
Fluke_path =os.path.join(current_path, 'Temperature 01.06.22.csv')
LAI24_path = os.path.join(current_path, 'La_i_24', '01.06.2022 13.59.12. 6.25Hz. Channels = 4.txt')
Press_path = os.path.join(current_path, 'log.log')
Siglent_path = os.path.join(current_path, 'Siglent', 'log.txt')

  #retriving files
Emission_data = readEmission(emission_path)
LCR_data = readLCR(lcr_path)
Tempr_data = readTemp(Fluke_path)
LAI24_data = readLAI(LAI24_path)
Press_data = readPress(Press_path)
Siglent_data = readSiglent(Siglent_path)
#end of reading data

#graphs section
  
  #functions for separate plotting, df to pass appropriate dataframe
def draw_Emi(df):
  fig = plt.figure(figsize=(13,6))
  ax = fig.add_axes([0.2, 0.2, 0.5, 0.7])

  x_e = df['datetime']
  y_e = df['step']

  ax.plot(x_e, y_e, color='r')
  ax.xaxis.set_major_locator(MaxNLocator(10))
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S.%f"))
  ax.grid(axis='both')
  fig.autofmt_xdate()
  plt.show()
  
def draw_Tempr(df):
  fig = plt.figure(figsize=(18,10))
  ax = fig.add_axes([0.2, 0.2, 0.5, 0.7])

  x = df['Start Time']
  y = df['Sample']


  ax.plot(x, y, color='r')
  ax.xaxis.set_major_locator(MaxNLocator(10))
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S.%f"))
  ax.xaxis.set_minor_locator(AutoMinorLocator())
  ax.grid(axis='x')
  fig.autofmt_xdate()

  #plt.get_current_fig_manager().window.showMaximized()
  plt.show()

def draw_LCR(df):
  fig = plt.figure(figsize=(18,10))
  ax1 = fig.add_axes([0.2, 0.2, 0.5, 0.7])


  x_lcr = df['datetime']
  y_lcr1 = df['var1']
  y_lcr2 = df['var2']

  ax1.plot(x_lcr, y_lcr1, color='r')
  ax1.yaxis.set_major_locator(MaxNLocator(10))
  ax1.xaxis.set_major_locator(MaxNLocator(10))
  ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S.%f"))
  ax1.xaxis.set_minor_locator(AutoMinorLocator())
  ax1.grid(axis='x')
  fig.autofmt_xdate()


  ax2 = ax1.twinx()
  ax2.plot(x_lcr, y_lcr2, color='b')

  ax2.yaxis.set_major_locator(MaxNLocator(10))

  #plt.get_current_fig_manager().window.showMaximized()
  plt.show()

def draw_LAI(df):
  fig = plt.figure(figsize=(18,10))
  ax1 = fig.add_axes([0.2, 0.2, 0.5, 0.7])

  x = df['datetime']
  y1 = df['var1']
  y2 = df['var2']
  y3 = df['var3']

  ax1.plot(x, y1, color='r')
  ax1.yaxis.set_major_locator(MaxNLocator(10))
  ax1.xaxis.set_major_locator(MaxNLocator(10))
  ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S.%f"))
  ax1.xaxis.set_minor_locator(AutoMinorLocator())
  ax1.grid(axis='x')
  fig.autofmt_xdate()

  ax2 = ax1.twinx()
  ax3 = ax1.twinx()
  ax2.plot(x, y2, color='b')
  ax2.yaxis.set_major_locator(MaxNLocator(10))
  ax2.xaxis.set_major_locator(MaxNLocator(10))
  ax2.spines['left'].set_position(('axes', 1))
  ax2.yaxis.tick_right()
  
  ax3.plot(x, y3, color='g')
  ax3.yaxis.set_major_locator(MaxNLocator(10))
  ax3.xaxis.set_major_locator(MaxNLocator(10))
  ax3.spines.right.set_position(("axes", 1.2))
  ax3.yaxis.tick_right()
  
  #plt.get_current_fig_manager().window.showMaximized()
  plt.show()

def draw_Siglent(df): 
  fig = plt.figure(figsize=(14,6))
  ax = fig.add_axes([0.2, 0.2, 0.5, 0.7])
  ax.step(df['datetime'],df['Power'], where = 'post', color='r')
  ax.set_yticks([0,1])
  ax.xaxis.set_major_locator(MaxNLocator(10))
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S.%f"))
  ax.grid(axis='x')
  fig.autofmt_xdate()
  plt.show()
  #end of separate plot functions
 
#gathering all read data for further work  
Data_Frames = [Emission_data, Tempr_data, LCR_data, LAI24_data, Siglent_data] 

  #arrays to use in main plotting
xs_not_interpolated = [Emission_data['datetime'], Tempr_data['datetime'], LCR_data['datetime'],
      LAI24_data['datetime'], Siglent_data['datetime']]
ys_not_interpolated = [Emission_data['step'], Tempr_data['Sample'], 
      LCR_data['var1'], LCR_data['var2'], 
        LAI24_data['var1'],LAI24_data['var2'],LAI24_data['var3'], Siglent_data['Power']]

#function to find min max times for overlap data, array_x is dataframes of
def cut_datetime(array_x):
  min_datetime = min(array_x[0])
  max_datetime = max(array_x[0])

  for x in range(1,5):
    if min_datetime < min(array_x[x]):
      min_datetime = min(array_x[x])
    if max_datetime > max(array_x[x]):
      max_datetime = max(array_x[x])
  return [min_datetime, max_datetime]    
#end of function

#section for interpolating data  
for x in range(4):
  
  df = Data_Frames[x]
  
  df = df.set_index('datetime').resample('1S').mean().interpolate()
  df.reset_index(inplace=True)
  if x == 0:
    Cleared_Emission_data = df
  if x == 1:
    Cleared_Tempr_data = df
  if x == 2:
    Cleared_LCR_data = df
  if x == 3:
    Cleared_LAI24_data = df
    
Cleared_Siglent_data = Data_Frames[4]
#finish of interpolating

#cuting data
datetime_lim_inter = cut_datetime([Cleared_Emission_data['datetime'], Cleared_Tempr_data['datetime'], Cleared_LCR_data['datetime'],
      Cleared_LAI24_data['datetime'], Siglent_data['datetime']])
min_dt = datetime_lim_inter[0].to_pydatetime()
max_dt = datetime_lim_inter[1].to_pydatetime()

Cleared_Data_Frames = [Cleared_Emission_data, Cleared_Tempr_data, Cleared_LCR_data, Cleared_LAI24_data]

for x in range(4):
  df = Cleared_Data_Frames[x]
  df = df[ (df['datetime'] >= min_dt )& (df['datetime'] <= max_dt)]
  if x == 0:
    Cleared_Emission_data = df
  if x == 1:
    Cleared_Tempr_data = df
  if x == 2:
    Cleared_LCR_data = df
  if x == 3:
    Cleared_LAI24_data = df
#data cut by dates

#lists of interpolated dataframes axises
xs_interpolated = [Cleared_Emission_data['datetime'], Cleared_Tempr_data['datetime'], Cleared_LCR_data['datetime'],
      Cleared_LAI24_data['datetime'], Siglent_data['datetime']]
ys_interpolated = [Cleared_Emission_data['step'], Cleared_Tempr_data['Sample'], 
      Cleared_LCR_data['var1'], Cleared_LCR_data['var2'], 
        Cleared_LAI24_data['var1'],Cleared_LAI24_data['var2'],Cleared_LAI24_data['var3'], Cleared_Siglent_data['Power']]

#main plot function, array_x: datetimes list of dataframes, array_y list of other data of dataframes 
def draw(array_x, array_y):
  datetime_lims = cut_datetime(array_x)
  
  axs = [None]*5 
  fig, axs = plt.subplots(5, 1, figsize = (16,9), sharex=True)

  for x in range(5):
    axs[x].yaxis.set_major_locator(MaxNLocator(5))
    axs[x].xaxis.set_major_locator(MaxNLocator(10))
    axs[x].xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S"))
    axs[x].xaxis.set_minor_locator(AutoMinorLocator())
    axs[x].grid(axis='x')
    axs[x].spines[['left', 'right', 'top', 'bottom']].set_linewidth(1.2)
    
    if x <= 1:
      axs[x].plot(array_x[x], array_y[x], alpha = 0.7, color='r')
      axs[x].spines['left'].set(color = 'r', linewidth = 1.5 )
      axs[x].tick_params(axis='y', color='r', width = 1.5)
            
    elif x == 2:
      ax1 = axs[x].twinx()
      ax1.spines['right'].set(color = 'b', linewidth = 1.5 )
      ax1.spines['left'].set(color = 'magenta', linewidth = 1.5 )
      axs[x].yaxis.set_major_locator(MaxNLocator(5))
      ax1.yaxis.set_major_locator(MaxNLocator(5))
      axs[x].plot(array_x[x], array_y[2], alpha = 0.7, color='magenta', linewidth = 1.5)
      ax1.plot(array_x[x], array_y[3], alpha = 0.7, color='b', linewidth = 1.5)
      axs[x].tick_params(axis='y', color='magenta', width = 1.5)
      ax1.tick_params(axis='y', color='b', width = 1.5)
        
    elif x == 3:
      ax1 = axs[x].twinx()
      ax2 = axs[x].twinx()
      ax1.spines['right'].set(color = 'orange', linewidth = 1.5 )
      ax2.spines['right'].set(color = 'olive', linewidth = 1.5 )
      ax2.spines['left'].set(color = 'cyan', linewidth = 1.5 )
      ax2.spines['right'].set_position(('axes', 1.2))
      axs[x].yaxis.set_major_locator(MaxNLocator(5))
      ax1.yaxis.set_major_locator(MaxNLocator(5))
      ax2.yaxis.set_major_locator(MaxNLocator(5))
      axs[x].plot(array_x[x], array_y[4], alpha = 0.7, color='cyan', linewidth = 1.5)
      ax1.plot(array_x[x], array_y[5], alpha = 0.7, color='orange', linewidth = 1.5)
      ax2.plot(array_x[x], array_y[6], alpha = 0.7, color='olive', linewidth = 1.5)
      axs[x].tick_params(axis='y', color='cyan', width = 1.5)
      ax1.tick_params(axis='y', color='orange', width = 1.5)
      ax2.tick_params(axis='y', color='olive', width = 1.5)
      
    elif x == 4:
      axs[x].spines['left'].set(color = 'g', linewidth = 1.5 )
      axs[x].step(array_x[x], array_y[7], alpha = 0.7, where = 'post', color='g', linewidth = 1.5)
      axs[x].set_yticks([0,1])
      axs[x].tick_params(axis='y', color='g', width = 1.5)
      
  axs[0].set_xlim(datetime_lims[0], datetime_lims[1])
  plt.subplots_adjust(right=0.75)                
  fig.autofmt_xdate()
  
  plt.show()
  
"""
clean = pd.DataFrame(Emission_data)
clean = clean.set_index('datetime').resample('1S').mean()


fig = plt.figure(figsize=(13,6))
ax = fig.add_axes([0.2, 0.2, 0.5, 0.7])

x_e = Emission_data['datetime']
y_e = Emission_data['step']
y_c = clean['step']


ax.xaxis.set_major_locator(MaxNLocator(10))
ax.yaxis.set_major_locator(MaxNLocator(10))
#ax.plot(x_e, y_e, color='r', alpha = 0.6)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S.%f"))
ax.grid(axis='x')
fig.autofmt_xdate()
clean['step'].interpolate(method='linear').plot()

#ax1 = ax.twinx()
#ax1.yaxis.set_major_locator(MaxNLocator(10))
#ax1.plot(y_c, color='b', alpha=0.6) 

plt.show()
"""
draw(xs_interpolated, ys_interpolated)