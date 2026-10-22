from datetime import datetime

from app.extensions import db


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    sender_type = db.Column(db.String(10), nullable=False)  # "admin" or "user"
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", backref=db.backref("chat_messages", lazy=True))

    def __repr__(self):
        return f"<ChatMessage {self.id} user={self.user_id} sender={self.sender_type}>"
