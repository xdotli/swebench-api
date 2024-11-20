# Virtual on-site

## 1. Run https://github.com/All-Hands-AI/OpenHands locally

Pull the runtime image and run OpenHands locally in an interactive mode.

```bash
docker pull docker.all-hands.dev/all-hands-ai/runtime:0.14-nikolaik

docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.14-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.14
```

It will start a local server at http://localhost:3000.

Test with my anthropic API key and choose the `claude-3-5-sonnet-20241022` model. Prompt with `Please write a bash script hello.sh that prints "hello world!"`

![Running OpenHands in GUI mode](/images/image-6.png)

## 2. Run https://github.com/princeton-nlp/swe-bench/ locally

### Install SWE-bench and test the installation

Follow the instructions in the [SWE-bench README](https://github.com/princeton-nlp/SWE-bench) to clone the repo and install the dependencies.

Test the installation by running the following command with a random instance `astropy__astropy-13803`. It will run the evaluation with the predictions path as gold (which means the predictions are the ground truth and should be resolved).

```bash
python3 -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench \
    --predictions_path gold \
    --max_workers 1 \
    --instance_ids astropy__astropy-13803 \
    --run_id validate-gold
```

The output should be like the following:
![Evaluation result](/images/image-5.png)
Only one instance is evaluated and it is resolved. This means the SWE-bench is installed correctly.

### Run Inference

In real environment, we need to run the inference first and get the prediction patches, and then run the evaluation with the predictions.

There are a couple of datasets we can use in the dataset collection, including the base one with only issue text and base commit `princeton-nlp/SWE-bench`, and more complete ones with different retrieval settings `princeton-nlp/SWE-bench_oracle`, `princeton-nlp/SWE-bench_bm25_13K`, `princeton-nlp/SWE-bench_bm25_27K`, etc.

For each dataset, there is one lite version which is a subset of the full version. For simplicity and cost consideration, I will use the `princeton-nlp/SWE-bench_Lite_bm25_13K` dataset here. There are 300 records in the lite dataset, by 30 shards each containing 10 records.

Here is the command to run the inference with anthropic claude-3.5 sonnet model, with a max cost of 1 USD, and only process the first shard.

```bash
pip install -e ".[inference]"
export ANTHROPIC_API_KEY="Your-Anthropic-API-Key"
python3 -m swebench.inference.run_api --dataset_name_or_path princeton-nlp/SWE-bench_Lite_bm25_13K --model_name_or_path claude-3-5-sonnet-20241022 --output_dir ./outputs --max_cost 1 --shard_id 0 --num_shards 30
```

![Inference result](/images/image-1.png)

The output is saved in the `./outputs` directory, named as `claude-3-5-sonnet-20241022__SWE-bench_Lite_bm25_13K__test__shard-0__num_shards-30.jsonl`.

### Run Evaluation

Similar to the testing section, we can run the evaluation with the predictions. Here is the command to run the evaluation with the predictions saved in the `./outputs` directory.

```bash
python3 -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite_bm25_13K \
    --predictions_path ./outputs/claude-3-5-sonnet-20241022__SWE-bench_Lite_bm25_13K__test__shard-0__num_shards-30.jsonl \
    --max_workers 1 \
    --run_id claude-3-5-sonnet-SWE-bench_Lite_bm25_13K__test__shard-0
```

The result is saved in current directory, named as `claude-3-5-sonnet-SWE-bench_Lite_bm25_13K__test__shard-0.json`.
![Evaluation result](/images/image-2.png)

From the result, we can see that 10 instances are submitted, only 3 are completed, but none of them are resolved. This is expected because we only use the standalone model claude-3.5 sonnet for inference, without any agents to process the responses and generate a valid patch, while the evaluation process requires a valid patch to apply to the base commit before running unit tests.

## 3. Run OpenHands against SWE-bench. Get an initial score.

OpenHands provides official support for SWE-bench, with given [instructions](https://github.com/All-Hands-AI/OpenHands/tree/main/evaluation/swe_bench#openhands-swe-bench-instance-level-docker-support) and scripts under the `evaluation/swe_bench` directory.

Before running the inference, we need to build and setup the environment. See the [Development.md](https://github.com/All-Hands-AI/OpenHands/blob/main/Development.md) for more details.

### Run Inference on SWE-Bench Instances

First create a config file `config.toml` from the template file `config.template.toml` and filling in the LLM configuration under the `[llm]` group. I've created a new config for claude-3.5 sonnet under the `[llm.claude-3-5-sonnet]` group.

Run the inference script with the following command to use the claude-3.5 sonnet model to run inference on the SWE-bench lite dataset, with the CodeActAgent, and only run first 5 instances of the 300 instances in the test split, with max iteration 30, and 1 worker. Dataset is set to the lite version as well, for performance and cost consideration.

Due to the rate limit of the Anthropic API, I only run 2 instances here and set the max iteration to 5, which may not be enough for the agent to generate a valid patch.

```bash
./evaluation/swe_bench/scripts/run_infer.sh llm.claude-3-5-sonnet HEAD CodeActAgent 2 5 1 princeton-nlp/SWE-bench_Lite_bm25_13K test
```

![Inference result](/images/image-3.png)

### Run Evaluation on SWE-Bench Instances

```bash
./evaluation/swe_bench/scripts/eval_infer.sh ./evaluation/evaluation_outputs/outputs/princeton-nlp__SWE-bench_Lite_bm25_13K-test/CodeActAgent/claude-3-5-sonnet-20241022_maxiter_5_N_v2.2-no-hint-run_1/output.jsonl "" princeton-nlp/SWE-bench_Lite_bm25_13K test
```

Here is the result of the evaluation, saved in the `./evaluation/evaluation_outputs/outputs/princeton-nlp__SWE-bench_Lite_bm25_13K-test/CodeActAgent/claude-3-5-sonnet-20241022_maxiter_5_N_v2.2-no-hint-run_1/report.json` file.

One of the two instances is resolved, and the other one is an empty patch.

![Evaluation result](/images/image-4.png)

## 4. Your part - make this benchmark publically available

Host a FastAPI server to serve the Benchmark, specifically:

- An agent like OpenHands should be able to get a task from the SWE-bench
- After the agent executes the task, it should be able to send its output to the Benchmark via a POST request, and get a evaluation result back
- Also make an endpoint to process task fetching and evaluating in batches. Make it available to pass in an array of task ids.
- Make the endpoint available to the public.
