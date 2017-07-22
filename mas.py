import numpy as np
import math as mt
import random as rand

#arr = np.array([2,2,2,1,1,1,2,2,2,2,2,2,0,0,2,0,1,1,1,1,0,0,2,0,0,2,0,0,0,2,2,2,2])

l = 1000
arr = np.zeros(l)
for i in range(0,l):
  arr[i] = rand.randint(0,2)

#max/min length -- these need to have (max-min) >= 2 for a single window
max_length = 20
min_length = 5

# density threshold
dt = 1.5
# initial window size
k = max_length
#max number of scores
score_max = 5
#number of window sizes
w = int(mt.floor(mt.log((max_length-min_length), 2)))
#list of scores
anom = np.zeros((w,score_max))

for i in range(0,w):

    # reset number of scores for this window size
    score_count = 0
    #slide the window over everything, take scores over the threshold
    for j in range(0,arr.shape[0] - (k-1)):

      s = float(np.sum(arr[j:j+k]))

      d = float(s / k)
      #print(arr[j:j+k], " ", d, d>dt)
      if ((d > dt) & (score_count < score_max)):
          anom[i][score_count] = d
          score_count += 1

    # cut the window size in half
    k = int(mt.floor(k / 2))
