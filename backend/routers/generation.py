from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas.generation import ContextRequest, ContextResponse
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated
from backend.core.database import get_db
from backend.models.user import User
from backend.utils.password_hash import hashed_password
from backend.schemas.user import Usercreate, UserRead
from backend.core.security import get_current_user
from graph.graph import app as graph_app

router = APIRouter(prefix="/generation", tags=["generation"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.post('/context', status_code=status.HTTP_200_OK)
async def generate_context(
    payload: ContextRequest,
    user: user_dependency,
    db: db_dependency
):
    result = await db.execute(select(User).where(User.id == user.get("id")))
    db_user = result.scalars().first()
    state = {
        "user_context": db_user.user_context,
        "job_description": payload.job_description,
        "type": "email" # Defaulting to email to satisfy graph routing
    }
    
    # Generate a random thread_id for this request since we are using a checkpointer
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    result_state = await graph_app.ainvoke(state, config=config)
    context = result_state.get('context', {})
    if isinstance(context, str):
        try:
            import json
            context = json.loads(context)
        except json.JSONDecodeError:
            # Fallback if it's just a string but not JSON
            context = {"raw_content": context}
            
    return ContextResponse(context=context)

