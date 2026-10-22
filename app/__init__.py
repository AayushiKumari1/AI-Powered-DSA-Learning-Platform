from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import inspect, text
from app.extensions import db, mail, login_manager, socketio
from app.config import Config
from app.models.user import User  # 👈 Add this import
from app.models.topic import Topic,UserTopicProgress
from app.models.test_topic import test_topics
from app.models.test import Test
from app.models.test_question import TestQuestion
from app.models.coding_test import CodingTest
from app.models.coding_question import CodingQuestion   
from app.models.coding_question_progress import CodingQuestionProgress
from app.models.coding_test_topic import coding_test_topics
from app.models.coding_test_question import coding_test_questions
from app.models.coding_test_progress import CodingTestProgress          
from app.models.badge import Badge, UserBadge
from app.models.chat_message import ChatMessage
from app.models.community_message import CommunityMessage
from app.models.flash_note import FlashNote
from app.models.announcement import Announcement
from app.models.user_notification import UserNotification
from app.models.submission import Submission

from app.models.topic import UserTopicProgress  # 👈 Add this import
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    migrate = Migrate(app, db)

    # Flask-Login setup
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth.login"

    @login_manager.unauthorized_handler
    def _unauthorized():
        """JSON 401 for the React app / fetch calls, redirect for server-rendered pages."""
        from flask import request, jsonify, redirect, url_for
        wants_json = (
            request.path.startswith("/api/")
            or request.is_json
            or "application/json" in (request.headers.get("Accept") or "")
            or request.headers.get("X-Requested-With") == "fetch"
        )
        if wants_json:
            return jsonify({"error": "Sign in required"}), 401
        return redirect("/app/auth?next=" + request.path)
    login_manager.login_message_category = "info"

    # Register Blueprints
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.study import study_bp
    from app.routes.admin_coding import admin_coding_bp
    from app.routes.coding import coding_bp
    from app.routes.admin_coding_test import admin_coding_test_bp   
    from app.routes.coding_test import coding_test_bp
    from app.routes.badge import badge_bp
    from app.routes.chat import chat_bp
    from app.routes.flash_notes import flash_notes_bp
    from app.routes.notifications import notifications_bp
    from app.routes.api import api_bp
    from app.routes.admin_api import admin_api_bp
    from app.routes.spa import spa_bp



    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(admin_coding_bp)
    app.register_blueprint(coding_bp)
    app.register_blueprint(admin_coding_test_bp)
    app.register_blueprint(coding_test_bp)
    app.register_blueprint(badge_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(flash_notes_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(api_bp)   # JSON API for the React frontend
    app.register_blueprint(admin_api_bp)   # JSON API for the React admin console
    app.register_blueprint(spa_bp)   # serves frontend/dist at /app

    # Old server-rendered page URLs -> React pages (the Jinja templates were removed)
    from app.routes.legacy_redirects import register_legacy_redirects
    register_legacy_redirects(app)


    with app.app_context():
        ChatMessage.__table__.create(bind=db.engine, checkfirst=True)
        CommunityMessage.__table__.create(bind=db.engine, checkfirst=True)
        FlashNote.__table__.create(bind=db.engine, checkfirst=True)
        Announcement.__table__.create(bind=db.engine, checkfirst=True)
        UserNotification.__table__.create(bind=db.engine, checkfirst=True)
        CodingQuestionProgress.__table__.create(bind=db.engine, checkfirst=True)

        inspector = inspect(db.engine)
        community_columns = {column["name"] for column in inspector.get_columns("community_messages")}
        if "group_key" not in community_columns:
            with db.engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE community_messages "
                        "ADD COLUMN group_key VARCHAR(60) NOT NULL DEFAULT 'arrays'"
                    )
                )
                conn.execute(
                    text(
                        "UPDATE community_messages "
                        "SET group_key = 'arrays' "
                        "WHERE group_key IS NULL OR group_key = ''"
                    )
                )


    from flask import render_template
    from flask_login import current_user

    @app.context_processor
    def inject_nav_state():
        """Values the shared layouts (base.html / admin_base.html) need on every page."""
        unread = 0
        try:
            if current_user.is_authenticated:
                unread = (
                    UserNotification.query
                    .filter_by(user_id=current_user.id, is_removed=False, is_read=False)
                    .join(UserNotification.announcement)
                    .count()
                )
        except Exception:
            unread = 0
        return {"nav_unread_count": unread}

    @app.route("/")
    def home():
        """The React app (frontend/) is the learner UI; its landing page lives at /app/."""
        from flask import redirect
        return redirect("/app/")

    return app
