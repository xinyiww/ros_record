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

print("Writing gt data")

with open(results_dir +"/"+filename+'_gt.csv', 'a', newline='') as gt_csv:
    log_writer = csv.writer(gt_csv, delimiter=' ')                         
    pre_pos = {} 
    for topic, msg, t in bag.read_messages(topics=['/region/lanes_perception']):
        t = msg.header.stamp.to_sec()
        print(t)
        veh_id = 0
        
        if pre_pos == {}: # first round, build the first veh_id dic
          for i, lane in enumerate(msg.vehicles):            
              for j, veh in enumerate(lane.vehicles): # some deplicates in the first round -- delete them
                  pos = veh.pose.pose.position   
                  log_writer.writerow([t, veh_id, pos.x, pos.y] )
                  
                  if [pos.x, pos.y, t] not in pre_pos.values():
                    pre_pos[veh_id] = [pos.x, pos.y, t]
                    veh_id += 1
                  
                  
                  
        else: # else: assign veh_id based on the position correspondence
          
          for i, lane in enumerate(msg.vehicles):            
              for j, veh in enumerate(lane.vehicles):
                  pre_pos_old = pre_pos.copy()
                  pos = veh.pose.pose.position   
                  veh_id = assign_id(pos.x, pos.y,t, pre_pos_old, 1e-3, 1, 0.2) # (1e-3, -0.4693756103515625)
                  log_writer.writerow([t, veh_id, pos.x, pos.y] )
                  
                  if [pos.x, pos.y, t] not in pre_pos.values():
                    pre_pos[veh_id] = [pos.x, pos.y, t]
                  
                
    # pred_csv.close()
                
