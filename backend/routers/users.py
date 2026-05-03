from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
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
from backend.utils.github_background import run_github_scrape_background


router = APIRouter(prefix="/users", tags=["users"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: Usercreate,
    background_tasks: BackgroundTasks,
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
        password_hash=hashed_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        linkedin=payload.linkedin,
        github=payload.github,
        portfolio=payload.portfolio
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # ── Fire GitHub README scrape as a background task ────────────────────
    # If the user provided a GitHub URL, kick off the background scraper.
    # The task runs asynchronously after the response is sent, so registration
    # returns instantly and the context builds silently in the background.
    if payload.github and payload.github.strip():
        background_tasks.add_task(
            run_github_scrape_background,
            user_id=str(new_user.id),
            github_url=payload.github.strip(),
        )


@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_user(user: user_dependency, db: db_dependency):
    result = await db.execute(select(User).where(User.id == user.get("id")))
    return result.scalars().first()


@router.get('/github_context_status', status_code=status.HTTP_200_OK)
async def github_context_status(user: user_dependency, db: db_dependency):
    """
    Returns whether GitHub project context has been scraped and stored.
    The frontend polls this endpoint after registration to show a status banner.
    """
    result = await db.execute(select(User).where(User.id == user.get("id")))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    has_github_context = (
        db_user.user_context is not None
        and "## GitHub Projects (auto-summarised)" in db_user.user_context
    )
    repo_count = 0
    if has_github_context:
        repo_count = db_user.user_context.count("### Project:")

    return {
        "has_github": bool(db_user.github),
        "context_ready": has_github_context,
        "repos_summarised": repo_count,
        "github_url": db_user.github or "",
    }


@router.post('/context', status_code=status.HTTP_200_OK)
async def upload_user_context(
    user: user_dependency,
    db: db_dependency,
    files: list[UploadFile] = File(..., description="Upload multiple context files")
):
    parsed_texts = []
    for file in files:
        try:
            content = parse_file(file.file, file.filename)
            parsed_texts.append(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing file {file.filename}: {str(e)}"
            )

    context_str = build_user_context(str(user.get("id")), parsed_texts)

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
async def get_jobs(user: user_dependency, db: db_dependency):
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