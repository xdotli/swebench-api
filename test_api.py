import requests
import json
from openai import OpenAI
import os

# BASE_URL = "http://localhost:8000"
BASE_URL = "http://159.89.229.132"

def test_api():
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint:", response.json())

    task_id = "sympy__sympy-24562"
    response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
    task_data = response.json()
    # print('task_data', task_data)
    print(f"\nTask {task_id}:", json.dumps(task_data, indent=2))

    task_ids = ["sympy__sympy-24562", "sympy__sympy-24562"]
    response = requests.post(
        f"{BASE_URL}/api/v1/tasks/batch",
        json={"task_ids": task_ids}
    )
    print("\nBatch tasks:", json.dumps(response.json(), indent=2))

    if "OPENAI_API_KEY" in os.environ:
        print("\nRunning inference with GPT-4...")
        client = OpenAI()
        
        prompt = f"""Given this GitHub issue:
{task_data['issue_text']}

Base commit: {task_data['base_commit']}
Files to modify: {', '.join(task_data['file_paths'])}

Additional context: {json.dumps(task_data['context'], indent=2)}

Please provide a patch in git diff format that resolves this issue.
The patch should be applicable to the base commit.
Only include the git diff, no additional explanation."""

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled software engineer. Provide patches in git diff format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        prediction = completion.choices[0].message.content
        print(f"\nModel prediction:\n{prediction}")
        
        # Evaluate the prediction
        response = requests.post(
            f"{BASE_URL}/api/v1/evaluate",
            json={
                "task_id": task_id,
                "prediction": prediction
            }
        )
        print("\nEvaluation result:", json.dumps(response.json(), indent=2))
    else:
        print("\nSkipping inference (OPENAI_API_KEY not set)")
        # Fall back to test prediction
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
        print("\nEvaluation result (with test prediction):", 
              json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_api() 