import os
import joblib
from collections import defaultdict

MODEL_PATH = os.path.join(os.path.dirname(__file__), "topic_mastery_model.pkl")
model = joblib.load(MODEL_PATH)

LABEL_MAP = {0: "Weak", 1: "Average", 2: "Strong"}

TOPICS = [
    "Arrays", "Strings", "Two Pointers", "Stack", "Queue",
    "Linked List", "Binary Search", "Recursion", "Trees",
    "Heap", "Graphs", "Dynamic Programming"
]

EXPECTED_TIME = {"easy": 60, "medium": 120, "hard": 240}
MAX_TIME_CAP = 600

PREREQ = {
    "Arrays": [],
    "Strings": ["Arrays"],
    "Two Pointers": ["Arrays"],
    "Stack": ["Arrays"],
    "Queue": ["Arrays"],
    "Linked List": ["Arrays"],
    "Binary Search": ["Arrays"],
    "Recursion": [],
    "Trees": ["Recursion"],
    "Heap": ["Arrays"],
    "Graphs": ["Trees"],
    "Dynamic Programming": ["Recursion"]
}

# ---------------- HELPERS ----------------
def extract_topic(title):
    title = (title or "").lower()
    for t in TOPICS:
        if t.lower() in title:
            return t
    return None


def rule_based_level(acc):
    if acc >= 0.75:
        return 2
    elif acc >= 0.4:
        return 1
    return 0


def safe_div(a, b):
    return a / b if b else 0


# =========================================================
# 🔥 PERSONAL WEAKNESS DETECTION ENGINE
# =========================================================
def detect_weakness(topic, stats):
    weaknesses = []

    acc = stats["accuracy"]
    avg_time = stats["avg_time"]
    hard_acc = stats["hard_acc"]
    medium_acc = stats["medium_acc"]
    attempts = stats["attempted"]

    # Accuracy weakness
    if acc < 0.5:
        weaknesses.append({
            "type": "LOW_ACCURACY",
            "message": "You are failing more than half of the problems",
            "fix": "Revise basic patterns and solve easy problems again"
        })

    # Speed weakness
    if avg_time > 180:
        weaknesses.append({
            "type": "SLOW_SPEED",
            "message": "You are taking too much time",
            "fix": "Practice timed problem solving (15-20 min limit)"
        })

    # Hard problem weakness
    if hard_acc < 0.3:
        weaknesses.append({
            "type": "HARD_PROBLEM_WEAK",
            "message": "Hard problems are not clear to you",
            "fix": "Focus on pattern recognition (DP, Graph templates)"
        })

    # Medium plateau
    if medium_acc < 0.6 and acc > 0.5:
        weaknesses.append({
            "type": "MEDIUM_PLATEAU",
            "message": "You are stuck at medium level",
            "fix": "Practice mixed difficulty sets"
        })

    # Low attempts
    if attempts < 3:
        weaknesses.append({
            "type": "LOW_DATA",
            "message": "Not enough practice data",
            "fix": "Solve at least 5–10 problems per topic"
        })

    return weaknesses


# =========================================================
# MAIN ANALYZER (UPDATED)
# =========================================================
def analyze_test(test, progress_map, code_map=None):

    topic_stats = defaultdict(lambda: {
        "attempted": 0,
        "passed": 0,
        "total_time": 0,
        "easy": {"p": 0, "t": 0},
        "medium": {"p": 0, "t": 0},
        "hard": {"p": 0, "t": 0},
    })

    # ---------------- COLLECT DATA ----------------
    for q in test.questions:
        topic = extract_topic(q.title)
        if not topic:
            continue

        p = progress_map.get(q.id)
        if not p:
            continue

        diff = (q.difficulty or "").lower()
        if diff not in EXPECTED_TIME:
            continue

        stats = topic_stats[topic]

        time_taken = min(p.time_taken or 0, MAX_TIME_CAP)

        stats["attempted"] += 1
        stats["total_time"] += time_taken
        stats[diff]["t"] += 1

        if p.status == "Passed":
            stats["passed"] += 1
            stats[diff]["p"] += 1

    analysis = {"Weak": [], "Average": [], "Strong": []}
    topic_details = {}
    topic_levels = {}
    weakness_report = {}

    # ---------------- ANALYZE ----------------
    for topic, s in topic_stats.items():
        if s["attempted"] == 0:
            continue

        accuracy = safe_div(s["passed"], s["attempted"])
        avg_time = safe_div(s["total_time"], s["attempted"])

        easy_acc = safe_div(s["easy"]["p"], s["easy"]["t"])
        medium_acc = safe_div(s["medium"]["p"], s["medium"]["t"])
        hard_acc = safe_div(s["hard"]["p"], s["hard"]["t"])

        time_pressure = EXPECTED_TIME["medium"] / (avg_time + 1)
        consistency = max(0.4, 1 - hard_acc * 0.2)

        X = [[
            accuracy,
            avg_time,
            s["attempted"],
            easy_acc,
            medium_acc,
            hard_acc,
            time_pressure,
            consistency
        ]]

        ml_level = model.predict(X)[0]
        rule_level = rule_based_level(accuracy)
        final_level = max(ml_level, rule_level)

        topic_levels[topic] = final_level
        analysis[LABEL_MAP[final_level]].append(topic)

        # ---------------- CORE STATS ----------------
        stats_obj = {
            "accuracy": accuracy,
            "avg_time": avg_time,
            "hard_acc": hard_acc,
            "medium_acc": medium_acc,
            "attempted": s["attempted"]
        }

        # ---------------- WEAKNESS ENGINE ----------------
        weaknesses = detect_weakness(topic, stats_obj)

        weakness_report[topic] = weaknesses

        topic_details[topic] = {
            "level": LABEL_MAP[final_level],
            "accuracy": accuracy,
            "avg_time": avg_time,
            "medium_acc": medium_acc,
            "hard_acc": hard_acc,
            "weaknesses": weaknesses
        }

    # ---------------- RECOMMENDATION ----------------
    sorted_topics = sorted(topic_levels, key=lambda x: topic_levels[x])

    return {
        "analysis": analysis,
        "details": topic_details,
        "weakness_report": weakness_report,
        "recommended": sorted_topics[:3]
    }

# =========================================================
# 🔥 ADAPTIVE LEARNING PATH GENERATOR
# =========================================================
def generate_learning_path(all_questions, analysis_result):
    weakness_report = analysis_result["weakness_report"]
    topic_levels = analysis_result["analysis"]

    weak_topics = analysis_result["analysis"]["Weak"]
    avg_topics = analysis_result["analysis"]["Average"]

    learning_path = []

    def score(q):
        topic = extract_topic(q.title)

        if topic in weak_topics:
            base = 100
        elif topic in avg_topics:
            base = 60
        else:
            base = 30

        difficulty = (q.difficulty or "").lower()
        diff_score = {"easy": 10, "medium": 20, "hard": 30}.get(difficulty, 0)

        return base + diff_score

    sorted_questions = sorted(all_questions, key=score, reverse=True)

    for q in sorted_questions:
        if len(learning_path) >= 10:
            break

        learning_path.append({
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "reason": "Based on your weak topics + ML prediction"
        })

    return learning_path    
