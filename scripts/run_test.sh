#!/bin/bash
# Usage: ./run_test.sh <replicas> <rate>
REPLICAS=$1
RATE=$2
OUTPUT_FILE="results/load_test_${REPLICAS}rep_${RATE}rps.txt"

# Total requests = rate * 60 seconds
TOTAL_REQ=$((RATE * 60))

echo "Running test: $REPLICAS replicas, $RATE req/s for 60s..."
ab -n $TOTAL_REQ -c $RATE -p scripts/body.json -T application/json http://emi.local:8080/api/emi > "$OUTPUT_FILE"

echo "Done. Output saved to $OUTPUT_FILE"
