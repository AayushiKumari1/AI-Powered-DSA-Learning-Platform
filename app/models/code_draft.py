# app/models/code_draft.py
from app.extensions import db
from datetime import datetime

class CodeDraft(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("coding_questions.id"), nullable=False)

    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)