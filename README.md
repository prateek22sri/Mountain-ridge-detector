# Mountain ridge finder

Team Members:
+ Sarvothaman Madhavan
+ Raghavendra Nataraj
+ Prateek Srivastava

# Based on skeleton code by David Crandall, Oct 2016
#
```
Output Color :
		Simplified				-	red
		MCMC					-	blue
		MCMC with user input			-	green

Emission Probabilty : It is the edge strength normalised over the column.(Assigning higher rows with more probability is misleading, so i have used uniform prior probability)
Transision probabitlty : It is the transition between row. Equal rows get higher probability and rows far away get less probability. I have normalised over all values of column. 

In simplified we have taken only the max of the edge strength, because P(S) is constant. (i.e Apriori, each row is 
equally likely to contain the mountain ridge)
In MCMC we define the probability based on edge strength and the transition from next column and previous column. 

If more importance(Weight) is given to edge strength, then images  in which the moutains are clear get good results but images in which mountains are a little out of scope(farther or a little faded i.e. having less intensity), get bad results. 
If more importance(Weight) is given to transistion probability then a single pixel's wrong calculation propogates over to the next points. So the results goes bad for clear mountains. 

The user input does not help to a great extent in finding the ridges. It helps in finding a few points but it normalizes as we progress thereby giving results very similar to MCMC. 

Note : Time for each image takes around 45 seconds to complete all three methodologies.
```
