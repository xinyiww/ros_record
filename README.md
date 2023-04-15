# ros_record

This is the repo for evaluation pipline of performance based on recorded rosbag in carla.


## how to use the pipeline

1. Run a single experiment on carla, record bags at the same time, make sure it contains valid prediction msgs in `/region/lanes_preception` as well as ground truth msgs in `/region/lanes_perception`.

2. Save the bag into the `bags/` folder. Specify the name of the bag in `run_eval.sh` and then you can run 
```
./run_eval.sh
```
remember to change the excutable mode of `run_eval.sh` .

