from datetime import datetime

from app.extensions import db


class FlashNote(db.Model):
    __tablename__ = "flash_notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    subject = db.Column(db.String(120), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship("User", backref=db.backref("flash_notes", lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<FlashNote {self.id} user={self.user_id} title={self.title}>"
