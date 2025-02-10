from fastapi import FastAPI, Depends
from auth import AuthHandler
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
auth_handler = AuthHandler()


class ProcessRequest(BaseModel):
    data_type: str
    processing_level: Optional[str] = "standard"
    batch_size: Optional[int] = 100


class ProcessResponse(BaseModel):
    job_id: str
    status: str
    config: dict
    user_id: str


@app.get("/health")
async def health_check(user_data: dict = Depends(auth_handler.auth_wrapper)):
    return {"status": "healthy", "version": "1.0.0", "user_id": user_data["user_id"]}


@app.post("/api/v1/process", response_model=ProcessResponse)
async def process_data(
    request: ProcessRequest, user_data: dict = Depends(auth_handler.auth_wrapper)
):
    processing_config = {
        "user_id": user_data["user_id"],
        "data_type": request.data_type,
        "processing_level": request.processing_level,
        "batch_size": request.batch_size,
    }

    return ProcessResponse(
        job_id="job_123",
        status="initiated",
        config=processing_config,
        user_id=user_data["user_id"],
    )
