import subprocess
import time
import csv
import os
import psutil
from datetime import datetime

CSV_FILE = "results/cpu_memory.csv"
HOST_CSV = "results/host_cpu.csv"

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

def profile(duration_sec, test_name):
    print(f"Profiling started for {test_name}...")
    end_time = time.time() + duration_sec
    
    # Host CPU CSV file
    with open(HOST_CSV, mode='a', newline='') as hfile:
        hwriter = csv.writer(hfile)
        if os.path.getsize(HOST_CSV) == 0:
            hwriter.writerow(["timestamp", "host_cpu_percent"])
            
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if os.path.getsize(CSV_FILE) == 0:
            writer.writerow(["timestamp", "test_name", "pod_name", "cpu_m", "memory_mi"])
            
        last_host_check = 0
        while time.time() < end_time:
            # Pods ka data har 15 seconds
            output = run_cmd("kubectl top pods -n emi --no-headers | grep emi-web")
            for line in output.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 4:
                        pod_name = parts[0]
                        cpu = parts[1].replace('m', '')
                        memory = parts[2].replace('Mi', '')
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        writer.writerow([timestamp, test_name, pod_name, cpu, memory])
            
            # Host CPU har second
            host_cpu = psutil.cpu_percent(interval=None)
            with open(HOST_CSV, mode='a', newline='') as hfile:
                hwriter = csv.writer(hfile)
                hwriter.writerow([datetime.now().strftime("%H:%M:%S"), host_cpu])
                
            time.sleep(15)
            
if __name__ == "__main__":
    import sys
    duration = int(sys.argv[1])
    test_name = sys.argv[2]
    profile(duration, test_name)
