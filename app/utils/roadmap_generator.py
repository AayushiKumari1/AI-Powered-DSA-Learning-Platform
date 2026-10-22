from collections import defaultdict
from app.models.submission import Submission
from app.models.coding_question import CodingQuestion
from app.routes.coding import _infer_topic_key

def generate_user_roadmap(user_id):
    submissions = Submission.query.filter_by(user_id=user_id).all()

    topic_stats = defaultdict(lambda: {"attempts": 0, "passed": 0})

    for sub in submissions:
        question = CodingQuestion.query.get(sub.question_id)
        if not question:
            continue

        topic = _infer_topic_key(question)

        topic_stats[topic]["attempts"] += 1
        topic_stats[topic]["passed"] += sub.passed

    roadmap = []

    for topic, stats in topic_stats.items():
        attempts = stats["attempts"]
        passed = stats["passed"]

        success_rate = passed / attempts if attempts > 0 else 0

        if success_rate < 0.4:
            level = "Weak"
        elif success_rate < 0.75:
            level = "Average"
        else:
            level = "Strong"

        roadmap.append({
            "topic": topic,
            "success_rate": round(success_rate * 100, 1),
            "level": level
        })

    # sort weakest first
    roadmap.sort(key=lambda x: x["success_rate"])

    return roadmap