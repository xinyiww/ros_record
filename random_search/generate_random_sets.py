import csv
from dataImport import * 

import sys

if __name__ == "__main__":
    
    save_fn = sys.argv[1]
    save_fd = sys.argv[2]
    n_sam = 150

    # max_acc = np.random.random (n_sam) * 1.8 + 0.2 t-junc
    max_acc = np.random.random (n_sam) * 0.25 + 0.0
    min_d_gap = np.random.random (n_sam) * 3.0 + 1.0
    min_t_gap = np.random.random (n_sam) * 3.9 + 0.1
    target_speed = np.random.random (n_sam) *2.0 + 4.0
    # max_deacc = np.ones(n_sam) * 1.67
    # quantitative_accuracy = np.random.random (n_sam) 

    # Define the headers and rows of data
    headers = ['id',
               'max_acc', 
               'min_d_gap',
               'min_t_gap', 
            #    'max_deacc', 
            #    'quantitative_accuracy'
            'target_speed'
               ]
    rows = []

    for i in range(n_sam):
        rows.append([i,
                     max_acc[i],
                     min_d_gap[i], 
                     min_t_gap[i], 
                    #  max_deacc[i], 
                    #  quantitative_accuracy[i]
                    target_speed[i]
                     ])

    # Open a file for writing
    with open(save_fd+save_fn, 'w', newline='') as csvfile:

        # Create a CSV writer object
        writer = csv.writer(csvfile)

        # Write the headers to the CSV file
        writer.writerow(headers)

        # Write the rows of data to the CSV file
        for row in rows:
            writer.writerow(row)

    print('Data written to CSV file.')