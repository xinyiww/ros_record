 # Prediction module
 a prediction module handles vehicle trajectory prediction and pedestrain trajectory prediction.
 
## branches 

- **master** 

This branch contains a default prediction module.

For traffic trajectory prediction, the default predictor provide a constant velocity prediction on the lane it is currently on. Specifically, it takes in lane perception information such as position, heading, vehicle id, etc in the ROS topic `/region/lane_perception`, lane infomation in topic `/region/lanes_center` and output prediction forward for at most 10 seconds at a specified frequency. The prediction is published to the topic `/region/all_car_predictions`.

For pedestrain trajectory prediction, the default predictor provide a constant velocity prediction ahead for at least 10 second, at a specified frequency. The prediction is published to the topic `/region/pedestrians_prediction`.


- **heuristic** 

This branch contains multiple modules other than the default predictor in master branch.

 1. `prediction_ct_vel`: default prediction module that stays basically the same with master branch.
 2. `prediction_GM`: Gaussian model that implements a Kalman filter that takes road prior as measurement, constant velocity as dynamic model, and iteratively update the prediction as the posterior estimation over multiple timesteps.
 3. `prediction_IDM`: Implementation of combining Intelligence Driver Model (IDM) on longtitude direction and lane sanpping on latitude direction. 
  ![IDM model math](imgs/IDM.jpg)

 4. `prediction_combo`: One implementation on combining Gaussian model with IDMf   model. 


 - **heuristic-citysim** 

This branch contains some adaption of the predictors in order to be used in CitySim dataset. 



## How to use the predictors as a ROS nodes 
1. You could also follow the standard procedure to build a catkin workspace in a ROS package and run the package using rosrun.

2. If you are using multiple predictor at the same time, or you are using scenarios within the carla simulator, then it is more convenient to 
link all the prediction modules within [carla-setup repo](https://github.com/honda-research-institute/carla-setup) and build and make packages in carla-setup project when setting up the whole carla-setup catkin workspace. Detailed steps could be found in **update from Xinyi** part in [carla-setup README.md](https://github.com/honda-research-institute/carla-setup).


After either 1. or 2., you should be able to run seperate ros node using terminal command 
```
rosrun prediction_<name of predictor> prediction_<name of predictor>_node
```


