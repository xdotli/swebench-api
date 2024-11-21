from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import (
    TaskResponse,
    EvaluationRequest,
    BatchEvaluationRequest,
    EvaluationResponse,
    BatchTaskRequest
)
from ..services.swe_bench import SWEBenchService

router = APIRouter()
swe_bench_service = SWEBenchService()

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    try:
        return swe_bench_service.get_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/batch", response_model=List[TaskResponse])
async def get_tasks_batch(request: BatchTaskRequest):
    try:
        return swe_bench_service.get_multiple_tasks(request.task_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_solution(request: EvaluationRequest):
    try:
        return swe_bench_service.evaluate_prediction(
            request.task_id,
            request.prediction
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate/batch", response_model=List[EvaluationResponse])
async def evaluate_batch(request: BatchEvaluationRequest):
    results = []
    for pred in request.predictions:
        try:
            result = swe_bench_service.evaluate_prediction(
                pred.task_id,
                pred.prediction
            )
            results.append(result)
        except Exception as e:
            results.append({
                "task_id": pred.task_id,
                "is_resolved": False,
                "error_message": str(e)
            })
    return results 