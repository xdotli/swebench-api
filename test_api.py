import requests
import json
import openai
from openai import OpenAI
import os
import tiktoken
import numpy as np
from datasets import load_dataset

# BASE_URL = "http://localhost:8002"
BASE_URL = "http://ec2-3-232-182-160.compute-1.amazonaws.com:8002"


def call_api(model_name_or_path, inputs, temperature, top_p, **model_args):
    """
    Calls the openai API to generate completions for the given inputs.

    Args:
    model_name_or_path (str): The name or path of the model to use.
    inputs (str): The inputs to generate completions for.
    use_azure (bool): Whether to use the azure API.
    temperature (float): The temperature to use.
    top_p (float): The top_p to use.
    **model_args (dict): A dictionary of model arguments.
    """
    system_messages = inputs.split("\n", 1)[0]
    user_message = inputs.split("\n", 1)[1]
    try:
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "OPENAI_API_KEY environment variable must be set when using OpenAI API."
            )

        client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            organization=os.environ.get("OPENAI_ORGANIZATION", ""),
        )
    
        response = client.chat.completions.create(
            model=model_name_or_path,
            messages=[
                {"role": "system", "content": system_messages},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            top_p=top_p,
            **model_args,
        )
        return response
    except openai.BadRequestError as e:
        if e.code == "context_length_exceeded":
            print("Context length exceeded")
            return None
        raise e

def gpt_tokenize(string: str, encoding) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens


def test_task():
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint:", response.json())
    
    task_id = "sympy__sympy-24562"
    
    response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
    task_data = response.json()
    print(f"\nTask {task_id}:", json.dumps(task_data, indent=2))
    
    task_ids = ["sympy__sympy-24562", "sympy__sympy-24562"]
    response = requests.post(
        f"{BASE_URL}/api/v1/tasks/batch",
        json={"task_ids": task_ids}
    )
    print("\nBatch tasks:", json.dumps(response.json(), indent=2))


def test_evaluate():
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

    response = requests.post(
        f"{BASE_URL}/api/v1/evaluate",
        json={
            "task_id": task_id,
            "prediction": prediction
        }
    )
    
    print(
        "\nEvaluation result (with test prediction):",
        json.dumps(response.json(), indent=2)
    )

def test_api():
    test_task()
    test_evaluate()

if __name__ == "__main__":
    test_api() 