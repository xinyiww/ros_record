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
from bag2csv_local import *

def run_ADE_eval_all(folder_path, gt_file, RUN_CALCULATION =  True): 
    GT = []
    ades = {}
    gt_fp = os.path.join(folder_path, gt_file)
    GT = getGTData(gt_fp)
    veh_ids = np.sort(np.unique(GT[:,1])).astype(int)
            
    # print(veh_ids)
    
    if GT == []:
        print("No GT data found. End eval.")

    for i, filename in enumerate(os.listdir(folder_path)):
        
    # file_path = os.path.join(folder_path, filename)
        # for filename in file_path:
        if filename[:11] == 'params_pred' and filename[-4:] == '.bag':
            # print(filename[-10:-6])
            param_id = int(filename[12:-4])
            print(param_id)
            bag2csv(filename, folder_path, isGT = False)
            filename_csv = filename[:-4] + '.csv'
            file_path_csv = os.path.join(folder_path, filename_csv)
            PRED = getPredData(file_path_csv) 
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
                data_pred[:,0] -= data_pred[0,0] - txys_gt[0,0] # to roughly sychronize time --hack for now
                # print(data_pred)
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
                        # print(counts_traj, counts_all)
                if RUN_CALCULATION: 
                    # print("avg trajectory-wise ade = ", running_l2e_traj/ counts_traj)
                    running_l2e_all += running_l2e_traj
                    counts_all += counts_traj
            if RUN_CALCULATION:     
                ade = running_l2e_all/ counts_all
                print("avg ADE of "+ file_path_csv +" = ", ade)    
                ades[param_id] = str(ade)
               

    return ades

                
    
    
    
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
                    
            
        
                
            
    
 


if __name__ == '__main__':
    

    # Get command line arguments
    gt_file = sys.argv[1]

    # Print the list of arguments

    # fn = argv[1]
    # save_dir = argv[2]
    # fn = "params_random_search_pred_0"
    save_dir = "/home/xliu/Documents/ros_record/random_search"

    # 
    ades = run_ADE_eval_all( save_dir, gt_file, RUN_CALCULATION =  True) 
    
    # with open('/home/xliu/Documents/ros_record/random_search/ade.txt','w') as tfile:
	#     tfile.write('\n'.join(ades))
    print(ades)
    with open('/home/xliu/Documents/ros_record/random_search/ade_'+gt_file, 'a', newline='') as csvfile:
        ade_writer = csv.writer(csvfile, delimiter=' ') 
        for i in ades.keys():
            ade_writer.writerow([str(i), ades[i]])
    
    # run_FDE_eval(fn)
    