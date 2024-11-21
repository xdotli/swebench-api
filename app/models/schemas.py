from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TaskResponse(BaseModel):
    task_id: str
    issue_text: str
    base_commit: str
    file_paths: List[str]
    context: Optional[Dict[str, Any]] = None

class EvaluationRequest(BaseModel):
    task_id: str
    prediction: str
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "sympy__sympy-24562",
                "prediction": """diff --git a/file.py b/file.py
--- a/file.py
+++ b/file.py
@@ -1,1 +1,1 @@
-old line
+new line"""
            }
        }

class BatchEvaluationRequest(BaseModel):
    predictions: List[EvaluationRequest]

class EvaluationResponse(BaseModel):
    task_id: str
    is_resolved: bool
    error_message: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None

class BatchTaskRequest(BaseModel):
    task_ids: List[str] 