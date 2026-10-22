"""
The UI lives in the React app (frontend/, served at /app). The old server-rendered
pages were removed; their URLs now redirect to the matching React page so old
links and bookmarks keep working.

Only GET page requests are redirected. JSON endpoints the React app still calls
(POST /coding/run, /coding/submit, /study/<id>/track-time, /coding-tests/submit-result,
/badges/equip|unequip, /chat/chatbot, DELETE /coding/delete_submission/<id>) are untouched.
"""
from flask import redirect, request, session

A = "/app"

# endpoint -> function(view_args, query_args) -> React URL
PAGES = {
    # learner
    "auth.login": lambda v, q: f"{A}/auth" + (f"?next={q['next']}" if q.get("next") else ""),
    "auth.signup": lambda v, q: f"{A}/auth?mode=signup",
    "auth.dashboard": lambda v, q: f"{A}/dashboard",
    "auth.progress_analytics": lambda v, q: f"{A}/analytics",
    "notifications.index": lambda v, q: f"{A}/notifications",
    "study.all_topics": lambda v, q: f"{A}/learn" + (f"?search={q['search']}" if q.get("search") else ""),
    "study.topic_detail": lambda v, q: f"{A}/learn/{v['topic_id']}",
    "study.topic_quiz": lambda v, q: f"{A}/learn/{v['topic_id']}/quiz",
    "coding.all_questions": lambda v, q: f"{A}/practice",
    "coding.coding_page": lambda v, q: f"{A}/practice/{v['id']}",
    "coding.submission_history": lambda v, q: f"{A}/practice/{v['question_id']}/submissions",
    "coding.view_analysis": lambda v, q: f"{A}/practice/{v['question_id']}/analysis",
    "coding_test.list_tests": lambda v, q: f"{A}/tests",
    "coding_test.test_overview": lambda v, q: f"{A}/tests/{v['test_id']}",
    "coding_test.solve_question": lambda v, q: f"{A}/tests/{v['test_id']}/solve/{v['index']}",
    "coding_test.result": lambda v, q: f"{A}/tests/{v['test_id']}/result",
    "badge.badge_collection": lambda v, q: f"{A}/dashboard",
    "chat.user_chat": lambda v, q: f"{A}/mentor",
    "chat.community": lambda v, q: (f"{A}/admin/community" if session.get("admin_logged_in") else f"{A}/community")
                                   + (f"?group={q['group']}" if q.get("group") else ""),
    "flash_notes.index": lambda v, q: f"{A}/notes",
    "flash_notes.edit": lambda v, q: f"{A}/notes",
    # admin
    "admin.admin_login": lambda v, q: f"{A}/admin/login",
    "admin.dashboard": lambda v, q: f"{A}/admin",
    "admin.analytics": lambda v, q: f"{A}/admin/learners",
    "admin.topic_analytics": lambda v, q: f"{A}/admin/topic-analytics",
    "admin.user_analytics": lambda v, q: f"{A}/admin/learners/{v['user_id']}",
    "admin.user_activity": lambda v, q: f"{A}/admin/learners/{v['user_id']}",
    "admin.all_topics": lambda v, q: f"{A}/admin/topics",
    "admin.add_topic": lambda v, q: f"{A}/admin/topics/new",
    "admin.announcements": lambda v, q: f"{A}/admin/announcements",
    "admin_coding.dashboard": lambda v, q: f"{A}/admin/problems",
    "admin_coding.add_question": lambda v, q: f"{A}/admin/problems/new",
    "admin_coding_test.dashboard": lambda v, q: f"{A}/admin/tests",
    "admin_coding_test.create_test": lambda v, q: f"{A}/admin/tests/new",
    "chat.admin_inbox": lambda v, q: f"{A}/admin/inbox" + (f"?user={q['user_id']}" if q.get("user_id") else ""),
    # these used to delete on a plain GET link; deletion now happens via DELETE /api/admin/...
    "admin.delete_topic": lambda v, q: f"{A}/admin/topics",
    "admin_coding.delete_question": lambda v, q: f"{A}/admin/problems",
}


# Non-API write endpoints the React app still calls. Every other write endpoint outside
# /api was a form handler for a removed HTML page and has an /api/... replacement.
KEEP_WRITE = {
    "coding.run_code", "coding.submit_code", "coding.delete_submission", "study.track_time",
    "coding_test.submit_result", "badge.equip_badge", "badge.unequip_badge", "chat.chatbot",
}
# where each retired form handler now lives (shown in the 410 response)
REPLACED_BY = {
    "auth.login": "POST /api/auth/login", "auth.signup": "POST /api/auth/signup",
    "admin.admin_login": "POST /api/admin/login", "admin.add_topic": "POST /api/admin/topics",
    "admin.upload_topics_csv": "POST /api/admin/topics/upload", "admin.announcements": "POST /api/admin/announcements",
    "admin_coding.add_question": "POST /api/admin/problems", "admin_coding.upload_csv": "POST /api/admin/problems/upload",
    "admin_coding_test.create_test": "POST /api/admin/tests", "admin_coding_test.delete_test": "DELETE /api/admin/tests/<id>",
    "chat.user_send": "POST /api/chat/messages", "chat.admin_send": "POST /api/admin/inbox/<user_id>",
    "chat.community_send": "POST /api/community", "flash_notes.create": "POST /api/notes",
    "flash_notes.edit": "PUT /api/notes/<id>", "flash_notes.delete": "DELETE /api/notes/<id>",
    "notifications.mark_read": "POST /api/notifications/<id>/read", "notifications.remove": "POST /api/notifications/<id>/remove",
    "notifications.read_all": "POST /api/notifications/read-all", "study.toggle_bookmark": "POST /api/topics/<id>/bookmark",
    "study.complete_topic": "POST /api/topics/<id>/complete", "study.submit_quiz": "POST /api/topics/<id>/quiz",
}


def register_legacy_redirects(app):
    from flask import jsonify

    @app.before_request
    def _legacy_page_redirect():
        ep = request.endpoint
        if request.method == "GET":
            if ep in PAGES:
                return redirect(PAGES[ep](request.view_args or {}, request.args), code=302)
            return None
        if ep in REPLACED_BY and ep not in KEEP_WRITE:
            return jsonify({"error": "This endpoint was retired with the old HTML pages.", "use": REPLACED_BY[ep]}), 410
        return None

    from jinja2 import TemplateNotFound  # noqa: E402

    @app.errorhandler(TemplateNotFound)
    def _removed_template(_err):
        # an old form handler tried to render a removed page: send the user to the React page instead
        fn = PAGES.get(request.endpoint)
        target = fn(request.view_args or {}, request.args) if fn else f"{A}/"
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "This page moved to the React app", "location": target}), 410
        return redirect(target, code=303)

    @app.after_request
    def _logout_redirects(resp):
        # old logout routes redirected to the removed login pages
        if request.endpoint == "auth.logout" and resp.status_code in (301, 302):
            resp.headers["Location"] = f"{A}/auth"
        if request.endpoint == "admin.logout" and resp.status_code in (301, 302):
            resp.headers["Location"] = f"{A}/admin/login"
        return resp
