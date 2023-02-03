#!/usr/bin/env python
import sys
import os
import csv
import math
import rosbag
import rospy
import copy

import numpy as np

# filename = sys.argv[2]
# directory = sys.argv[1]

def assign_id(x,y, t, pre_pos_dict, max_dx, max_dy, max_dt):
  n_in_scope = 0
  best_id = None
  min_dist = math.inf
  for i, (veh_id, pre_pos) in enumerate(pre_pos_dict.items()):
    x_dist = abs(pre_pos[0] -  x)
    y_dist = abs(pre_pos[1] - y)
    t_dist = abs(pre_pos[2] - t)
    if (x_dist <= max_dx) and (y_dist <= max_dy) and (t_dist <= max_dt): 
      n_in_scope += 1
      dist = math.sqrt(x_dist**2 + y_dist**2)
      min_dist = np.min([dist, min_dist])
      ids = [veh_id, best_id]
      best_id = ids[np.argmin([dist, min_dist])]
  
  if n_in_scope >= 1:     
    print("[Log] For this vehicle, there are "+ str(n_in_scope) 
        +" candidates, cand with min euler distance id = "+ str(best_id)
        + ". Dist = " + str(min_dist) )
    return best_id
  else:
    new_id = max(pre_pos_dict.keys()) + 1
    print("[Log] For this vehicle, there are  no candidate in scope, so we assign it with new id = "+str(new_id))
    return new_id


filename = "t_jun_pred_3"
directory = "/home/xliu/Documents/ros_record/"

# Read the rosbag file
print("Reading the rosbag file")
if not directory.endswith("/"):
  directory += "/"
extension = ""
if not filename.endswith(".bag"):
  extension = ".bag"
bag = rosbag.Bag(directory + filename + extension)

# Create directory with name filename (without extension)
results_dir = directory + filename[:] + "_results"
if not os.path.exists(results_dir):
  os.makedirs(results_dir)

print("Writing prediction data")
with open(results_dir +"/"+filename+'_pred.csv', 'a', newline='') as pred_csv:
  log_writer = csv.writer(pred_csv, delimiter=' ')                         
  
  pre_pos = {} 
  for topic, msg, t in bag.read_messages(topics=['/region/all_cars_predictions']):
    veh_id = 0
    if msg.predictions != []:
      
      if pre_pos == {}: # first round, build the first veh_id dic
        for i, veh in enumerate(msg.predictions):
        
          xs = []
          ys = []
          dxs = []
          dys = []

          t_start = msg.header.stamp.to_sec()
          print(t_start)
          n_pred = len(veh.trajectories[0].trajectory_uncertainty.waypoints) # assume we only have one discrete possibility
          dt = veh.dt      
                              
          for j, wps in enumerate(veh.trajectories[0].trajectory_estimated.waypoints):
            x = wps.pose.pose.position.x
            y = wps.pose.pose.position.y
            
            xs.append(x)
            ys.append(y)
        
          
              
          for j, wps in enumerate(veh.trajectories[0].trajectory_uncertainty.waypoints):
            dx = wps.pose.pose.position.x
            dy = wps.pose.pose.position.y
            
            dxs.append(dx)
            dys.append(dy)  
            
          if [xs[0], ys[0], t_start] not in pre_pos.values():
            pre_pos[veh_id] = [xs[0], ys[0], t_start]
            veh_id += 1
            log_writer.writerow([t_start,dt,n_pred,veh_id] + xs + ys + dxs + dys )
      
      else:
        for i, veh in enumerate(msg.predictions):
          
          pre_pos_old = pre_pos.copy()
          xs = []
          ys = []
          dxs = []
          dys = []
          
          
          t_start = msg.header.stamp.to_sec()
          # print(t_start)
          n_pred = len(veh.trajectories[0].trajectory_uncertainty.waypoints) # assume we only have one discrete possibility
          dt = veh.dt      
                              
          for j, wps in enumerate(veh.trajectories[0].trajectory_estimated.waypoints):
            x = wps.pose.pose.position.x
            y = wps.pose.pose.position.y
            
            xs.append(x)
            ys.append(y)
        
          
              
          for j, wps in enumerate(veh.trajectories[0].trajectory_uncertainty.waypoints):
            dx = wps.pose.pose.position.x
            dy = wps.pose.pose.position.y
            
            dxs.append(dx)
            dys.append(dy)  
          
              
          veh_id = assign_id(xs[0],ys[0], t_start, pre_pos_old, 1e-3, 1, 0.3) # (1e-3, -0.4693756103515625)
          print(veh_id)     
          
          if [xs[0], ys[0], t_start] not in pre_pos.values():
            pre_pos[veh_id] = [xs[0], ys[0], t_start]
            log_writer.writerow([t_start,dt,n_pred,veh_id] + xs + ys + dxs + dys )
      
        
                    
                
    # pred_csv.close()

 id_gt2pred = {}               
 id_gt2pred[6] = 2
 id_gt2pred[7] = 3
 id_gt2pred[4] = 6
 id_gt2pred[5] = 7
 id_gt2pred[8] = 8
 id_gt2pred[10] = 25
 id_gt2pred[11] = 38     