from celery import Celery
from config import REDIS_URL
celery_app = Celery('tasks', broker=REDIS_URL)
@celery_app.task
def escalate_ticket(ticket_id):
    from db import SessionLocal, Ticket
    session = SessionLocal()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket and ticket.status == "unclaimed":
            ticket.status = "escalated"
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
