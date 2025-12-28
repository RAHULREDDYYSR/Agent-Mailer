from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated
from backend.core.database import get_db
from backend.models.user import User
from backend.models.job_descriptions import JobDescription
from backend.utils.password_hash import hashed_password
from backend.schemas.user import Usercreate, UserRead
from backend.schemas.jobs import JobsResponse
from backend.core.security import get_current_user
from backend.utils.file_parser import parse_file
from backend.utils.context_builder import build_user_context


router = APIRouter(prefix="/users", tags=["users"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[AsyncSession, Depends(get_db)]

@router.post('/',  status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: Usercreate,
    db: db_dependency
):
    user_model = select(User).where(User.username == payload.username)
    result = await db.execute(user_model)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists."
        )

    new_user = User(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        password_hash=hashed_password(payload.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)



@router.get('/me', status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency, db:db_dependency):
    result = await db.execute(select(User).where(User.id == user.get("id")))
    return result.scalars().first()




@router.post('/context', status_code=status.HTTP_200_OK)
async def upload_user_context(
    user: user_dependency,
    db: db_dependency,
    files: list[UploadFile] = File(...,description="Upload multiple context files")
):
    parsed_texts = []
    for file in files:
        # file.file is the file-like object
        try:
            content = parse_file(file.file, file.filename)
            parsed_texts.append(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing file {file.filename}: {str(e)}"
            )
        
    context_str = build_user_context(str(user.get("id")), parsed_texts)
    
    # Update user in DB
    result = await db.execute(select(User).where(User.id == user.get("id")))
    db_user = result.scalars().first()
    if db_user:
        if db_user.user_context is None:
            db_user.user_context = ""
        db_user.user_context += context_str
        await db.commit()
        await db.refresh(db_user)
        
    return {"message": "User context updated successfully", "files_processed": len(files)}


@router.delete('/context', status_code=status.HTTP_200_OK)
async def delete_user_context(user: user_dependency, db: db_dependency):
    result = await db.execute(select(User).where(User.id == user.get("id")))
    db_user = result.scalars().first()
    
    if db_user:
        db_user.user_context = None
        await db.commit()
        await db.refresh(db_user)
        
    return {"message": "User context deleted successfully"}



@router.get('/jobs', status_code=status.HTTP_200_OK, response_model=list[JobsResponse])
async def get_jobs(user:user_dependency, db:db_dependency):
    result = await db.execute(select(JobDescription).where(JobDescription.user_id == user.get("id")))
    jobs = result.scalars().all()
    response = []
    for job in jobs:
        response.append(JobsResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            jd_text=job.jd_text,
            generated_context=job.generated_context
        ))
    return response