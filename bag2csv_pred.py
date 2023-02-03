#!/usr/bin/env python
import sys
import os
import csv
import math
import rosbag
import rospy
import copy

# filename = sys.argv[2]
# directory = sys.argv[1]

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
    

    for topic, msg, t in bag.read_messages(topics=['/region/all_cars_predictions']):
        
        if msg.predictions != []:
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
                
                    
                log_writer.writerow([t_start,dt,n_pred,i] + xs + ys + dxs + dys )
                
    # pred_csv.close()
                
            