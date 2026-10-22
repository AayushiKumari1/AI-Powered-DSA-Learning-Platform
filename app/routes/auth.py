from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.user import User
from app.models.topic import UserTopicProgress
from app.models.topic import Topic
from app.models.badge import Badge,UserBadge
from app.models.user_notification import UserNotification
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# --------------------------
# Signup
# --------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.signup"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


# --------------------------
# Login
# --------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email not found. Please check and try again.", "danger")
            return redirect(url_for("auth.login"))

        if check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("auth.dashboard"))

        flash("Incorrect password. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


# --------------------------
# Dashboard (for testing)
# --------------------------
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    from app.routes.badge import init_badges
    from app.models.topic import Topic, UserTopicProgress
    from app.models.badge import Badge, UserBadge
    # 1️⃣ Initialize badges (idempotent)
    init_badges()

    # 2️⃣ Award badges based on XP
    current_user.check_and_award_badges()

    # 3️⃣ User XP (always int)
    xp = int(current_user.xp or 0)

    # 4️⃣ Topic progress stats
    total_topics = Topic.query.count()

    progresses = UserTopicProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    completed_count = sum(1 for p in progresses if p.completed)
    bookmarked_count = sum(1 for p in progresses if p.bookmarked)
    total_time = sum(p.total_time_spent or 0 for p in progresses)

    progress_percent = int((completed_count / total_topics) * 100) if total_topics else 0

    # 5️⃣ Badges
    all_badges = Badge.query.order_by(Badge.xp_threshold.asc()).all()

    earned_badge_ids = [
        ub.badge_id
        for ub in UserBadge.query.filter_by(user_id=current_user.id).all()
    ]

    # 6️⃣ Equipped badge
    equipped_badge = None
    if current_user.equipped_badge_id:
        equipped_badge = Badge.query.get(current_user.equipped_badge_id)

    # 7️⃣ Next badge
    next_badge = None
    for badge in all_badges:
        if badge.id not in earned_badge_ids:
            next_badge = badge
            break

    # 8️⃣ Current badge (highest earned)
    current_badge = None
    if earned_badge_ids:
        current_badge = (
            Badge.query
            .filter(Badge.id.in_(earned_badge_ids))
            .order_by(Badge.xp_threshold.desc())
            .first()
        )

    # 9️⃣ Next badge progress (🔥 FIX)
    next_badge_progress_percent = 0
    xp_needed_for_next = 0

    if next_badge:
        xp_needed_for_next = max(next_badge.xp_threshold - xp, 0)
        if next_badge.xp_threshold > 0:
            next_badge_progress_percent = min(
                int((xp / next_badge.xp_threshold) * 100),
                100
            )
        else:
            next_badge_progress_percent = 100

    unread_notifications_query = (
        UserNotification.query
        .filter_by(user_id=current_user.id, is_removed=False, is_read=False)
        .join(UserNotification.announcement)
        .order_by(UserNotification.id.desc())
    )
    unread_notification_count = unread_notifications_query.count()
    latest_unread_notification = unread_notifications_query.first()

    return render_template(
        "auth/dashboard.html",
        xp=xp,
        completed_count=completed_count,
        bookmarked_count=bookmarked_count,
        total_time=total_time,
        progress_percent=progress_percent,
        all_badges=all_badges,
        earned_badge_ids=earned_badge_ids,
        next_badge=next_badge,
        next_badge_progress_percent=next_badge_progress_percent,
        xp_needed_for_next=xp_needed_for_next,
        equipped_badge=equipped_badge,
        current_badge=current_badge,
        unread_notification_count=unread_notification_count,
        latest_unread_notification=latest_unread_notification,
    )


# --------------------------
# Progress Analytics
# --------------------------
@auth_bp.route("/progress")
@login_required
def progress_analytics():
    from app.models.topic import Topic, UserTopicProgress
    from app.models.coding_question import CodingQuestion
    from app.models.coding_test_progress import CodingTestProgress

    XP_MAP = {
        "easy": 10,
        "medium": 20,
        "hard": 30,
    }

    topics = Topic.query.order_by(Topic.title.asc()).all()
    topic_progresses = UserTopicProgress.query.filter_by(user_id=current_user.id).all()
    topic_progress_map = {progress.topic_id: progress for progress in topic_progresses}

    coding_questions = CodingQuestion.query.order_by(CodingQuestion.title.asc()).all()
    coding_progresses = CodingTestProgress.query.filter_by(user_id=current_user.id).all()
    coding_progress_map = {progress.question_id: progress for progress in coding_progresses}

    topic_labels = []
    topic_completion_data = []
    topic_revision_data = []
    topic_time_data = []

    completed_topics = 0
    passed_quizzes = 0
    total_time_seconds = 0

    for topic in topics:
        progress = topic_progress_map.get(topic.id)
        completed = bool(progress and progress.completed)
        quiz_passed = bool(progress and progress.quiz_passed)
        revisions = int(progress.revision_count or 0) if progress else 0
        time_spent_minutes = round((progress.total_time_spent or 0) / 60, 1) if progress else 0

        topic_labels.append(topic.title)
        topic_completion_data.append(1 if completed else 0)
        topic_revision_data.append(revisions)
        topic_time_data.append(time_spent_minutes)

        if completed:
            completed_topics += 1
        if quiz_passed:
            passed_quizzes += 1
        total_time_seconds += (progress.total_time_spent or 0) if progress else 0

    coding_marks_by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
    coding_count_by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
    coding_solved_total = 0

    for question in coding_questions:
        difficulty = (question.difficulty or "").strip().lower()
        progress = coding_progress_map.get(question.id)
        solved = bool(progress and (progress.status or "").strip().lower() in {"passed", "solved"})

        if solved:
            coding_solved_total += 1
            coding_count_by_difficulty[difficulty] = coding_count_by_difficulty.get(difficulty, 0) + 1
            coding_marks_by_difficulty[difficulty] = coding_marks_by_difficulty.get(difficulty, 0) + XP_MAP.get(difficulty, 0)

    topic_xp = completed_topics * 10
    mcq_xp = passed_quizzes * 10
    coding_xp = sum(coding_marks_by_difficulty.values())
    other_xp = max(int(current_user.xp or 0) - (topic_xp + mcq_xp + coding_xp), 0)
    total_xp = int(current_user.xp or 0)

    quiz_total = len(topics)
    quiz_pending = max(quiz_total - passed_quizzes, 0)
    quiz_pass_rate = round((passed_quizzes / quiz_total) * 100, 1) if quiz_total else 0
    completion_rate = round((completed_topics / len(topics)) * 100, 1) if topics else 0

    top_topics_by_time = sorted(
        [
            {
                "title": topic.title,
                "time_spent": topic_progress_map.get(topic.id).total_time_spent if topic_progress_map.get(topic.id) else 0,
                "revisions": topic_progress_map.get(topic.id).revision_count if topic_progress_map.get(topic.id) else 0,
            }
            for topic in topics
        ],
        key=lambda item: item["time_spent"],
        reverse=True,
    )[:8]

    return render_template(
        "auth/progress.html",
        total_xp=total_xp,
        topic_xp=topic_xp,
        mcq_xp=mcq_xp,
        coding_xp=coding_xp,
        other_xp=other_xp,
        completed_topics=completed_topics,
        quiz_total=quiz_total,
        passed_quizzes=passed_quizzes,
        quiz_pending=quiz_pending,
        quiz_pass_rate=quiz_pass_rate,
        coding_solved_total=coding_solved_total,
        completion_rate=completion_rate,
        total_time_minutes=round(total_time_seconds / 60, 1),
        topic_labels=topic_labels,
        topic_completion_data=topic_completion_data,
        topic_revision_data=topic_revision_data,
        topic_time_data=topic_time_data,
        coding_count_by_difficulty=coding_count_by_difficulty,
        coding_marks_by_difficulty=coding_marks_by_difficulty,
        top_topics_by_time=top_topics_by_time,
    )

# --------------------------
# Logout
# --------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))




