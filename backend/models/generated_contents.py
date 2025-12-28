import uuid
import enum
from sqlalchemy import String, Text, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from backend.core.database import Base

class ContentTypes(str, enum.Enum):
    COLD_EMAIL = "cold_email"
    LINKEDIN_MESSAGE = "linkedin_message"
    COVER_LETTER = "cover_letter"

class GeneratedContents(Base):
    __tablename__ = "generated_contents"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jd_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    
    content_type: Mapped[ContentTypes] = mapped_column(Enum(ContentTypes, name="content_type_enum", values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    to_address: Mapped[str] = mapped_column(Text, nullable=True)
    subject: Mapped[str] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    model_used: Mapped[str] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )