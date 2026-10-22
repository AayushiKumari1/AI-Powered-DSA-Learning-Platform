"""
JSON API for the React admin console (frontend/src/pages/admin).

Uses the same admin session flag and credentials as routes/admin.py, so signing in
here also signs you in to the old server-rendered admin pages and vice versa.
"""
import csv
import html
import io
import json
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, jsonify, request, session
from sqlalchemy import func

from app.extensions import db, socketio
from app.models.announcement import Announcement
from app.models.badge import Badge, UserBadge
from app.models.chat_message import ChatMessage
from app.models.coding_question import CodingQuestion
from app.models.coding_question_progress import CodingQuestionProgress
from app.models.coding_test import CodingTest
from app.models.coding_test_progress import CodingTestProgress
from app.models.community_message import CommunityMessage
from app.models.submission import Submission
from app.models.topic import Topic, UserTopicProgress
from app.models.user import User
from app.models.user_notification import UserNotification
from app.routes.admin import ADMIN_PASSWORD, ADMIN_USERNAME

admin_api_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")
XP_MAP = {"easy": 10, "medium": 20, "hard": 30}


def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Admin sign in required"}), 401
        return fn(*a, **kw)
    return wrapper


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


def diff(q):
    return (q.difficulty or "").strip().lower()


def body():
    return request.get_json(silent=True) or {}


def case_count(q):
    try:
        return len(json.loads(q.test_cases or "[]"))
    except (ValueError, TypeError):
        return 0


def build_lesson(intro, example, code, details):
    e = lambda s: html.escape(s or "").replace("\n", "<br>")
    return (f"<section><h4>Introduction</h4><p>{e(intro)}</p></section>"
            f"<section><h4>Example / Explanation</h4><p>{e(example)}</p></section>"
            f"<section><h4>Code Example</h4><pre><code>{html.escape(code or '')}</code></pre></section>"
            f"<section><h4>Additional Details</h4><p>{e(details)}</p></section>")


def validate_cases(raw):
    cases = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(cases, list) or not cases or not all(isinstance(c, dict) and "input" in c and "output" in c for c in cases):
        raise ValueError("Test cases must be a non-empty JSON array of {\"input\", \"output\"} objects.")
    return json.dumps(cases)


# ------------------------------------------------------------------ auth
@admin_api_bp.post("/login")
def login():
    d = body()
    if d.get("username") == ADMIN_USERNAME and d.get("password") == ADMIN_PASSWORD:
        session["admin_logged_in"] = True
        return jsonify({"admin": True})
    return jsonify({"error": "Invalid admin credentials."}), 401


@admin_api_bp.post("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return jsonify({"ok": True})


@admin_api_bp.get("/me")
def me():
    return jsonify({"admin": bool(session.get("admin_logged_in"))})


# ------------------------------------------------------------------ dashboard
@admin_api_bp.get("/dashboard")
@admin_required
def dashboard():
    since = datetime.utcnow() - timedelta(days=14)
    subs = Submission.query.filter(Submission.created_at >= since).all()
    users = User.query.all()
    start = datetime.utcnow().date() - timedelta(days=13)
    activity = []
    for i in range(14):
        d = start + timedelta(days=i)
        ds = [s for s in subs if s.created_at and s.created_at.date() == d]
        activity.append({"label": d.strftime("%d %b"), "submissions": len(ds), "accepted": sum(1 for s in ds if s.status == "Passed"),
                         "signups": sum(1 for u in users if u.created_at and u.created_at.date() == d)})
    active_ids = {s.user_id for s in subs}
    badge_counts = dict(db.session.query(UserBadge.badge_id, func.count(UserBadge.id)).group_by(UserBadge.badge_id).all())
    qd = {"easy": 0, "medium": 0, "hard": 0}
    for q in CodingQuestion.query.all():
        qd[diff(q)] = qd.get(diff(q), 0) + 1
    recent = []
    for s in Submission.query.order_by(Submission.created_at.desc()).limit(8).all():
        u, q = User.query.get(s.user_id), CodingQuestion.query.get(s.question_id)
        recent.append({"user": u.username if u else "—", "user_id": s.user_id, "problem": q.title if q else "—", "problem_id": s.question_id,
                       "status": s.status, "language": s.language, "passed": s.passed, "total": s.total, "at": iso(s.created_at)})
    all_subs = Submission.query.count()
    return jsonify({
        "counts": {"learners": len(users), "active_14d": len(active_ids), "topics": Topic.query.count(),
                   "problems": CodingQuestion.query.count(), "tests": CodingTest.query.count(),
                   "submissions": all_subs, "acceptance": round(Submission.query.filter_by(status="Passed").count() / all_subs * 100, 1) if all_subs else 0,
                   "announcements": Announcement.query.count()},
        "activity": activity,
        "badges": [{"name": b.name, "icon": b.icon, "count": badge_counts.get(b.id, 0)} for b in Badge.query.order_by(Badge.xp_threshold).all()],
        "problems_by_difficulty": qd,
        "top_learners": [{"id": u.id, "username": u.username, "xp": u.xp or 0} for u in sorted(users, key=lambda u: -(u.xp or 0))[:5]],
        "recent_submissions": recent,
    })


# ------------------------------------------------------------------ learners
def learner_row(u, prog, subs, test_rows):
    solved = {s.question_id for s in subs if s.status == "Passed"} | {t.question_id for t in test_rows if (t.status or "").lower() == "passed"}
    last = max([s.created_at for s in subs if s.created_at] + [p.last_accessed_at for p in prog if p.last_accessed_at] or [None], key=lambda x: x or datetime.min)
    badge = u.get_current_level_badge()
    return {"id": u.id, "username": u.username, "email": u.email, "xp": u.xp or 0,
            "completed_topics": sum(1 for p in prog if p.completed), "minutes": round(sum(p.total_time_spent or 0 for p in prog) / 60),
            "solved": len(solved), "submissions": len(subs),
            "acceptance": round(sum(1 for s in subs if s.status == "Passed") / len(subs) * 100) if subs else 0,
            "joined": iso(u.created_at), "last_active": iso(last),
            "badge": {"name": badge.name, "icon": badge.icon} if badge else None}


@admin_api_bp.get("/learners")
@admin_required
def learners():
    prog, subs, tests = {}, {}, {}
    for p in UserTopicProgress.query.all(): prog.setdefault(p.user_id, []).append(p)
    for s in Submission.query.all(): subs.setdefault(s.user_id, []).append(s)
    for t in CodingTestProgress.query.all(): tests.setdefault(t.user_id, []).append(t)
    rows = [learner_row(u, prog.get(u.id, []), subs.get(u.id, []), tests.get(u.id, [])) for u in User.query.all()]
    return jsonify({"learners": sorted(rows, key=lambda r: -r["xp"])})


@admin_api_bp.get("/learners/<int:uid>")
@admin_required
def learner_detail(uid):
    u = User.query.get_or_404(uid)
    prog = UserTopicProgress.query.filter_by(user_id=uid).all()
    subs = Submission.query.filter_by(user_id=uid).order_by(Submission.created_at.desc()).all()
    tests = CodingTestProgress.query.filter_by(user_id=uid).order_by(CodingTestProgress.attempted_at.desc()).all()
    topics = {t.id: t.title for t in Topic.query.all()}
    qs = {q.id: q for q in CodingQuestion.query.all()}
    tnames = {t.id: t.title for t in CodingTest.query.all()}
    start = datetime.utcnow().date() - timedelta(days=29)
    daily = []
    for i in range(30):
        d = start + timedelta(days=i)
        ds = [s for s in subs if s.created_at and s.created_at.date() == d]
        daily.append({"label": d.strftime("%d %b"), "submissions": len(ds), "accepted": sum(1 for s in ds if s.status == "Passed")})
    return jsonify({
        "learner": learner_row(u, prog, subs, tests),
        "daily": daily,
        "topics": sorted([{"id": p.topic_id, "title": topics.get(p.topic_id, "—"), "completed": p.completed, "quiz_passed": p.quiz_passed,
                           "visits": p.revision_count or 0, "minutes": round((p.total_time_spent or 0) / 60, 1),
                           "last_accessed": iso(p.last_accessed_at), "completed_at": iso(p.completed_at)} for p in prog], key=lambda r: -r["minutes"]),
        "submissions": [{"id": s.id, "problem": qs[s.question_id].title if s.question_id in qs else "—", "problem_id": s.question_id,
                         "difficulty": diff(qs[s.question_id]) if s.question_id in qs else None, "status": s.status, "language": s.language,
                         "passed": s.passed, "total": s.total, "at": iso(s.created_at)} for s in subs[:50]],
        "tests": [{"test": tnames.get(t.test_id, "—"), "problem": qs[t.question_id].title if t.question_id in qs else "—",
                   "difficulty": diff(qs[t.question_id]) if t.question_id in qs else None, "status": t.status, "time_taken": t.time_taken or 0,
                   "marks": XP_MAP.get(diff(qs[t.question_id]), 0) if t.xp_awarded and t.question_id in qs else 0, "at": iso(t.attempted_at)} for t in tests],
    })


# ------------------------------------------------------------------ topics
@admin_api_bp.get("/topics")
@admin_required
def topics():
    stats = {}
    for p in UserTopicProgress.query.all():
        s = stats.setdefault(p.topic_id, {"started": 0, "completed": 0, "quiz_passed": 0, "seconds": 0})
        s["started"] += 1; s["completed"] += 1 if p.completed else 0
        s["quiz_passed"] += 1 if p.quiz_passed else 0; s["seconds"] += p.total_time_spent or 0
    out = []
    for t in Topic.query.order_by(Topic.id).all():
        s = stats.get(t.id, {"started": 0, "completed": 0, "quiz_passed": 0, "seconds": 0})
        out.append({"id": t.id, "title": t.title, "tags": [x.strip() for x in (t.tags or "").split(",") if x.strip()],
                    "started": s["started"], "completed": s["completed"], "quiz_passed": s["quiz_passed"],
                    "minutes": round(s["seconds"] / 60), "has_lesson": bool(t.description)})
    return jsonify({"topics": out, "learners": User.query.count()})


@admin_api_bp.get("/topics/<int:tid>")
@admin_required
def topic_get(tid):
    t = Topic.query.get_or_404(tid)
    return jsonify({"topic": {"id": t.id, "title": t.title, "tags": t.tags or "", "description": t.description or ""}})


@admin_api_bp.post("/topics")
@admin_required
def topic_create():
    d = body()
    title = (d.get("title") or "").strip()
    if not title or not (d.get("intro") or "").strip():
        return jsonify({"error": "Title and introduction are required."}), 400
    t = Topic(title=title[:200], tags=(d.get("tags") or "").strip(),
              description=build_lesson(d.get("intro"), d.get("example"), d.get("code"), d.get("details")))
    db.session.add(t); db.session.commit()
    return jsonify({"id": t.id}), 201


@admin_api_bp.put("/topics/<int:tid>")
@admin_required
def topic_update(tid):
    t = Topic.query.get_or_404(tid)
    d = body()
    if not (d.get("title") or "").strip():
        return jsonify({"error": "Title is required."}), 400
    t.title, t.tags, t.description = d["title"].strip()[:200], (d.get("tags") or "").strip(), d.get("description") or ""
    db.session.commit()
    return jsonify({"ok": True})


@admin_api_bp.delete("/topics/<int:tid>")
@admin_required
def topic_delete(tid):
    t = Topic.query.get_or_404(tid)
    UserTopicProgress.query.filter_by(topic_id=tid).delete()
    for test in CodingTest.query.all():
        if t in test.topics: test.topics.remove(t)
    db.session.delete(t); db.session.commit()
    return jsonify({"ok": True})


def read_csv_upload():
    f = request.files.get("file")
    if not f or not f.filename.lower().endswith(".csv"):
        raise ValueError("Upload a .csv file.")
    return list(csv.DictReader(io.StringIO(f.stream.read().decode("utf-8-sig"))))


@admin_api_bp.post("/topics/upload")
@admin_required
def topics_upload():
    try:
        rows = read_csv_upload()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    added, skipped = 0, 0
    for r in rows:
        title = (r.get("title") or "").strip()
        if not title or Topic.query.filter_by(title=title).first():
            skipped += 1; continue
        fix = lambda s: (s or "").replace("\\n", "\n")
        db.session.add(Topic(title=title, tags=(r.get("tags") or "").strip(),
                             description=build_lesson(fix(r.get("intro")), fix(r.get("example")), fix(r.get("code")), fix(r.get("details")))))
        added += 1
    db.session.commit()
    return jsonify({"added": added, "skipped": skipped})


# ------------------------------------------------------------------ problems
def question_json(q, full=False, stats=None):
    d = {"id": q.id, "title": q.title, "difficulty": diff(q), "cases": case_count(q)}
    if stats is not None:
        s = stats.get(q.id, {"attempts": 0, "learners": set(), "solved": set()})
        d.update(attempts=s["attempts"], learners=len(s["learners"]), solved_by=len(s["solved"]))
    if full:
        d.update(description=q.description or "", sample_input=q.sample_input or "", sample_output=q.sample_output or "",
                 test_cases=json.dumps(json.loads(q.test_cases or "[]"), indent=2))
    return d


@admin_api_bp.get("/problems")
@admin_required
def problems():
    stats = {}
    for s in Submission.query.all():
        x = stats.setdefault(s.question_id, {"attempts": 0, "learners": set(), "solved": set()})
        x["attempts"] += 1; x["learners"].add(s.user_id)
        if s.status == "Passed": x["solved"].add(s.user_id)
    return jsonify({"problems": [question_json(q, stats=stats) for q in CodingQuestion.query.order_by(CodingQuestion.id).all()]})


@admin_api_bp.get("/problems/<int:qid>")
@admin_required
def problem_get(qid):
    return jsonify({"problem": question_json(CodingQuestion.query.get_or_404(qid), full=True)})


def apply_problem(q, d):
    title = (d.get("title") or "").strip()
    level = (d.get("difficulty") or "").strip().lower()
    if not title or not (d.get("description") or "").strip() or level not in XP_MAP:
        raise ValueError("Title, description and a difficulty (easy, medium, hard) are required.")
    q.title, q.description, q.difficulty = title[:200], d["description"], level.capitalize()
    q.sample_input, q.sample_output = d.get("sample_input") or "", d.get("sample_output") or ""
    q.test_cases = validate_cases(d.get("test_cases") or "")


@admin_api_bp.post("/problems")
@admin_required
def problem_create():
    q = CodingQuestion()
    try:
        apply_problem(q, body())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    db.session.add(q); db.session.commit()
    return jsonify({"id": q.id}), 201


@admin_api_bp.put("/problems/<int:qid>")
@admin_required
def problem_update(qid):
    q = CodingQuestion.query.get_or_404(qid)
    try:
        apply_problem(q, body())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    db.session.commit()
    return jsonify({"ok": True})


@admin_api_bp.delete("/problems/<int:qid>")
@admin_required
def problem_delete(qid):
    q = CodingQuestion.query.get_or_404(qid)
    for model in (Submission, CodingQuestionProgress, CodingTestProgress):
        model.query.filter_by(question_id=qid).delete()
    for test in CodingTest.query.all():
        if q in test.questions: test.questions.remove(q)
    db.session.delete(q); db.session.commit()
    return jsonify({"ok": True})


@admin_api_bp.post("/problems/upload")
@admin_required
def problems_upload():
    try:
        rows = read_csv_upload()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    added, errors = 0, []
    for n, r in enumerate(rows, start=2):
        q = CodingQuestion()
        try:
            apply_problem(q, r)
        except (ValueError, json.JSONDecodeError) as e:
            errors.append(f"Row {n}: {e}"); continue
        db.session.add(q); added += 1
    db.session.commit()
    return jsonify({"added": added, "errors": errors[:10]})


# ------------------------------------------------------------------ tests
@admin_api_bp.get("/tests")
@admin_required
def tests():
    prog = {}
    for p in CodingTestProgress.query.all():
        x = prog.setdefault(p.test_id, {"users": set(), "passed": 0, "rows": 0})
        x["users"].add(p.user_id); x["rows"] += 1; x["passed"] += 1 if p.status == "Passed" else 0
    out = []
    for t in CodingTest.query.order_by(CodingTest.id.desc()).all():
        x = prog.get(t.id, {"users": set(), "passed": 0, "rows": 0})
        out.append({"id": t.id, "title": t.title, "description": t.description, "created_at": iso(t.created_at),
                    "questions": [{"id": q.id, "title": q.title, "difficulty": diff(q)} for q in t.questions],
                    "topics": [tp.title for tp in t.topics], "max_xp": sum(XP_MAP.get(diff(q), 0) for q in t.questions),
                    "takers": len(x["users"]), "pass_rate": round(x["passed"] / x["rows"] * 100) if x["rows"] else 0})
    return jsonify({"tests": out})


@admin_api_bp.post("/tests")
@admin_required
def test_create():
    d = body()
    title = (d.get("title") or "").strip()
    qids = [int(i) for i in d.get("question_ids") or []]
    if not title or not qids:
        return jsonify({"error": "A title and at least one question are required."}), 400
    t = CodingTest(title=title[:200], description=(d.get("description") or "").strip())
    t.questions = CodingQuestion.query.filter(CodingQuestion.id.in_(qids)).all()
    t.topics = Topic.query.filter(Topic.id.in_([int(i) for i in d.get("topic_ids") or []])).all()
    db.session.add(t); db.session.commit()
    return jsonify({"id": t.id}), 201


@admin_api_bp.delete("/tests/<int:test_id>")
@admin_required
def test_delete(test_id):
    t = CodingTest.query.get_or_404(test_id)
    CodingTestProgress.query.filter_by(test_id=test_id).delete()
    t.questions, t.topics = [], []
    db.session.delete(t); db.session.commit()
    return jsonify({"ok": True})


# ------------------------------------------------------------------ announcements
@admin_api_bp.route("/announcements", methods=["GET", "POST"])
@admin_required
def announcements():
    if request.method == "POST":
        d = body()
        title, content = (d.get("title") or "").strip(), (d.get("content") or "").strip()
        if not title or not content:
            return jsonify({"error": "Title and message are required."}), 400
        a = Announcement(title=title[:200], content=content)
        db.session.add(a); db.session.flush()
        for (uid,) in User.query.with_entities(User.id).all():
            db.session.add(UserNotification(user_id=uid, announcement_id=a.id, is_read=False, is_removed=False))
        db.session.commit()
        return jsonify({"id": a.id, "recipients": User.query.count()}), 201
    reads = dict(db.session.query(UserNotification.announcement_id, func.count(UserNotification.id))
                 .filter_by(is_read=True).group_by(UserNotification.announcement_id).all())
    totals = dict(db.session.query(UserNotification.announcement_id, func.count(UserNotification.id))
                  .group_by(UserNotification.announcement_id).all())
    return jsonify({"announcements": [{"id": a.id, "title": a.title, "content": a.content, "at": iso(a.created_at),
                                       "read": reads.get(a.id, 0), "recipients": totals.get(a.id, 0)}
                                      for a in Announcement.query.order_by(Announcement.created_at.desc()).all()]})


# ------------------------------------------------------------------ mentor inbox
@admin_api_bp.get("/inbox")
@admin_required
def inbox():
    last = {}
    for m in ChatMessage.query.order_by(ChatMessage.created_at).all():
        x = last.setdefault(m.user_id, {"count": 0})
        x.update(count=x["count"] + 1, message=m.message, sender=m.sender_type, at=iso(m.created_at))
    users = User.query.all()
    rows = [{"id": u.id, "username": u.username, "email": u.email, **last.get(u.id, {"count": 0, "message": None, "sender": None, "at": None})} for u in users]
    rows = sorted([r for r in rows if r["at"]], key=lambda r: r["at"], reverse=True) + [r for r in rows if not r["at"]]
    return jsonify({"conversations": rows})


@admin_api_bp.route("/inbox/<int:uid>", methods=["GET", "POST"])
@admin_required
def inbox_thread(uid):
    u = User.query.get_or_404(uid)
    if request.method == "POST":
        text = (body().get("message") or "").strip()
        if not text:
            return jsonify({"error": "Message cannot be empty."}), 400
        m = ChatMessage(user_id=uid, sender_type="admin", message=text[:2000])
        db.session.add(m); db.session.commit()
        socketio.emit("new_chat_message", {"id": m.id, "user_id": uid, "sender_type": "admin", "message": m.message,
                                           "created_at": m.created_at.strftime("%d %b %I:%M %p")}, room=f"chat_user_{uid}")
        return jsonify({"message": {"id": m.id, "sender_type": "admin", "message": m.message, "created_at": iso(m.created_at)}}), 201
    msgs = ChatMessage.query.filter_by(user_id=uid).order_by(ChatMessage.created_at, ChatMessage.id).all()
    return jsonify({"user": {"id": u.id, "username": u.username, "email": u.email},
                    "messages": [{"id": m.id, "sender_type": m.sender_type, "message": m.message, "created_at": iso(m.created_at)} for m in msgs]})


# ------------------------------------------------------------------ community (as admin)
@admin_api_bp.route("/community", methods=["GET", "POST"])
@admin_required
def community():
    from app.routes.chat import COMMUNITY_GROUPS, _community_group_key
    if request.method == "POST":
        d = body()
        text = (d.get("message") or "").strip()
        if not text:
            return jsonify({"error": "Message cannot be empty."}), 400
        m = CommunityMessage(group_key=_community_group_key(d.get("group")), user_id=None, sender_name="Admin", is_admin=True, message=text[:2000])
        db.session.add(m); db.session.commit()
        socketio.emit("new_community_message", {"id": m.id, "group_key": m.group_key, "user_id": None, "sender_name": "Admin", "is_admin": True,
                                                "message": m.message, "created_at": m.created_at.strftime("%d %b %I:%M %p")}, room=f"community_{m.group_key}")
        return jsonify({"ok": True, "id": m.id}), 201
    key = _community_group_key(request.args.get("group"))
    counts = dict(db.session.query(CommunityMessage.group_key, func.count(CommunityMessage.id)).group_by(CommunityMessage.group_key).all())
    msgs = CommunityMessage.query.filter_by(group_key=key).order_by(CommunityMessage.created_at, CommunityMessage.id).limit(300).all()
    return jsonify({"groups": [dict(g, count=counts.get(g["key"], 0)) for g in COMMUNITY_GROUPS], "current": key,
                    "me": {"id": None, "name": "Admin", "is_admin": True},
                    "messages": [{"id": m.id, "user_id": m.user_id, "sender_name": m.sender_name, "is_admin": m.is_admin,
                                  "message": m.message, "created_at": iso(m.created_at)} for m in msgs]})


@admin_api_bp.delete("/community/<int:mid>")
@admin_required
def community_delete(mid):
    m = CommunityMessage.query.get_or_404(mid)
    db.session.delete(m); db.session.commit()
    return jsonify({"ok": True})
