import sys
import os
import csv
import math
# import rosbag
import rospy
import copy
import numpy as np

from dataImport import *
import matplotlib.pyplot as plt

def run_ADE_eval(folder_path, PLOT_ERROR_DIST=True, PLOT_ONE_TRAJECTORY = True, RUN_CALCULATION =  True): 
    GT = []
    for i, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if filename[:2] == 'gt':
            GT = getGTData(file_path)
            veh_ids = np.sort(np.unique(GT[:,1])).astype(int)
    
    if GT == []:
        print("No GT data found. End eval.")
    
    if PLOT_ERROR_DIST and RUN_CALCULATION:
        fig_error= plt.figure(1)
        ax = fig_error.add_subplot(111)
        ax.set_xlabel('Sample Index (sorted by error)')
        ax.set_ylabel('Error')
        ax.set_title('Sorted prediction error distribution')
    
    if PLOT_ONE_TRAJECTORY:   
        plot_count = 0
        filename_list = ['ct_vel', 'GM', 'idm']
        fig_xy_vs_t = plt.figure()
        ax1 = fig_xy_vs_t.add_subplot(311) 
        ax2 = fig_xy_vs_t.add_subplot(312)
        ax3 = fig_xy_vs_t.add_subplot(313)
        axs = [ax1, ax2, ax3]
        ax3.set_xlabel ("t")
        
        
          
    for i, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if filename[:4] == 'pred':
            
            PRED = getPredData(file_path) 
            dt, n_pred = PRED[0,1:3]
            n_pred = int(n_pred)
            hrz = dt * n_pred
            
            # if filename == "pred_GM.csv":
            #     PRED[:,0] += dt

            running_l2e_all = 0
            counts_all = 0
            preds_pw_mean_std = [] 
            pred_all_vs_t = []
            
            preds_all = []
            
            # for i, (veh_id, veh_id) in enumerate(id_gt2pred.items()):
            for veh_id in veh_ids:
                
                running_l2e_traj = 0
                counts_traj = 0
                data_gt = GT[GT[:,1] == float(veh_id)]
                txys_gt = data_gt[:, (0,2,3)]
                data_pred = PRED[PRED[:,3] == float(veh_id)] # t_start,dt,n_pred,i | xs,ys,dxs, dys
                
                ### we might want to visualize the trajectories a bit 
                if PLOT_ONE_TRAJECTORY and (veh_id == veh_ids[2]) and filename[5:-4] in filename_list:
                    
                    axs[plot_count].set_ylim([-180,0])
                    axs[plot_count].plot(txys_gt[:,0], txys_gt[:,2], '-o',markersize=7, label = 'GT')
                    asp = np.diff(axs[0].get_xlim())[0] / np.diff(axs[0].get_ylim())[0]
                    axs[plot_count].set_aspect("auto")
                    axs[plot_count].set_title(filename[5:-4])
                    axs[plot_count].set_ylabel("longitute (m)")
                    axs[plot_count].legend()
                    for j in range(data_pred.shape[0]):
                        if j % 10 == 0:
                            t_start = data_pred[j,0]
                            ts = np.linspace(t_start, t_start + hrz, n_pred)
                            xs = data_pred[j, 4+ n_pred: 4+ n_pred * 2]
                            sigs = data_pred[j, 4+ +n_pred * 2: 4+n_pred * 3]
                            axs[plot_count].scatter(ts, xs, s = 4, marker = '*')
                            axs[plot_count].fill_between(ts, xs - sigs , xs + sigs, color='gray', alpha=0.1)
                    plot_count += 1
                
                if RUN_CALCULATION:
                    for txy_gt in txys_gt:
                        running_l2e_pt = 0
                        t_gt = txy_gt[0]
                        pred = data_pred [ data_pred[:,0] <= t_gt]
                        pred = pred [pred[:,0] >= t_gt - hrz] 
                        l2es_temp = []
                        if pred.shape[0] > 0 :
                            for pred_traj in pred:
                                t_start = pred_traj[0] 
                                xs = pred_traj[4: 4+1+n_pred]
                                ys = pred_traj[4+1+n_pred: 4+(1+n_pred)*2]
                                x_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), xs)
                                y_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), ys)
                                l2e = np.sqrt((txy_gt[1] - x_pred) **2 +  (txy_gt[2] - y_pred) **2)
                                l2es_temp.append(l2e)
                                preds_all.append(l2e)
                                running_l2e_pt += l2e
                                pred_all_vs_t.append([t_gt - pred_traj[0], l2e])
                            
                            preds_pw_mean_std.append([np.mean(np.array(l2es_temp)), np.std(np.array(l2es_temp))])
                            # print("avg point-wise ade = ", running_l2e_pt/ pred.shape[0])
                        
                        running_l2e_traj += running_l2e_pt
                        counts_traj+= pred.shape[0]
                if RUN_CALCULATION: 
                    # print("avg trajectory-wise ade = ", running_l2e_traj/ counts_traj)
                    running_l2e_all += running_l2e_traj
                    counts_all += counts_traj
            if RUN_CALCULATION:     
                print("avg ADE of "+ file_path +" = ", running_l2e_all/ counts_all)    

        
                if PLOT_ERROR_DIST:
                    preds_pw_mean_std = np.array(preds_pw_mean_std)
                    preds_pw_mean_std_sorted = preds_pw_mean_std[preds_pw_mean_std[:, 0].argsort()] 
                    # plt.errorbar(x, preds_pw_mean_std_sorted[:,0], yerr=preds_pw_mean_std_sorted[:,1], fmt='-', capsize=5, markersize=5)
                    x = np.linspace(0,1,preds_pw_mean_std_sorted.shape[0])
                    # plt.fill_between(x, preds_pw_mean_std_sorted[:,0] - preds_pw_mean_std_sorted[:,1] , preds_pw_mean_std_sorted[:,0] + preds_pw_mean_std_sorted[:,1], color='gray', alpha=0.5)
                    # ax.plot(x, preds_pw_mean_std_sorted[:,0], '-o', markersize=3,label = filename[:-4])
                    preds_all = np.array(preds_all)
                    print(preds_pw_mean_std_sorted.shape, preds_all.shape)
                    
                    preds_all_sorted = preds_all[preds_all.argsort()]
                    x = np.linspace(0,1,preds_all_sorted.shape[0])
                    ax.plot(x, preds_all_sorted, '-o', markersize=3,label = filename[:-4])
                    ax.set_xlabel("sorted error index percentile")
                    ax.legend()
                
            
    plt.show()   
    
    
    # ### FDE: 

    # # - For each selected GT trajectory's end point (veh_id):

    # #     - Count how many prediction trajectories' time range covers the time stamp of this GT point 
    # #     - For each prediction trajectory:
    # #         - Calulate a linear interpolation on that GT point
    # #         - store it in order of predicted length in a list, which direct to the GT point
            
def run_FDE_eval(folder_path): 
    GT = []
    for i, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if filename[:2] == 'gt':
            GT = getGTData(file_path)
            veh_ids = np.sort(np.unique(GT[:,1])).astype(int)
    
    if GT == []:
        print("No GT data found. End eval.")
        
    for i, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
    
        if filename[:4] == 'pred':
            
            PRED = getPredData(file_path) 
            dt, n_pred = PRED[0,1:3]
            n_pred = int(n_pred)
            hrz = dt * n_pred
            
            
            ##### remove this two lines after collecting new data
            if filename == "pred_GM.csv":
                PRED[:,0] += dt
    

            running_l2e_all = 0
            counts_all = 0

            for veh_id in veh_ids:
                
                
                data_gt = GT[GT[:,1] == float(veh_id)]
                txys_gt = data_gt[:, (0,2,3)]
                data_pred = PRED[PRED[:,3] == float(veh_id)] # t_start,dt,n_pred,i | xs,ys,dxs, dys
                
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
                        
                # print("avg ade for one final point = ", running_l2e_pt/ pred.shape[0])
                
                running_l2e_all += running_l2e_pt
                counts_all += pred.shape[0]
                
            print("avg ADE for all final points of " + file_path +" =  ",running_l2e_all/ counts_all)
                    
            
        
                
            
    
    # if PLOT_ERROR_VS_TIME_ELLAPSED:
    #     fig = plt.figure()
    #     pred_all_vs_t = np.array(pred_all_vs_t)
    #     pred_all_vs_t_sorted = pred_all_vs_t[pred_all_vs_t[:,0].argsort()]
    #     print(pred_all_vs_t_sorted.shape)
    #     # plt.errorbar(x, preds_pw_mean_std_sorted[:,0], yerr=preds_pw_mean_std_sorted[:,1], fmt='-', capsize=5, markersize=5)
    #     plt.bar(pred_all_vs_t_sorted[:,0], pred_all_vs_t_sorted[:,1])
        
        
            
    #     plt.xlabel('Prediction Time elapse')
    #     plt.ylabel('Prediction Error')
    #     plt.title('Error vs. Time Ellapsed')
    #     # plt.legend()
    #     plt.show()   



if __name__ == '__main__':
    result_folder = "lane_change_pred_1_filtered_results/"

    run_ADE_eval(result_folder, RUN_CALCULATION =  True, PLOT_ONE_TRAJECTORY=True, PLOT_ERROR_DIST=True) 
    run_FDE_eval(result_folder)
    