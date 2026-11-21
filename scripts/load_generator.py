import requests
import random
import time
import sys
from concurrent.futures import ThreadPoolExecutor

URL = "http://emi.local:8080/api/emi"

def send_request():
    # Random valid inputs generate karein
    principal = random.randint(10000, 1000000)
    rate = random.randint(1, 20)
    months = random.randint(12, 360)
    
    payload = {"principal": principal, "rate": rate, "months": months}
    try:
        start = time.time()
        res = requests.post(URL, json=payload, timeout=5)
        end = time.time()
        return res.status_code, (end - start) * 1000 # response time in ms
    except Exception as e:
        return 500, 0

def run_test(rate, duration):
    total_requests = rate * duration
    status_codes = []
    response_times = []
    
    print(f"Starting test: {rate} req/s for {duration}s (Total: {total_requests} requests)")
    
    with ThreadPoolExecutor(max_workers=rate) as executor:
        futures = [executor.submit(send_request) for _ in range(total_requests)]
        for f in futures:
            status, rt = f.result()
            status_codes.append(status)
            response_times.append(rt)
            
    success = status_codes.count(200)
    errors = len(status_codes) - success
    avg_rt = sum(response_times) / len(response_times) if response_times else 0
    
    print(f"Done: {success} success, {errors} errors, Avg Response Time: {avg_rt:.2f} ms")
    return success, errors, avg_rt

if __name__ == "__main__":
    rate = int(sys.argv[1])
    duration = int(sys.argv[2])
    run_test(rate, duration)
