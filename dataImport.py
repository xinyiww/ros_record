
import sys, numpy as np, os

# get t, veh_id, pos.x, pos.y
def getGTData(filename):
    file = open(filename, 'r')
    dat_str = file.readlines()
    data = np.zeros([len(dat_str), 4])
    for i in range(len(dat_str)):
        sample = dat_str[i].split(' ')
        print(sample)
        if len(sample) != 4:
            print ('!check at line ', str(i), ' of file ', str(filename))
        else:
            
            t, veh_id, x, y= (float(sample[i]) for i in range(4))
            
            data[i, :] = t, veh_id, x, y
    return data


# get 
def getPredData(filename):
    file = open(filename, 'r')
    dat_str = file.readlines()
    data = np.zeros([len(dat_str), 4])
    for i in range(len(dat_str)):
        sample = dat_str[i].split(' ')
        
        if len(sample) != 4:
            print ('!check at line ', str(i), ' of file ', str(filename))
        else:
            
            t, veh_id, x, y= (float(sample[i]) for i in range(4))
            
            data[i, :] = t, veh_id, x, y
    return data

def getArucoData(filename):
    file = open(filename, 'r')
    dat_str = file.readlines()
    data = np.zeros([len(dat_str), 7])
    for i in range(len(dat_str)):
        sample = dat_str[i].split('\t')
        if len(sample) != 7:
            print (
             '!check at line ', str(i), ' of file ', str(filename))
        else:
            t, x, y, z, r1, r2, r3 = (float(sample[i]) for i in range(7))
            data[i, :] = (
             t, x, y, z, r1, r2, r3)

    return data


def getAirsimRecData(filename):
    file = open(filename, 'r')
    dat_str = file.readlines()
    data = np.zeros([len(dat_str), 8])
    for i in range(1, len(dat_str)):
        sample = dat_str[i].split('\t')
        if len(sample) != 9:
            print (
             '!check at line ', str(i), ' of file ', len(sample))
        else:
            t, x, y, z, qw, qx, qy, qz = (float(sample[i]) for i in range(8))
            t = t / 1000
            data[i, :] = (t, x, y, z, qw, qx, qy, qz)

    while data[(0, 0)] < 1:
        data = np.delete(data, obj=0, axis=0)

    return data


def getROSData(filename):
    file = open(filename, 'r')
    dat_str = file.readlines()
    data = np.zeros([len(dat_str), 7])
    for i in range(len(dat_str)):
        sample = dat_str[i].split('\t')
        if len(sample) != 8:
            print (
             '!check at line ', str(i), ' of file ', len(sample))
        else:
            t, _, x, y, z, yaw, pitch, roll = (float(sample[i]) for i in range(8))
            data[i, :] = (
             t, x, y, z, yaw, pitch, roll)

    return data
