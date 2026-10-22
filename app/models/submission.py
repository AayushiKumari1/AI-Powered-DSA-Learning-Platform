from app.extensions import db
from datetime import datetime


class Submission(db.Model):
    __tablename__ = "submission"   # 👈 IMPORTANT (explicit table name)

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("coding_questions.id"), nullable=False)

    code = db.Column(db.Text)
    language = db.Column(db.String(20))

    status = db.Column(db.String(20))
    passed = db.Column(db.Integer)
    total = db.Column(db.Integer)

    runtime = db.Column(db.Float)
    solve_time = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ FIXED