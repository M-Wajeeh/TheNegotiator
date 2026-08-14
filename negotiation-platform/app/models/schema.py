import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Negotiation(Base):
    __tablename__ = "negotiations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String, default="intake")
    state_payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Business(Base):
    __tablename__ = "businesses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"))
    name = Column(String)
    phone_number = Column(String)
    details = Column(JSON, default=dict)

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"))
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"))
    amount = Column(String)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class CallRecord(Base):
    __tablename__ = "calls"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"))
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"))
    status = Column(String)
    outcome = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"))
    report_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
