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

#reading text files
def readLCR(filename):
    with open(filename, 'r') as file:
        data = ' '.join(file.read().split())
    temparray = np.reshape((np.array(data.split())), (-1, 10)) 
    file = pd.DataFrame(temparray)
    return file

def readTemp(filename):
    with open(filename, 'rb') as file:
        data = file.read()
    return data   

def readLAI (filename):
    with open(filename, 'r') as file:
        data = np.array(file.read().split('\n'))
    return pd.DataFrame(data)



months = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}
LCRvalues = ["var1", "var2", "var3", "var4", "var5",  "weekday", "month", "day", "time", "year"]


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
lcr_data.columns = LCRvalues
lcr_data.replace({"month":months})

print(lcr_data)

Fluke_data = readTemp(Fluke_path)

LAI24_data = open(LAI24_path).read()

LAI24_data = readLAI(LAI24_path)

#Press_data
