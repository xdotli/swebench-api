from datasets import load_dataset
from typing import List, Dict, Any, Optional
import subprocess
import json
import tempfile
import os
from pathlib import Path

class SWEBenchService:
    def __init__(self):
        try:
            # Create cache directory in the project root
            cache_dir = Path("./dataset_cache")
            cache_dir.mkdir(exist_ok=True)
            
            print("Loading dataset...")
            self.dataset = load_dataset(
                "princeton-nlp/SWE-bench",
                split="test",
                cache_dir=str(cache_dir)
            )
            print(f"Dataset loaded successfully with {len(self.dataset)} instances")
            print("Available instance IDs (first 5):", [
                item["instance_id"] for item in list(self.dataset)[:5]
            ])
        except Exception as e:
            print(f"Error loading dataset: {str(e)}")
            self.dataset = None
        
    def get_task(self, task_id: str) -> Dict[str, Any]:
        if self.dataset is None:
            raise ValueError("Dataset not properly initialized")
        
        # Find the task in the dataset
        matching_tasks = [
            item for item in self.dataset 
            if item["instance_id"] == task_id
        ]
        
        if not matching_tasks:
            raise ValueError(f"Task {task_id} not found in dataset")
            
        task = matching_tasks[0]
        
        # Make sure all required fields are present
        return {
            "task_id": task["instance_id"],
            "issue_text": task.get("issue_text", ""),  # Use get() with default value
            "base_commit": task.get("base_commit", ""),
            "file_paths": task.get("file_paths", []),
            "context": task.get("context", {})
        }

    def get_multiple_tasks(self, task_ids: List[str]) -> List[Dict[str, Any]]:
        return [self.get_task(task_id) for task_id in task_ids]

    def evaluate_prediction(self, task_id: str, prediction: str) -> Dict[str, Any]:
        # Create logs directory if it doesn't exist
        logs_dir = Path("./logs/run_evaluation")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary file to store the prediction
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            prediction_data = {
                "instance_id": task_id,
                "model_name_or_path": "api-client",
                "model_patch": prediction
            }
            json.dump(prediction_data, f)
            f.write('\n')  # Add newline as required by jsonl format
            predictions_path = f.name

        try:
            run_id = f"api-evaluation-{task_id}"
            result_file = f"{run_id}.json"
            
            cmd = [
                "python3", "-m", "swebench.harness.run_evaluation",
                "--dataset_name", "princeton-nlp/SWE-bench",
                "--predictions_path", predictions_path,
                "--max_workers", "1",
                "--instance_ids", task_id,
                "--run_id", run_id
            ]
            
            env = os.environ.copy()
            env["DOCKER_HOST"] = "unix:///var/run/docker.sock"
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                env=env,
                cwd="."  # Ensure we're in the correct directory
            )
            
            print(f"Command output: {result.stdout}")
            print(f"Command error: {result.stderr}")
            
            # Wait a moment for file to be created
            import time
            time.sleep(2)
            
            if os.path.exists(result_file):
                with open(result_file) as f:
                    evaluation_result = json.load(f)
                os.remove(result_file)
                
                return {
                    "task_id": task_id,
                    "is_resolved": evaluation_result.get("resolved", False),
                    "test_results": evaluation_result
                }
            else:
                return {
                    "task_id": task_id,
                    "is_resolved": False,
                    "error_message": f"Evaluation failed. Stdout: {result.stdout}, Stderr: {result.stderr}"
                }
                
        finally:
            os.unlink(predictions_path) 