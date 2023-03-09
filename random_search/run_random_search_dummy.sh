#!/bin/bash

# where I store those random parameter sets in 125 * 3 sheet
CSV_FILE=params_random_search.csv
# define the rosbag we gain GT and generate prediction
ROSBAG=/home/xliu/Documents/ros_record/random_search/t_jun_pred_combo_gap_filtered.bag # should not contain /region/lanes_prediction and /region/all_cars_predictions_idm
# working space
WS=/home/xliu/Documents/ros_record/random_search
# define GT
python bag2csv_local.py $ROSBAG $WS

# rosrun prediction_IDM prediction_IDM_node &
# Skip the header row
tail -n +2 "$CSV_FILE" | while IFS=, read -r id max_acc min_d_gap min_t_gap ADE_t_jun_filtered ADE_t_jun_combo_2; do
  echo "max_acc: $max_acc , min_d_gap: $min_d_gap , min_t_gap: $min_t_gap"
  rosparam set /max_acc $max_acc
  rosparam set /min_d_gap $min_d_gap
  rosparam set /min_t_gap $min_t_gap
  rosparam set use_sim_time true
  # Start recording messages to a rosbag file
  rosbag record -e "/region/all_cars_predictions_idm" -O params_pred_${id}.bag __name:=my_bag & </dev/null
  # Play the rosbag file
  rosbag play $ROSBAG --clock </dev/null

  # Kill the ROS nodes and stop recording messages
  rosnode kill my_bag
  # rosnode cleanup

  # python eval_and_save.py params_random_search_pred_${id} $WS


done


# ros_pid=$(pgrep roscore)
# kill -SIGTERM $ros_pid


