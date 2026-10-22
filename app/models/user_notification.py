from datetime import datetime

from app.extensions import db


class UserNotification(db.Model):
    __tablename__ = "user_notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    announcement_id = db.Column(
        db.Integer,
        db.ForeignKey("announcements.id"),
        nullable=False,
        index=True,
    )
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_removed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", backref=db.backref("notifications", lazy=True))
    announcement = db.relationship("Announcement", backref=db.backref("notifications", lazy=True))

    def __repr__(self):
        return f"<UserNotification {self.id} user={self.user_id} ann={self.announcement_id}>"
