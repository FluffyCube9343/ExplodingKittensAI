import pickle

def report_min_totalstates(pkl_file='aggregate.pkl'):
    with open(pkl_file, 'rb') as f:
        data = pickle.load(f)

    totalstates = data.get('totalstates', {})
    
    if not totalstates:
        print("No data found in 'totalstates'.")
        return

    min_key = min(totalstates, key=totalstates.get)
    min_value = totalstates[min_key]

    print(f"Minimum value in 'totalstates': {min_value} (key: {min_key})")

if __name__ == '__main__':
    report_min_totalstates()
