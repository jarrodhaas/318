library("mhsmm")



# grab the training window data
data = as.matrix(read.csv("/Users/JRod/Desktop/Summer 2017/318D2/project/tw1.csv"))
data = as.numeric(data)
train = list(x=data, N=779)
#train_t <- rw_list[c("x","N")]
class(train) <- "hsmm.data"

# grab the testing window data
data = as.matrix(read.csv("/Users/JRod/Desktop/Summer 2017/318D2/project/tw1.csv"))
data = as.numeric(data)
test = list(x=data, N=780)
#train_t <- rw_list[c("x","N")]
class(test) <- "hsmm.data"



# initialize values for learning the HSMM

J <- 3
M = 500

d <- cbind(dunif(1:M,0,150),dunif(1:M,0,150),dunif(1:M,0,150))

start.np <- hsmmspec(init=rep(1/J,J),
                     transition=matrix(c(0,.5,.5, .5,0,.5, .5,.5,0),nrow=J),
                     parms.emission=list(mu=c(1,2,3), sigma=c(0.5,1,1)),
                     sojourn=list(d=d,type='nonparametric'),
                     dens.emission=dnorm.hsmm)


#fit the model and predict
h.act <- hsmmfit(train,start.np,mstep=mstep.norm,M=M,graphical=FALSE)
predicted <- predict(h.act,test)
#mean(predicted$s!=train$s)

#plot prediction and provide summary
p <- predicted[[c("x")]]
p["s"] <- predicted["s"]
plot(p,xlim=c(0,780))
summary(h.act)

plot(train_t,xlim=c(0,780))
