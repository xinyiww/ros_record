#!/bin/bash

# example of running one single trail evaluation

BAG_PRED=bags/lane_change_pred_1_filtered # to be generated in this file
WS=~/Documents/ros_record/

python3 bag2csv.py $BAG_PRED $WS
python3  eval.py ${BAG_PRED}_results/ # saved in bags/
