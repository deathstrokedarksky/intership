from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import (MaxNLocator, AutoMinorLocator)
import sys
import os

#global variables
begin_date = end_date = begin_cut = end_cut = pd.to_datetime(0, unit='s')
last_path = os.path.join(os.path.expanduser('~')) #user path
Emission_path=LCR_path=Tempr_path=LAI24_path= Siglent_path = str()
Emission_data=LCR_data=Tempr_data=LAI24_data=Siglent_data = pd.DataFrame() #for raw data
Cleared_Emission_data=Cleared_LCR_data=Cleared_Tempr_data=Cleared_LAI24_data = pd.DataFrame() #for interpolated

interpolated = False

Data_Frames = []

xs = []

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
  
  tempxs = np.reshape((np.array(data.split())), (-1, 10)) 
  df = pd.DataFrame(tempxs)
  df = df.iloc[:, [0, 4, 6, 7, 8, 9]]

  df.iloc[:, 2] = df.iloc[:, 2].replace(months)
  
  df['datetime'] = df.iloc[:, 5]+' '+ df.iloc[:, 2]+' '+ df.iloc[:, 3]+' '+ df.iloc[:, 4]+'.0'
  df = df.iloc[:, [0,1,-1]]
  df.columns=['var1', 'var2', 'datetime']
  
  df['datetime'] = pd.to_datetime(df['datetime'], format='%Y %m %d %H:%M:%S.%f')
  df['var1'] = df['var1'].astype(np.float64)
  df['var2'] = df['var2'].astype(np.float64)
  
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
  
  d_temp = (filename.split('/')[-1]).split(' ')
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

#function to find min max times for overlap data, xs is dataframes of
def cut_datetime(xs):
  min_datetime = min(xs[0])
  max_datetime = max(xs[0])

  for x in range(1,5):
    if min_datetime < min(xs[x]):
      min_datetime = min(xs[x])
    if max_datetime > max(xs[x]):
      max_datetime = max(xs[x])
  return [min_datetime, max_datetime]    
#end of function

class Canvas(FigureCanvas):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('app.ui', self)
        
        #buttons that calls functions to load data, interpolate and plot
        self.load_emi.clicked.connect(self.br1)
        self.load_lcr.clicked.connect(self.br2)
        self.load_fluke.clicked.connect(self.br3)
        self.load_lai.clicked.connect(self.br4)
        self.load_gen.clicked.connect(self.br5)
        self.plotter.clicked.connect(self.draw)
        self.begin.dateTimeChanged.connect(self.set_begin)
        self.end.dateTimeChanged.connect(self.set_end)
        self.begincut.dateTimeChanged.connect(self.set_beginc)
        self.endcut.dateTimeChanged.connect(self.set_endc)
        self.cutter.clicked.connect(self.cutdata)
        self.exporter.clicked.connect(self.exportdata)
        #----------------------------------------------------------------
    
    def set_begin(self):
        global begin_date 
        temp = self.begin.dateTime().toPyDateTime()
        begin_date =pd.to_datetime(temp)
    
    def set_end(self):
        global end_date
        temp = self.end.dateTime().toPyDateTime()
        end_date =pd.to_datetime(temp)  
    
    def set_beginc(self):
        global begin_cut 
        temp = self.begincut.dateTime().toPyDateTime()
        begin_cut =pd.to_datetime(temp)
    
    def set_endc(self):
        global end_cut
        temp = self.endcut.dateTime().toPyDateTime()
        end_cut =pd.to_datetime(temp)        

    def cutdata(self):
        global interpolated, Cleared_Emission_data, Cleared_Tempr_data, Cleared_LCR_data, Cleared_LAI24_data, Data_Frames, Emission_data, Tempr_data, LCR_data, LAI24_data, Siglent_data, xs
            
        Data_Frames = [Emission_data, Tempr_data, LCR_data, LAI24_data, Siglent_data]
        
        if not interpolated:
            #interpolator function         
            for x in range(4):
                df = Data_Frames[x]
                df = df.set_index('datetime').resample('1S').mean().interpolate()
                df.reset_index(inplace=True)
                if x == 0:
                    Emission_data = df
                if x == 1:
                    Tempr_data = df
                if x == 2:
                    LCR_data = df
                if x == 3:
                    LAI24_data = df
            #finish of interpolating
        
        for x in range(4):
            df = Data_Frames[x]
            df = df[ (df['datetime'] >= begin_cut )& (df['datetime'] <= end_cut)]
            if x == 0:
                Cleared_Emission_data = df
            if x == 1:
                Cleared_Tempr_data = df
            if x == 2:
                Cleared_LCR_data = df
            if x == 3:
                Cleared_LAI24_data = df
    
               
    def exportdata(self):
        global Cleared_Emission_data,Cleared_LCR_data,Cleared_Tempr_data,Cleared_LAI24_data,Siglent_data, Emission_path,LCR_path,Tempr_path,LAI24_path,Siglent_path
        Cleared_Emission_data.to_csv(Emission_path[:-4] + '_cleared.txt', index=False)
        Cleared_LCR_data.to_csv(LCR_path[:-4] + '_cleared.txt', index=False)
        Cleared_Tempr_data.to_csv(Tempr_path[:-4] + '_cleared.txt', index=False)
        Cleared_LAI24_data.to_csv(LAI24_path[:-4] + '_cleared.txt', index=False)
        Siglent_data.to_csv(Siglent_path[:-4] + '_cleared.txt', index=False)
            
#functions to upload data to respectable dataframes and into edit lines to visualise path    
    def br1(self):
        global last_path, Emission_path, Emission_data
        Emission_path=QFileDialog.getOpenFileName(self, 'Открыть файл Эмиссии', last_path)[0]
        self.line_emi.setText(Emission_path)
        if Emission_path != '':
            Emission_data = readEmission(Emission_path)
            last_path = Emission_path
        
    def br2(self):
        global last_path, LCR_path, LCR_data
        LCR_path=QFileDialog.getOpenFileName(self, 'Открыть файл LCR датчика', last_path)[0]
        self.line_lcr.setText(LCR_path)
        if LCR_path != '':
            LCR_data = readLCR(LCR_path)
            last_path = LCR_path
        
    def br3(self):
        global last_path, Tempr_data, Tempr_path
        Fluke_path=QFileDialog.getOpenFileName(self, 'Открыть файл Fluke датчика', last_path)[0]
        self.line_fluke.setText(Fluke_path)
        if Fluke_path != '':
            Tempr_data = readTemp(Fluke_path)
            last_path = Fluke_path
        
    def br4(self):
        global last_path, LAI24_path, LAI24_data
        LAI24_path=QFileDialog.getOpenFileName(self, 'Открыть файл LAI24 датчика', last_path)[0]
        self.line_lai.setText(LAI24_path)
        if LAI24_path != '':
            LAI24_data = readLAI(LAI24_path)
            last_path = LAI24_path
     
    def br5(self):
        global last_path, Siglent_path, Siglent_data
        Siglent_path=QFileDialog.getOpenFileName(self, 'Открыть файл датчика пресса', last_path)[0]
        self.line_gen.setText(Siglent_path)
        if Siglent_path != '':
            Siglent_data = readSiglent(Siglent_path)
            last_path = Siglent_path
#--------------------------------end of functions--------------------------------

    def draw(self):
        
        global Data_Frames, Emission_data, Tempr_data, LCR_data, LAI24_data, Siglent_data, xs, interpolated
        
        Data_Frames = [Emission_data, Tempr_data, LCR_data, LAI24_data, Siglent_data]
        
        #interpolator function         
        for x in range(4):
            df = Data_Frames[x]
            df = df.set_index('datetime').resample('1S').mean().interpolate()
            df.reset_index(inplace=True)
            if x == 0:
                Emission_data = df
            if x == 1:
                Tempr_data = df
            if x == 2:
                LCR_data = df
            if x == 3:
                LAI24_data = df
                 
        interpolated = True    
        #finish of interpolating
        
        #lists of dataframes axises
        xs = [Emission_data['datetime'], Tempr_data['datetime'], LCR_data['datetime'], LAI24_data['datetime'], Siglent_data['datetime']]
        ys = [Emission_data['step'], Tempr_data['Sample'], LCR_data['var1'], LCR_data['var2'], 
                LAI24_data['var1'],LAI24_data['var2'],LAI24_data['var3'], Siglent_data['Power']]

        datetime_lims = [None] * 2
        
        if self.checkBox.isChecked():
            datetime_lims[0] = begin_date
            datetime_lims[1] = end_date
        else:
            datetime_lims = cut_datetime(xs)
        
        axs = [None]*5 
        fig, axs = plt.subplots(5, 1, figsize = (16,9), sharex=True)

        for x in range(5):
            axs[x].yaxis.set_major_locator(MaxNLocator(5))
            axs[x].xaxis.set_major_locator(MaxNLocator(10))
            axs[x].xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y %H:%M:%S.%f"))
            axs[x].xaxis.set_minor_locator(AutoMinorLocator())
            axs[x].grid(axis='x')
            axs[x].spines[['left', 'right', 'top', 'bottom']].set_linewidth(1.2)
            
            if x <= 1:
                axs[0].set_ylabel('Emission Steps')
                axs[1].set_ylabel('Temperature')
                axs[x].yaxis.label.set_color('r')
                axs[x].plot(xs[x], ys[x], alpha = 0.7, color='r')
                axs[x].spines['left'].set(color = 'r', linewidth = 1.5 )
                axs[x].tick_params(axis='y', color='r', width = 1.5)          
            elif x == 2:
                ax1 = axs[x].twinx()
                ax1.spines['right'].set(color = 'b', linewidth = 1.5 )
                ax1.spines['left'].set(color = 'magenta', linewidth = 1.5 )
                axs[x].set_ylabel('Tangent')
                ax1.set_ylabel('Resistance (Ohm)')
                axs[x].yaxis.label.set_color('magenta')
                ax1.yaxis.label.set_color('b')
                axs[x].yaxis.set_major_locator(MaxNLocator(5))
                ax1.yaxis.set_major_locator(MaxNLocator(5))
                axs[x].plot(xs[x], ys[2], alpha = 0.7, color='magenta', linewidth = 1.5)
                ax1.plot(xs[x], ys[3], alpha = 0.7, color='b', linewidth = 1.5)
                axs[x].tick_params(axis='y', color='magenta', width = 1.5)
                ax1.tick_params(axis='y', color='b', width = 1.5)   
            elif x == 3:
                ax1 = axs[x].twinx()
                ax2 = axs[x].twinx()
                ax1.spines['right'].set(color = 'orange', linewidth = 1.5 )
                ax2.spines['right'].set(color = 'olive', linewidth = 1.5 )
                ax2.spines['left'].set(color = 'lime', linewidth = 1.5 )
                ax2.spines['right'].set_position(('axes', 1.1))
                axs[x].set_ylabel('Pressure (MPa)')
                ax1.set_ylabel('Longitudinal deformation')
                ax2.set_ylabel('Transverse deformation')
                axs[x].yaxis.label.set_color('lime')
                ax1.yaxis.label.set_color('orange')
                ax2.yaxis.label.set_color('olive')
                axs[x].yaxis.set_major_locator(MaxNLocator(5))
                ax1.yaxis.set_major_locator(MaxNLocator(5))
                ax2.yaxis.set_major_locator(MaxNLocator(5))
                axs[x].plot(xs[x], ys[4], alpha = 0.7, color='lime', linewidth = 1.5)
                ax1.plot(xs[x], ys[5], alpha = 0.7, color='orange', linewidth = 1.5)
                ax2.plot(xs[x], ys[6], alpha = 0.7, color='olive', linewidth = 1.5)
                axs[x].tick_params(axis='y', color='lime', width = 1.5)
                ax1.tick_params(axis='y', color='orange', width = 1.5)
                ax2.tick_params(axis='y', color='olive', width = 1.5)
            elif x == 4:
                axs[x].spines['left'].set(color = 'g', linewidth = 1.5 )
                axs[x].set_ylabel('Press ON/OFF')
                axs[x].yaxis.label.set_color('g')
                axs[x].step(xs[x], ys[7], alpha = 0.7, where = 'post', color='g', linewidth = 1.5)
                axs[x].set_yticks([0,1])
                axs[x].tick_params(axis='y', color='g', width = 1.5)
            
        axs[0].set_xlim(datetime_lims[0], datetime_lims[1])
        plt.subplots_adjust(right=0.8)                
        fig.autofmt_xdate()
        plt.show()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()