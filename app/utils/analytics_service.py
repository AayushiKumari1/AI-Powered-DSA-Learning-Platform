# import sqlite3

# def get_user_context(user_id):

#     # Example dynamic data from DB
#     return {
#         "weak_topics": ["DP", "Graphs"],
#         "next_topic": "Practice Sliding Window this week.",
#         "mistakes": "Recent mistakes: recursion base case, hashmap edge case.",
#         "slowest": "Longest time taken: Graph traversal problem.",
#         "avg_score": 72,
#         "consistency": "5 days streak"
#     }



"""
analytics_service.py — Real user context pulled from DB for chatbot personalization.
"""

def get_user_context(user_id):
    try:
        from app.extensions import db
        from app.models.user import User
        from app.models.topic import UserTopicProgress
        from app.models.coding_question_progress import CodingQuestionProgress
        from app.models.coding_question import CodingQuestion
        from sqlalchemy import func

        user = User.query.get(user_id)
        if not user:
            return _empty_context()

        # Completed topics count
        completed = UserTopicProgress.query.filter_by(
            user_id=user_id, completed=True
        ).count()

        # Total topics
        from app.models.topic import Topic
        total_topics = Topic.query.count()

        # Quiz pass rate (approximate avg score)
        passed_quizzes = UserTopicProgress.query.filter_by(
            user_id=user_id, quiz_passed=True
        ).count()
        total_attempted = UserTopicProgress.query.filter_by(user_id=user_id).count()
        avg_score = round((passed_quizzes / total_attempted * 100) if total_attempted else 0)

        # Weak topics — topics visited but quiz not passed
        weak_progresses = UserTopicProgress.query.filter_by(
            user_id=user_id, quiz_passed=False, completed=False
        ).all()
        from app.models.topic import Topic
        weak_topics = []
        for p in weak_progresses[:5]:
            topic = Topic.query.get(p.topic_id)
            if topic:
                weak_topics.append(topic.title)

        # Next topic — first topic not yet started
        started_ids = {p.topic_id for p in UserTopicProgress.query.filter_by(user_id=user_id).all()}
        next_topic_obj = Topic.query.filter(~Topic.id.in_(started_ids)).first() if started_ids else Topic.query.first()
        next_topic = next_topic_obj.title if next_topic_obj else "Arrays"

        # Streak — consecutive days with activity (approximate via last_accessed_at)
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        streak = 0
        for delta in range(30):
            day = today - timedelta(days=delta)
            day_start = datetime(day.year, day.month, day.day)
            day_end   = datetime(day.year, day.month, day.day, 23, 59, 59)
            activity = UserTopicProgress.query.filter(
                UserTopicProgress.user_id == user_id,
                UserTopicProgress.last_accessed_at >= day_start,
                UserTopicProgress.last_accessed_at <= day_end
            ).first()
            if activity:
                streak += 1
            elif delta > 0:
                break

        # Slowest topic (most time spent but not completed)
        slowest_progress = UserTopicProgress.query.filter_by(
            user_id=user_id, completed=False
        ).order_by(UserTopicProgress.total_time_spent.desc()).first()
        slowest = "N/A"
        if slowest_progress:
            t = Topic.query.get(slowest_progress.topic_id)
            if t:
                slowest = t.title

        return {
            "xp": user.xp,
            "completed_topics": completed,
            "total_topics": total_topics,
            "avg_score": avg_score,
            "weak_topics": weak_topics,
            "next_topic": next_topic,
            "streak": streak,
            "slowest": slowest,
        }

    except Exception:
        return _empty_context()


def _empty_context():
    return {
        "xp": 0,
        "completed_topics": 0,
        "total_topics": 0,
        "avg_score": 0,
        "weak_topics": [],
        "next_topic": "Arrays",
        "streak": 0,
        "slowest": "N/A",
    }