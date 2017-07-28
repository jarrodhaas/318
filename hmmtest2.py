import gnureadline
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import math as mt
import random as rand


from rpy2.robjects import r, pandas2ri
import rpy2.robjects as ro
from rpy2.robjects.packages import importr


ro.numpy2ri.activate()
pandas2ri.activate()


# read data
print("\nReading data...\n")
parser = lambda date: pd.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
data = pd.read_csv("sorted.csv", nrows=300000, parse_dates=[1], date_parser=parser, index_col=0)


def findDateIndexOld(date):
    for i in range(0,data.shape[0]):
        d = dt.date(data.iloc[i][0].year, data.iloc[i][0].month, data.iloc[i][0].day)
        if (date == d):
            return i

    return -1

def findDateIndex(date):
    # start date of first full day of observations in the data
    start_date = dt.date(2006, 12, 17)
    #how many days have passed between start date and input date
    days = (date - start_date).days

    # return the index: 60 obs/minute; 1440 obs/day
    # we return the csv row where our input date occurs
    return days*1440


#initially, just get day_periods
# num = number of reference windows to learn from
# date = date of test window
# wintype = 7, get same day in previous num weeks
# windtype = 1, get previous num days
def getRefWindow(num, wintype, date):
    idx = findDateIndex(date)

    #create empty data frames
    rf = pd.DataFrame([])
    tf = pd.DataFrame([])

    #now jump back (wintype = 7 for day_period, day, or week), and copy slices into our new DataFrame
    idx = idx - (num*1440*wintype)

    # add reference windows to dataframe
    for i in range(0,num):
      # I think the 1:2 is the global active power column
      rf = rf.append(data.iloc[idx+day_start:idx+day_end, 1:2])

      #output to csv for testing.
      temp = data.iloc[idx+day_start:idx+day_end, 1:2]
      temp.to_csv('ref' + str(i) + '.csv', header=False, index=False)

      # advance through the days and append
      idx = idx + (1440*wintype)

    # get test window
    tf = tf.append(data.iloc[idx+day_start:idx+day_end, 1:2])
    # output to csv
    tf.to_csv('testwin.csv', header=False, index=False)

    return rf.as_matrix(), tf

def getChunk(start_date, len_days, csv_name):

    idx = findDateIndex(date)
    chunk = data.iloc[idx:idx+(1440*len_days), 1:2]

    chunk.to_csv(csv_name, header=False,index=False)

    return


#########################
# Compare LL of different day periods
#########################


# get reference window data for training
print("\nGetting reference windows...\n")

#
# parameters
#

test_date = dt.date(2007, 5, 20)
#0700
day_start = 420
#1900
day_end = 1140

# number of reference windows
num_ref = 3
# intervals -- 7 is same day previous week, 1 is previous day
win_type = 7

#
# End parameters
#

rw,tw = getRefWindow(num_ref, win_type, test_date)

# move the dataframes over to R

#rw = rw.reshape((rw.shape[0],))
#r_rw = ro.numpy2ri.py2ri(rw)
# r_tw = pandas2ri.py2ri(tw)

#note: need to swap order of these later!
#also: need to set N to proper length for each rw!!

#r_rwlist = r.list(N=780, x=r_rw)

#def testLL():

# send this to R
rstring="""
    function(){

        library("mhsmm")

        # grab the testing window data -- this acts as our baseline
        dataT = as.matrix(read.csv("/Users/JRod/Desktop/Summer 2017/318D2/project/testwin.csv"))
        dataT = as.numeric(dataT)
        baseline = list(x=dataT, N=length(dataT))
        #train_t <- rw_list[c("x","N")]
        class(baseline) <- "hsmm.data"

        # initialize values for learning the HSMM

        J <- 4
        M = 150

        d <- cbind(dunif(1:M,0,150),
                   dunif(1:M,0,150),
                   dunif(1:M,0,150),
                   dunif(1:M,0,150))

        start.np <- hsmmspec(init=rep(1/J,J),
                             transition=matrix(c(.00,.5,.5,.5,
                                                 .5,.00,.5,.5,
                                                 .5,.50,.00,.50,
                                                 .5,.50,.50,.00),nrow=J),
                             parms.emission=list(mu=c(0.5, 1.5, 2.5, 3.5),
                                                 sigma=c(0.75, 0.5, 0.5, 0.5)),
                             sojourn=list(d=d,type='nonparametric'),
                             dens.emission=dnorm.hsmm)

        #fit the model and predict
        h.act <- hsmmfit(baseline,start.np,mstep=mstep.norm,M=M,graphical=FALSE)
        predicted <- predict(h.act,baseline)


        ll <- predicted$loglik

        for (i in 0:""" + str(num_ref-1) + """) {

          # grab the test data and compare to baseline
          data1 = as.matrix(read.csv(paste("/Users/JRod/Desktop/Summer 2017/318D2/project/ref", i, ".csv", sep="")))
          data1 = as.numeric(data1)
          train = list(x=data1, N=length(data1))
          class(train) <- "hsmm.data"

          predicted <- predict(h.act,train)

          ll <- c(ll,predicted$loglik)
        }

        ll
    }
"""


# put the string into a function
rfunc=ro.r(rstring)
# call the function in R and return the log likelyhood
loglik=rfunc()

# calculate some descriptive info from our data


loglik = np.asarray(loglik)
baseline = loglik[0]

loglik = loglik[1:]

dist = abs(loglik - baseline)
avg = np.mean(dist)
mx = dist[np.argmax(dist)]
mn = dist[np.argmin(dist)]
std = np.std(dist)

output = pd.DataFrame({'date': [test_date],'avg':[avg], 'std':[std], 'max':[mx], 'min':[mn], 'baseline':[baseline], 'win_type' : [win_type], 'num_ref' : [num_ref]})
# resort headers
output = output[['date','num_ref', 'win_type', 'baseline', 'avg', 'std', 'max', 'min']]

# changes the order for some reason to avg, max, min, std
output.to_csv('results.csv', header=False, index=False, mode='a')


print("baseline date: ", test_date, "rw type: ", win_type)
print("baseline: ", baseline)
print("output: ", loglik)
print("avg dist: ", avg)
print("std dev: ", std)
print("max dist: ", mx)
print("min dist: ", mn)
