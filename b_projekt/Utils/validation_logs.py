from sqlalchemy.orm import Session
from Models.ValidationLog import ValidationLog

def fetch_validation_logs(session: Session):
    return session.query(ValidationLog).all()

