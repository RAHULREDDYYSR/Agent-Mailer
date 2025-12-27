from pydantic import BaseModel
import uuid
class JobsResponse(BaseModel):
    id: uuid.UUID
    title: str
    company: str
    jd_text: str
    generated_context: str | None = None