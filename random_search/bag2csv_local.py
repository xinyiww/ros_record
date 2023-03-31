#!/usr/bin/env python
import sys
import os
import csv
import math
import rosbag
import rospy
import copy

import numpy as np

def bag2csv(filename, directory, isGT):
 # Read the rosbag file
  print("Reading the rosbag file")
  if not directory.endswith("/"):
    directory += "/"
  extension = ".bag"
  if filename.endswith(".bag"):
    filename = filename [:-4]
  bag = rosbag.Bag(directory + filename + extension)

  # Create directory with name filename (without extension)
  results_dir = directory
  if not os.path.exists(results_dir):
    os.makedirs(results_dir)
    
  print("Writing prediction data")
  
  pred_topics = set()
  
  for topic, msg, t in bag.read_messages():
    # print(topic)
    if topic[:28] == '/region/all_cars_predictions':
      pred_topics.add(topic)
  
  fn = filename
  for tp in pred_topics:

      
    with open(results_dir +"/"+fn+'.csv', 'a', newline='') as pred_csv:
      log_writer = csv.writer(pred_csv, delimiter=' ')      
      
      
      for topic, msg, t in bag.read_messages(topics=[topic]):
        if msg.predictions != []:
          for i, veh in enumerate(msg.predictions):
          
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
              
            veh_id = veh.agent_id 
                
            log_writer.writerow([t_start,dt,n_pred,veh_id] + xs + ys + dxs + dys )
  


                
def bag2csv_GT(fp, directory, gt_fn):
 # Read the rosbag file
  print("Reading the rosbag file at " + fp)
  if not directory.endswith("/"):
    directory += "/"
  extension = ".bag"
  if fp.endswith(".bag"):
    fp= fp [:-4]
  bag = rosbag.Bag(fp + extension)

  # Create directory with name filename (without extension)
  results_dir = directory
  if not os.path.exists(results_dir):
    os.makedirs(results_dir)            
    
 
  print("saving the GT file to "+ results_dir +"/"+gt_fn)
  with open(results_dir +"/"+gt_fn, 'a+', newline='') as gt_csv:
      log_writer = csv.writer(gt_csv, delimiter=' ')   
      for topic, msg, t in bag.read_messages(topics=['/region/lanes_perception']):
          t = msg.header.stamp.to_sec()

          for i, lane in enumerate(msg.vehicles):            
              for j, veh in enumerate(lane.vehicles): # some deplicates in the first round -- delete them
                  pos = veh.pose.pose.position   
                  veh_id = veh.lifetime_id
                  log_writer.writerow([t, veh_id, pos.x, pos.y] )


if __name__ == "__main__":

# Get command line arguments
  argv = sys.argv

  # Print the list of arguments

  fn = argv[1] # filename of rosbag
  save_dir = argv[2]
  GT_filename = argv[3]
  
  # print(fp, save_dir)

  bag2csv_GT(fn, save_dir, GT_filename)
  


      
      
