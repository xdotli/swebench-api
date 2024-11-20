#!/bin/bash

# Default values
MODEL_CONFIG=${MODEL_CONFIG:-"llm.claude-3-5-sonnet"}
MODEL_NAME=${MODEL_NAME:-"claude-3-5-sonnet-20241022"}
GIT_VERSION=${GIT_VERSION:-"HEAD"}
AGENT=${AGENT:-"CodeActAgent"}
EVAL_LIMIT=${EVAL_LIMIT:-5}
MAX_ITER=${MAX_ITER:-30}
NUM_WORKERS=${NUM_WORKERS:-1}
DATASET=${DATASET:-"princeton-nlp/SWE-bench_Lite_bm25_13K"}
DATASET_SPLIT=${DATASET_SPLIT:-"test"}

# Run inference
echo "Running inference..."
./evaluation/swe_bench/scripts/run_infer.sh \
    "$MODEL_CONFIG" \
    "$GIT_VERSION" \
    "$AGENT" \
    "$EVAL_LIMIT" \
    "$MAX_ITER" \
    "$NUM_WORKERS" \
    "$DATASET" \
    "$DATASET_SPLIT"

# Run evaluation
echo "Running evaluation..."
./evaluation/swe_bench/scripts/eval_infer.sh \
    "./evaluation/evaluation_outputs/outputs/${DATASET//\//__}-${DATASET_SPLIT}/${AGENT}/${MODEL_NAME}_maxiter_${MAX_ITER}_N_v2.2-no-hint-run_1/output.jsonl" \
    "" \ 
    "$DATASET" \
    "$DATASET_SPLIT" 