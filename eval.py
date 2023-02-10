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

def run_ADE_eval(folder_path, PLOT_ERROR_DIST=False, PLOT_ONE_TRAJECTORY = True): 
    GT = []
    for i, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if filename[:2] == 'gt':
            GT = getGTData(file_path)
            veh_ids = np.sort(np.unique(GT[:,1])).astype(int)
    
    if GT == []:
        print("No GT data found. End eval.")
    
    if PLOT_ERROR_DIST:
        fig_error= plt.figure(1)
        ax = fig_error.add_subplot(111)
        ax.set_xlabel('Sample Index (sorted by error)')
        ax.set_ylabel('Error')
        ax.set_title('Sorted prediction error distribution')
    
    if PLOT_ONE_TRAJECTORY:        
        fig_xy_vs_t = plt.figure()
        ax1 = fig_xy_vs_t.add_subplot(211, aspect='equal') 
        ax2 = fig_xy_vs_t.add_subplot(212, aspect='equal')
        axs = [ax1, ax2]
        ax2.set_xlabel('t')
        ax1.set_ylabel('x')
        ax2.set_ylabel('y')
        ax1.set_title('Plot of x, y vs t of one trajectory compared to the predictions')
          
    for i, filename in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if filename[:4] == 'pred':
            PRED = getPredData(file_path) 
            dt, n_pred = PRED[0,1:3]
            n_pred = int(n_pred)
            hrz = dt * n_pred
            


            running_l2e_all = 0
            counts_all = 0
            preds_pw_mean_std = [] 
            pred_all_vs_t = []
            
            # for i, (veh_id, veh_id) in enumerate(id_gt2pred.items()):
            for veh_id in veh_ids:
                
                running_l2e_traj = 0
                counts_traj = 0
                data_gt = GT[GT[:,1] == float(veh_id)]
                txys_gt = data_gt[:, (0,2,3)]
                data_pred = PRED[PRED[:,3] == float(veh_id)] # t_start,dt,n_pred,i | xs,ys,dxs, dys
                
                ### we might want to visualize the trajectories a bit 
                if (veh_id == veh_ids[5]) and (filename == 'pred_ct_vel.csv'):
                   axs[0].set_ylim(91.25, 93.50)
                   for k in range(2):
                        axs[k].plot(txys_gt[:,0], txys_gt[:,k+1], '-o',markersize=3, label = 'GT')
                        asp = np.diff(axs[0].get_xlim())[0] / np.diff(axs[0].get_ylim())[0]
                        axs[k].set_aspect("auto")
                        
                        for j in range(data_pred.shape[0]):
                            if j % 10 == 0:
                                t_start = data_pred[j,0]
                                ts = np.linspace(t_start, t_start + hrz, n_pred)
                                xs = data_pred[j, 4+ n_pred * k: 4+ n_pred * (k+1)]
                                sigs = data_pred[j, 4+ +n_pred * 2: 4+n_pred * 3]
                                axs[k].scatter(ts, xs, s = 5, marker = '*')
                                axs[k].fill_between(ts, xs - sigs , xs + sigs, color='gray', alpha=0.1)
                    
                

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
                            running_l2e_pt += l2e
                            pred_all_vs_t.append([t_gt - pred_traj[0], l2e])
                        
                        preds_pw_mean_std.append([np.mean(np.array(l2es_temp)), np.std(np.array(l2es_temp))])
                        # print("avg point-wise ade = ", running_l2e_pt/ pred.shape[0])
                    
                    running_l2e_traj += running_l2e_pt
                    counts_traj+= pred.shape[0]
                # print("avg trajectory-wise ade = ", running_l2e_traj/ counts_traj)
                running_l2e_all += running_l2e_traj
                counts_all += counts_traj
                
            print("avg ADE of "+ file_path +" = ", running_l2e_all/ counts_all)    

        
            if PLOT_ERROR_DIST:
                preds_pw_mean_std = np.array(preds_pw_mean_std)
                preds_pw_mean_std_sorted = preds_pw_mean_std[preds_pw_mean_std[:, 0].argsort()] 
                # plt.errorbar(x, preds_pw_mean_std_sorted[:,0], yerr=preds_pw_mean_std_sorted[:,1], fmt='-', capsize=5, markersize=5)
                x = np.arange(preds_pw_mean_std_sorted.shape[0])
                # plt.fill_between(x, preds_pw_mean_std_sorted[:,0] - preds_pw_mean_std_sorted[:,1] , preds_pw_mean_std_sorted[:,0] + preds_pw_mean_std_sorted[:,1], color='gray', alpha=0.5)
                ax.plot(x, preds_pw_mean_std_sorted[:,0], '-o', markersize=3,label = filename[:-4])
                ax.legend()
                
            
    plt.show()   
                
            
    
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
    result_folder = "t_jun_pred_gm_results/"

    run_ADE_eval(result_folder) 
    # run_FDE_eval(fn_GT, fn_pred)
    # run_FDE_eval(fn_GT, fn_pred)     
    # RUN_ADE_EVAL = True
    # RUN_FDE_EVAL = False
    # PLOT_ERROR_DIST = True
    # PLOT_ERROR_VS_TIME_ELLAPSED = False
    
    
    
    # dt = 0.1
    # n_pred = 100
    # hrz = 10
    
    
    
    
    # # at freq ~ 20 hz
    # fn_GT = "t_jun_pred_3_results/t_jun_pred_3_gt.csv"
    # GT = getGTData(fn_GT)

    # # at freq ~ 10 hz
    # fn_pred = "t_jun_pred_3_results/t_jun_pred_3_pred.csv"
    # PRED = getPredData(fn_pred)

    # veh_ids_gt = np.sort(np.unique(GT[:,1]))
    # veh_ids_pred = np.sort(np.unique(PRED[:,1]))

    # veh_ids = veh_ids_gt

    # # ADE
    # # - For each selected GT trajectory (veh_id):

    # #     - For each pt on that GT trajectory:
        
    # #         - Count how many prediction trajectories' time range covers the time stamp of this GT point 
    # #         - For each prediction trajectory:
    # #             - Calulate a linear interpolation on that GT point
    # #             - store it in order of predicted length in a list, which direct to the GT point



    # if RUN_ADE_EVAL: 

            
            
    #     if PLOT_ERROR_DIST:
    #         fig = plt.figure()
    #         preds_pw_mean_std = np.array(preds_pw_mean_std)
    #         preds_pw_mean_std_sorted = preds_pw_mean_std[preds_pw_mean_std[:, 0].argsort()] 
    #         # plt.errorbar(x, preds_pw_mean_std_sorted[:,0], yerr=preds_pw_mean_std_sorted[:,1], fmt='-', capsize=5, markersize=5)
    #         x = np.arange(preds_pw_mean_std_sorted.shape[0])
    #         plt.fill_between(x, preds_pw_mean_std_sorted[:,0] - preds_pw_mean_std_sorted[:,1] , preds_pw_mean_std_sorted[:,0] + preds_pw_mean_std_sorted[:,1], color='gray', alpha=0.5)
    #         plt.plot(x, preds_pw_mean_std_sorted[:,0], '-o', color='red', markersize=3,label = "Constant Velocity")
            
            
    #         plt.xlabel('Sample Index (sorted by error)')
    #         plt.ylabel('Error')
    #         plt.title('Sorted prediction error distribution')
    #         plt.legend()
    #         plt.show()   
            
            
            

    # ### FDE: 

    # # - For each selected GT trajectory's end point (veh_id):

    # #     - Count how many prediction trajectories' time range covers the time stamp of this GT point 
    # #     - For each prediction trajectory:
    # #         - Calulate a linear interpolation on that GT point
    # #         - store it in order of predicted length in a list, which direct to the GT point
            

    # if RUN_FDE_EVAL: 
    #     running_l2e_all = 0
    #     counts_all = 0

    #     for veh_id in veh_ids:
            
    #         running_l2e_traj = 0
    #         counts_traj = 0
            
    #         data_gt = GT[GT[:,1] == float(veh_id)]
    #         txys_gt = data_gt[:, (0,2,3)]
    #         data_pred = PRED[PRED[:,3] == float(veh_id)] # t_start,dt,n_pred,i | xs,ys,dxs, dys
            
    #         txy_pt = txys_gt[txys_gt.shape[0]-1]
    #         running_l2e_pt = 0
    #         t_gt = txy_pt[0]
    #         pred = data_pred [ data_pred[:,0] <= t_gt]
    #         pred = pred [pred[:,0] >= t_gt - hrz]
            
    #         if pred.shape[0] > 0 :
    #             for pred_traj in pred:
    #                 # linear interp
    #                 t_start = pred_traj[0]
    #                 xs = pred_traj[4: 4+1+n_pred]
    #                 ys = pred_traj[4+1+n_pred: 4+(1+n_pred)*2]
    #                 x_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), xs)
    #                 y_pred = np.interp(t_gt, np.linspace(t_start, t_start + hrz, 1+n_pred), ys)
    #                 running_l2e_pt += np.sqrt((txy_pt[1] - x_pred) **2 +  (txy_pt[2] - y_pred) **2)
                    
    #         print("avg ade for one final point = ", running_l2e_pt/ pred.shape[0])
            
    #         running_l2e_all += running_l2e_pt
    #         counts_all = pred.shape[0]
            
    #     print("avg ade for all final points = ", running_l2e_all/ counts_all)
                
            
        
        
        
            
        

            
            
            
        
        
    
    
    