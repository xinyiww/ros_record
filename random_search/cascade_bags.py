from dataImport import * 
# from eval import *
import matplotlib.pyplot as plt
import rosbag
# following are the data we use 
# [x[0] for x in os.walk(os. getcwd())]
# data_folders = [ f.path for f in os.scandir(os. getcwd()) if f.is_dir() and f.name[:5] == 't_jun']
bags_fn= [ f.path for f in os.scandir(os. getcwd()) if f.is_dir() == False and f.name[:5] == 't_jun']
# Create the output bag
output_bag = rosbag.Bag('ALL_t_jun.bag', 'w')

# Iterate through the messages in the input bags and write them to the output bag
for bag_fn in bags_fn:
    bag = rosbag.Bag(bag_fn)
    for topic, msg, timestamp in bag.read_messages():
        output_bag.write(topic, msg, timestamp)
    # Close the bags
    bag.close()
output_bag.close()