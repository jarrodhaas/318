remove(list=ls())
library("mhsmm")

# grab the training window data
data1 = as.matrix(read.csv("D:/Users/Alex/318/tw1.csv"))
data1 = as.numeric(data1)
data1List = list(x=data1, N=length(data1))

data2 = as.matrix(read.csv("D:/Users/Alex/318/tw2.csv"))
data2 = as.numeric(data2)
data2List = list(x=data2, N=length(data2))
class(data2List) <- "hsmm.data"

train = list(x=c(data1,data2), N=c(length(data1),length(data2)))
class(train) <- "hsmm.data"

# grab the testing window data
dataT = as.matrix(read.csv("D:/Users/Alex/318/test1.csv"))
dataT = as.numeric(dataT)
test = list(x=dataT, N=length(dataT))
#train_t <- rw_list[c("x","N")]
class(test) <- "hsmm.data"



# initialize values for learning the HSMM

J <- 4
M = 500

d <- cbind(dunif(1:M,0,150),
           dunif(1:M,0,150),
           dunif(1:M,0,150),
           dunif(1:M,0,150))

start.np <- hsmmspec(init=rep(1/J,J),
                     transition=matrix(c(.00,.10,.90,.00,
                                         .33,.00,.60,.07,
                                         .00,.90,.00,.10,
                                         .00,.90,.10,.00),nrow=J),
                     parms.emission=list(mu=c(1,1), sigma=c(0,7)),
                     sojourn=list(d=d,type='nonparametric'),
                     dens.emission=dnorm.hsmm)


#fit the model and predict
h.act <- hsmmfit(train,start.np,mstep=mstep.norm,M=M,graphical=FALSE)
test_predicted <- predict(h.act,test)
train_predicted <- predict(h.act,data1List)
#mean(predicted$s!=train$s)

#plot prediction and provide summary
test_p <- test_predicted[[c("x")]]
test_p["s"] <- test_predicted["s"]
# plot(test_p,xlim=c(0,779))

train_p <- train_predicted[[c("x")]]
train_p["s"] <- train_predicted["s"]

plot(x=c(1:test_p[["N"]]),y=test_p[["s"]]
     
     
     
     
     )
plot(x=c(1:train_p[["N"]]),y=train_p[["s"]])
# summary(h.act)

# plot(train_t,xlim=c(0,780))
