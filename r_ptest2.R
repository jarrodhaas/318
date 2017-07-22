remove(list=ls())
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

for (i in 0:2) {

  # grab the test data and compare to baseline
  data1 = as.matrix(read.csv(paste("/Users/JRod/Desktop/Summer 2017/318D2/project/ref", i, ".csv", sep="")))
  data1 = as.numeric(data1)
  train = list(x=data1, N=length(data1))
  class(train) <- "hsmm.data"
  
  predicted <- predict(h.act,train)
  
  ll <- c(ll,predicted$loglik)
}
  



