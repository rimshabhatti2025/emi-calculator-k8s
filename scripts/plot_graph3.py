import matplotlib.pyplot as plt
import csv

def plot_graph3():
    timestamps = []
    replicas = []
    cpu_percent = []
    
    # Nayi file use karein jo abhi banayi hai
    try:
        with open('results/autoscale_test_final.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamps.append(row['timestamp'])
                replicas.append(int(row['replicas']))
                # CPU value "4/50" se sirf "4" nikalna
                cpu_str = row['cpu_percent'].split('/')[0]
                cpu_percent.append(float(cpu_str))
    except FileNotFoundError:
        print("File not found!")
        return
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # CPU Line (Red)
    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU Utilization (%)', color=color)
    ax1.plot(range(len(cpu_percent)), cpu_percent, color=color, marker='o', label='CPU %')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Replicas Line (Blue) - Step plot taake clear nazar aaye
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Number of Replicas', color=color)
    ax2.step(range(len(replicas)), replicas, color=color, marker='s', where='post', label='Replicas')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_yticks([1, 2, 3, 4, 5]) # Sirf 1 se 5 tak dikhaye
    
    plt.title('Autoscaling Test: CPU and Replicas over Time')
    fig.tight_layout()
    plt.savefig('results/graph3_autoscaling.png')
    print("Graph 3 saved perfectly!")
    plt.close()

if __name__ == "__main__":
    plot_graph3()
