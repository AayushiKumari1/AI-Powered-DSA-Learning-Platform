from datetime import datetime

from app.extensions import db


class CodingQuestionProgress(db.Model):
    __tablename__ = "coding_question_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("coding_questions.id"),
        nullable=False,
        index=True,
    )

    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    xp_awarded = db.Column(db.Boolean, default=False, nullable=False)
    solved_at = db.Column(db.DateTime)
    last_attempt_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "question_id", name="uq_user_question_progress"),
    )
