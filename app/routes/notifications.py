from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.user_notification import UserNotification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


def _base_notifications_query(include_removed=False):
    q = (
        UserNotification.query
        .filter_by(user_id=current_user.id)
        .join(UserNotification.announcement)
    )
    if not include_removed:
        q = q.filter(UserNotification.is_removed.is_(False))
    return q


@notifications_bp.route("/")
@login_required
def index():
    view_filter = (request.args.get("filter") or "all").strip().lower()
    query = _base_notifications_query(include_removed=True)

    if view_filter == "pending":
        query = query.filter(
            UserNotification.is_read.is_(False),
            UserNotification.is_removed.is_(False),
        )
    elif view_filter == "read":
        query = query.filter(
            UserNotification.is_read.is_(True),
            UserNotification.is_removed.is_(False),
        )
    elif view_filter == "removed":
        query = query.filter(UserNotification.is_removed.is_(True))
    else:
        view_filter = "all"

    notifications = query.order_by(UserNotification.id.desc()).all()
    unread_count = _base_notifications_query().filter(UserNotification.is_read.is_(False)).count()

    return render_template(
        "auth/notifications.html",
        notifications=notifications,
        view_filter=view_filter,
        unread_count=unread_count,
    )


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    n = UserNotification.query.filter_by(
        id=notification_id,
        user_id=current_user.id,
        is_removed=False,
    ).first_or_404()

    if not n.is_read:
        n.is_read = True
        db.session.commit()

    return redirect(request.referrer or url_for("notifications.index"))


@notifications_bp.route("/<int:notification_id>/remove", methods=["POST"])
@login_required
def remove(notification_id):
    n = UserNotification.query.filter_by(
        id=notification_id,
        user_id=current_user.id,
        is_removed=False,
    ).first_or_404()

    n.is_removed = True
    db.session.commit()
    return redirect(request.referrer or url_for("notifications.index"))


@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def read_all():
    # update() cannot run on a joined query, so filter the table directly
    (
        UserNotification.query
        .filter_by(user_id=current_user.id, is_removed=False, is_read=False)
        .update({"is_read": True}, synchronize_session=False)
    )
    db.session.commit()
    return redirect(request.referrer or url_for("notifications.index"))
