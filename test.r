library("mhsmm")

J<-3
initial <- rep(1/J,J)
P <- matrix(c(.8,.5,.1,0.05,.2,.5,.15,.3,.4),nrow=J)
b <- list(mu=c(-3,0,2),sigma=c(2,1,.5))
model <- hmmspec(init=initial, trans=P, parms.emission=b,dens.emission=dnorm.hsmm)
train <- simulate(model, nsim=300, seed=123456, rand.emis=rnorm.hsmm)


J <- 3
init <- c(0,0,1)
P <- matrix(c(0,.1,.4, .5,0,.6, .5,.9,0),nrow=J)
B <- list(mu=c(10,15,20),sigma=c(2,1,1.5))
d <- list(lambda=c(10,30,60),shift=c(1,1,1),type='poisson')
model <- hsmmspec(init,P,parms.emission=B,sojourn=d,dens.emission=dnorm.hsmm)
train <- simulate(model,nsim=11,seed=123456,rand.emis=rnorm.hsmm)


plot(train,xlim=c(0,100))
init0 <- rep(1/J,J)
P0 <- matrix(1/J,nrow=J,ncol=J)
b0 <- list(mu=c(-3,1,3),sigma=c(1,1,1))
startval <- hmmspec(init=init0, trans=P0,parms.emission=b0,dens.emission=dnorm.hsmm)
h1 = hmmfit(train,startval,mstep=mstep.norm)
plot(h1$loglik,type='b',ylab='Log-likelihood',xlab='Iteration')
summary(h1)
#proportion of incorrect states
mean(train$s!=predict(h1,train)$s)
#simulate a new test set
test <- simulate(model, nsim=c(100,200,300), seed=1234,rand.emis=rnorm.hsmm)
mean(test$s!=predict(h1,test)$s)


