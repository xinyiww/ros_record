import sys
import os
import csv
import math
import rosbag
import rospy
import copy
import numpy as np

from dataImport import *
import matplotlib.pyplot as plt

# at freq ~ 20 hz
fn_GT = "t_jun_pred_3_results/t_jun_pred_3_gt.csv"
GT = getGTData(fn_GT)

# at freq ~ 10 hz
fn_pred = "t_jun_pred_3_results/t_jun_pred_3_pred.csv"
PRED = getPredData(fn_pred)

dt = 0.1
n_pred = 100
hrz = 10

# we can define the id map by hands specifically for t_jun_pred_3
id_pred2gt = {}               
id_pred2gt[2] = 6
id_pred2gt[3] = 7
id_pred2gt[6] = 4
id_pred2gt[7] = 5
id_pred2gt[8] = 8
id_pred2gt[25] = 10
id_pred2gt[38] = 11   

id_gt2pred = {}               
id_gt2pred[6] = 2
id_gt2pred[7] = 3
id_gt2pred[4] = 6
id_gt2pred[5] = 7
id_gt2pred[8] = 8
id_gt2pred[10] = 25
id_gt2pred[11] = 38  

# ADE
# - For each selected GT trajectory (gt_id):

#     - For each pt on that GT trajectory:
       
#         - Count how many prediction trajectories' time range covers the time stamp of this GT point 
#         - For each prediction trajectory:
#             - Calulate a linear interpolation on that GT point
#             - store it in order of predicted length in a list, which direct to the GT point


running_sse = 0

for i, (gt_id, pred_id) in enumerate(id_gt2pred.items()):
    data_gt = GT[GT[:,1] == float(gt_id)]
    txys_gt = data_gt[:, (0,2,3)]
    data_pred = PRED[PRED[:,3] == float(pred_id)] # t_start,dt,n_pred,i | xs,ys,dxs, dys
    
    for txy_gt in txys_gt:
        t_gt = txy_gt[0]
        pred = data_pred [ data_pred[:,0] <= t_gt]
        pred = pred [pred[:,0] >= t_gt - hrz]
        plt.scatter(txy_gt[1], txy_gt[2])
        if pred.shape[0] > 0 :
            for pred_traj in pred:
                # linear interp
                t_start = pred_traj[0]
                xs = pred_traj[4: 4+1+n_pred]
                ys = pred_traj[4+1+n_pred: 4+(1+n_pred)*2]
                x_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), xs)
                y_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), ys)
                running_sse += (txy_gt[0] - x_pred) **2 +  (txy_gt[1] - y_pred) **2
                
                plt.scatter(x_pred, y_pred, marker="x")
        plt.show()
        plt.clf()
        plt.legend()
        pass
                
        
        
        
        
        
    
    
    