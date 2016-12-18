#!/usr/bin/python
#
# Mountain ridge finder

# Your names and user ids:
#   Sarvothaman Madhavan    -   madhavas
#   Raghavendra Nataraj     -   natarajr
#   Prateek Srivastava      -   pratsriv

# Based on skeleton code by D. Crandall, Oct 2016
#
'''
Read Me
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
'''
from PIL import Image
from numpy import *
from scipy.ndimage import filters
from scipy.misc import imsave
import sys
import random
from collections import Counter

global col_len, row_len
helper_list = {}


# calculate "Edge strength map" of an image
#
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale, 0, filtered_y)
    return filtered_y ** 2


# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#
def draw_edge(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range(max(y - thickness / 2, 0), min(y + thickness / 2, image.size[1] - 1)):
            image.putpixel((x, t), color)
    return image

def draw_edge1(image,x, y, color, thickness):
    for t in range(max(y - thickness / 2, 0), min(y + thickness / 2, image.size[1] - 1)):
        image.putpixel((x, t), color)
    return image

# main program
#
(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]

input_filename = sys.argv[1]

# load in image 
input_image = Image.open(input_filename)

# compute edge strength mask
edge_strength = edge_strength(input_image)
imsave('edges.jpg', edge_strength)

# You'll need to add code here to figure out the results! For now,
col_len = 0
row_len = len(edge_strength)
for row in edge_strength:
    col_len = len(row)
    break

# print col_len, row_len
############################################
# Question 1 of the code
def simple():
    edge_list = []
    for col in range(0, col_len):
        col_list = [edge_strength[row][col] for row in range(0, row_len)]
        for state_index, intensity in enumerate(col_list):
            if intensity == max(col_list):
                edge_list.append(state_index)
                break
    return edge_list


# print col_len
ridge = [0] * col_len
# print ridge

# print max(ridge),len(ridge)

# Question 1 ends here and ridge is the answer
##############################################

# Calculate P(S_i|S_i-1) or P(S_i|S_i+1)
def trans_prob(curr, n_curr, length):
    weight = 2
    return (length - abs(curr - n_curr))**weight


# Calculate P(W|S_i)
def emis_prob(index, col):
    return (col[index]**(0.90))#* ((len(col)-index))


def random_roll(col):
    global helper_list
    dist_list = helper_list[col]
    x = (random.randint(1, 100)) / 100.0
    for index in range(len(dist_list) - 1, -1, -1):
        # print x,dist_list[index], index
        if (x > dist_list[index]):
            return index
    return 0


# Calculate P(S_i|S_i+1,S_i-1,W_i)
def posterior_prob(prev, post, emis, column):
    if column == 0:
        # print "dsdsdsd", post, emis
        return (post) * (emis/2)
    elif column == col_len - 1:
        # print "aaa", prev, emis
        # print prev,emis
        return (prev) * (emis/2)
    else:
        # print "asd", prev, post, emis
        return ((prev * post)) * (emis/2)


prob_array = {}
posterior_prob_list = {}
# Gibb's sampling
for col in range(0, col_len):
    col_list = [int(edge_strength[row][col]) for row in range(0, row_len)]
    length = len(col_list)
    sum_trans_dif_post = float(0.00001)
    sum_trans_dif_prev = float(0.00001)
    sum_emis = float(0.0)
    prob_array[col] = {}
    posterior_prob_list[col] = {}
    helper_list[col] = {}
    for i, row in enumerate(col_list):
        # print i,row
        # for 1st column there is no previous state
        if col == 0:
            trans_prob_post = trans_prob(i, ridge[col + 1], length)
            sum_trans_dif_post += trans_prob_post
            emis_probs = emis_prob(i, col_list)
            sum_emis += emis_probs
            # print trans_prob_post, 1, emis_probs
            # emis_probs = 1
            prob_array[col][i] = ([1, trans_prob_post, emis_probs])
            # print prob_array[col][i]

        # for last column there is no next state
        elif col == col_len - 1:
            trans_prob_prev = trans_prob(i, ridge[col - 1], length)
            sum_trans_dif_prev += trans_prob_prev
            emis_probs = emis_prob(i, col_list)
            sum_emis += emis_probs
            prob_array[col][i] = ([trans_prob_prev, 1, emis_probs])
            # print prob_array[col][i]

        else:
            trans_prob_prev = trans_prob(i, ridge[col - 1], length)
            sum_trans_dif_prev += trans_prob_prev
            trans_prob_post = trans_prob(i, ridge[col + 1], length)
            sum_trans_dif_post += trans_prob_post
            emis_probs = emis_prob(i, col_list)
            sum_emis += emis_probs
            # emis_probs = 1
            prob_array[col][i] = ([trans_prob_prev, trans_prob_post, emis_probs])
            # print prob_array[col][i]
    sum_of_col = 0
    for index, row in enumerate(prob_array[col]):
        probs = prob_array[col][index]
        posterior_prob_list[col][index] = posterior_prob(probs[0] / sum_trans_dif_prev, probs[1] / sum_trans_dif_post,
                                                         probs[2] / sum_emis, col)
        sum_of_col += posterior_prob_list[col][index]
    # print posterior_prob_list[0]

    for index, prob in enumerate(posterior_prob_list[col]):
        if index == 0:
            helper_list[col][index] = (posterior_prob_list[col][index] / sum_of_col)
        else:
            helper_list[col][index] = (posterior_prob_list[col][index] / sum_of_col + helper_list[col][index - 1])
            # print helper_list[col]
            #
            # x = random.randint(0,1)
            # # print x

# ridge = [edge_strength.shape[0] / 2] * edge_strength.shape[1]
def mcmc(ridges):
    #ridges = [0] * col_len
    for x in range(0, 1000):
        col = (random.randint(1, col_len-1))
        for i in range(col, -1,-1):
            ridges[i] = random_roll(i)
        for i in range(col+1, col_len):
            ridges[i] = random_roll(i)
            
    final_ridge=[]
    for x in range(0, 2000):
        col = (random.randint(1, col_len-1))
        for i in range(col-1, -1,-1):
            ridges[i] = random_roll(i)
        for i in range(col+1, col_len):
            ridges[i] = random_roll(i)
            tmp_ridge = ridges[:]
        final_ridge.append(tmp_ridge)

    rid = array(final_ridge)
    ret_ridge = []
    for col in range(0, col_len):
        ret_ridge.append(Counter(rid[:,col]).most_common()[0][0])
    # print Counter(col_list).items()
    # print col_list
    return ret_ridge

def usr_mcmc(ridges,col,row):
    #ridges = [0] * col_len
    ridges = [row]*col_len
    for x in range(0, 1000):
        #print x
        for i in range(col-1, -1,-1):
            ridges[i] = random_roll(i)
        for i in range(col+1, col_len):
            ridges[i] = random_roll(i)
            
    final_ridge=[]
    for x in range(0, 2000):
    # print x
        for i in range(col-1, -1,-1):
            ridges[i] = random_roll(i)
        for i in range(col+1, col_len):
            ridges[i] = random_roll(i)
            tmp_ridge = ridges[:]
        final_ridge.append(tmp_ridge)

    rid = array(final_ridge)
    ret_ridge = []
    for col in range(0, col_len):
        ret_ridge.append(Counter(rid[:,col]).most_common()[0][0])
    # print Counter(col_list).items()
    # print col_list
    return ret_ridge


x_axis = int(sys.argv[4])
y_axis = int(sys.argv[3])
#imsave(output_filename, draw_edge(input_image, ridge, (i % 255, x % 255, (i + x) % 255), 5))

sim_ridge = simple()
imsave(output_filename, draw_edge(input_image, sim_ridge, (255, 0,0), 5))
mcmc_ridge = mcmc(sim_ridge)
# output answer
imsave(output_filename, draw_edge(input_image, mcmc_ridge, (0, 0,255), 5))

mcmc_usr_ridge = usr_mcmc(sim_ridge,x_axis,y_axis)
# output answer
imsave(output_filename, draw_edge(input_image, mcmc_usr_ridge, (0, 255,0), 5))
'''
# print random_roll(100),row_len
imsave(output_filename,draw_edge1(input_image,x_axis, y_axis, (0, 0,255), 5))
'''
