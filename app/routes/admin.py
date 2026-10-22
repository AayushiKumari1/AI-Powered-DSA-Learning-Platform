# High Priority
 
# from flask import Blueprint, render_template, request, redirect, url_for, session, flash
# from app.extensions import db
# from app.models.topic import Topic
# from app.models.user import User
# from app.models.topic import Topic
# from app.models.coding_question import CodingQuestion
# from app.models.badge import Badge, UserBadge
# from app.models.coding_test import CodingTest   # adjust import if needed
# from app.models.announcement import Announcement
# from app.models.user_notification import UserNotification
# from sqlalchemy import func
# import json
# import csv 
# from io import TextIOWrapper
# from app.routes.admin_coding import admin_logged_in 

# admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# XP_MAP = {
#     "easy": 10,
#     "medium": 20,
#     "hard": 30
# }

# # Hardcoded admin credentials
# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "admin123"


# # ---------------------------
# # Admin Login
# # ---------------------------
# @admin_bp.route("/login", methods=["GET", "POST"])
# def admin_login():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session["admin_logged_in"] = True
#             flash("Welcome, Admin!", "success")
#             return redirect(url_for("admin.dashboard"))
#         else:
#             flash("Invalid credentials", "danger")
#             return redirect(url_for("admin.admin_login"))

#     return render_template("admin/login.html")


# # ---------------------------
# # Admin Dashboard
# # ---------------------------
# @admin_bp.route("/dashboard")
# def dashboard():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     # 🔢 TOTAL COUNTS
#     total_users = User.query.count()
#     total_topics = Topic.query.count()
#     total_coding_questions = CodingQuestion.query.count()
#     total_coding_tests = CodingTest.query.count()
#     total_badges = Badge.query.count()

#     # 🏅 BADGE → USER COUNT
#     badge_stats = (
#         db.session.query(
#             Badge.name,
#             Badge.icon,
#             Badge.color,
#             func.count(UserBadge.user_id).label("user_count")
#         )
#         .outerjoin(UserBadge, Badge.id == UserBadge.badge_id)
#         .group_by(Badge.id)
#         .order_by(Badge.xp_threshold.asc())
#         .all()
#     )

#     return render_template(
#         "admin/dashboard.html",
#         total_users=total_users,
#         total_topics=total_topics,
#         total_coding_questions=total_coding_questions,
#         total_coding_tests=total_coding_tests,
#         total_badges=total_badges,
#         badge_stats=badge_stats
#     )

# # ---------------------------
# # Add Topic
# # ---------------------------
# @admin_bp.route("/add_topic", methods=["GET", "POST"])
# def add_topic():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     if request.method == "POST":
#         title = request.form.get("title")
#         intro = request.form.get("intro")
#         example = request.form.get("example")
#         code = request.form.get("code")
#         details = request.form.get("details")
#         tags = request.form.get("tags")

#         # ✅ Combine all sections into one HTML-formatted description
#         description = f"""
#         <section>
#             <h4>Introduction</h4>
#             <p>{intro}</p>
#         </section>
#         <section>
#             <h4>Example / Explanation</h4>
#             <p>{example}</p>
#         </section>
#         <section>
#             <h4>Code Example</h4>
#             <pre><code>{code}</code></pre>
#         </section>
#         <section>
#             <h4>Additional Details</h4>
#             <p>{details}</p>
#         </section>
#         """

#         new_topic = Topic(title=title, description=description, tags=tags)
#         db.session.add(new_topic)
#         db.session.commit()

#         flash("Topic added successfully!", "success")
#         return redirect(url_for("admin.dashboard"))

#     return render_template("admin/add_topic.html")

# # ---------------------------
# # Delete Topic
# # ---------------------------
# @admin_bp.route("/delete/<int:id>")
# def delete_topic(id):
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     topic = Topic.query.get_or_404(id)
#     db.session.delete(topic)
#     db.session.commit()
#     flash("Topic deleted successfully!", "info")
#     return redirect(url_for("admin.dashboard"))


# # ---------------------------
# # Logout
# # ---------------------------
# @admin_bp.route("/logout")
# def logout():
#     session.pop("admin_logged_in", None)
#     flash("Logged out successfully.", "info")
#     return redirect(url_for("admin.admin_login"))


# # ---------------------------
# # View All Topics
# # ---------------------------
# @admin_bp.route("/topics")
# def all_topics():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     topics = Topic.query.all()
#     return render_template("admin/all_topics.html", topics=topics)



# # ---------------------------
# # Admin Analytics
# # ---------------------------
# @admin_bp.route("/analytics")
# def analytics():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     from app.models.topic import UserTopicProgress
#     from app.models.badge import UserBadge
#     from app.models.coding_test_progress import CodingTestProgress
#     from app.models.user import User

#     users = User.query.all()
#     analytics_data = []

#     def format_time(seconds):
#         minutes = seconds // 60
#         remaining_seconds = seconds % 60
#         return f"{minutes} min {remaining_seconds} sec"

#     for user in users:
#         # Topic progress
#         topic_progress = UserTopicProgress.query.filter_by(
#             user_id=user.id
#         ).all()

#         completed_topics = sum(1 for t in topic_progress if t.completed)
#         total_time_seconds = sum(t.total_time_spent or 0 for t in topic_progress)

#         # Coding questions solved
#         coding_progress = CodingTestProgress.query.filter_by(
#             user_id=user.id
#         ).all()
#         solved_progress = [
#             p for p in coding_progress
#             if (p.status or "").strip().lower() in {"passed", "solved"}
#         ]
#         solved_questions = len(solved_progress)

#         # Coding marks based on solved question difficulty
#         coding_marks = 0
#         for p in solved_progress:
#             question = CodingQuestion.query.get(p.question_id)
#             difficulty = (question.difficulty or "").strip().lower() if question else ""
#             coding_marks += XP_MAP.get(difficulty, 0)

#         # Badges
#         earned_badges = UserBadge.query.filter_by(user_id=user.id).count()
#         current_badge = user.get_current_level_badge()

#         analytics_data.append({
#             "user": user,
#             "completed_topics": completed_topics,
#             "total_time": format_time(total_time_seconds),  # ✅ formatted here
#             "solved_questions": solved_questions,
#             "coding_marks": coding_marks,
#             "xp": user.xp,
#             "badge_count": earned_badges,
#             "current_badge": current_badge
#         })

#     return render_template(
#         "admin/analytics.html",
#         analytics_data=analytics_data
#     )


# # ---------------------------
# # Topic Analytics (Charts)
# # ---------------------------
# @admin_bp.route("/analytics/topics")
# def topic_analytics():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     from app.models.topic import Topic, UserTopicProgress
#     from sqlalchemy import func

#     # Count completed topics WITHOUT case()
#     completed_count = func.count(
#         func.nullif(UserTopicProgress.completed.is_(False), True)
#     )

#     topic_stats = (
#         db.session.query(
#             Topic.id,
#             Topic.title,

#             # Total attempts (rows in progress table)
#             func.count(UserTopicProgress.user_id).label("attempts"),

#             # Completed count
#             completed_count.label("completed"),

#             # Total time spent (seconds)
#             func.coalesce(
#                 func.sum(UserTopicProgress.total_time_spent),
#                 0
#             ).label("time_spent")
#         )
#         .outerjoin(
#             UserTopicProgress,
#             Topic.id == UserTopicProgress.topic_id
#         )
#         .group_by(Topic.id)
#         .order_by(Topic.title.asc())
#         .all()
#     )

#     # Prepare chart data
#     labels = []
#     completion_data = []
#     time_data = []

#     for t in topic_stats:
#         labels.append(t.title)
#         completion_data.append(int(t.completed or 0))
#         time_data.append(int(t.time_spent or 0))

#     return render_template(
#         "admin/topic_analytics.html",
#         topic_stats=topic_stats,
#         labels=labels,
#         completion_data=completion_data,
#         time_data=time_data
#     )


# # ---------------------------
# # User Analytics (Per Topic)
# # ---------------------------
# @admin_bp.route("/analytics/user/<int:user_id>")
# def user_analytics(user_id):
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     from app.models.user import User
#     from app.models.topic import Topic, UserTopicProgress
#     from sqlalchemy import func

#     user = User.query.get_or_404(user_id)

#     topic_data = (
#         db.session.query(
#             Topic.title,
#             func.coalesce(
#                 func.sum(UserTopicProgress.total_time_spent),
#                 0
#             ).label("time_spent")
#         )
#         .join(UserTopicProgress, Topic.id == UserTopicProgress.topic_id)
#         .filter(UserTopicProgress.user_id == user.id)
#         .group_by(Topic.id)
#         .order_by(Topic.title.asc())
#         .all()
#     )

#     labels = [t.title for t in topic_data]
#     time_data = [int(t.time_spent or 0) for t in topic_data]

#     return render_template(
#         "admin/user_analytics.html",
#         user=user,
#         labels=labels,
#         time_data=time_data
#     )


# # ---------------------------
# # User Activity (Topic + Coding)
# # ---------------------------
# @admin_bp.route("/analytics/user/<int:user_id>/activity")
# def user_activity(user_id):
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     from app.models.user import User
#     from app.models.topic import Topic, UserTopicProgress
#     from app.models.coding_test_progress import CodingTestProgress
#     from app.models.coding_test import CodingTest
#     from app.models.coding_question import CodingQuestion

#     user = User.query.get_or_404(user_id)

#     topic_activity = (
#         db.session.query(
#             Topic.title,
#             UserTopicProgress.completed,
#             UserTopicProgress.completed_at,
#             UserTopicProgress.quiz_passed,
#             UserTopicProgress.revision_count,
#             UserTopicProgress.total_time_spent,
#             UserTopicProgress.last_accessed_at
#         )
#         .join(UserTopicProgress, Topic.id == UserTopicProgress.topic_id)
#         .filter(UserTopicProgress.user_id == user.id)
#         .order_by(UserTopicProgress.last_accessed_at.desc())
#         .all()
#     )

#     coding_rows = (
#         db.session.query(
#             CodingTest.title.label("test_title"),
#             CodingQuestion.title.label("question_title"),
#             CodingQuestion.difficulty.label("difficulty"),
#             CodingTestProgress.status.label("status"),
#             CodingTestProgress.time_taken.label("time_taken"),
#             CodingTestProgress.attempted_at.label("attempted_at")
#         )
#         .join(CodingQuestion, CodingQuestion.id == CodingTestProgress.question_id)
#         .join(CodingTest, CodingTest.id == CodingTestProgress.test_id)
#         .filter(CodingTestProgress.user_id == user.id)
#         .order_by(CodingTestProgress.attempted_at.desc())
#         .all()
#     )

#     coding_activity = []
#     solved_count = 0
#     total_marks = 0

#     for row in coding_rows:
#         difficulty = (row.difficulty or "").strip().lower()
#         status_text = (row.status or "").strip()
#         solved = status_text.lower() in {"passed", "solved"}
#         marks = XP_MAP.get(difficulty, 0) if solved else 0

#         if solved:
#             solved_count += 1
#             total_marks += marks

#         coding_activity.append({
#             "test_title": row.test_title,
#             "question_title": row.question_title,
#             "difficulty": difficulty or "-",
#             "status": status_text or "Not Attempted",
#             "time_taken": row.time_taken or 0,
#             "attempted_at": row.attempted_at,
#             "marks": marks
#         })

#     completed_topics = sum(1 for row in topic_activity if row.completed)

#     return render_template(
#         "admin/user_activity.html",
#         user=user,
#         topic_activity=topic_activity,
#         coding_activity=coding_activity,
#         completed_topics=completed_topics,
#         solved_count=solved_count,
#         total_marks=total_marks
#     )


# # ---------------------------
# # Announcements
# # ---------------------------
# @admin_bp.route("/announcements", methods=["GET", "POST"])
# def announcements():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     if request.method == "POST":
#         title = (request.form.get("title") or "").strip()
#         content = (request.form.get("content") or "").strip()

#         if not title or not content:
#             flash("Title and announcement content are required.", "warning")
#             return redirect(url_for("admin.announcements"))

#         announcement = Announcement(title=title, content=content)
#         db.session.add(announcement)
#         db.session.flush()

#         users = User.query.with_entities(User.id).all()
#         for user in users:
#             db.session.add(
#                 UserNotification(
#                     user_id=user.id,
#                     announcement_id=announcement.id,
#                     is_read=False,
#                     is_removed=False,
#                 )
#             )

#         db.session.commit()
#         flash("Announcement sent to all users.", "success")
#         return redirect(url_for("admin.announcements"))

#     announcements_list = Announcement.query.order_by(Announcement.created_at.desc()).all()
#     return render_template("admin/announcements.html", announcements=announcements_list)



# # -------------------------------------------------- 

# # Upload Topics CSV 

# # -------------------------------------------------- 


# @admin_bp.route("/upload_topics_csv", methods=["POST"])
# def upload_topics_csv():

#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin.admin_login"))

#     file = request.files.get("file")

#     if not file:
#         flash("❌ No CSV file uploaded", "danger")
#         return redirect(url_for("admin.add_topic"))

#     try:
#         import csv

#         stream = file.stream.read().decode("utf-8-sig").splitlines()
#         reader = csv.DictReader(stream)

#         print("CSV Headers:", reader.fieldnames)

#         required_columns = [
#             "title",
#             "tags"
#         ]

#         if not reader.fieldnames:
#             flash("❌ CSV file is empty", "danger")
#             return redirect(url_for("admin.add_topic"))

#         missing = []

#         for col in required_columns:
#             if col not in reader.fieldnames:
#                 missing.append(col)

#         if missing:
#             flash(
#                 f"❌ Missing columns: {', '.join(missing)}",
#                 "danger"
#             )
#             return redirect(url_for("admin.add_topic"))

#         success_count = 0
#         failed_count = 0

#         for row_num, row in enumerate(reader, start=2):

#             try:

#                 title = (row.get("title") or "").strip()
#                 description = (row.get("description") or "").strip()
#                 tags = (row.get("tags") or "").strip()

#                 if not title:
#                     failed_count += 1
#                     print(f"Row {row_num}: Missing title")
#                     continue

#                 topic = Topic(
#                     title=title,
#                     description=description,
#                     tags=tags
#                 )

#                 db.session.add(topic)

#                 success_count += 1

#             except Exception as row_error:

#                 failed_count += 1

#                 print(
#                     f"Row {row_num} Error:",
#                     str(row_error)
#                 )

#         db.session.commit()

#         flash(
#             f"✅ {success_count} Topics Uploaded Successfully | ❌ {failed_count} Failed",
#             "success"
#         )

#     except Exception as e:

#         db.session.rollback()

#         print("UPLOAD ERROR:", str(e))

#         flash(
#             f"❌ Upload Failed: {str(e)}",
#             "danger"
#         )

#     return redirect(url_for("admin.all_topics"))












from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.extensions import db
from app.models.topic import Topic
from app.models.user import User
from app.models.topic import Topic
from app.models.coding_question import CodingQuestion
from app.models.badge import Badge, UserBadge
from app.models.coding_test import CodingTest   # adjust import if needed
from app.models.announcement import Announcement
from app.models.user_notification import UserNotification
from sqlalchemy import func
import json
import csv 
from io import TextIOWrapper
from app.routes.admin_coding import admin_logged_in 

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

XP_MAP = {
    "easy": 10,
    "medium": 20,
    "hard": 30
}

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ---------------------------
# Admin Login
# ---------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Welcome, Admin!", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("admin.admin_login"))

    return render_template("admin/login.html")


# ---------------------------
# Admin Dashboard
# ---------------------------
@admin_bp.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    # 🔢 TOTAL COUNTS
    total_users = User.query.count()
    total_topics = Topic.query.count()
    total_coding_questions = CodingQuestion.query.count()
    total_coding_tests = CodingTest.query.count()
    total_badges = Badge.query.count()

    # 🏅 BADGE → USER COUNT
    badge_stats = (
        db.session.query(
            Badge.name,
            Badge.icon,
            Badge.color,
            func.count(UserBadge.user_id).label("user_count")
        )
        .outerjoin(UserBadge, Badge.id == UserBadge.badge_id)
        .group_by(Badge.id)
        .order_by(Badge.xp_threshold.asc())
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_topics=total_topics,
        total_coding_questions=total_coding_questions,
        total_coding_tests=total_coding_tests,
        total_badges=total_badges,
        badge_stats=badge_stats
    )

# ---------------------------
# Add Topic
# ---------------------------
@admin_bp.route("/add_topic", methods=["GET", "POST"])
def add_topic():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":
        title = request.form.get("title")
        intro = request.form.get("intro")
        example = request.form.get("example")
        code = request.form.get("code")
        details = request.form.get("details")
        tags = request.form.get("tags")

        # ✅ Combine all sections into one HTML-formatted description
        description = f"""
        <section>
            <h4>Introduction</h4>
            <p>{intro}</p>
        </section>
        <section>
            <h4>Example / Explanation</h4>
            <p>{example}</p>
        </section>
        <section>
            <h4>Code Example</h4>
            <pre><code>{code}</code></pre>
        </section>
        <section>
            <h4>Additional Details</h4>
            <p>{details}</p>
        </section>
        """

        new_topic = Topic(title=title, description=description, tags=tags)
        db.session.add(new_topic)
        db.session.commit()

        flash("Topic added successfully!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_topic.html")

# ---------------------------
# Delete Topic
# ---------------------------
@admin_bp.route("/delete/<int:id>")
def delete_topic(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    topic = Topic.query.get_or_404(id)
    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted successfully!", "info")
    return redirect(url_for("admin.dashboard"))


# ---------------------------
# Logout
# ---------------------------
@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin.admin_login"))


# ---------------------------
# View All Topics
# ---------------------------
@admin_bp.route("/topics")
def all_topics():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    topics = Topic.query.all()
    return render_template("admin/all_topics.html", topics=topics)



# ---------------------------
# Admin Analytics
# ---------------------------
@admin_bp.route("/analytics")
def analytics():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    from app.models.topic import UserTopicProgress
    from app.models.badge import UserBadge
    from app.models.coding_test_progress import CodingTestProgress
    from app.models.user import User

    users = User.query.all()
    analytics_data = []

    def format_time(seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes} min {remaining_seconds} sec"

    for user in users:
        # Topic progress
        topic_progress = UserTopicProgress.query.filter_by(
            user_id=user.id
        ).all()

        completed_topics = sum(1 for t in topic_progress if t.completed)
        total_time_seconds = sum(t.total_time_spent or 0 for t in topic_progress)

        # Coding questions solved
        coding_progress = CodingTestProgress.query.filter_by(
            user_id=user.id
        ).all()
        solved_progress = [
            p for p in coding_progress
            if (p.status or "").strip().lower() in {"passed", "solved"}
        ]
        solved_questions = len(solved_progress)

        # Coding marks based on solved question difficulty
        coding_marks = 0
        for p in solved_progress:
            question = CodingQuestion.query.get(p.question_id)
            difficulty = (question.difficulty or "").strip().lower() if question else ""
            coding_marks += XP_MAP.get(difficulty, 0)

        # Badges
        earned_badges = UserBadge.query.filter_by(user_id=user.id).count()
        current_badge = user.get_current_level_badge()

        analytics_data.append({
            "user": user,
            "completed_topics": completed_topics,
            "total_time": format_time(total_time_seconds),  # ✅ formatted here
            "solved_questions": solved_questions,
            "coding_marks": coding_marks,
            "xp": user.xp,
            "badge_count": earned_badges,
            "current_badge": current_badge
        })

    return render_template(
        "admin/analytics.html",
        analytics_data=analytics_data
    )


# ---------------------------
# Topic Analytics (Charts)
# ---------------------------
@admin_bp.route("/analytics/topics")
def topic_analytics():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    from app.models.topic import Topic, UserTopicProgress
    from sqlalchemy import func

    # Count completed topics WITHOUT case()
    completed_count = func.count(
        func.nullif(UserTopicProgress.completed.is_(False), True)
    )

    topic_stats = (
        db.session.query(
            Topic.id,
            Topic.title,

            # Total attempts (rows in progress table)
            func.count(UserTopicProgress.user_id).label("attempts"),

            # Completed count
            completed_count.label("completed"),

            # Total time spent (seconds)
            func.coalesce(
                func.sum(UserTopicProgress.total_time_spent),
                0
            ).label("time_spent")
        )
        .outerjoin(
            UserTopicProgress,
            Topic.id == UserTopicProgress.topic_id
        )
        .group_by(Topic.id)
        .order_by(Topic.title.asc())
        .all()
    )

    # Prepare chart data
    labels = []
    completion_data = []
    time_data = []

    for t in topic_stats:
        labels.append(t.title)
        completion_data.append(int(t.completed or 0))
        time_data.append(int(t.time_spent or 0))

    return render_template(
        "admin/topic_analytics.html",
        topic_stats=topic_stats,
        labels=labels,
        completion_data=completion_data,
        time_data=time_data
    )


# ---------------------------
# User Analytics (Per Topic)
# ---------------------------
@admin_bp.route("/analytics/user/<int:user_id>")
def user_analytics(user_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    from app.models.user import User
    from app.models.topic import Topic, UserTopicProgress
    from sqlalchemy import func

    user = User.query.get_or_404(user_id)

    topic_data = (
        db.session.query(
            Topic.title,
            func.coalesce(
                func.sum(UserTopicProgress.total_time_spent),
                0
            ).label("time_spent")
        )
        .join(UserTopicProgress, Topic.id == UserTopicProgress.topic_id)
        .filter(UserTopicProgress.user_id == user.id)
        .group_by(Topic.id)
        .order_by(Topic.title.asc())
        .all()
    )

    labels = [t.title for t in topic_data]
    time_data = [int(t.time_spent or 0) for t in topic_data]

    return render_template(
        "admin/user_analytics.html",
        user=user,
        labels=labels,
        time_data=time_data
    )


# ---------------------------
# User Activity (Topic + Coding)
# ---------------------------
@admin_bp.route("/analytics/user/<int:user_id>/activity")
def user_activity(user_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    from app.models.user import User
    from app.models.topic import Topic, UserTopicProgress
    from app.models.coding_test_progress import CodingTestProgress
    from app.models.coding_test import CodingTest
    from app.models.coding_question import CodingQuestion

    user = User.query.get_or_404(user_id)

    topic_activity = (
        db.session.query(
            Topic.title,
            UserTopicProgress.completed,
            UserTopicProgress.completed_at,
            UserTopicProgress.quiz_passed,
            UserTopicProgress.revision_count,
            UserTopicProgress.total_time_spent,
            UserTopicProgress.last_accessed_at
        )
        .join(UserTopicProgress, Topic.id == UserTopicProgress.topic_id)
        .filter(UserTopicProgress.user_id == user.id)
        .order_by(UserTopicProgress.last_accessed_at.desc())
        .all()
    )

    coding_rows = (
        db.session.query(
            CodingTest.title.label("test_title"),
            CodingQuestion.title.label("question_title"),
            CodingQuestion.difficulty.label("difficulty"),
            CodingTestProgress.status.label("status"),
            CodingTestProgress.time_taken.label("time_taken"),
            CodingTestProgress.attempted_at.label("attempted_at")
        )
        .join(CodingQuestion, CodingQuestion.id == CodingTestProgress.question_id)
        .join(CodingTest, CodingTest.id == CodingTestProgress.test_id)
        .filter(CodingTestProgress.user_id == user.id)
        .order_by(CodingTestProgress.attempted_at.desc())
        .all()
    )

    coding_activity = []
    solved_count = 0
    total_marks = 0

    for row in coding_rows:
        difficulty = (row.difficulty or "").strip().lower()
        status_text = (row.status or "").strip()
        solved = status_text.lower() in {"passed", "solved"}
        marks = XP_MAP.get(difficulty, 0) if solved else 0

        if solved:
            solved_count += 1
            total_marks += marks

        coding_activity.append({
            "test_title": row.test_title,
            "question_title": row.question_title,
            "difficulty": difficulty or "-",
            "status": status_text or "Not Attempted",
            "time_taken": row.time_taken or 0,
            "attempted_at": row.attempted_at,
            "marks": marks
        })

    completed_topics = sum(1 for row in topic_activity if row.completed)

    return render_template(
        "admin/user_activity.html",
        user=user,
        topic_activity=topic_activity,
        coding_activity=coding_activity,
        completed_topics=completed_topics,
        solved_count=solved_count,
        total_marks=total_marks
    )


# ---------------------------
# Announcements
# ---------------------------
@admin_bp.route("/announcements", methods=["GET", "POST"])
def announcements():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        content = (request.form.get("content") or "").strip()

        if not title or not content:
            flash("Title and announcement content are required.", "warning")
            return redirect(url_for("admin.announcements"))

        announcement = Announcement(title=title, content=content)
        db.session.add(announcement)
        db.session.flush()

        users = User.query.with_entities(User.id).all()
        for user in users:
            db.session.add(
                UserNotification(
                    user_id=user.id,
                    announcement_id=announcement.id,
                    is_read=False,
                    is_removed=False,
                )
            )

        db.session.commit()
        flash("Announcement sent to all users.", "success")
        return redirect(url_for("admin.announcements"))

    announcements_list = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("admin/announcements.html", announcements=announcements_list)



# -------------------------------------------------- 

# Upload Topics CSV 

# -------------------------------------------------- 


@admin_bp.route("/upload_topics_csv", methods=["POST"])
def upload_topics_csv():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    file = request.files.get("file")

    if not file:
        flash("❌ No CSV file uploaded", "danger")
        return redirect(url_for("admin.add_topic"))

    try:
        import csv

        stream = file.stream.read().decode("utf-8-sig").splitlines()
        reader = csv.DictReader(stream)

        print("CSV Headers:", reader.fieldnames)

        required_columns = [
            "title",
            "intro",
            "example",
            "code",
            "details",
            "tags"
        ]

        if not reader.fieldnames:
            flash("❌ CSV file is empty", "danger")
            return redirect(url_for("admin.add_topic"))

        missing = []

        for col in required_columns:
            if col not in reader.fieldnames:
                missing.append(col)

        if missing:
            flash(
                f"❌ Missing columns: {', '.join(missing)}",
                "danger"
            )
            return redirect(url_for("admin.add_topic"))

        success_count = 0
        failed_count = 0

        for row_num, row in enumerate(reader, start=2):
            try:

                title = (row.get("title") or "").strip()
                intro = (row.get("intro") or "").strip()
                example = (row.get("example") or "").strip()
                code = (row.get("code") or "").strip()
                details = (row.get("details") or "").strip()
                tags = (row.get("tags") or "").strip()
                
                intro = intro.replace("\\n", "<br>")
                example = example.replace("\\n", "<br>")
                details = details.replace("\\n", "<br>")
                code = code.encode().decode('unicode_escape')

                description = f"""
                <section>
                    <h4>Introduction</h4>
                    <p>{intro}</p>
                </section>

                <section>
                    <h4>Example / Explanation</h4>
                    <p>{example}</p>
                </section>

                <section>
                    <h4>Code Example</h4>
                    <pre><code>{code}</code></pre>
                </section>

                <section>
                    <h4>Additional Details</h4>
                    <p>{details}</p>
                </section>
                """

                if not title:
                    failed_count += 1
                    print(f"Row {row_num}: Missing title")
                    continue

                topic = Topic(
                    title=title,
                    description=description,
                    tags=tags
                )

                db.session.add(topic)

                success_count += 1

            except Exception as row_error:

                failed_count += 1

                print(
                    f"Row {row_num} Error:",
                    str(row_error)
                )

        db.session.commit()

        flash(
            f"✅ {success_count} Topics Uploaded Successfully | ❌ {failed_count} Failed",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print("UPLOAD ERROR:", str(e))

        flash(
            f"❌ Upload Failed: {str(e)}",
            "danger"
        )

    return redirect(url_for("admin.all_topics"))










# #  -------------- Replaced Part ----------------------

# # @admin_bp.route("/upload_csv", methods=["POST"])
# # def upload_csv():

# #     if not admin_logged_in():
# #         return redirect(url_for("admin.admin_login"))

# #     file = request.files.get("file")

# #     if not file:
# #         flash("❌ No file uploaded", "danger")
# #         return redirect(url_for("admin_coding.add_question"))

# #     try:
# #         import csv

# #         # Handle UTF-8 BOM files
# #         stream = file.stream.read().decode("utf-8-sig").splitlines()

# #         reader = csv.DictReader(stream)

# #         # Debug headers
# #         print("CSV HEADERS:")
# #         print(reader.fieldnames)

# #         if not reader.fieldnames:
# #             flash("❌ CSV file is empty", "danger")
# #             return redirect(url_for("admin_coding.add_question"))

# #         success_count = 0
# #         failed_count = 0

# #         for row_num, row in enumerate(reader, start=2):

# #             try:

# #                 print(f"Processing Row {row_num}:")
# #                 print(row)

# #                 title = (row.get("title") or "").strip()
# #                 description = (row.get("description") or "").strip()
# #                 sample_input = (row.get("sample_input") or "").strip()
# #                 sample_output = (row.get("sample_output") or "").strip()
# #                 difficulty = (row.get("difficulty") or "Easy").strip()
# #                 test_cases = (row.get("test_cases") or "[]").strip()

# #                 # Skip empty title
# #                 if not title:
# #                     print(f"Row {row_num}: Missing title")
# #                     failed_count += 1
# #                     continue

# #                 # Validate JSON
# #                 try:
# #                     json.loads(test_cases)
# #                 except Exception:
# #                     print(f"Row {row_num}: Invalid JSON")
# #                     failed_count += 1
# #                     continue

# #                 question = CodingQuestion(
# #                     title=title,
# #                     description=description,
# #                     sample_input=sample_input,
# #                     sample_output=sample_output,
# #                     difficulty=difficulty,
# #                     test_cases=test_cases
# #                 )

# #                 db.session.add(question)

# #                 success_count += 1

# #             except Exception as row_error:

# #                 failed_count += 1

# #                 print(
# #                     f"Row {row_num} Error:",
# #                     str(row_error)
# #                 )

# #         db.session.commit()

# #         flash(
# #             f"✅ {success_count} Questions Uploaded | ❌ {failed_count} Failed",
# #             "success"
# #         )

# #     except Exception as e:

# #         db.session.rollback()

# #         print("UPLOAD ERROR:", str(e))

# #         flash(
# #             f"❌ Upload Failed: {str(e)}",
# #             "danger"
# #         )

# #     return redirect(url_for("admin_coding.add_question"))




# #  Working Part but Topic Upload is not working

# # @admin_bp.route("/upload_topics_csv", methods=["POST"]) 

# # def upload_topics_csv(): 

# #     if not session.get("admin_logged_in"): 

# #         return redirect(url_for("admin.admin_login")) 

# #     file = request.files.get("file") 

# #     if not file: 

# #         flash("❌ No file uploaded", "danger") 

# #         return redirect(url_for("admin.add_topic")) 

# #     try: 

# #         stream = TextIOWrapper(file.stream, encoding="utf-8") 

# #         csv_reader = csv.DictReader(stream) 

# #         for row in csv_reader: 

# #             new_topic = Topic( 

# #                 title=row["title"], 

# #                 description=row["description"] 

# #             ) 

# #             db.session.add(new_topic) 

# #         db.session.commit() 

# #         flash("✅ Topics Uploaded Successfully!", "success") 

# #     except Exception as e: 

# #         flash(f"❌ Error: {str(e)}", "danger") 

# #     return redirect(url_for("admin.all_topics")) 

