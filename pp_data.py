#preprocess data
# convert strings to dates,
# sort ascending
# assign day and week numbers, and 12hour period marks


# coding: utf-8

# In[1]:
import gnureadline
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess as ls

# In[2]:

def getTimeCategory(data):

    yr = data[0].year
    wk = dt.date.isocalendar(data[0])[1]

    # 1 is day, 0 is night

    data[8] = data[0].month
    data[9] = wk + ( abs(2006 - yr) * 52)
    data[10] = dt.date.weekday(data[0])
    # check if daytime or nighttime...
    if ((data[0].hour > 6) & (data[0].hour < 20)):
      data[11] = 1
    else:
      data[11] = 0

    return data


# In[3]:

#convert date strings to dates
def conDates(data):
    try:
        data[0] = pd.datetime.strptime(data[0], '%d/%m/%Y %H:%M:%S')
    except ValueError:
        data[0] = pd.datetime.strptime(data[0], '%d/%m/%Y %H:%M')
    return data


# In[5]:

#nrows=1000 to get first 1000 rows
print("\nReading CSV...\n")
data = pd.read_csv("test_v1.csv", usecols=[1,3,4,5,6,7,8,9])

# In[6]:

print("\nConverting dates...\n")
data = data.apply(conDates, axis=1)
print("\nSorting... \n")
data = data.sort_values(['DateTime'], ascending=True)
data = data.reset_index()
del data['index']

# In[8]:

#data['month'] = pd.DataFrame({'month' : np.zeros(data.size)})
#data['week'] = pd.DataFrame({'week' : np.zeros(data.size)})
#data['dow'] = pd.DataFrame({'dow' : np.zeros(data.size)})
#data['day_period'] = pd.DataFrame({'day_period' : np.zeros(data.size)})

#get time categories: month, week, day, day_period
#print("\nGetting time categories...\n")
#data = data.apply(getTimeCategory, axis=1)

print("\nWriting CSV...\n")
data.to_csv("sorted.csv")
