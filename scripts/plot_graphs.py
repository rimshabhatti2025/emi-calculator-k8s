import matplotlib.pyplot as plt
import csv

def plot_graph1():
    rates = [10, 25, 50, 100, 200]
    replicas = [1, 2, 3]
    
    plt.figure(figsize=(8, 5))
    for rep in replicas:
        avg_times = []
        for rate in rates:
            filename = f"results/load_test_{rep}rep_{rate}rps.txt"
            avg_time = 0
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        if "Avg Response Time:" in line:
                            parts = line.split()
                            avg_time = float(parts[-2])
                            break
            except FileNotFoundError:
                pass
            avg_times.append(avg_time)
        plt.plot(rates, avg_times, marker='o', label=f'{rep} Replica(s)')
    
    plt.title('Average Response Time vs Request Rate')
    plt.xlabel('Request Rate (req/s)')
    plt.ylabel('Average Response Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.savefig('results/graph1_response_time.png')
    print("Graph 1 saved.")
    plt.close()

def plot_graph2():
    timestamps = []
    cpu_values = []
    
    try:
        with open('results/autoscale_test.csv', 'r') as f: # Graph 2 ke liye purani file theek hai
            reader = csv.DictReader(f)
            for row in reader:
                cpu_str = row['cpu_percent'].split('/')[0]
                cpu_val = float(cpu_str)
                if cpu_val > 50:
                    timestamps.append(row['timestamp'])
                    cpu_values.append(cpu_val)
    except FileNotFoundError:
        print("autoscale_test.csv not found")
        return
    
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(cpu_values)), cpu_values, marker='o', color='red')
    plt.title('CPU Utilization during 100 req/s (3 replicas)')
    plt.xlabel('Time (intervals)')
    plt.ylabel('CPU Utilization (%)')
    plt.grid(True)
    plt.savefig('results/graph2_cpu_per_pod.png')
    print("Graph 2 saved.")
    plt.close()

def plot_graph3():
    timestamps = []
    replicas = []
    cpu_percent = []
    
    # Yahan hum FIXED file use kar rahe hain
    try:
        with open('results/autoscale_test_fixed.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamps.append(row['timestamp'])
                replicas.append(int(row['replicas']))
                cpu_str = row['cpu_percent'].split('/')[0]
                cpu_percent.append(float(cpu_str))
    except FileNotFoundError:
        print("autoscale_test_fixed.csv not found")
        return
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU Utilization (%)', color=color)
    ax1.plot(range(len(cpu_percent)), cpu_percent, color=color, marker='o', label='CPU %')
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Number of Replicas', color=color)
    # Yahan step plot use karenge taake 1, 2, 3, 5 clear nazar aaye
    ax2.step(range(len(replicas)), replicas, color=color, marker='s', where='post', label='Replicas')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_yticks([1, 2, 3, 4, 5])
    
    plt.title('Autoscaling Test: CPU and Replicas over Time')
    fig.tight_layout()
    plt.savefig('results/graph3_autoscaling.png')
    print("Graph 3 saved.")
    plt.close()

if __name__ == "__main__":
    plot_graph1()
    plot_graph2()
    plot_graph3()
