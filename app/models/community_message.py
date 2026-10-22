from datetime import datetime

from app.extensions import db


class CommunityMessage(db.Model):
    __tablename__ = "community_messages"

    id = db.Column(db.Integer, primary_key=True)
    group_key = db.Column(db.String(60), nullable=False, default="arrays", index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    sender_name = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", backref=db.backref("community_messages", lazy=True))

    def __repr__(self):
        role = "admin" if self.is_admin else "user"
        return f"<CommunityMessage {self.id} group={self.group_key} sender={self.sender_name} role={role}>"
