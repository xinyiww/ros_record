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

RUN_ADE_EVAL = True
RUN_FDE_EVAL = False
PLOT_ERROR_DIST = False
PLOT_ERROR_VS_TIME_ELLAPSED = True
dt = 0.1
n_pred = 100
hrz = 10

# at freq ~ 20 hz
fn_GT = "t_jun_pred_3_results/t_jun_pred_3_gt.csv"
GT = getGTData(fn_GT)

# at freq ~ 10 hz
fn_pred = "t_jun_pred_3_results/t_jun_pred_3_pred.csv"
PRED = getPredData(fn_pred)


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



if RUN_ADE_EVAL: 
    running_l2e_all = 0
    counts_all = 0
    preds_pw_mean_std = [] 
    pred_all_vs_t = []
    
    for i, (gt_id, pred_id) in enumerate(id_gt2pred.items()):
        
        running_l2e_traj = 0
        counts_traj = 0
        data_gt = GT[GT[:,1] == float(gt_id)]
        txys_gt = data_gt[:, (0,2,3)]
        data_pred = PRED[PRED[:,3] == float(pred_id)] # t_start,dt,n_pred,i | xs,ys,dxs, dys
        
        for txy_gt in txys_gt:
            running_l2e_pt = 0
            t_gt = txy_gt[0]
            pred = data_pred [ data_pred[:,0] <= t_gt]
            pred = pred [pred[:,0] >= t_gt - hrz] 
            l2es_temp = []
            if pred.shape[0] > 0 :
                for pred_traj in pred:
                    # linear interp
                    # print(t_gt - pred_traj[0])
                    t_start = pred_traj[0]
                    xs = pred_traj[4: 4+1+n_pred]
                    ys = pred_traj[4+1+n_pred: 4+(1+n_pred)*2]
                    x_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), xs)
                    y_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), ys)
                    l2e = np.sqrt((txy_gt[1] - x_pred) **2 +  (txy_gt[2] - y_pred) **2)
                    l2es_temp.append(l2e)
                    running_l2e_pt += l2e
                    pred_all_vs_t.append([t_gt - pred_traj[0], l2e])
                
                preds_pw_mean_std.append([np.mean(np.array(l2es_temp)), np.std(np.array(l2es_temp))])
                # print("avg point-wise ade = ", running_l2e_pt/ pred.shape[0])
            
            running_l2e_traj += running_l2e_pt
            counts_traj+= pred.shape[0]
        # print("avg trajectory-wise ade = ", running_l2e_traj/ counts_traj)
        running_l2e_all += running_l2e_traj
        counts_all += counts_traj
        
    print("avg all ade = ", running_l2e_all/ counts_all)    
    
    if PLOT_ERROR_VS_TIME_ELLAPSED:
        fig = plt.figure()
        pred_all_vs_t = np.array(pred_all_vs_t)
        pred_all_vs_t_sorted = pred_all_vs_t[pred_all_vs_t[:,0].argsort()]
        print(pred_all_vs_t_sorted.shape)
        # plt.errorbar(x, preds_pw_mean_std_sorted[:,0], yerr=preds_pw_mean_std_sorted[:,1], fmt='-', capsize=5, markersize=5)
        plt.bar(pred_all_vs_t_sorted[:,0], pred_all_vs_t_sorted[:,1])

        # plt.xlabel('Prediction Time elapse')
        # plt.ylabel('Prediction Error')
        # plt.title('Error vs. Time Ellapsed')
        # plt.legend()
        plt.show()   
        
        
    if PLOT_ERROR_DIST:
        fig = plt.figure()
        preds_pw_mean_std = np.array(preds_pw_mean_std)
        preds_pw_mean_std_sorted = preds_pw_mean_std[preds_pw_mean_std[:, 0].argsort()] 
        # plt.errorbar(x, preds_pw_mean_std_sorted[:,0], yerr=preds_pw_mean_std_sorted[:,1], fmt='-', capsize=5, markersize=5)
        x = np.arange(preds_pw_mean_std_sorted.shape[0])
        plt.fill_between(x, preds_pw_mean_std_sorted[:,0] - preds_pw_mean_std_sorted[:,1] , preds_pw_mean_std_sorted[:,0] + preds_pw_mean_std_sorted[:,1], color='gray', alpha=0.5)
        plt.plot(x, preds_pw_mean_std_sorted[:,0], '-o', color='red', markersize=3,label = "Constant Velocity")
        
        
        plt.xlabel('Sample Index (sorted by error)')
        plt.ylabel('Error')
        plt.title('Sorted prediction error distribution')
        plt.legend()
        plt.show()   
        
        
        

### FDE: 

# - For each selected GT trajectory's end point (gt_id):

#     - Count how many prediction trajectories' time range covers the time stamp of this GT point 
#     - For each prediction trajectory:
#         - Calulate a linear interpolation on that GT point
#         - store it in order of predicted length in a list, which direct to the GT point
        

if RUN_FDE_EVAL: 
    running_l2e_all = 0
    counts_all = 0

    for i, (gt_id, pred_id) in enumerate(id_gt2pred.items()):
        
        running_l2e_traj = 0
        counts_traj = 0
        
        data_gt = GT[GT[:,1] == float(gt_id)]
        txys_gt = data_gt[:, (0,2,3)]
        data_pred = PRED[PRED[:,3] == float(pred_id)] # t_start,dt,n_pred,i | xs,ys,dxs, dys
        
        txy_pt = txys_gt[txys_gt.shape[0]-1]
        running_l2e_pt = 0
        t_gt = txy_pt[0]
        pred = data_pred [ data_pred[:,0] <= t_gt]
        pred = pred [pred[:,0] >= t_gt - hrz]
        
        if pred.shape[0] > 0 :
            for pred_traj in pred:
                # linear interp
                t_start = pred_traj[0]
                xs = pred_traj[4: 4+1+n_pred]
                ys = pred_traj[4+1+n_pred: 4+(1+n_pred)*2]
                x_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), xs)
                y_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), ys)
                running_l2e_pt += np.sqrt((txy_pt[1] - x_pred) **2 +  (txy_pt[2] - y_pred) **2)
                
        print("avg ade for one final point = ", running_l2e_pt/ pred.shape[0])
        
        running_l2e_all += running_l2e_pt
        counts_all = pred.shape[0]
        
    print("avg ade for all final points = ", running_l2e_all/ counts_all)
            
        
    
    
    
        
    

        
        
        
        
        
    
    
    