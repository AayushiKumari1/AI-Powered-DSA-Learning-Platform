"""
JSON API used by the React frontend (frontend/).

The existing Flask routes are unchanged. Endpoints that were already JSON are
called by React directly and are NOT duplicated here:
    POST /coding/run, POST /coding/submit, DELETE /coding/delete_submission/<id>
    POST /study/<id>/track-time, POST /coding-tests/submit-result
    POST /badges/equip/<id>, POST /badges/unequip, POST /chat/chatbot
Realtime chat keeps using the existing Socket.IO events in routes/chat.py.

Auth uses the same Flask-Login session cookie as the rest of the app.
"""
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_user, logout_user
from sqlalchemy import case, func, or_
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, socketio
from app.models.announcement import Announcement  # noqa: F401  (relationship target)
from app.models.badge import Badge, UserBadge
from app.models.chat_message import ChatMessage
from app.models.coding_question import CodingQuestion
from app.models.coding_question_progress import CodingQuestionProgress
from app.models.coding_test import CodingTest
from app.models.coding_test_progress import CodingTestProgress
from app.models.community_message import CommunityMessage
from app.models.flash_note import FlashNote
from app.models.submission import Submission
from app.models.topic import Topic, UserTopicProgress
from app.models.user import User
from app.models.user_notification import UserNotification

api_bp = Blueprint("api", __name__, url_prefix="/api")

XP_MAP = {"easy": 10, "medium": 20, "hard": 30}


# ----------------------------------------------------------------- helpers
def api_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Sign in required"}), 401
        return fn(*args, **kwargs)
    return wrapper


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


def diff(q):
    return (q.difficulty or "").strip().lower()


def tags(text):
    return [t.strip() for t in (text or "").split(",") if t.strip()]


def user_json(u):
    badge = Badge.query.get(u.equipped_badge_id) if u.equipped_badge_id else u.get_current_level_badge()
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "xp": int(u.xp or 0),
        "badge": badge_json(badge) if badge else None,
        "created_at": iso(u.created_at),
    }


def badge_json(b):
    return {"id": b.id, "name": b.name, "description": b.description, "icon": b.icon,
            "xp_threshold": b.xp_threshold, "color": b.color, "level": b.level}


def problem_json(q, solved_ids=None, full=False):
    d = {"id": q.id, "title": q.title, "difficulty": diff(q) or None, "xp": XP_MAP.get(diff(q), 10)}
    if solved_ids is not None:
        d["solved"] = q.id in solved_ids
    if full:
        d.update(description=q.description, sample_input=q.sample_input, sample_output=q.sample_output)
    return d


def solved_problem_ids(user_id):
    return {qid for (qid,) in db.session.query(CodingQuestionProgress.question_id)
            .filter_by(user_id=user_id, is_completed=True).all()}


def unread_count(user_id):
    return (UserNotification.query.filter_by(user_id=user_id, is_removed=False, is_read=False)
            .join(UserNotification.announcement).count())


def get_progress(topic_id, create=False):
    p = UserTopicProgress.query.filter_by(user_id=current_user.id, topic_id=topic_id).first()
    if not p and create:
        p = UserTopicProgress(user_id=current_user.id, topic_id=topic_id, revision_count=0, total_time_spent=0)
        db.session.add(p)
    return p


def body():
    return request.get_json(silent=True) or {}


# ----------------------------------------------------------------- auth
@api_bp.post("/auth/signup")
def signup():
    data = body()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not username or not email or len(password) < 6:
        return jsonify({"error": "Username, email and a password of at least 6 characters are required."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "That username is taken."}), 409
    user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({"user": user_json(user)}), 201


@api_bp.post("/auth/login")
def login():
    data = body()
    user = User.query.filter_by(email=(data.get("email") or "").strip().lower()).first() \
        or User.query.filter_by(email=(data.get("email") or "").strip()).first()
    if not user:
        return jsonify({"error": "No account found with this email."}), 404
    if not check_password_hash(user.password, data.get("password") or ""):
        return jsonify({"error": "Incorrect password."}), 401
    login_user(user, remember=bool(data.get("remember")))
    return jsonify({"user": user_json(user)})


@api_bp.post("/auth/logout")
def logout():
    logout_user()
    return jsonify({"ok": True})


@api_bp.get("/auth/me")
def me():
    if not current_user.is_authenticated:
        return jsonify({"user": None})
    return jsonify({"user": user_json(current_user), "unread_notifications": unread_count(current_user.id)})


# ----------------------------------------------------------------- landing (public)
@api_bp.get("/stats")
def public_stats():
    return jsonify({
        "learners": User.query.count(),
        "topics": Topic.query.count(),
        "problems": CodingQuestion.query.count(),
        "tests": CodingTest.query.count(),
        "submissions": Submission.query.count(),
    })


# ----------------------------------------------------------------- dashboard
@api_bp.get("/dashboard")
@api_login_required
def dashboard():
    from app.routes.badge import init_badges
    init_badges()
    current_user.check_and_award_badges()
    uid = current_user.id
    xp = int(current_user.xp or 0)

    total_topics = Topic.query.count()
    progresses = UserTopicProgress.query.filter_by(user_id=uid).all()
    completed = sum(1 for p in progresses if p.completed)
    total_time = sum(p.total_time_spent or 0 for p in progresses)

    all_badges = Badge.query.order_by(Badge.xp_threshold.asc()).all()
    earned_ids = {ub.badge_id for ub in UserBadge.query.filter_by(user_id=uid).all()}
    next_badge = next((b for b in all_badges if b.id not in earned_ids), None)

    solved_ids = solved_problem_ids(uid)
    rank = case((func.lower(CodingQuestion.difficulty) == "easy", 1),
                (func.lower(CodingQuestion.difficulty) == "medium", 2), else_=3)
    recommended = [problem_json(q, solved_ids) for q in
                   CodingQuestion.query.filter(~CodingQuestion.id.in_(solved_ids or [0]))
                   .order_by(rank, CodingQuestion.id).limit(5).all()]

    # Activity over the last 7 days (submissions + topic completions)
    today = datetime.utcnow().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    subs = Submission.query.filter(Submission.user_id == uid,
                                   Submission.created_at >= datetime.combine(days[0], datetime.min.time())).all()
    week = []
    for d in days:
        week.append({
            "day": d.strftime("%a"),
            "submissions": sum(1 for s in subs if s.created_at and s.created_at.date() == d),
            "solved": sum(1 for s in subs if s.created_at and s.created_at.date() == d and s.status == "Passed"),
            "topics": sum(1 for p in progresses if p.completed_at and p.completed_at.date() == d),
        })

    # Recent activity feed
    activity = []
    for s in Submission.query.filter_by(user_id=uid).order_by(Submission.created_at.desc()).limit(6).all():
        q = CodingQuestion.query.get(s.question_id)
        activity.append({"kind": "solve" if s.status == "Passed" else "fail",
                         "what": f"{'Solved' if s.status == 'Passed' else 'Attempted'} {q.title if q else 'a problem'}",
                         "meta": f"{s.passed or 0}/{s.total or 0} tests · {s.language}", "at": iso(s.created_at)})
    for p in sorted([p for p in progresses if p.completed_at], key=lambda p: p.completed_at, reverse=True)[:4]:
        t = Topic.query.get(p.topic_id)
        activity.append({"kind": "lesson", "what": f"Completed {t.title if t else 'a topic'}",
                         "meta": "+10 XP", "at": iso(p.completed_at)})
    for ub in UserBadge.query.filter_by(user_id=uid).order_by(UserBadge.earned_at.desc()).limit(2).all():
        b = Badge.query.get(ub.badge_id)
        if b:
            activity.append({"kind": "badge", "what": f"Earned {b.name}", "meta": b.icon, "at": iso(ub.earned_at)})
    activity.sort(key=lambda a: a["at"] or "", reverse=True)

    # Continue learning: most recently opened, not completed
    recent = (db.session.query(Topic, UserTopicProgress)
              .join(UserTopicProgress, Topic.id == UserTopicProgress.topic_id)
              .filter(UserTopicProgress.user_id == uid)
              .order_by(UserTopicProgress.completed.asc(), UserTopicProgress.last_accessed_at.desc())
              .limit(3).all())
    if len(recent) < 3:
        seen = {t.id for t, _ in recent}
        for t in Topic.query.order_by(Topic.id).limit(10).all():
            if t.id not in seen and len(recent) < 3:
                recent.append((t, None))
    continue_learning = [{"id": t.id, "title": t.title, "tags": tags(t.tags),
                          "completed": bool(p and p.completed), "visits": p.revision_count if p else 0,
                          "minutes": round((p.total_time_spent or 0) / 60) if p else 0} for t, p in recent]

    latest = (UserNotification.query.filter_by(user_id=uid, is_removed=False, is_read=False)
              .join(UserNotification.announcement).order_by(UserNotification.id.desc()).first())

    return jsonify({
        "user": user_json(current_user),
        "stats": {
            "xp": xp, "completed_topics": completed, "total_topics": total_topics,
            "bookmarked": sum(1 for p in progresses if p.bookmarked),
            "minutes": total_time // 60, "solved": len(solved_ids),
            "total_problems": CodingQuestion.query.count(),
        },
        "next_badge": badge_json(next_badge) if next_badge else None,
        "next_badge_progress": min(int(xp / next_badge.xp_threshold * 100), 100) if next_badge and next_badge.xp_threshold else 100,
        "xp_to_next": max((next_badge.xp_threshold - xp) if next_badge else 0, 0),
        "badges_earned": len(earned_ids), "badges_total": len(all_badges),
        "week": week,
        "recommended": recommended,
        "activity": activity[:7],
        "continue_learning": continue_learning,
        "live_test": next(({"id": t.id, "title": t.title, "questions": len(t.questions),
                            "minutes": len(t.questions) * 10} for t in CodingTest.query.order_by(CodingTest.id.desc()).all()
                           if t.questions), None),
        "announcement": {"id": latest.id, "title": latest.announcement.title, "content": latest.announcement.content,
                         "at": iso(latest.announcement.created_at)} if latest else None,
    })


# ----------------------------------------------------------------- analytics
@api_bp.get("/analytics")
@api_login_required
def analytics():
    uid = current_user.id
    topics = Topic.query.order_by(Topic.title.asc()).all()
    prog = {p.topic_id: p for p in UserTopicProgress.query.filter_by(user_id=uid).all()}
    rows, completed, passed, total_secs = [], 0, 0, 0
    for t in topics:
        p = prog.get(t.id)
        rows.append({"id": t.id, "title": t.title, "completed": bool(p and p.completed),
                     "quiz_passed": bool(p and p.quiz_passed), "visits": int(p.revision_count or 0) if p else 0,
                     "minutes": round((p.total_time_spent or 0) / 60, 1) if p else 0})
        completed += 1 if p and p.completed else 0
        passed += 1 if p and p.quiz_passed else 0
        total_secs += (p.total_time_spent or 0) if p else 0

    # Practice solves (CodingQuestionProgress) and test solves (CodingTestProgress) both count
    solved_ids = solved_problem_ids(uid)
    for tp in CodingTestProgress.query.filter_by(user_id=uid).all():
        if (tp.status or "").lower() in {"passed", "solved"}:
            solved_ids.add(tp.question_id)
    by_diff = {"easy": 0, "medium": 0, "hard": 0}
    for q in CodingQuestion.query.filter(CodingQuestion.id.in_(solved_ids or [0])).all():
        if diff(q) in by_diff:
            by_diff[diff(q)] += 1
    marks = {k: v * XP_MAP[k] for k, v in by_diff.items()}

    total_xp = int(current_user.xp or 0)
    topic_xp, mcq_xp, coding_xp = completed * 10, passed * 10, sum(marks.values())

    # Submission history (last 30 days)
    start = datetime.utcnow().date() - timedelta(days=29)
    subs = Submission.query.filter(Submission.user_id == uid,
                                   Submission.created_at >= datetime.combine(start, datetime.min.time())).all()
    daily = []
    for i in range(30):
        d = start + timedelta(days=i)
        day_subs = [s for s in subs if s.created_at and s.created_at.date() == d]
        daily.append({"date": d.isoformat(), "label": d.strftime("%d %b"),
                      "submissions": len(day_subs), "accepted": sum(1 for s in day_subs if s.status == "Passed")})
    all_subs = Submission.query.filter_by(user_id=uid).count()
    accepted = Submission.query.filter_by(user_id=uid, status="Passed").count()

    return jsonify({
        "totals": {
            "xp": total_xp, "topic_xp": topic_xp, "quiz_xp": mcq_xp, "coding_xp": coding_xp,
            "other_xp": max(total_xp - topic_xp - mcq_xp - coding_xp, 0),
            "topics": len(topics), "completed_topics": completed, "quizzes_passed": passed,
            "minutes": round(total_secs / 60, 1), "solved": len(solved_ids),
            "submissions": all_subs, "acceptance": round(accepted / all_subs * 100, 1) if all_subs else 0,
        },
        "solved_by_difficulty": by_diff, "marks_by_difficulty": marks,
        "topics": rows, "daily": daily,
    })


# ----------------------------------------------------------------- learn
@api_bp.get("/topics")
@api_login_required
def topics_list():
    q = (request.args.get("search") or "").strip()
    query = Topic.query
    if q:
        query = query.filter(or_(Topic.title.ilike(f"%{q}%"), Topic.tags.ilike(f"%{q}%")))
    prog = {p.topic_id: p for p in UserTopicProgress.query.filter_by(user_id=current_user.id).all()}
    out = []
    for t in query.order_by(Topic.id).all():
        p = prog.get(t.id)
        out.append({"id": t.id, "title": t.title, "tags": tags(t.tags),
                    "completed": bool(p and p.completed), "bookmarked": bool(p and p.bookmarked),
                    "quiz_passed": bool(p and p.quiz_passed),
                    "visits": p.revision_count if p else 0, "seconds": p.total_time_spent if p else 0})
    return jsonify({"topics": out})


@api_bp.get("/topics/<int:topic_id>")
@api_login_required
def topic_detail(topic_id):
    from app.routes.study import recommend_dsa_videos
    topic = Topic.query.get_or_404(topic_id)
    p = get_progress(topic_id, create=True)
    p.revision_count = (p.revision_count or 0) + 1
    p.last_accessed_at = datetime.utcnow()
    db.session.commit()
    try:
        videos = recommend_dsa_videos(topic.title).get("results", [])
    except Exception:
        videos = []
    return jsonify({
        "topic": {"id": topic.id, "title": topic.title, "description": topic.description, "tags": tags(topic.tags)},
        "progress": {"completed": bool(p.completed), "bookmarked": bool(p.bookmarked), "quiz_passed": bool(p.quiz_passed),
                     "visits": p.revision_count, "seconds": p.total_time_spent or 0},
        "videos": [{"id": v.get("videoId"), "title": v.get("title"), "thumbnail": v.get("thumbnail"),
                    "channel": v.get("channel") or v.get("channelTitle")} for v in videos if v.get("videoId")],
    })


@api_bp.post("/topics/<int:topic_id>/complete")
@api_login_required
def topic_complete(topic_id):
    Topic.query.get_or_404(topic_id)
    p = get_progress(topic_id, create=True)
    if p.completed:
        return jsonify({"ok": True, "already": True, "xp": current_user.xp})
    p.completed, p.completed_at = True, datetime.utcnow()
    current_user.xp = (current_user.xp or 0) + 10
    current_user.check_and_award_badges()
    db.session.commit()
    return jsonify({"ok": True, "xp": current_user.xp})


@api_bp.post("/topics/<int:topic_id>/bookmark")
@api_login_required
def topic_bookmark(topic_id):
    Topic.query.get_or_404(topic_id)
    p = get_progress(topic_id, create=True)
    p.bookmarked = not p.bookmarked
    db.session.commit()
    return jsonify({"bookmarked": p.bookmarked})


@api_bp.get("/topics/<int:topic_id>/quiz")
@api_login_required
def quiz_get(topic_id):
    from app.routes.study import generate_mcq_quiz
    topic = Topic.query.get_or_404(topic_id)
    try:
        quiz = generate_mcq_quiz(topic.title) or []
    except Exception:
        quiz = []
    session[f"quiz_{topic_id}"] = quiz
    # never send the answers to the browser
    return jsonify({"topic": {"id": topic.id, "title": topic.title},
                    "questions": [{"question": q["question"], "options": q["options"]} for q in quiz]})


@api_bp.post("/topics/<int:topic_id>/quiz")
@api_login_required
def quiz_submit(topic_id):
    quiz = session.get(f"quiz_{topic_id}")
    if not quiz:
        return jsonify({"error": "This quiz expired. Load a new one."}), 410
    answers = body().get("answers") or []
    results, score = [], 0
    for i, q in enumerate(quiz):
        a = answers[i] if i < len(answers) else None
        ok = a is not None and int(a) == q["correct_index"]
        score += 1 if ok else 0
        results.append({"question": q["question"], "options": q["options"], "correct_index": q["correct_index"],
                        "user_answer": a, "is_correct": ok})
    passed = score >= 3
    p = get_progress(topic_id, create=True)
    already = bool(p.quiz_passed)
    if passed and not p.quiz_passed:
        p.quiz_passed, p.completed, p.completed_at = True, True, datetime.utcnow()
        current_user.xp = (current_user.xp or 0) + 10
    db.session.commit()
    session.pop(f"quiz_{topic_id}", None)
    return jsonify({"score": score, "total": len(quiz), "passed": passed, "already_passed": already, "results": results})


# ----------------------------------------------------------------- practice
@api_bp.get("/problems")
@api_login_required
def problems():
    q = (request.args.get("search") or "").strip()
    d = (request.args.get("difficulty") or "").strip().lower()
    query = CodingQuestion.query
    if q:
        query = query.filter(or_(CodingQuestion.title.ilike(f"%{q}%"), CodingQuestion.description.ilike(f"%{q}%")))
    if d in XP_MAP:
        query = query.filter(func.lower(CodingQuestion.difficulty) == d)
    rank = case((func.lower(CodingQuestion.difficulty) == "easy", 1),
                (func.lower(CodingQuestion.difficulty) == "medium", 2),
                (func.lower(CodingQuestion.difficulty) == "hard", 3), else_=4)
    solved = solved_problem_ids(current_user.id)
    attempts = dict(db.session.query(Submission.question_id, func.count(Submission.id))
                    .filter_by(user_id=current_user.id).group_by(Submission.question_id).all())
    out = []
    for item in query.order_by(rank, CodingQuestion.id).all():
        j = problem_json(item, solved)
        j["attempts"] = attempts.get(item.id, 0)
        out.append(j)
    return jsonify({"problems": out, "solved": len(solved)})


@api_bp.get("/problems/<int:qid>")
@api_login_required
def problem_detail(qid):
    q = CodingQuestion.query.get_or_404(qid)
    last = (Submission.query.filter_by(user_id=current_user.id, question_id=qid)
            .order_by(Submission.created_at.desc()).first())
    ids = [r.id for r in CodingQuestion.query.order_by(CodingQuestion.id).with_entities(CodingQuestion.id)]
    i = ids.index(qid)
    return jsonify({
        "problem": problem_json(q, solved_problem_ids(current_user.id), full=True),
        "last_submission": {"code": last.code, "language": last.language, "status": last.status,
                            "passed": last.passed, "total": last.total, "at": iso(last.created_at)} if last else None,
        "prev_id": ids[i - 1] if i > 0 else None, "next_id": ids[i + 1] if i + 1 < len(ids) else None,
    })


@api_bp.get("/problems/<int:qid>/submissions")
@api_login_required
def problem_submissions(qid):
    q = CodingQuestion.query.get_or_404(qid)
    subs = (Submission.query.filter_by(user_id=current_user.id, question_id=qid)
            .order_by(Submission.created_at.desc()).all())
    return jsonify({"problem": problem_json(q), "submissions": [
        {"id": s.id, "code": s.code, "language": s.language, "status": s.status, "passed": s.passed,
         "total": s.total, "runtime": s.runtime, "solve_time": s.solve_time, "at": iso(s.created_at)} for s in subs]})


@api_bp.get("/problems/<int:qid>/analysis")
@api_login_required
def problem_analysis(qid):
    from app.routes.coding import _infer_topic_key, _topic_recommendation_pack
    analysis = session.get("last_complexity_analysis")
    if not analysis or session.get("last_question_id") != qid:
        return jsonify({"error": "No analysis yet. Submit a solution first."}), 404
    q = CodingQuestion.query.get_or_404(qid)
    key = _infer_topic_key(q)
    pack = _topic_recommendation_pack(key)
    terms = pack.get("search_terms") or [key]
    related = (CodingQuestion.query.filter(CodingQuestion.id != q.id)
               .filter(or_(*[CodingQuestion.title.ilike(f"%{t}%") for t in terms])).limit(4).all())
    rating = int(analysis.get("performance_rating") or 0)
    clean = analysis.get("total_cases") and analysis.get("passed_cases") == analysis.get("total_cases") and rating > 5
    return jsonify({"problem": problem_json(q), "analysis": analysis, "topic_label": pack.get("label"),
                    "next_steps": pack.get("next_steps", []), "focus_message": pack.get("focus_message"),
                    "solved_cleanly": bool(clean), "related": [problem_json(r) for r in related]})


# ----------------------------------------------------------------- tests
def test_level(t):
    ds = {diff(q) for q in t.questions}
    return "hard" if "hard" in ds else "medium" if "medium" in ds else "easy"


@api_bp.get("/tests")
@api_login_required
def tests():
    done = {p.test_id for p in CodingTestProgress.query.filter_by(user_id=current_user.id).all()}
    return jsonify({"tests": [{
        "id": t.id, "title": t.title, "description": t.description, "level": test_level(t),
        "questions": len(t.questions), "minutes": len(t.questions) * 10,
        "max_xp": sum(XP_MAP.get(diff(q), 0) for q in t.questions),
        "topics": [tp.title for tp in t.topics], "attempted": t.id in done,
    } for t in CodingTest.query.order_by(CodingTest.id.desc()).all()]})


@api_bp.get("/tests/<int:test_id>")
@api_login_required
def test_detail(test_id):
    t = CodingTest.query.get_or_404(test_id)
    return jsonify({"test": {
        "id": t.id, "title": t.title, "description": t.description, "level": test_level(t),
        "minutes": len(t.questions) * 10, "max_xp": sum(XP_MAP.get(diff(q), 0) for q in t.questions),
        "topics": [tp.title for tp in t.topics],
        "questions": [problem_json(q, full=True) for q in t.questions],
    }})


@api_bp.get("/tests/<int:test_id>/result")
@api_login_required
def test_result(test_id):
    from app.ml.analyzer import analyze_test
    t = CodingTest.query.get_or_404(test_id)
    pm = {p.question_id: p for p in CodingTestProgress.query.filter_by(user_id=current_user.id, test_id=test_id).all()}
    rows, passed, total_time, xp = [], 0, 0, 0
    for q in t.questions:
        p = pm.get(q.id)
        status = p.status if p else "Not attempted"
        tt = (p.time_taken or 0) if p else 0
        total_time += tt
        passed += 1 if status == "Passed" else 0
        xp += XP_MAP.get(diff(q), 0) if p and p.xp_awarded else 0
        rows.append({"id": q.id, "title": q.title, "difficulty": diff(q), "status": status, "time_taken": tt})
    try:
        a = analyze_test(t, pm)
    except Exception:
        a = {"analysis": {}, "details": {}, "blocked": [], "recommended": None}
    explanations = {}
    try:
        from app.utils.topic_explainer import explain_topic
        for topic, details in (a.get("details") or {}).items():
            try:
                explanations[topic] = explain_topic(topic=topic, level=details["level"], stats=details)
            except Exception:
                explanations[topic] = f"You are at {details.get('level')} level in {topic}. Practise more to build consistency."
    except Exception:
        pass
    return jsonify({"test": {"id": t.id, "title": t.title}, "rows": rows, "passed": passed, "total": len(t.questions),
                    "total_time": total_time, "xp_earned": xp,
                    "mastery": {k: list(v) for k, v in (a.get("analysis") or {}).items()},
                    "blocked": list(a.get("blocked") or []), "recommended": a.get("recommended"),
                    "explanations": explanations})


# ----------------------------------------------------------------- achievements
@api_bp.get("/badges")
@api_login_required
def badges():
    from app.routes.badge import init_badges
    init_badges()
    current_user.check_and_award_badges()
    earned = {ub.badge_id: ub.earned_at for ub in UserBadge.query.filter_by(user_id=current_user.id).all()}
    return jsonify({"xp": int(current_user.xp or 0), "equipped_id": current_user.equipped_badge_id,
                    "badges": [dict(badge_json(b), earned=b.id in earned, earned_at=iso(earned.get(b.id)))
                               for b in Badge.query.order_by(Badge.xp_threshold.asc()).all()]})


# ----------------------------------------------------------------- notes
def note_json(n):
    return {"id": n.id, "subject": n.subject, "title": n.title, "content": n.content, "updated_at": iso(n.updated_at)}


@api_bp.get("/notes")
@api_login_required
def notes():
    return jsonify({"notes": [note_json(n) for n in FlashNote.query.filter_by(user_id=current_user.id)
                              .order_by(FlashNote.updated_at.desc(), FlashNote.id.desc()).all()]})


@api_bp.post("/notes")
@api_login_required
def note_create():
    d = body()
    subject, title, content = (d.get("subject") or "").strip(), (d.get("title") or "").strip(), (d.get("content") or "").strip()
    if not subject or not title or not content:
        return jsonify({"error": "Subject, title and content are required."}), 400
    n = FlashNote(user_id=current_user.id, subject=subject[:120], title=title[:200], content=content[:1000])
    db.session.add(n)
    db.session.commit()
    return jsonify({"note": note_json(n)}), 201


@api_bp.put("/notes/<int:note_id>")
@api_login_required
def note_update(note_id):
    n = FlashNote.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    d = body()
    for field, limit in (("subject", 120), ("title", 200), ("content", 1000)):
        v = (d.get(field) or "").strip()
        if not v:
            return jsonify({"error": f"{field.capitalize()} is required."}), 400
        setattr(n, field, v[:limit])
    db.session.commit()
    return jsonify({"note": note_json(n)})


@api_bp.delete("/notes/<int:note_id>")
@api_login_required
def note_delete(note_id):
    n = FlashNote.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(n)
    db.session.commit()
    return jsonify({"ok": True})


# ----------------------------------------------------------------- notifications
@api_bp.get("/notifications")
@api_login_required
def notifications():
    items = (UserNotification.query.filter_by(user_id=current_user.id).join(UserNotification.announcement)
             .order_by(UserNotification.id.desc()).all())
    return jsonify({"notifications": [{"id": n.id, "title": n.announcement.title, "content": n.announcement.content,
                                       "at": iso(n.announcement.created_at), "is_read": n.is_read,
                                       "is_removed": n.is_removed} for n in items],
                    "unread": unread_count(current_user.id)})


@api_bp.post("/notifications/<int:nid>/<action>")
@api_login_required
def notification_action(nid, action):
    n = UserNotification.query.filter_by(id=nid, user_id=current_user.id).first_or_404()
    if action == "read":
        n.is_read = True
    elif action == "remove":
        n.is_removed = True
    else:
        return jsonify({"error": "Unknown action"}), 400
    db.session.commit()
    return jsonify({"ok": True, "unread": unread_count(current_user.id)})


@api_bp.post("/notifications/read-all")
@api_login_required
def notifications_read_all():
    (UserNotification.query.filter_by(user_id=current_user.id, is_removed=False, is_read=False)
     .update({"is_read": True}, synchronize_session=False))
    db.session.commit()
    return jsonify({"ok": True, "unread": 0})


# ----------------------------------------------------------------- chat
def msg_json(m):
    return {"id": m.id, "sender_type": m.sender_type, "message": m.message, "created_at": iso(m.created_at)}


@api_bp.route("/chat/messages", methods=["GET", "POST"])
@api_login_required
def mentor_chat():
    if request.method == "POST":
        text = (body().get("message") or "").strip()
        if not text:
            return jsonify({"error": "Message cannot be empty."}), 400
        m = ChatMessage(user_id=current_user.id, sender_type="user", message=text[:2000])
        db.session.add(m)
        db.session.commit()
        # same event/room as routes/chat.py so the admin inbox updates live
        socketio.emit("new_chat_message", {"id": m.id, "user_id": m.user_id, "sender_type": m.sender_type,
                                           "message": m.message, "created_at": m.created_at.strftime("%d %b %I:%M %p")},
                      room=f"chat_user_{current_user.id}")
        return jsonify({"message": msg_json(m)}), 201
    msgs = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at, ChatMessage.id).all()
    return jsonify({"user_id": current_user.id, "messages": [msg_json(m) for m in msgs]})


@api_bp.route("/community", methods=["GET", "POST"])
@api_login_required
def community():
    from app.routes.chat import COMMUNITY_GROUPS, _community_group_key
    if request.method == "POST":
        d = body()
        text = (d.get("message") or "").strip()
        if not text:
            return jsonify({"error": "Message cannot be empty."}), 400
        m = CommunityMessage(group_key=_community_group_key(d.get("group")), user_id=current_user.id,
                             sender_name=current_user.username, is_admin=False, message=text[:2000])
        db.session.add(m)
        db.session.commit()
        socketio.emit("new_community_message", {
            "id": m.id, "group_key": m.group_key, "user_id": m.user_id, "sender_name": m.sender_name,
            "is_admin": m.is_admin, "message": m.message, "created_at": m.created_at.strftime("%d %b %I:%M %p"),
        }, room=f"community_{m.group_key}")
        return jsonify({"ok": True, "id": m.id}), 201
    key = _community_group_key(request.args.get("group"))
    counts = dict(db.session.query(CommunityMessage.group_key, func.count(CommunityMessage.id))
                  .group_by(CommunityMessage.group_key).all())
    msgs = (CommunityMessage.query.filter_by(group_key=key)
            .order_by(CommunityMessage.created_at, CommunityMessage.id).limit(300).all())
    return jsonify({
        "groups": [dict(g, count=counts.get(g["key"], 0)) for g in COMMUNITY_GROUPS],
        "current": key, "me": {"id": current_user.id, "name": current_user.username},
        "messages": [{"id": m.id, "user_id": m.user_id, "sender_name": m.sender_name, "is_admin": m.is_admin,
                      "message": m.message, "created_at": iso(m.created_at)} for m in msgs],
    })
