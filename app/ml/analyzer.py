# import os
# import joblib
# from collections import defaultdict

# # ---------------- LOAD MODEL ----------------
# MODEL_PATH = os.path.join(
#     os.path.dirname(__file__),
#     "topic_mastery_model.pkl"
# )

# model = joblib.load(MODEL_PATH)

# # ---------------- CONSTANTS ----------------
# LABEL_MAP = {
#     0: "Weak",
#     1: "Average",
#     2: "Strong"
# }

# TOPICS = [
#     "Arrays", "Strings", "Two Pointers", "Stack", "Queue",
#     "Linked List", "Binary Search", "Recursion", "Trees",
#     "Heap", "Graphs", "Dynamic Programming"
# ]

# EXPECTED_TIME = {
#     "easy": 60,
#     "medium": 120,
#     "hard": 240
# }

# MAX_TIME_CAP = 600

# PREREQ = {
#     "Arrays": [],
#     "Strings": ["Arrays"],
#     "Two Pointers": ["Arrays"],
#     "Stack": ["Arrays"],
#     "Queue": ["Arrays"],
#     "Linked List": ["Arrays"],
#     "Binary Search": ["Arrays"],
#     "Recursion": [],
#     "Trees": ["Recursion"],
#     "Heap": ["Arrays"],
#     "Graphs": ["Trees"],
#     "Dynamic Programming": ["Recursion"]
# }

# # ---------------- HELPERS ----------------
# def extract_topic(title, tags=None):
#     text = title.lower()
#     if tags:
#         text += " " + " ".join(tags).lower()

#     for t in TOPICS:
#         if t.lower() in text:
#             return t
#     return None


# def rule_based_level(accuracy):
#     if accuracy >= 0.75:
#         return 2
#     elif accuracy >= 0.4:
#         return 1
#     return 0


# # ---------------- NEW: CODE ANALYZER ----------------
# def analyze_code_quality(code):
#     issues = []

#     if not code:
#         return issues

#     if code.count("for") >= 2:
#         issues.append("Nested loops detected → high time complexity")

#     if "while" in code and "<" in code:
#         issues.append("Check loop boundary conditions")

#     if "=" in code and "==" not in code:
#         issues.append("Possible assignment instead of comparison")

#     if "def" in code and code.count("return") > 1:
#         issues.append("Recursive pattern detected")

#     return issues

# # --------------------------

# def detect_specific_issues(topic_data, code_issues):
#     issues = []
#     suggestions = []

#     # -------- Accuracy issues --------
#     if topic_data["medium_acc"] < 0.5:
#         issues.append("Struggling with medium-level problems")
#         suggestions.append("Practice more medium-level questions")

#     if topic_data["hard_acc"] < 0.3:
#         issues.append("Weak in hard problems")
#         suggestions.append("Focus on advanced problem-solving patterns")

#     # -------- Time issues --------
#     if topic_data["avg_time"] > 150:
#         issues.append("Taking too much time")
#         suggestions.append("Practice timed problem solving")

#     # -------- Code issues --------
#     if "Nested loops detected → high time complexity" in code_issues:
#         issues.append("Using inefficient nested loops")
#         suggestions.append("Learn optimization techniques like hashing")

#     if "Check loop boundary conditions" in code_issues:
#         issues.append("Loop boundary mistakes")
#         suggestions.append("Handle edge cases carefully")

#     if "Possible assignment instead of comparison" in code_issues:
#         issues.append("Incorrect condition logic")
#         suggestions.append("Revise comparison operators")

#     return issues, suggestions

# # ---------------- NEW: FEEDBACK GENERATOR ----------------
# def generate_topic_feedback(topic, data, issues, suggestions):
#     return f"""
# Topic: {topic}

# Accuracy: {round(data['accuracy']*100)}%
# Avg Time: {int(data['avg_time'])} sec

# Problems Identified:
# {"- " + "\n- ".join(issues) if issues else "No major issues"}

# How to Improve:
# {"- " + "\n- ".join(suggestions) if suggestions else "Keep practicing"}
# """

# # ---------------- MAIN ANALYZER ----------------
# def analyze_test(test, progress_map, code_map=None):

#     topic_stats = defaultdict(lambda: {
#         "attempted": 0,
#         "passed": 0,
#         "total_time": 0,
#         "easy": {"passed": 0, "total": 0},
#         "medium": {"passed": 0, "total": 0},
#         "hard": {"passed": 0, "total": 0},
#     })

#     code_issues_map = defaultdict(list)

#     # ---------- AGGREGATE ----------
#     for q in test.questions:
#         topic = extract_topic(q.title)
#         if not topic:
#             continue

#         p = progress_map.get(q.id)
#         if not p:
#             continue

#         diff = (q.difficulty or "").lower()
#         if diff not in EXPECTED_TIME:
#             continue

#         stats = topic_stats[topic]

#         time_taken = min(p.time_taken or 0, MAX_TIME_CAP)

#         stats["attempted"] += 1
#         stats["total_time"] += time_taken
#         stats[diff]["total"] += 1

#         if p.status == "Passed":
#             stats["passed"] += 1
#             stats[diff]["passed"] += 1

#         # -------- NEW: CODE ANALYSIS --------
#         if code_map and q.id in code_map:
#             issues = analyze_code_quality(code_map[q.id])
#             code_issues_map[topic].extend(issues)

#     # ---------- ANALYSIS ----------
#     analysis = {"Weak": [], "Average": [], "Strong": []}
#     topic_details = {}
#     topic_levels = {}
#     feedback = {}

#     for topic, s in topic_stats.items():
#         if s["attempted"] == 0:
#             continue

#         accuracy = s["passed"] / s["attempted"]
#         avg_time = s["total_time"] / s["attempted"]

#         def acc(d):
#             return d["passed"] / d["total"] if d["total"] else 0

#         easy_acc = acc(s["easy"])
#         medium_acc = acc(s["medium"])
#         hard_acc = acc(s["hard"])

#         time_pressure = EXPECTED_TIME["medium"] / avg_time if avg_time else 0
#         consistency = max(0.4, 1 - (hard_acc * 0.2))

#         only_easy = (
#             s["easy"]["total"] > 0 and
#             s["medium"]["total"] == 0 and
#             s["hard"]["total"] == 0
#         )

#         if only_easy and accuracy >= 0.8:
#             final_level = 1
#         else:
#             X = [[
#                 accuracy, avg_time, s["attempted"],
#                 easy_acc, medium_acc, hard_acc,
#                 time_pressure, consistency
#             ]]

#             ml_level = model.predict(X)[0]
#             rule_level = rule_based_level(accuracy)
#             final_level = max(ml_level, rule_level)

#         topic_levels[topic] = final_level
#         analysis[LABEL_MAP[final_level]].append(topic)

#         # -------- CONFIDENCE SCORE --------
#         confidence = round((accuracy * 0.6 + (1/(avg_time+1)) * 0.4), 2)

#         issues_list, suggestions_list = detect_specific_issues(
#         {
#             "medium_acc": medium_acc,
#             "hard_acc": hard_acc,
#             "avg_time": avg_time
#         },
#         code_issues_map[topic]
#     )

#         topic_details[topic] = {
#             "level": LABEL_MAP[final_level],
#             "accuracy": accuracy,
#             "avg_time": avg_time,
#             "confidence": confidence,
#             "issues": issues_list,
#             "suggestions": suggestions_list
#         }

#         feedback[topic] = generate_topic_feedback(
#             topic,
#             {
#                 "accuracy": accuracy,
#                 "avg_time": avg_time
#             },
#             issues_list,
#             suggestions_list
#         )

#     # ---------- RECOMMENDATION ----------
#     recommended_list = sorted(topic_levels, key=lambda x: topic_levels[x])

#     # ---------- PREREQ ----------
#     blocked = []
#     for topic, prereqs in PREREQ.items():
#         for p in prereqs:
#             if topic_levels.get(p, 2) == 0:
#                 blocked.append(topic)

#     return {
#         "analysis": analysis,
#         "details": topic_details,
#         "feedback": feedback,
#         "blocked": blocked,
#         "recommended": recommended_list[:3]  # top 3 weak topics
#     }

# # # # # # ==========================================================
# # # # # # FILE: app/utils/topic_mastery_analyzer.py
# # # # # # Build analyze_test V2
# # # # # # Hybrid ML + Rule Engine + Better Accuracy Logic
# # # # # # ==========================================================

# # # # # import os
# # # # # import joblib
# # # # # from collections import defaultdict

# # # # # # ==========================================================
# # # # # # LOAD MODEL
# # # # # # ==========================================================
# # # # # MODEL_PATH = os.path.join(
# # # # #     os.path.dirname(__file__),
# # # # #     "topic_mastery_model.pkl"
# # # # # )

# # # # # model = joblib.load(MODEL_PATH)

# # # # # # ==========================================================
# # # # # # LABELS
# # # # # # ==========================================================
# # # # # LABEL_MAP = {
# # # # #     0: "Weak",
# # # # #     1: "Average",
# # # # #     2: "Strong"
# # # # # }

# # # # # # ==========================================================
# # # # # # TOPICS
# # # # # # ==========================================================
# # # # # TOPICS = [
# # # # #     "Arrays",
# # # # #     "Strings",
# # # # #     "Two Pointers",
# # # # #     "Stack",
# # # # #     "Queue",
# # # # #     "Linked List",
# # # # #     "Binary Search",
# # # # #     "Recursion",
# # # # #     "Trees",
# # # # #     "Heap",
# # # # #     "Graphs",
# # # # #     "Dynamic Programming"
# # # # # ]

# # # # # # ==========================================================
# # # # # # EXPECTED TIME PER QUESTION
# # # # # # ==========================================================
# # # # # EXPECTED_TIME = {
# # # # #     "easy": 60,
# # # # #     "medium": 120,
# # # # #     "hard": 240
# # # # # }

# # # # # MAX_TIME_CAP = 600

# # # # # # ==========================================================
# # # # # # PREREQUISITES
# # # # # # ==========================================================
# # # # # PREREQ = {
# # # # #     "Arrays": [],
# # # # #     "Strings": ["Arrays"],
# # # # #     "Two Pointers": ["Arrays"],
# # # # #     "Stack": ["Arrays"],
# # # # #     "Queue": ["Arrays"],
# # # # #     "Linked List": ["Arrays"],
# # # # #     "Binary Search": ["Arrays"],
# # # # #     "Recursion": [],
# # # # #     "Trees": ["Recursion"],
# # # # #     "Heap": ["Arrays"],
# # # # #     "Graphs": ["Trees"],
# # # # #     "Dynamic Programming": ["Recursion"]
# # # # # }

# # # # # # ==========================================================
# # # # # # TOPIC EXTRACTOR
# # # # # # ==========================================================
# # # # # def extract_topic(title):
# # # # #     title = (title or "").lower()

# # # # #     for topic in TOPICS:
# # # # #         if topic.lower() in title:
# # # # #             return topic

# # # # #     return None


# # # # # # ==========================================================
# # # # # # RULE ENGINE
# # # # # # ==========================================================
# # # # # def rule_based_level(accuracy, attempted, hard_acc, avg_time):
# # # # #     if attempted < 2:
# # # # #         return 1

# # # # #     if accuracy >= 0.85 and hard_acc >= 0.55 and avg_time <= 180:
# # # # #         return 2

# # # # #     if accuracy >= 0.45:
# # # # #         return 1

# # # # #     return 0


# # # # # # ==========================================================
# # # # # # SAFE DIVISION
# # # # # # ==========================================================
# # # # # def safe_acc(passed, total):
# # # # #     return passed / total if total else 0


# # # # # # ==========================================================
# # # # # # MAIN ANALYZER V2
# # # # # # ==========================================================
# # # # # def analyze_test(test, progress_map):

# # # # #     # ------------------------------------------------------
# # # # #     # STORE TOPIC STATS
# # # # #     # ------------------------------------------------------
# # # # #     topic_stats = defaultdict(lambda: {
# # # # #         "attempted": 0,
# # # # #         "passed": 0,
# # # # #         "total_time": 0,

# # # # #         "easy": {"passed": 0, "total": 0},
# # # # #         "medium": {"passed": 0, "total": 0},
# # # # #         "hard": {"passed": 0, "total": 0},
# # # # #     })

# # # # #     # ------------------------------------------------------
# # # # #     # READ ALL QUESTIONS
# # # # #     # ------------------------------------------------------
# # # # #     for q in test.questions:

# # # # #         topic = extract_topic(q.title)
# # # # #         if not topic:
# # # # #             continue

# # # # #         progress = progress_map.get(q.id)
# # # # #         if not progress:
# # # # #             continue

# # # # #         diff = (q.difficulty or "").lower()
# # # # #         if diff not in EXPECTED_TIME:
# # # # #             continue

# # # # #         stats = topic_stats[topic]

# # # # #         time_taken = min(progress.time_taken or 0, MAX_TIME_CAP)

# # # # #         stats["attempted"] += 1
# # # # #         stats["total_time"] += time_taken
# # # # #         stats[diff]["total"] += 1

# # # # #         if progress.status == "Passed":
# # # # #             stats["passed"] += 1
# # # # #             stats[diff]["passed"] += 1

# # # # #     # ------------------------------------------------------
# # # # #     # FINAL OUTPUT
# # # # #     # ------------------------------------------------------
# # # # #     analysis = {
# # # # #         "Weak": [],
# # # # #         "Average": [],
# # # # #         "Strong": []
# # # # #     }

# # # # #     topic_details = {}
# # # # #     topic_levels = {}

# # # # #     # ------------------------------------------------------
# # # # #     # PER TOPIC ANALYSIS
# # # # #     # ------------------------------------------------------
# # # # #     for topic, s in topic_stats.items():

# # # # #         attempted = s["attempted"]

# # # # #         if attempted == 0:
# # # # #             continue

# # # # #         passed = s["passed"]

# # # # #         accuracy = passed / attempted
# # # # #         avg_time = s["total_time"] / attempted

# # # # #         easy_acc = safe_acc(
# # # # #             s["easy"]["passed"],
# # # # #             s["easy"]["total"]
# # # # #         )

# # # # #         medium_acc = safe_acc(
# # # # #             s["medium"]["passed"],
# # # # #             s["medium"]["total"]
# # # # #         )

# # # # #         hard_acc = safe_acc(
# # # # #             s["hard"]["passed"],
# # # # #             s["hard"]["total"]
# # # # #         )

# # # # #         # --------------------------------------------------
# # # # #         # NEW FEATURES
# # # # #         # --------------------------------------------------
# # # # #         speed_score = EXPECTED_TIME["medium"] / max(avg_time, 1)

# # # # #         difficulty_score = (
# # # # #             easy_acc * 0.2 +
# # # # #             medium_acc * 0.35 +
# # # # #             hard_acc * 0.45
# # # # #         )

# # # # #         growth_score = medium_acc - easy_acc

# # # # #         consistency = max(
# # # # #             0.4,
# # # # #             1 - (hard_acc * 0.2)
# # # # #         )

# # # # #         # --------------------------------------------------
# # # # #         # ML PREDICTION
# # # # #         # --------------------------------------------------
# # # # #         X = [[
# # # # #             accuracy,
# # # # #             avg_time,
# # # # #             attempted,
# # # # #             easy_acc,
# # # # #             medium_acc,
# # # # #             hard_acc,
# # # # #             speed_score,
# # # # #             consistency
# # # # #         ]]

# # # # #         try:
# # # # #             ml_level = int(model.predict(X)[0])
# # # # #         except:
# # # # #             ml_level = 1

# # # # #         # --------------------------------------------------
# # # # #         # RULE ENGINE
# # # # #         # --------------------------------------------------
# # # # #         rule_level = rule_based_level(
# # # # #             accuracy,
# # # # #             attempted,
# # # # #             hard_acc,
# # # # #             avg_time
# # # # #         )

# # # # #         # --------------------------------------------------
# # # # #         # FINAL LEVEL
# # # # #         # --------------------------------------------------
# # # # #         final_level = round((ml_level + rule_level) / 2)

# # # # #         # Promote if excellent hard accuracy
# # # # #         if hard_acc >= 0.75 and accuracy >= 0.75:
# # # # #             final_level = 2

# # # # #         # Demote if too slow
# # # # #         if avg_time > 420 and final_level == 2:
# # # # #             final_level = 1

# # # # #         # Too few attempts = avoid strong
# # # # #         if attempted < 3 and final_level == 2:
# # # # #             final_level = 1

# # # # #         label = LABEL_MAP[final_level]

# # # # #         topic_levels[topic] = final_level
# # # # #         analysis[label].append(topic)

# # # # #         # --------------------------------------------------
# # # # #         # WEAK REASON
# # # # #         # --------------------------------------------------
# # # # #         weak_reason = []

# # # # #         if accuracy < 0.45:
# # # # #             weak_reason.append("low accuracy")

# # # # #         if avg_time > 250:
# # # # #             weak_reason.append("slow solving speed")

# # # # #         if hard_acc < 0.30:
# # # # #             weak_reason.append("hard problems weak")

# # # # #         if attempted < 3:
# # # # #             weak_reason.append("low attempts")

# # # # #         if not weak_reason:
# # # # #             weak_reason.append("stable")

# # # # #         # --------------------------------------------------
# # # # #         # NEXT ACTION
# # # # #         # --------------------------------------------------
# # # # #         if final_level == 0:
# # # # #             next_action = f"Practice Easy {topic} problems first."
# # # # #         elif final_level == 1:
# # # # #             next_action = f"Move to Medium {topic} problems."
# # # # #         else:
# # # # #             next_action = f"Try Hard {topic} + contests."

# # # # #         # --------------------------------------------------
# # # # #         # STORE DETAILS
# # # # #         # --------------------------------------------------
# # # # #         topic_details[topic] = {
# # # # #             "level": label,
# # # # #             "accuracy": round(accuracy * 100, 1),
# # # # #             "avg_time": round(avg_time, 1),
# # # # #             "easy_acc": round(easy_acc * 100, 1),
# # # # #             "medium_acc": round(medium_acc * 100, 1),
# # # # #             "hard_acc": round(hard_acc * 100, 1),
# # # # #             "difficulty_score": round(difficulty_score * 100, 1),
# # # # #             "growth_score": round(growth_score * 100, 1),
# # # # #             "reason": ", ".join(weak_reason),
# # # # #             "next_action": next_action
# # # # #         }

# # # # #     # ------------------------------------------------------
# # # # #     # BLOCKED TOPICS
# # # # #     # ------------------------------------------------------
# # # # #     blocked = []

# # # # #     for topic, prereqs in PREREQ.items():

# # # # #         if topic not in topic_levels:
# # # # #             continue

# # # # #         for p in prereqs:
# # # # #             if topic_levels.get(p, 2) == 0:
# # # # #                 blocked.append(topic)
# # # # #                 break

# # # # #     # ------------------------------------------------------
# # # # #     # BEST RECOMMENDED TOPIC
# # # # #     # ------------------------------------------------------
# # # # #     recommended = None

# # # # #     for topic, lvl in topic_levels.items():
# # # # #         if lvl == 0:
# # # # #             recommended = topic
# # # # #             break

# # # # #     if not recommended:
# # # # #         for topic, lvl in topic_levels.items():
# # # # #             if lvl == 1:
# # # # #                 recommended = topic
# # # # #                 break

# # # # #     # ------------------------------------------------------
# # # # #     # OVERALL SCORE
# # # # #     # ------------------------------------------------------
# # # # #     if topic_levels:
# # # # #         overall_score = round(
# # # # #             sum(topic_levels.values()) /
# # # # #             len(topic_levels) * 50
# # # # #         )
# # # # #     else:
# # # # #         overall_score = 0

# # # # #     # ------------------------------------------------------
# # # # #     # RETURN
# # # # #     # ------------------------------------------------------
# # # # #     return {
# # # # #         "analysis": analysis,
# # # # #         "details": topic_details,
# # # # #         "blocked": blocked,
# # # # #         "recommended": recommended,
# # # # #         "overall_score": overall_score,
# # # # #         "model_version": "V2 Hybrid"
# # # # #     }




















# # ==========================================================
# # FILE: app/utils/topic_mastery_analyzer.py
# # VERSION: V4 PRODUCTION HYBRID (ML + RULE + BEHAVIOR + PWDE)
# # ==========================================================

# import os
# import joblib
# from collections import defaultdict, Counter

# # ---------------- LOAD MODEL ----------------
# MODEL_PATH = os.path.join(
#     os.path.dirname(__file__),
#     "topic_mastery_model.pkl"
# )

# model = joblib.load(MODEL_PATH)

# # ---------------- CONSTANTS ----------------
# LABEL_MAP = {0: "Weak", 1: "Average", 2: "Strong"}

# TOPICS = [
#     "Arrays", "Strings", "Two Pointers", "Stack", "Queue",
#     "Linked List", "Binary Search", "Recursion", "Trees",
#     "Heap", "Graphs", "Dynamic Programming"
# ]

# EXPECTED_TIME = {"easy": 60, "medium": 120, "hard": 240}
# MAX_TIME_CAP = 600

# PREREQ = {
#     "Arrays": [],
#     "Strings": ["Arrays"],
#     "Two Pointers": ["Arrays"],
#     "Stack": ["Arrays"],
#     "Queue": ["Arrays"],
#     "Linked List": ["Arrays"],
#     "Binary Search": ["Arrays"],
#     "Recursion": [],
#     "Trees": ["Recursion"],
#     "Heap": ["Arrays"],
#     "Graphs": ["Trees"],
#     "Dynamic Programming": ["Recursion"]
# }

# # ---------------- HELPERS ----------------
# def extract_topic(title):
#     title = (title or "").lower()
#     for t in TOPICS:
#         if t.lower() in title:
#             return t
#     return None


# def safe_div(a, b):
#     return a / b if b else 0


# # ---------------- RULE ENGINE ----------------
# def rule_based_level(accuracy, avg_time, hard_acc):
#     if accuracy >= 0.85 and hard_acc >= 0.5 and avg_time < 150:
#         return 2
#     elif accuracy >= 0.45:
#         return 1
#     return 0


# # ---------------- BEHAVIOR FEATURES ----------------
# def compute_behavior_features(progress):
#     return {
#         "retry": getattr(progress, "retry_count", 0),
#         "wrong": getattr(progress, "wrong_attempts", 0),
#         "hints": getattr(progress, "hint_usage", 0),
#     }


# # ==========================================================
# # 🧠 PERSONAL WEAKNESS ENGINE (IMPROVED)
# # ==========================================================
# def build_personal_weakness_profile(all_attempts):

#     weakness_counter = Counter()
#     weak_topics = Counter()

#     for a in all_attempts:

#         if a["accuracy"] < 0.5:
#             weakness_counter["Low Accuracy"] += 1
#             weak_topics[a["topic"]] += 1

#         if a["avg_time"] > 180:
#             weakness_counter["Slow Problem Solving"] += 1

#         if a["hard_acc"] < 0.3:
#             weakness_counter["Weak in Hard Problems"] += 1

#         if a["consistency"] < 0.6:
#             weakness_counter["Inconsistent Performance"] += 1

#     return {
#         "weakness_summary": dict(weakness_counter),
#         "weak_topics": dict(weak_topics.most_common(5))
#     }


# # ==========================================================
# # MAIN ANALYZER (V4)
# # ==========================================================
# def analyze_test(test, progress_map):

#     topic_stats = defaultdict(lambda: {
#         "attempted": 0,
#         "passed": 0,
#         "total_time": 0,
#         "easy": {"passed": 0, "total": 0},
#         "medium": {"passed": 0, "total": 0},
#         "hard": {"passed": 0, "total": 0},

#         # behavior
#         "retry": 0,
#         "wrong": 0,
#         "hints": 0
#     })

#     # ---------------- COLLECT DATA ----------------
#     for q in test.questions:

#         topic = extract_topic(q.title)
#         if not topic:
#             continue

#         p = progress_map.get(q.id)
#         if not p:
#             continue

#         diff = (q.difficulty or "").lower()
#         if diff not in EXPECTED_TIME:
#             continue

#         stats = topic_stats[topic]
#         time_taken = min(p.time_taken or 0, MAX_TIME_CAP)

#         stats["attempted"] += 1
#         stats["total_time"] += time_taken
#         stats[diff]["total"] += 1

#         if p.status == "Passed":
#             stats["passed"] += 1
#             stats[diff]["passed"] += 1

#         bf = compute_behavior_features(p)
#         stats["retry"] += bf["retry"]
#         stats["wrong"] += bf["wrong"]
#         stats["hints"] += bf["hints"]

#     # ---------------- OUTPUT ----------------
#     analysis = {"Weak": [], "Average": [], "Strong": []}
#     topic_details = {}
#     topic_levels = {}
#     all_attempts = []

#     # ---------------- PER TOPIC ----------------
#     for topic, s in topic_stats.items():

#         if s["attempted"] == 0:
#             continue

#         accuracy = safe_div(s["passed"], s["attempted"])
#         avg_time = safe_div(s["total_time"], s["attempted"])

#         easy_acc = safe_div(s["easy"]["passed"], s["easy"]["total"])
#         medium_acc = safe_div(s["medium"]["passed"], s["medium"]["total"])
#         hard_acc = safe_div(s["hard"]["passed"], s["hard"]["total"])

#         # ---------------- ADVANCED FEATURES ----------------
#         speed_score = EXPECTED_TIME["medium"] / max(avg_time, 1)

#         difficulty_score = (
#             easy_acc * 0.2 +
#             medium_acc * 0.35 +
#             hard_acc * 0.45
#         )

#         consistency = max(0.4, 1 - (hard_acc * 0.2))

#         # ---------------- ML ----------------
#         X = [[
#             accuracy,
#             avg_time,
#             s["attempted"],
#             easy_acc,
#             medium_acc,
#             hard_acc,
#             speed_score,
#             consistency,
#             s["retry"],
#             s["wrong"],
#             s["hints"]
#         ]]

#         try:
#             ml_level = int(model.predict(X)[0])
#         except:
#             ml_level = 1

#         rule_level = rule_based_level(accuracy, avg_time, hard_acc)

#         # ---------------- SMART FUSION ----------------
#         final_level = round(0.6 * ml_level + 0.4 * rule_level)

#         # ---------------- BOOST / PENALTY ----------------
#         if hard_acc > 0.75 and accuracy > 0.75:
#             final_level = min(2, final_level + 1)

#         if avg_time > 400:
#             final_level = max(0, final_level - 1)

#         if s["attempted"] < 3:
#             final_level = min(final_level, 1)

#         topic_levels[topic] = final_level
#         analysis[LABEL_MAP[final_level]].append(topic)

#         # ---------------- STORE ATTEMPTS ----------------
#         all_attempts.append({
#             "topic": topic,
#             "accuracy": accuracy,
#             "avg_time": avg_time,
#             "hard_acc": hard_acc,
#             "consistency": consistency
#         })

#         # ---------------- DETAILS ----------------
#         topic_details[topic] = {
#             "level": LABEL_MAP[final_level],
#             "accuracy": round(accuracy, 2),
#             "avg_time": round(avg_time, 1),
#             "easy_acc": round(easy_acc, 2),
#             "medium_acc": round(medium_acc, 2),
#             "hard_acc": round(hard_acc, 2),
#             "difficulty_score": round(difficulty_score, 2),
#             "speed_score": round(speed_score, 2),
#             "retry": s["retry"],
#             "wrong_attempts": s["wrong"],
#             "hint_usage": s["hints"]
#         }

#     # ======================================================
#     # 🧠 PERSONAL WEAKNESS PROFILE
#     # ======================================================
#     pw_profile = build_personal_weakness_profile(all_attempts)

#     # ---------------- BLOCKED ----------------
#     blocked = []
#     for topic, prereqs in PREREQ.items():
#         for p in prereqs:
#             if topic_levels.get(p, 2) == 0:
#                 blocked.append(topic)

#     # ---------------- RECOMMENDATION ----------------
#     recommended = sorted(topic_levels, key=lambda x: topic_levels[x])[:3]

#     # ---------------- OVERALL SCORE ----------------
#     if topic_levels:
#         overall_score = round(
#             sum(topic_levels.values()) / len(topic_levels) * 50
#         )
#     else:
#         overall_score = 0

#     # ---------------- RETURN ----------------
#     return {
#         "analysis": analysis,
#         "details": topic_details,
#         "blocked": blocked,
#         "recommended": recommended,
#         "overall_score": overall_score,
#         "personal_weakness_profile": pw_profile,
#         "model_version": "V4-Production-Hybrid"
#     }


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