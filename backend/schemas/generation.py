from pydantic import BaseModel, Field

class ContextRequest(BaseModel):
    job_description: str = Field(..., description="A detailed description of the job role.")
    cache_key: str = Field(..., description="A unique key to cache the generated context.")


class ContextResponse(BaseModel):
    context: dict = Field(..., description="The generated context for the job description.")