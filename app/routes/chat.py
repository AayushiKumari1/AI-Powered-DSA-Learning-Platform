# from flask import Blueprint, flash, redirect, render_template, request, session, url_for
# from flask_login import current_user, login_required
# from flask_socketio import emit, join_room

# from app.extensions import db, socketio
# from app.models.chat_message import ChatMessage
# from app.models.community_message import CommunityMessage
# from app.models.user import User

# chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

# COMMUNITY_GROUPS = [
#     {
#         "key": "arrays",
#         "label": "Arrays",
#         "icon": "fa-layer-group",
#         "description": "Array tricks, traversal patterns, and subarray problems.",
#     },
#     {
#         "key": "strings",
#         "label": "Strings",
#         "icon": "fa-font",
#         "description": "String matching, parsing, and pattern-based problems.",
#     },
#     {
#         "key": "two-pointers",
#         "label": "Two Pointers",
#         "icon": "fa-arrows-left-right",
#         "description": "Fast and slow pointers, pair finding, and window-style thinking.",
#     },
#     {
#         "key": "linked-list",
#         "label": "Linked List",
#         "icon": "fa-link",
#         "description": "Pointer rewiring, cycle detection, and list manipulation.",
#     },
#     {
#         "key": "stack-queue",
#         "label": "Stack & Queue",
#         "icon": "fa-clone",
#         "description": "Monotonic stacks, queues, and order-sensitive problems.",
#     },
#     {
#         "key": "trees",
#         "label": "Trees",
#         "icon": "fa-tree",
#         "description": "Traversal, recursion, BSTs, and tree-based reasoning.",
#     },
#     {
#         "key": "dynamic-programming",
#         "label": "Dynamic Programming",
#         "icon": "fa-chart-line",
#         "description": "State transitions, memoization, and optimization patterns.",
#     },
# ]

# COMMUNITY_GROUP_BY_KEY = {group["key"]: group for group in COMMUNITY_GROUPS}
# DEFAULT_COMMUNITY_GROUP_KEY = COMMUNITY_GROUPS[0]["key"]


# def _community_group_key(raw_value):
#     value = (raw_value or "").strip()
#     return value if value in COMMUNITY_GROUP_BY_KEY else DEFAULT_COMMUNITY_GROUP_KEY


# def _community_group_payload(group_key):
#     group = COMMUNITY_GROUP_BY_KEY[_community_group_key(group_key)]
#     return {
#         "key": group["key"],
#         "label": group["label"],
#         "icon": group["icon"],
#         "description": group["description"],
#     }


# def _community_message_query(group_key):
#     return (
#         CommunityMessage.query.filter_by(group_key=group_key)
#         .order_by(CommunityMessage.created_at.asc(), CommunityMessage.id.asc())
#         .limit(300)
#         .all()
#     )


# def _community_redirect(group_key):
#     return redirect(url_for("chat.community", group=group_key))


# def _admin_logged_in():
#     return bool(session.get("admin_logged_in"))


# def _room_for_user(user_id):
#     return f"chat_user_{user_id}"


# def _can_access_user_chat(user_id):
#     if _admin_logged_in():
#         return True
#     return bool(current_user.is_authenticated and current_user.id == user_id)


# def _community_actor():
#     if _admin_logged_in():
#         return {
#             "name": "Admin",
#             "is_admin": True,
#             "user_id": current_user.id,  
#         }
#     if current_user.is_authenticated:
#         return {"name": current_user.username, "is_admin": False, "user_id": current_user.id}
#     return None


# @chat_bp.route("/admin")
# def admin_inbox():
#     if not _admin_logged_in():
#         return redirect(url_for("admin.admin_login"))

#     users = User.query.order_by(User.username.asc()).all()
#     selected_user_id = request.args.get("user_id", type=int)
#     valid_user_ids = {u.id for u in users}

#     if users and selected_user_id not in valid_user_ids:
#         selected_user_id = users[0].id

#     selected_user = User.query.get(selected_user_id) if selected_user_id else None
#     messages = []

#     if selected_user:
#         messages = (
#             ChatMessage.query.filter_by(user_id=selected_user.id)
#             .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
#             .all()
#         )

#     return render_template(
#         "chat/admin_chat.html",
#         users=users,
#         selected_user=selected_user,
#         messages=messages,
#     )


# @chat_bp.route("/admin/send/<int:user_id>", methods=["POST"])
# def admin_send(user_id):
#     if not _admin_logged_in():
#         return redirect(url_for("admin.admin_login"))

#     user = User.query.get_or_404(user_id)
#     text = (request.form.get("message") or "").strip()

#     if not text:
#         flash("Message cannot be empty.", "warning")
#         return redirect(url_for("chat.admin_inbox", user_id=user.id))

#     db.session.add(ChatMessage(user_id=user.id, sender_type="admin", message=text))
#     db.session.commit()
#     return redirect(url_for("chat.admin_inbox", user_id=user.id))


# @chat_bp.route("/user")
# @login_required
# def user_chat():
#     messages = (
#         ChatMessage.query.filter_by(user_id=current_user.id)
#         .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
#         .all()
#     )
#     return render_template("chat/user_chat.html", messages=messages)


# @chat_bp.route("/user/send", methods=["POST"])
# @login_required
# def user_send():
#     text = (request.form.get("message") or "").strip()

#     if not text:
#         flash("Message cannot be empty.", "warning")
#         return redirect(url_for("chat.user_chat"))

#     db.session.add(ChatMessage(user_id=current_user.id, sender_type="user", message=text))
#     db.session.commit()
#     return redirect(url_for("chat.user_chat"))


# @chat_bp.route("/community")
# def community():
#     actor = _community_actor()
#     if not actor:
#         return redirect(url_for("auth.login"))

#     group_key = _community_group_key(request.args.get("group"))
#     group = _community_group_payload(group_key)
#     messages = _community_message_query(group_key)

#     return render_template(
#         "chat/community.html",
#         messages=messages,
#         actor=actor,
#         community_groups=COMMUNITY_GROUPS,
#         current_group=group,
#     )


# @chat_bp.route("/community/send", methods=["POST"])
# def community_send():
#     actor = _community_actor()
#     if not actor:
#         return redirect(url_for("auth.login"))

#     text = (request.form.get("message") or "").strip()
#     group_key = _community_group_key(request.form.get("group_key") or request.args.get("group"))
#     if not text:
#         flash("Message cannot be empty.", "warning")
#         return _community_redirect(group_key)

#     msg = CommunityMessage(
#         group_key=group_key,
#         user_id=actor["user_id"],
#         sender_name=actor["name"],
#         is_admin=actor["is_admin"],
#         message=text,
#     )
#     db.session.add(msg)
#     db.session.commit()
#     return _community_redirect(group_key)


# @socketio.on("join_chat")
# def join_chat(data):
#     user_id = (data or {}).get("user_id")
#     try:
#         user_id = int(user_id)
#     except (TypeError, ValueError):
#         emit("chat_error", {"message": "Invalid chat room."})
#         return

#     if not _can_access_user_chat(user_id):
#         emit("chat_error", {"message": "Unauthorized chat access."})
#         return

#     join_room(_room_for_user(user_id))


# @socketio.on("send_chat_message")
# def send_chat_message(data):
#     user_id = (data or {}).get("user_id")
#     message_text = ((data or {}).get("message") or "").strip()

#     try:
#         user_id = int(user_id)
#     except (TypeError, ValueError):
#         emit("chat_error", {"message": "Invalid chat room."})
#         return

#     if not _can_access_user_chat(user_id):
#         emit("chat_error", {"message": "Unauthorized message action."})
#         return

#     if not message_text:
#         emit("chat_error", {"message": "Message cannot be empty."})
#         return

#     sender_type = "admin" if _admin_logged_in() else "user"

#     msg = ChatMessage(user_id=user_id, sender_type=sender_type, message=message_text)
#     db.session.add(msg)
#     db.session.commit()

#     emit(
#         "new_chat_message",
#         {
#             "id": msg.id,
#             "user_id": msg.user_id,
#             "sender_type": msg.sender_type,
#             "message": msg.message,
#             "created_at": msg.created_at.strftime("%d %b %I:%M %p"),
#         },
#         room=_room_for_user(user_id),
#     )


# @socketio.on("join_community")
# def join_community(data):
#     actor = _community_actor()
#     if not actor:
#         emit("chat_error", {"message": "Unauthorized community access."})
#         return
#     group_key = _community_group_key((data or {}).get("group_key"))
#     join_room(f"community_{group_key}")


# @socketio.on("send_community_message")
# def send_community_message(data):
#     actor = _community_actor()
#     if not actor:
#         emit("chat_error", {"message": "Unauthorized community action."})
#         return

#     message_text = ((data or {}).get("message") or "").strip()
#     group_key = _community_group_key((data or {}).get("group_key"))
#     if not message_text:
#         emit("chat_error", {"message": "Message cannot be empty."})
#         return

#     msg = CommunityMessage(
#         group_key=group_key,
#         user_id=actor["user_id"],
#         sender_name=actor["name"],
#         is_admin=actor["is_admin"],
#         message=message_text,
#     )
#     db.session.add(msg)
#     db.session.commit()

#     emit(
#         "new_community_message",
#         {
#             "id": msg.id,
#             "group_key": msg.group_key,
#             "user_id": msg.user_id,
#             "sender_name": msg.sender_name,
#             "is_admin": msg.is_admin,
#             "message": msg.message,
#             "created_at": msg.created_at.strftime("%d %b %I:%M %p"),
#         },
#         room=f"community_{group_key}",
#     )




# from flask import Blueprint, flash, redirect, render_template, request, session, url_for
# from flask_login import current_user, login_required
# from flask_socketio import emit, join_room

# from app.extensions import db, socketio
# from app.models.chat_message import ChatMessage
# from app.models.community_message import CommunityMessage
# from app.models.user import User

# chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

# COMMUNITY_GROUPS = [
#     {
#         "key": "arrays",
#         "label": "Arrays",
#         "icon": "fa-layer-group",
#         "description": "Array tricks, traversal patterns, and subarray problems.",
#     },
#     {
#         "key": "strings",
#         "label": "Strings",
#         "icon": "fa-font",
#         "description": "String matching, parsing, and pattern-based problems.",
#     },
#     {
#         "key": "two-pointers",
#         "label": "Two Pointers",
#         "icon": "fa-arrows-left-right",
#         "description": "Fast and slow pointers, pair finding, and window-style thinking.",
#     },
#     {
#         "key": "linked-list",
#         "label": "Linked List",
#         "icon": "fa-link",
#         "description": "Pointer rewiring, cycle detection, and list manipulation.",
#     },
#     {
#         "key": "stack-queue",
#         "label": "Stack & Queue",
#         "icon": "fa-clone",
#         "description": "Monotonic stacks, queues, and order-sensitive problems.",
#     },
#     {
#         "key": "trees",
#         "label": "Trees",
#         "icon": "fa-tree",
#         "description": "Traversal, recursion, BSTs, and tree-based reasoning.",
#     },
#     {
#         "key": "dynamic-programming",
#         "label": "Dynamic Programming",
#         "icon": "fa-chart-line",
#         "description": "State transitions, memoization, and optimization patterns.",
#     },
# ]

# COMMUNITY_GROUP_BY_KEY = {group["key"]: group for group in COMMUNITY_GROUPS}
# DEFAULT_COMMUNITY_GROUP_KEY = COMMUNITY_GROUPS[0]["key"]


# def _community_group_key(raw_value):
#     value = (raw_value or "").strip()
#     return value if value in COMMUNITY_GROUP_BY_KEY else DEFAULT_COMMUNITY_GROUP_KEY


# def _community_group_payload(group_key):
#     group = COMMUNITY_GROUP_BY_KEY[_community_group_key(group_key)]
#     return {
#         "key": group["key"],
#         "label": group["label"],
#         "icon": group["icon"],
#         "description": group["description"],
#     }


# def _community_message_query(group_key):
#     return (
#         CommunityMessage.query.filter_by(group_key=group_key)
#         .order_by(CommunityMessage.created_at.asc(), CommunityMessage.id.asc())
#         .limit(300)
#         .all()
#     )


# def _community_redirect(group_key):
#     return redirect(url_for("chat.community", group=group_key))


# def _admin_logged_in():
#     return bool(session.get("admin_logged_in"))


# def _room_for_user(user_id):
#     return f"chat_user_{user_id}"


# def _can_access_user_chat(user_id):
#     if _admin_logged_in():
#         return True
#     return bool(current_user.is_authenticated and current_user.id == user_id)


# def _community_actor():
#     if _admin_logged_in():
#         return {"name": "Admin", "is_admin": True, "user_id": None}
#     if current_user.is_authenticated:
#         return {"name": current_user.username, "is_admin": False, "user_id": current_user.id}
#     return None


# @chat_bp.route("/admin")
# def admin_inbox():
#     if not _admin_logged_in():
#         return redirect(url_for("admin.admin_login"))

#     users = User.query.order_by(User.username.asc()).all()
#     selected_user_id = request.args.get("user_id", type=int)
#     valid_user_ids = {u.id for u in users}

#     if users and selected_user_id not in valid_user_ids:
#         selected_user_id = users[0].id

#     selected_user = User.query.get(selected_user_id) if selected_user_id else None
#     messages = []

#     if selected_user:
#         messages = (
#             ChatMessage.query.filter_by(user_id=selected_user.id)
#             .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
#             .all()
#         )

#     return render_template(
#         "chat/admin_chat.html",
#         users=users,
#         selected_user=selected_user,
#         messages=messages,
#     )


# @chat_bp.route("/admin/send/<int:user_id>", methods=["POST"])
# def admin_send(user_id):
#     if not _admin_logged_in():
#         return redirect(url_for("admin.admin_login"))

#     user = User.query.get_or_404(user_id)
#     text = (request.form.get("message") or "").strip()

#     if not text:
#         flash("Message cannot be empty.", "warning")
#         return redirect(url_for("chat.admin_inbox", user_id=user.id))

#     db.session.add(ChatMessage(user_id=user.id, sender_type="admin", message=text))
#     db.session.commit()
#     return redirect(url_for("chat.admin_inbox", user_id=user.id))


# @chat_bp.route("/user")
# @login_required
# def user_chat():
#     messages = (
#         ChatMessage.query.filter_by(user_id=current_user.id)
#         .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
#         .all()
#     )
#     return render_template("chat/user_chat.html", messages=messages)


# @chat_bp.route("/user/send", methods=["POST"])
# @login_required
# def user_send():
#     text = (request.form.get("message") or "").strip()

#     if not text:
#         flash("Message cannot be empty.", "warning")
#         return redirect(url_for("chat.user_chat"))

#     db.session.add(ChatMessage(user_id=current_user.id, sender_type="user", message=text))
#     db.session.commit()
#     return redirect(url_for("chat.user_chat"))


# @chat_bp.route("/community")
# def community():
#     actor = _community_actor()
#     if not actor:
#         return redirect(url_for("auth.login"))

#     group_key = _community_group_key(request.args.get("group"))
#     group = _community_group_payload(group_key)
#     messages = _community_message_query(group_key)

#     return render_template(
#         "chat/community.html",
#         messages=messages,
#         actor=actor,
#         community_groups=COMMUNITY_GROUPS,
#         current_group=group,
#     )


# @chat_bp.route("/community/send", methods=["POST"])
# def community_send():
#     actor = _community_actor()
#     if not actor:
#         return redirect(url_for("auth.login"))

#     text = (request.form.get("message") or "").strip()
#     group_key = _community_group_key(request.form.get("group_key") or request.args.get("group"))
#     if not text:
#         flash("Message cannot be empty.", "warning")
#         return _community_redirect(group_key)

#     msg = CommunityMessage(
#         group_key=group_key,
#         user_id=actor["user_id"],
#         sender_name=actor["name"],
#         is_admin=actor["is_admin"],
#         message=text,
#     )
#     db.session.add(msg)
#     db.session.commit()
#     return _community_redirect(group_key)


# @socketio.on("join_chat")
# def join_chat(data):
#     user_id = (data or {}).get("user_id")
#     try:
#         user_id = int(user_id)
#     except (TypeError, ValueError):
#         emit("chat_error", {"message": "Invalid chat room."})
#         return

#     if not _can_access_user_chat(user_id):
#         emit("chat_error", {"message": "Unauthorized chat access."})
#         return

#     join_room(_room_for_user(user_id))


# @socketio.on("send_chat_message")
# def send_chat_message(data):
#     user_id = (data or {}).get("user_id")
#     message_text = ((data or {}).get("message") or "").strip()

#     try:
#         user_id = int(user_id)
#     except (TypeError, ValueError):
#         emit("chat_error", {"message": "Invalid chat room."})
#         return

#     if not _can_access_user_chat(user_id):
#         emit("chat_error", {"message": "Unauthorized message action."})
#         return

#     if not message_text:
#         emit("chat_error", {"message": "Message cannot be empty."})
#         return

#     sender_type = "admin" if _admin_logged_in() else "user"

#     msg = ChatMessage(user_id=user_id, sender_type=sender_type, message=message_text)
#     db.session.add(msg)
#     db.session.commit()

#     emit(
#         "new_chat_message",
#         {
#             "id": msg.id,
#             "user_id": msg.user_id,
#             "sender_type": msg.sender_type,
#             "message": msg.message,
#             "created_at": msg.created_at.strftime("%d %b %I:%M %p"),
#         },
#         room=_room_for_user(user_id),
#     )


# @socketio.on("join_community")
# def join_community(data):
#     actor = _community_actor()
#     if not actor:
#         emit("chat_error", {"message": "Unauthorized community access."})
#         return
#     group_key = _community_group_key((data or {}).get("group_key"))
#     join_room(f"community_{group_key}")


# @socketio.on("send_community_message")
# def send_community_message(data):
#     actor = _community_actor()
#     if not actor:
#         emit("chat_error", {"message": "Unauthorized community action."})
#         return

#     message_text = ((data or {}).get("message") or "").strip()
#     group_key = _community_group_key((data or {}).get("group_key"))
#     if not message_text:
#         emit("chat_error", {"message": "Message cannot be empty."})
#         return

#     msg = CommunityMessage(
#         group_key=group_key,
#         user_id=actor["user_id"],
#         sender_name=actor["name"],
#         is_admin=actor["is_admin"],
#         message=message_text,
#     )
#     db.session.add(msg)
#     db.session.commit()

#     emit(
#         "new_community_message",
#         {
#             "id": msg.id,
#             "group_key": msg.group_key,
#             "user_id": msg.user_id,
#             "sender_name": msg.sender_name,
#             "is_admin": msg.is_admin,
#             "message": msg.message,
#             "created_at": msg.created_at.strftime("%d %b %I:%M %p"),
#         },
#         room=f"community_{group_key}",
#     )






from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
)
from flask_login import current_user, login_required
from flask_socketio import emit, join_room

from app.extensions import db, socketio
from app.models.chat_message import ChatMessage
from app.models.community_message import CommunityMessage
from app.models.user import User
from app.utils.chatbot_service import ask_chatbot

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

# =====================================================
# COMMUNITY GROUPS
# =====================================================

COMMUNITY_GROUPS = [
    {
        "key": "arrays",
        "label": "Arrays",
        "icon": "fa-layer-group",
        "description": "Array tricks, traversal patterns, and subarray problems.",
    },
    {
        "key": "strings",
        "label": "Strings",
        "icon": "fa-font",
        "description": "String matching, parsing, and pattern-based problems.",
    },
    {
        "key": "two-pointers",
        "label": "Two Pointers",
        "icon": "fa-arrows-left-right",
        "description": "Fast and slow pointers, pair finding, and window-style thinking.",
    },
    {
        "key": "linked-list",
        "label": "Linked List",
        "icon": "fa-link",
        "description": "Pointer rewiring, cycle detection, and list manipulation.",
    },
    {
        "key": "stack-queue",
        "label": "Stack & Queue",
        "icon": "fa-clone",
        "description": "Monotonic stacks, queues, and order-sensitive problems.",
    },
    {
        "key": "trees",
        "label": "Trees",
        "icon": "fa-tree",
        "description": "Traversal, recursion, BSTs, and tree-based reasoning.",
    },
    {
        "key": "dynamic-programming",
        "label": "Dynamic Programming",
        "icon": "fa-chart-line",
        "description": "State transitions, memoization, and optimization patterns.",
    },
]

COMMUNITY_GROUP_BY_KEY = {group["key"]: group for group in COMMUNITY_GROUPS}
DEFAULT_COMMUNITY_GROUP_KEY = COMMUNITY_GROUPS[0]["key"]

# =====================================================
# HELPERS
# =====================================================

def _community_group_key(raw_value):
    value = (raw_value or "").strip()
    return value if value in COMMUNITY_GROUP_BY_KEY else DEFAULT_COMMUNITY_GROUP_KEY


def _community_group_payload(group_key):
    group = COMMUNITY_GROUP_BY_KEY[_community_group_key(group_key)]
    return {
        "key": group["key"],
        "label": group["label"],
        "icon": group["icon"],
        "description": group["description"],
    }


def _community_message_query(group_key):
    return (
        CommunityMessage.query.filter_by(group_key=group_key)
        .order_by(CommunityMessage.created_at.asc(), CommunityMessage.id.asc())
        .limit(300)
        .all()
    )


def _community_redirect(group_key):
    return redirect(url_for("chat.community", group=group_key))


def _admin_logged_in():
    return bool(session.get("admin_logged_in"))


def _room_for_user(user_id):
    return f"chat_user_{user_id}"


def _can_access_user_chat(user_id):
    if _admin_logged_in():
        return True
    return bool(current_user.is_authenticated and current_user.id == user_id)


def _community_actor():
    if _admin_logged_in():
        return {"name": "Admin", "is_admin": True, "user_id": None}

    if current_user.is_authenticated:
        return {
            "name": current_user.username,
            "is_admin": False,
            "user_id": current_user.id,
        }

    return None


# =====================================================
# ADMIN CHAT
# =====================================================

@chat_bp.route("/admin")
def admin_inbox():
    if not _admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    users = User.query.order_by(User.username.asc()).all()

    selected_user_id = request.args.get("user_id", type=int)
    valid_user_ids = {u.id for u in users}

    if users and selected_user_id not in valid_user_ids:
        selected_user_id = users[0].id

    selected_user = User.query.get(selected_user_id) if selected_user_id else None
    messages = []

    if selected_user:
        messages = (
            ChatMessage.query.filter_by(user_id=selected_user.id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            .all()
        )

    return render_template(
        "chat/admin_chat.html",
        users=users,
        selected_user=selected_user,
        messages=messages,
    )


@chat_bp.route("/admin/send/<int:user_id>", methods=["POST"])
def admin_send(user_id):
    if not _admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    user = User.query.get_or_404(user_id)
    text = (request.form.get("message") or "").strip()

    if not text:
        flash("Message cannot be empty.", "warning")
        return redirect(url_for("chat.admin_inbox", user_id=user.id))

    db.session.add(
        ChatMessage(
            user_id=user.id,
            sender_type="admin",
            message=text
        )
    )
    db.session.commit()

    return redirect(url_for("chat.admin_inbox", user_id=user.id))


# =====================================================
# USER CHAT
# =====================================================

@chat_bp.route("/user")
@login_required
def user_chat():
    messages = (
        ChatMessage.query.filter_by(user_id=current_user.id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )

    return render_template("chat/user_chat.html", messages=messages)


@chat_bp.route("/user/send", methods=["POST"])
@login_required
def user_send():
    text = (request.form.get("message") or "").strip()

    if not text:
        flash("Message cannot be empty.", "warning")
        return redirect(url_for("chat.user_chat"))

    db.session.add(
        ChatMessage(
            user_id=current_user.id,
            sender_type="user",
            message=text
        )
    )
    db.session.commit()

    return redirect(url_for("chat.user_chat"))


# =====================================================
# COMMUNITY CHAT
# =====================================================

@chat_bp.route("/community")
def community():
    actor = _community_actor()

    if not actor:
        return redirect(url_for("auth.login"))

    group_key = _community_group_key(request.args.get("group"))
    group = _community_group_payload(group_key)
    messages = _community_message_query(group_key)

    return render_template(
        "chat/community.html",
        messages=messages,
        actor=actor,
        community_groups=COMMUNITY_GROUPS,
        current_group=group,
    )


@chat_bp.route("/community/send", methods=["POST"])
def community_send():
    actor = _community_actor()

    if not actor:
        return redirect(url_for("auth.login"))

    text = (request.form.get("message") or "").strip()
    group_key = _community_group_key(
        request.form.get("group_key") or request.args.get("group")
    )

    if not text:
        flash("Message cannot be empty.", "warning")
        return _community_redirect(group_key)

    msg = CommunityMessage(
        group_key=group_key,
        user_id=actor["user_id"],
        sender_name=actor["name"],
        is_admin=actor["is_admin"],
        message=text,
    )

    db.session.add(msg)
    db.session.commit()

    return _community_redirect(group_key)


# =====================================================
# AI CHATBOT ROUTE
# =====================================================

# @chat_bp.route("/chatbot", methods=["POST"])
# @login_required
# def chatbot():

#     data = request.get_json()

#     msg = (data.get("message") or "").strip()

#     if not msg:
#         return jsonify({
#             "reply": "Please type a message."
#         })

#     try:
#         reply = ask_chatbot(current_user.id, msg)

#     except Exception:
#         reply = "AI Mentor is temporarily unavailable."

#     return jsonify({
#         "reply": reply
#     })

@chat_bp.route("/chatbot", methods=["POST"])
@login_required
def chatbot():
    data   = request.get_json(silent=True) or {}
    msg    = (data.get("message") or "").strip()
    action = (data.get("action")  or "").strip()   # optional: "reset"
 
    # Handle reset action (called when user clicks "Clear chat")
    if action == "reset":
        from app.utils.chatbot_service import reset_chat
        reply = reset_chat(current_user.id)
        return jsonify({"reply": reply})
 
    if not msg:
        return jsonify({"reply": "Please type a message."})
 
    try:
        reply = ask_chatbot(current_user.id, msg)
    except Exception as exc:
        print(f"[/chatbot route ERROR] {exc}")
        reply = "⚠️ AI Mentor is temporarily unavailable. Please try again."
 
    return jsonify({"reply": reply})


# =====================================================
# SOCKET USER CHAT
# =====================================================

@socketio.on("join_chat")
def join_chat(data):
    user_id = (data or {}).get("user_id")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        emit("chat_error", {"message": "Invalid chat room."})
        return

    if not _can_access_user_chat(user_id):
        emit("chat_error", {"message": "Unauthorized chat access."})
        return

    join_room(_room_for_user(user_id))


@socketio.on("send_chat_message")
def send_chat_message(data):
    user_id = (data or {}).get("user_id")
    message_text = ((data or {}).get("message") or "").strip()

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        emit("chat_error", {"message": "Invalid chat room."})
        return

    if not _can_access_user_chat(user_id):
        emit("chat_error", {"message": "Unauthorized message action."})
        return

    if not message_text:
        emit("chat_error", {"message": "Message cannot be empty."})
        return

    sender_type = "admin" if _admin_logged_in() else "user"

    msg = ChatMessage(
        user_id=user_id,
        sender_type=sender_type,
        message=message_text
    )

    db.session.add(msg)
    db.session.commit()

    emit(
        "new_chat_message",
        {
            "id": msg.id,
            "user_id": msg.user_id,
            "sender_type": msg.sender_type,
            "message": msg.message,
            "created_at": msg.created_at.strftime("%d %b %I:%M %p"),
        },
        room=_room_for_user(user_id),
    )


# =====================================================
# SOCKET COMMUNITY CHAT
# =====================================================

@socketio.on("join_community")
def join_community(data):
    actor = _community_actor()

    if not actor:
        emit("chat_error", {"message": "Unauthorized community access."})
        return

    group_key = _community_group_key((data or {}).get("group_key"))

    join_room(f"community_{group_key}")


@socketio.on("send_community_message")
def send_community_message(data):
    actor = _community_actor()

    if not actor:
        emit("chat_error", {"message": "Unauthorized community action."})
        return

    message_text = ((data or {}).get("message") or "").strip()
    group_key = _community_group_key((data or {}).get("group_key"))

    if not message_text:
        emit("chat_error", {"message": "Message cannot be empty."})
        return

    msg = CommunityMessage(
        group_key=group_key,
        user_id=actor["user_id"],
        sender_name=actor["name"],
        is_admin=actor["is_admin"],
        message=message_text,
    )

    db.session.add(msg)
    db.session.commit()

    emit(
        "new_community_message",
        {
            "id": msg.id,
            "group_key": msg.group_key,
            "user_id": msg.user_id,
            "sender_name": msg.sender_name,
            "is_admin": msg.is_admin,
            "message": msg.message,
            "created_at": msg.created_at.strftime("%d %b %I:%M %p"),
        },
        room=f"community_{group_key}",
    )