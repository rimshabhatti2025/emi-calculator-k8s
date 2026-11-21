import requests
import random
import time
import sys
import subprocess
import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

URL = "http://emi.local:8080/api/emi"
CSV_FILE = "results/autoscale_test.csv"

def send_request():
    principal = random.randint(10000, 1000000)
    rate = random.randint(1, 20)
    months = random.randint(12, 360)
    payload = {"principal": principal, "rate": rate, "months": months}
    try:
        start = time.time()
        res = requests.post(URL, json=payload, timeout=5)
        end = time.time()
        return res.status_code, (end - start) * 1000
    except Exception:
        return 500, 0

def get_hpa_replicas():
    out = subprocess.run("kubectl get hpa emi-web -n emi --no-headers", shell=True, capture_output=True, text=True).stdout
    if out:
        parts = out.split()
        if len(parts) >= 6:
            return parts[5]
    return "Unknown"

def get_hpa_cpu():
    out = subprocess.run("kubectl get hpa emi-web -n emi --no-headers", shell=True, capture_output=True, text=True).stdout
    if out:
        parts = out.split()
        if len(parts) >= 4:
            return parts[3].replace('%', '')
    return "0"

def record_hpa(writer):
    replicas = get_hpa_replicas()
    cpu = get_hpa_cpu()
    timestamp = datetime.now().strftime("%H:%M:%S")
    writer.writerow([timestamp, replicas, cpu])
    print(f"{timestamp} - HPA Replicas: {replicas}, CPU: {cpu}%")

def run_phase(rate, duration, writer, phase_name):
    print(f"--- Phase: {phase_name} ({rate} req/s for {duration}s) ---")
    total_req = rate * duration
    interval = 15  # HPA record every 15 seconds
    end_time = time.time() + duration
    last_hpa_record = 0
    
    with ThreadPoolExecutor(max_workers=rate) as executor:
        futures = [executor.submit(send_request) for _ in range(total_req)]
        
        while time.time() < end_time:
            if time.time() - last_hpa_record >= interval:
                record_hpa(writer)
                last_hpa_record = time.time()
            time.sleep(1)

if __name__ == "__main__":
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "replicas", "cpu_percent"])
        
        # Phase 1: 10 req/s for 2 minutes
        run_phase(10, 120, writer, "Phase 1: 10 req/s")
        
        # Phase 2: 100 req/s for 5 minutes
        run_phase(100, 300, writer, "Phase 2: 100 req/s")
        
        # Phase 3: 10 req/s for 3 minutes
        run_phase(10, 180, writer, "Phase 3: 10 req/s")
        
    print("Autoscaling test complete!")
