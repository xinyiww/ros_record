import csv
from eval import *

n_sam = 5
max_acc = np.random.random (n_sam) * 1.8 + 0.2
min_d_gap = np.random.random (n_sam) * 3.9 + 0.1
min_t_gap = np.random.random (n_sam) * 7.0 + 1.0


# Define the headers and rows of data
headers = ['id','max_acc', 'min_d_gap', 'min_t_gap', 'ADE', 'FDE']
rows = []
count = 0
for i in max_acc:
    for j in min_d_gap:
        for k in min_t_gap:
            rows.append([count, i,j,k])
            count += 1

# Open a file for writing
with open('/home/xliu/Documents/ros_record/random_search/params_random_search.csv', 'w+', newline='') as csvfile:

    # Create a CSV writer object
    writer = csv.writer(csvfile)

    # Write the headers to the CSV file
    writer.writerow(headers)

    # Write the rows of data to the CSV file
    for row in rows:
        writer.writerow(row)

print('Data written to CSV file.')