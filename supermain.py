import subprocess

import os
import glob
import pickle


processes = []


def spamrun(n=30):
    for _ in range(n):
        # Start the main.py script as a subprocess
        p = subprocess.Popen(['python3', 'main.py'])
        processes.append(p)

    # Wait for all processes to complete
    for p in processes:
        p.wait()

    print("All 10 instances finished.")


def merge_dicts_sum(d1, d2):
    result = d1.copy()
    for k, v in d2.items():
        if k in result:
            if isinstance(v, dict) and isinstance(result[k], dict):
                result[k] = merge_dicts_sum(result[k], v)
            else:
                result[k] += v
        else:
            result[k] = v
    return result

def aggregate_pickles(output_file='aggregate.pkl'):
    pkl_files = glob.glob('*.pkl')

    aggregate_data = None

    for pkl_file in pkl_files:
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
            if aggregate_data is None:
                aggregate_data = data
            else:
                aggregate_data = merge_dicts_sum(aggregate_data, data)

        os.remove(pkl_file)
        print(f"Deleted {pkl_file}")

    with open(output_file, 'wb') as f:
        pickle.dump(aggregate_data, f)

    print(f"Aggregated data saved to {output_file}")


spamrun()
aggregate_pickles()
