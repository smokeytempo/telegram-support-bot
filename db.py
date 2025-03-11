from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
from config import DATABASE_URL
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    role = Column(String, nullable=False, default="user")
    language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tickets = relationship("Ticket", back_populates="user")
    claimed_tickets = relationship("Ticket", back_populates="claimer", foreign_keys='Ticket.claimed_by')
class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="unclaimed")
    claimed_by = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    content = Column(Text, nullable=False)
    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket")
    rating = relationship("Rating", uselist=False, back_populates="ticket")
class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    chat_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ticket = relationship("Ticket", back_populates="messages")
class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ticket = relationship("Ticket", back_populates="rating")
def init_db():
    Base.metadata.create_all(bind=engine)
