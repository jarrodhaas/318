import gnureadline
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt


from rpy2.robjects import r, pandas2ri
import rpy2.robjects as ro
from rpy2.robjects.packages import importr


ro.numpy2ri.activate()
pandas2ri.activate()


day_start = 420
day_end = 1200

# read data
print("\nReading data...\n")
parser = lambda date: pd.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
data = pd.read_csv("sorted.csv", nrows=88827, parse_dates=[1], date_parser=parser, index_col=0)


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

test_date = dt.date(2007, 2, 15)


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

    return rf.as_matrix(), tf

# get reference window data for training
print("\nGetting reference windows...\n")
rw,tw = getRefWindow(3, 1, test_date)

# move the dataframes over to R

# rw = rw.reshape((rw.shape[0],))
#
# r_rw = ro.numpy2ri.py2ri(rw)
# r_tw = pandas2ri.py2ri(tw)

#note: need to swap order of these later!
#also: need to set N to proper length for each rw!!

# r_rwlist = r.list(N=780, x=r_rw)



# convert R code into python...

# train <- simulate(model, c(100,200), seed=1234, rand.emis=rnorm.hsmm)
#
# plot(train,xlim=c(0,100))
# init0 <- rep(1/J,J)
# P0 <- matrix(1/J,nrow=J,ncol=J)
# b0 <- list(mu=c(-3,1,3),sigma=c(1,1,1))
# startval <- hmmspec(init=init0, trans=P0,parms.emission=b0,dens.emission=dnorm.hsmm)
#
# h1 = hmmfit(train,startval,mstep=mstep.norm)


# rstring="""
#     function(rw_list){
#
#         library("mhsmm")
#
#         # initialize values for learning the HSMM
#         J <- 5
#         init <- c(1, 0, 0, 0, 0)
#         P <- matrix(c(0,0,0,0,1, 0,0,0,1,0, 0,0,0,0,1, 0,1,0,0,0, 1,0,0,0,0), nrow = J)
#
#         mu <- list(c(2,3,4,5,6), c(2,3,4,5,6 ), c(2,3,4,5,6), c(3,4,5,6,7), c(3,4,5,6,7))
#         sigma <- list(matrix(c(4,2,2,3,5,4,3,4,5,4,3,2,2,3,4,4,3,2,3,4,4,3,2,3,4), ncol = 5))
#
#         B <- list(mu = mu, sigma = sigma, diag(5))
#
#         d <- list(shape = c(10,25,1,10,5), scale = c(2,2,2,2,2), type = "gamma")
#         startval <- hsmmspec(init, P, parms.emis = B, sojourn = d, dens.emis = dmvnorm.hsmm)
#
#
#         # prep rw training data
#         train <- rw_list
#         class(train) <- "hsmm.data"
#
#         # fit model
#         h.model <- hsmmfit(train, startval, mstep = mstep.norm, maxit = 10, M = 1000, lock.transition = TRUE)
#         h.model
#
#     }
# """

rstring="""
    function(rw_list){

        library("mhsmm")

        J <- 3

        init <- c(0,0,1)
        P <- matrix(c(0,.1,.4, .5,0,.6, .5,.9,0),nrow=J)
        B <- list(mu=c(10,15,20),sigma=c(2,1,1.5))
        d <- list(lambda=c(10,30,60),shift=c(1,1,1),type='poisson')
        model <- hsmmspec(init,P,parms.emission=B,sojourn=d,dens.emission=dnorm.hsmm)
        train <- simulate(model,r=rnorm.hsmm,nsim=11,seed=123456)


        M = 500

        # initialize values for learning the HSMM

        d <- cbind(dunif(1:M,0,50),dunif(1:M,100,175),dunif(1:M,50,130))

        start.np <- hsmmspec(init=rep(1/J,J),
        transition=matrix(c(0,.5,.5, .5,0,.5, .5,.5,0),nrow=J),
        parms.emission=list(mu=c(4,12,23), sigma=c(1,1,1)),
        sojourn=list(d=d,type='nonparametric'),
        dens.emission=dnorm.hsmm)

        # prep rw training data
        train1 <- rw_list[c("x","N")]
        class(train1) <- "hsmm.data"

        train[1] <- NULL

        h.act <- hsmmfit(train,start.np,mstep=mstep.norm,M=M,graphical=FALSE)
        #predicted <- predict(h.act,train)
        #mean(predicted$s!=train$s)
        train

    }
"""


# put the string into a function
# rfunc=ro.r(rstring)
# call the function in R
# r_df=rfunc(r_rwlist)





# rw = getRefWindow(number, type, twdate)
# tw = getTestWindow(type, twdate)
#
# train (rw)
# test(tw)
# evaluate()
