from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, UploadFile, File
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated
from backend.core.database import get_db
from backend.models.user import User
from backend.models.job_descriptions import JobDescription
from backend.models.generated_contents import GeneratedContents
from backend.models.generated_contents import ContentTypes
from backend.schemas.user import Usercreate, UserRead
from backend.core.security import get_current_user
from backend.graph.main import draft_graph, generate_graph
from backend.utils.email_sender import send_email
from fastapi.concurrency import run_in_threadpool

router = APIRouter(prefix="/generation", tags=["generation"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.post('/context', status_code=status.HTTP_200_OK)
async def generate_context(
    user: user_dependency,
    db: db_dependency,
    job_description: str = Form(..., description="A detailed description of the job role."),
):
    
    result = await db.execute(select(User).where(User.id == user.get("id")))
    db_user = result.scalars().first()
    if db_user.user_context is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User context not found. Please create a user context first.")
    state = {
        "user_context": db_user.user_context,
        "job_description": job_description,
    }
    
    # Generate a random thread_id for this request since we are using a checkpointer
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        result_state = await generate_graph.ainvoke(state, config=config)
    except Exception as e:
        print(f"Error generating context: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate context")
    context = result_state.get('context', {})
    
    # Handle context whether it's a string (from LLM raw output) or dict (if pre-parsed)
    context_dict = {}
    if isinstance(context, str):
        try:
            import json
            context_dict = json.loads(context)
        except json.JSONDecodeError:
            # Fallback if it's just a string but not JSON
            context_dict = {"raw_content": context}
    elif isinstance(context, dict):
        context_dict = context
        
    if context_dict:
        try:
            import json
            # Ensure we serialize it back to string for the DB 'generated_context' field
            job_description = JobDescription(
                title=context_dict.get('job_title'),
                company=context_dict.get('company_name'),
                jd_text=job_description,
                user_id=user.get("id"),
                generated_context=json.dumps(context_dict)
            )
            db.add(job_description)
            await db.commit()
        except Exception as e:
            print(f"Error saving job description: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save job description")
        
    return context_dict


@router.post('/draft_context', status_code=status.HTTP_200_OK)
async def draft_context(
    jd_id: uuid.UUID,
    type: str,
    user: user_dependency,
    db: db_dependency,
    feedback: str | None = Form(None, description="Feedback for the generated content"),
):
    if type not in ["email", "linkedin_message", "cover_letter"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content type")

    type_mapping = {
        "email": ContentTypes.COLD_EMAIL,
        "linkedin_message": ContentTypes.LINKEDIN_MESSAGE,
        "cover_letter": ContentTypes.COVER_LETTER
    }
    
    # Fetch job description and verify ownership
    result = await db.execute(select(JobDescription).where(JobDescription.id == jd_id, JobDescription.user_id == user.get("id")))
    job_description = result.scalars().first()
    
    if not job_description:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        
    if not job_description.generated_context:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No generated context found for this job description. Please generate context first.")
    
    user_result = await db.execute(select(User).where(User.id == user.get("id")))
    db_user = user_result.scalars().first()
    user_details = {
        "name": f"{db_user.first_name} {db_user.last_name}",
        "email": db_user.email,
        "phone": db_user.phone,
        "linkedin_url": db_user.linkedin,
        "github_url": db_user.github,
      
    }
    
    # Prepare state with existing context and explicit start point
    state = {
        "context": job_description.generated_context, # Reuse stored context
        "type": type,
        "user_details": user_details,
        "feedback": feedback
    }

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Invoke graph - logic in graph.py will route to 'start_at' node
    try:
        result_state = await draft_graph.ainvoke(state, config=config)
    except Exception as e:
        print(f"Error drafting context: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to draft context")
    
    # Save Generated Content
    try:
        import json
        context_dict = json.loads(job_description.generated_context)
        
        db_content_type = type_mapping.get(type)
        if not db_content_type:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content type")

        generated_data = result_state.get(type, {})
        
        generated_content = GeneratedContents(
            jd_id=job_description.id,
            user_id=user.get("id"),
            content_type=db_content_type,
            to_address=result_state.get(type).get('recipient'),
            subject=result_state.get(type).get('subject'),
            body=result_state.get(type).get('body'),
            model_used=result_state.get('model_used'),
            prompt_version=result_state.get('prompt_version')
        )
            
        db.add(generated_content)
        await db.commit()
    except Exception as e:
        print(f"Error saving generated content: {e}")
        # We still return the response even if saving fails, or we could raise. 
        # For now, let's proceed to return response.
        
    return result_state.get(type)


@router.post('/send_email', status_code=status.HTTP_200_OK)
async def send_email_endpoint(
    user: user_dependency,
    db: db_dependency,
    to_address: str = Form(..., description="Recipient email address"),
    subject: str = Form(..., description="Email subject"),
    body: str = Form(..., description="Email body"),
    files: list[UploadFile] = File(None, description="Upload multiple context files")
):
    
    # Process attachments
    attachment_data = []
    if files:
        for file in files:
            content = await file.read()
            attachment_data.append({
                'filename': file.filename,
                'content': content,
                'content_type': file.content_type
            })

    try:
        # Run synchronous send_email in threadpool to avoid blocking event loop
        result = await run_in_threadpool(
            send_email,
            recipient=to_address,
            subject=subject,
            body=body,
            attachments=attachment_data
        )
        
        if result.startswith("Error") or result.startswith("Failed"):
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result)
             
        return {"message": result}

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email: {str(e)}")
    
    

@router.get('/generated_contents', status_code=status.HTTP_200_OK)
async def get_all_generated_contents(user:user_dependency, db:db_dependency):
    stmt = (
        select(GeneratedContents, JobDescription.title, JobDescription.company)
        .join(JobDescription, GeneratedContents.jd_id == JobDescription.id)
        .where(GeneratedContents.user_id == user.get("id"))
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    response = []
    for content, job_title, company_name in rows:
        content_dict = {c.name: getattr(content, c.name) for c in content.__table__.columns}
        content_dict['job_title'] = job_title
        content_dict['company_name'] = company_name
        response.append(content_dict)
        
    return response

    
    
@router.get('/generated_contents/{content_type}', status_code=status.HTTP_200_OK)
async def get_generated_contents_by_type(user:user_dependency, db:db_dependency, content_type: str):
    stmt = (
        select(GeneratedContents, JobDescription.title, JobDescription.company)
        .join(JobDescription, GeneratedContents.jd_id == JobDescription.id)
        .where(
            GeneratedContents.user_id == user.get("id"),
            GeneratedContents.content_type == content_type
        )
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    response = []
    for content, job_title, company_name in rows:
        content_dict = {c.name: getattr(content, c.name) for c in content.__table__.columns}
        content_dict['job_title'] = job_title
        content_dict['company_name'] = company_name
        response.append(content_dict)
        
    return response
    
@router.get('/generated_contents/job/{jd_id}', status_code=status.HTTP_200_OK)
async def get_generated_contents_by_job(user:user_dependency, db:db_dependency, jd_id: uuid.UUID):
    stmt = (
        select(GeneratedContents, JobDescription.title, JobDescription.company)
        .join(JobDescription, GeneratedContents.jd_id == JobDescription.id)
        .where(
            GeneratedContents.user_id == user.get("id"),
            GeneratedContents.jd_id == jd_id
        )
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    response = []
    for content, job_title, company_name in rows:
        content_dict = {c.name: getattr(content, c.name) for c in content.__table__.columns}
        content_dict['job_title'] = job_title
        content_dict['company_name'] = company_name
        response.append(content_dict)
        
    return response