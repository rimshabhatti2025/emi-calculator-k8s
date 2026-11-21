# Loan EMI Calculator on Kubernetes (Assignment 4)

This repository contains the complete implementation for Cloud Computing Assignment 4. The project is a Loan EMI Calculator web application deployed on a single-node Minikube Kubernetes cluster with a 3-member MongoDB replica set, NGINX Ingress, and Horizontal Pod Autoscaling.

## Project Structure
- `app/`: Contains the Node.js/Express application code, Dockerfile, and frontend (HTML/jQuery/Bootstrap).
- `k8s/`: Contains all Kubernetes YAML manifests.
- `scripts/`: Contains Python scripts for load generation, profiling, and plotting graphs.
- `results/`: Contains raw load test outputs, CSV profiling data, and generated graphs.

---

## Milestone 01: Develop a Loan EMI Calculator with MongoDB
- Developed a Node.js (Express) backend and a Bootstrap/jQuery frontend.
- Implemented three API endpoints:
  - `POST /api/emi`: Calculates EMI using the formula, saves to MongoDB, and returns pod name (`HOSTNAME`) and IP.
  - `GET /api/history`: Retrieves the last 10 calculations.
  - `GET /health`: Readiness probe endpoint that pings MongoDB.
- The application uses AJAX (no postback) and reads the `MONGO_URL` environment variable.
- Tested locally with a MongoDB Docker container.

## Milestone 02: Deploy MongoDB and the Web App on Minikube
- **Dockerization:** Wrote a multi-stage `Dockerfile` using `node:20-alpine` and ran it as a non-root user. Built the image as `emi-web:1.0` and loaded it into Minikube.
- **MongoDB Replica Set:** Created a headless Service (`mongo`) and a StatefulSet (`mongo`) with 3 replicas using `volumeClaimTemplates` for 1Gi PVCs. Used a Kubernetes Job (`mongo-init`) to initiate the replica set (`rs0`).
- **Configuration:** Stored the MongoDB connection string in a ConfigMap (`mongo-config`) and injected it into the web pods.
- **Web App Deployment:** Created a Deployment (`emi-web`) with 3 replicas, configured with readiness/liveness probes on `/health`, and resource limits (100m CPU, 128Mi Memory).
- **Persistence Test:** Deleted `mongo-1` pod to verify that the StatefulSet recreates it with the same PVC and data is not lost.

## Milestone 03: Ingress, Load Balancing and Self-Healing
- **Ingress:** Enabled the NGINX Ingress addon and created an Ingress resource (`emi-ingress.yaml`) mapping `emi.local` to the `emi-web` Service.
- **Load Balancing:** Sent 30 requests via the Ingress and observed that NGINX distributes traffic evenly across the 3 (and later 5) web pods.
- **Self-Healing:** Deleted a web pod and the MongoDB PRIMARY pod. Kubernetes successfully recreated the web pod without dropping requests, and MongoDB automatically elected a new PRIMARY.
- **Rolling Update:** Changed the page title, built `emi-web:1.1`, and used `kubectl set image` to update the deployment with zero downtime. Rolled back to `1.0` using `kubectl rollout undo`.

## Milestone 04: Load Testing, Profiling and Autoscaling
- **Load Testing:** Wrote a Python load generator (`scripts/load_generator.py`) that sends concurrent `POST /api/emi` requests with random valid inputs.
- **Experiments:** Ran 15 load tests (10, 25, 50, 100, 200 req/s) for 60 seconds each, across 1, 2, and 3 replicas. Recorded average response times and error counts.
- **Profiling:** Wrote a Python script (`scripts/profiler.py`) to record per-pod CPU/memory (using `kubectl top pods`) and host CPU (using `psutil`) into CSV files.
- **Autoscaling:** Created an HPA (`autoscaling/v2`) targeting 50% CPU utilization, scaling between 1 and 5 replicas. Ran a 10-minute test (2m at 10 req/s, 5m at 100 req/s, 3m at 10 req/s).
- **Graphs:** Generated three graphs using `matplotlib` (`scripts/plot_graphs.py`):
  1. Average response time vs request rate (1, 2, 3 replicas).
  2. CPU utilization during the 100 req/s run.
  3. CPU utilization and number of replicas over the 10-minute autoscaling test.

---

## How to Deploy on a Fresh Minikube Cluster

1. **Start Minikube and enable addons:**
   minikube start --driver=docker --memory=3072mb --cpus=2
   minikube addons enable ingress
   minikube addons enable metrics-server

2. **Build and load the Docker image:**
   cd app
   docker build -t emi-web:1.0 .
   minikube image load emi-web:1.0
   cd ..

3. **Deploy MongoDB and the Web App:**
   kubectl create namespace emi
   kubectl apply -f k8s/

4. **Verify the Deployment:**
   kubectl get all,pvc,configmap -n emi
   (Wait until all pods are Running and the mongo-init job is Completed.)

5. **Access the Application:**
   Map `emi.local` to `127.0.0.1` in your hosts file and port-forward the Ingress controller:
   kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80 --address 0.0.0.0
   (Open http://emi.local:8080 in your browser.)
