import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    # Test root endpoint
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint:", response.json())

    # Test getting a single task
    task_id = "sympy__sympy-24562"
    response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
    print(f"\nTask {task_id}:", json.dumps(response.json(), indent=2))

    # Test batch task retrieval
    task_ids = ["sympy__sympy-24562", "sympy__sympy-24562"]
    response = requests.post(
        f"{BASE_URL}/api/v1/tasks/batch",
        json={"task_ids": task_ids}
    )
    print("\nBatch tasks:", json.dumps(response.json(), indent=2))

    # Test single evaluation with a more realistic prediction
    sample_prediction = """diff --git a/sympy/core/numbers.py b/sympy/core/numbers.py
--- a/sympy/core/numbers.py
+++ b/sympy/core/numbers.py
@@ -100,6 +100,7 @@ class Number(AtomicExpr):
     def _eval_is_finite(self):
         return True
+    def _eval_is_extended_real(self):
+        return True
"""
    
    response = requests.post(
        f"{BASE_URL}/api/v1/evaluate",
        json={
            "task_id": task_id,
            "prediction": sample_prediction
        }
    )
    print("\nEvaluation result:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_api() 