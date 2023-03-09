import csv
from dataImport import * 
from eval import *
import sys

if __name__ == "__main__":
    
    save_folder = sys.argv[1]

    n_sam = 300

    max_acc = np.random.random (n_sam) * 1.8 + 0.2
    min_d_gap = np.random.random (n_sam) * 3.9 + 0.1
    min_t_gap = np.random.random (n_sam) * 7.0 + 1.0


    # Define the headers and rows of data
    headers = ['max_acc', 'min_d_gap', 'min_t_gap']
    rows = []

    for i in range(max_acc):
        rows.append([max_acc[i],min_d_gap[i], min_t_gap[i]])

    # Open a file for writing
    with open('aaaaaaaa.csv', 'w', newline='') as csvfile:

        # Create a CSV writer object
        writer = csv.writer(csvfile)

        # Write the headers to the CSV file
        writer.writerow(headers)

        # Write the rows of data to the CSV file
        for row in rows:
            writer.writerow(row)

    print('Data written to CSV file.')