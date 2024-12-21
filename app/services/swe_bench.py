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
            # print(f'Dataset sample: {self.dataset[0]}')
            # Get columns of the dataset
            dataset_columns = self.dataset.column_names
            print("Dataset columns:", dataset_columns)
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
        
        # Debug print
        print(f"\nRaw task data for {task_id}:")
        for key, value in task.items():
            print(f"{key}: {value}")
        
        # Construct issue text from problem statement and hints
        issue_text_parts = []
        print(f'Task: {task}')
        if task.get("problem_statement"):
            print(f'Problem statement: {task["problem_statement"]}')
            issue_text_parts.append(task["problem_statement"])
        if task.get("hints_text"):
            issue_text_parts.append("Additional Hints:\n" + task["hints_text"])
        
        issue_text = "\n\n".join(filter(None, issue_text_parts))
        
        # Get file paths from the patch field if available
        file_paths = []
        if task.get("patch"):
            # Extract file paths from the patch
            for line in task["patch"].split('\n'):
                if line.startswith('diff --git'):
                    # Extract the b/ path from diff --git a/path b/path
                    file_path = line.split()[-1].lstrip('b/')
                    file_paths.append(file_path)
        
        # Build context with all relevant information
        context = {
            "repo": task.get("repo", ""),
            "created_at": task.get("created_at", ""),
            "version": task.get("version", ""),
            "test_patch": task.get("test_patch", ""),
            "environment_setup_commit": task.get("environment_setup_commit", ""),
            "FAIL_TO_PASS": task.get("FAIL_TO_PASS", ""),
            "PASS_TO_PASS": task.get("PASS_TO_PASS", "")
        }
        
        return {
            "task_id": task["instance_id"],
            "issue_text": issue_text,
            "base_commit": task.get("base_commit", ""),
            "file_paths": file_paths,
            "context": context
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

if __name__ == "__main__":
    swe_bench_service = SWEBenchService()
    task_id = "astropy__astropy-11693"
    prediction = """diff --git a/astropy/wcs/wcsapi/fitswcs.py b/astropy/wcs/wcsapi/fitswcs.py
--- a/astropy/wcs/wcsapi/fitswcs.py
+++ b/astropy/wcs/wcsapi/fitswcs.py
@@ -323,7 +323,17 @@ def pixel_to_world_values(self, *pixel_arrays):
         return world[0] if self.world_n_dim == 1 else tuple(world)
 
     def world_to_pixel_values(self, *world_arrays):
-        pixel = self.all_world2pix(*world_arrays, 0)
+        # avoid circular import
+        from astropy.wcs.wcs import NoConvergence
+        try:
+            pixel = self.all_world2pix(*world_arrays, 0)
+        except NoConvergence as e:
+            warnings.warn(str(e))
+            # use best_solution contained in the exception and format the same
+            # way as all_world2pix does (using _array_converter)
+            pixel = self._array_converter(lambda *args: e.best_solution,
+                                         'input', *world_arrays, 0)
+
         return pixel[0] if self.pixel_n_dim == 1 else tuple(pixel)
 
     @property

"""
    evaluation_result = swe_bench_service.evaluate_prediction(task_id, prediction)
    print(f"Evaluation result: {evaluation_result}")