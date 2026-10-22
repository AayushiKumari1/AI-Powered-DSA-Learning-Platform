from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.coding_question import CodingQuestion
from app.models.coding_question_progress import CodingQuestionProgress
from app.extensions import db
import requests
import json
import re
import time
from sqlalchemy import case, func, or_

coding_bp = Blueprint("coding", __name__, url_prefix="/coding")

CODING_QUESTION_XP = 10

LANGUAGE_CONFIG = {
    "python": {"id": 71},
    "cpp": {"id": 54},
    "java": {"id": 62}
}

def _build_files(language, code):
    if language == "java":
        match = re.search(r"public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)", code)
        class_name = match.group(1) if match else "Main"
        return [{"name": f"{class_name}.java", "content": code}]

    extension_map = {
        "python": "py",
        "cpp": "cpp",
    }
    extension = extension_map.get(language, language)
    return [{"name": f"main.{extension}", "content": code}]


def _extract_output(result):
    parts = []

    for key in ("stdout", "stderr", "compile_output", "message"):
        value = result.get(key)
        if value:
            parts.append(value)

    if not parts:
        return "No output returned."

    return "\n".join(parts).strip()


def _runner_request(payload):
    runner_url = current_app.config["CODE_RUNNER_URL"]

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        runner_url,
        json=payload,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()
    return response.json()


def _calculate_performance_rating(passed, total, solve_time_seconds, avg_case_time_ms):
    if total <= 0:
        return 0, "No attempts"

    pass_rate = passed / total
    correctness_score = pass_rate * 5.5

    if solve_time_seconds <= 45:
        solve_time_score = 1.5
        solve_time_label = "Very fast"
    elif solve_time_seconds <= 180:
        solve_time_score = 3.0
        solve_time_label = "Balanced"
    elif solve_time_seconds <= 420:
        solve_time_score = 2.4
        solve_time_label = "Steady"
    elif solve_time_seconds <= 900:
        solve_time_score = 1.4
        solve_time_label = "Slow"
    else:
        solve_time_score = 0.8
        solve_time_label = "Very slow"

    if avg_case_time_ms <= 250:
        execution_score = 1.5
        execution_label = "Efficient runtime"
    elif avg_case_time_ms <= 1000:
        execution_score = 1.2
        execution_label = "Normal runtime"
    elif avg_case_time_ms <= 3000:
        execution_score = 0.8
        execution_label = "Heavy runtime"
    else:
        execution_score = 0.4
        execution_label = "Very heavy runtime"

    consistency_bonus = 0
    if passed == total:
        if 60 <= solve_time_seconds <= 420:
            consistency_bonus = 0.5
        elif solve_time_seconds > 900:
            consistency_bonus = -0.5

    raw_score = correctness_score + solve_time_score + execution_score + consistency_bonus
    rating = max(0, min(10, round(raw_score)))

    if pass_rate == 0:
        label = "Needs major improvement"
    elif rating >= 9:
        label = "Excellent"
    elif rating >= 7:
        label = "Strong"
    elif rating >= 5:
        label = "Average"
    else:
        label = "Needs improvement"

    return rating, f"{label} | {solve_time_label}, {execution_label}"


def _infer_topic_key(question):
    title = (question.title or "").strip().lower()
    description = (question.description or "").strip().lower()
    haystack = f"{title} {description}"

    topic_aliases = {
        "array": ["array", "arrays", "prefix sum", "sliding window"],
        "string": ["string", "strings", "palindrome", "anagram"],
        "stack": ["stack", "bracket", "parentheses", "monotonic"],
        "queue": ["queue", "fifo"],
        "linked list": ["linked list", "list node", "node"],
        "binary search": ["binary search", "sorted array", "logn"],
        "recursion": ["recursion", "recursive", "backtracking"],
        "tree": ["tree", "binary tree", "depth", "traversal"],
        "heap": ["heap", "priority queue", "kth largest"],
        "graph": ["graph", "connected component", "bfs", "dfs", "path"],
        "dynamic programming": ["dynamic programming", "dp", "memoization", "tabulation"],
    }

    for topic_key, aliases in topic_aliases.items():
        if any(alias in haystack for alias in aliases):
            return topic_key

    return "general"


def _topic_recommendation_pack(topic_key):
    packs = {
        "array": {
            "label": "Array mastery",
            "next_steps": [
                "Practice array traversal and indexing without looking at notes.",
                "Move to prefix sums and subarray patterns.",
                "Try two pointers on sorted arrays after this.",
            ],
            "focus_message": "Focus on arrays first: indexing, traversal, and dry-running loops step by step.",
            "search_terms": ["array", "arrays", "prefix sum", "sliding window", "two pointers"],
        },
        "string": {
            "label": "String mastery",
            "next_steps": [
                "Review character frequency counting and string traversal.",
                "Practice palindrome and anagram problems.",
                "Then move to pattern matching and two-pointer string problems.",
            ],
            "focus_message": "Focus on strings first: characters, loops, and frequency maps.",
            "search_terms": ["string", "strings", "palindrome", "anagram"],
        },
        "stack": {
            "label": "Stack mastery",
            "next_steps": [
                "Practice stack push/pop behavior until it feels natural.",
                "Try bracket matching and expression problems.",
                "Then explore monotonic stack questions.",
            ],
            "focus_message": "Focus on stack thinking: last in, first out, and keeping track of open/close states.",
            "search_terms": ["stack", "bracket", "parentheses", "monotonic"],
        },
        "queue": {
            "label": "Queue mastery",
            "next_steps": [
                "Practice first in, first out simulations.",
                "Try queue-based string and window problems.",
                "Then move toward BFS-style thinking.",
            ],
            "focus_message": "Focus on queues first: order of arrival, simulation, and FIFO behavior.",
            "search_terms": ["queue", "fifo"],
        },
        "linked list": {
            "label": "Linked list mastery",
            "next_steps": [
                "Review pointer movement one node at a time.",
                "Practice reversal, merging, and slow-fast pointer problems.",
                "Then work on cycle and split-list questions.",
            ],
            "focus_message": "Focus on linked list basics: nodes, pointers, and careful pointer updates.",
            "search_terms": ["linked list", "node", "pointer"],
        },
        "binary search": {
            "label": "Binary search mastery",
            "next_steps": [
                "Practice search on sorted arrays until the mid logic is automatic.",
                "Move to lower bound and upper bound style problems.",
                "Then try answer-space binary search.",
            ],
            "focus_message": "Focus on binary search basics: sorted input, mid calculation, and boundary changes.",
            "search_terms": ["binary search", "sorted array", "logn"],
        },
        "recursion": {
            "label": "Recursion mastery",
            "next_steps": [
                "Practice base case and recursive step identification.",
                "Try factorial, subsequences, and backtracking patterns.",
                "Then connect recursion to tree traversal.",
            ],
            "focus_message": "Focus on recursion basics: base case, recursion tree, and stack flow.",
            "search_terms": ["recursion", "recursive", "backtracking"],
        },
        "tree": {
            "label": "Tree mastery",
            "next_steps": [
                "Practice depth-first traversal patterns.",
                "Try height, diameter, and level-order problems.",
                "Then explore tree + recursion combinations.",
            ],
            "focus_message": "Focus on trees first: traversal, depth, and parent-child relationships.",
            "search_terms": ["tree", "binary tree", "traversal", "depth"],
        },
        "heap": {
            "label": "Heap mastery",
            "next_steps": [
                "Practice heap push/pop and priority selection.",
                "Try top-k, kth largest, and stream problems.",
                "Then work on min-heap and max-heap variations.",
            ],
            "focus_message": "Focus on heaps first: priority ordering and top-k style selection.",
            "search_terms": ["heap", "priority queue", "kth largest"],
        },
        "graph": {
            "label": "Graph mastery",
            "next_steps": [
                "Practice graph traversal with BFS and DFS.",
                "Try connected components and path discovery.",
                "Then move to shortest path and cycle detection.",
            ],
            "focus_message": "Focus on graphs first: adjacency, BFS, DFS, and connected components.",
            "search_terms": ["graph", "bfs", "dfs", "connected component", "path"],
        },
        "dynamic programming": {
            "label": "Dynamic programming mastery",
            "next_steps": [
                "Review subproblem overlap and recurrence building.",
                "Practice memoization, then tabulation.",
                "Then move to 1D and 2D DP problems.",
            ],
            "focus_message": "Focus on DP first: identify repeated subproblems and define states clearly.",
            "search_terms": ["dynamic programming", "dp", "memoization", "tabulation"],
        },
        "general": {
            "label": "Foundations",
            "next_steps": [
                "Re-read the problem and trace the input-output by hand.",
                "Practice building solutions from simple loops and conditions first.",
                "Then move to a few easier problems in the same topic area.",
            ],
            "focus_message": "Focus on the core pattern of this problem type and practice a few easier variants first.",
            "search_terms": [],
        },
    }

    return packs.get(topic_key, packs["general"])

# -----------------------------------------------
# Show all coding questions
# -----------------------------------------------
@coding_bp.route("/")
@login_required
def all_questions():
    search_query = (request.args.get("search") or "").strip()
    difficulty = (request.args.get("difficulty") or "").strip().lower()
    completed_question_ids = set(
        question_id
        for (question_id,) in db.session.query(CodingQuestionProgress.question_id)
        .filter_by(user_id=current_user.id, is_completed=True)
        .all()
    )

    query = CodingQuestion.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                CodingQuestion.title.ilike(search_term),
                CodingQuestion.description.ilike(search_term),
            )
        )

    if difficulty in {"easy", "medium", "hard"}:
        query = query.filter(func.lower(CodingQuestion.difficulty) == difficulty)

    difficulty_rank = case(
        (func.lower(CodingQuestion.difficulty) == "easy", 1),
        (func.lower(CodingQuestion.difficulty) == "medium", 2),
        (func.lower(CodingQuestion.difficulty) == "hard", 3),
        else_=4,
    )

    questions = query.order_by(difficulty_rank, CodingQuestion.id.asc()).all()
    return render_template(
        "coding/all_questions.html",
        questions=questions,
        search_query=search_query,
        difficulty=difficulty if difficulty in {"easy", "medium", "hard"} else "",
        completed_question_ids=completed_question_ids,
    )

# -----------------------------------------------
# Show a specific coding question
# -----------------------------------------------
# @coding_bp.route("/<int:id>")
# @login_required
# def coding_page(id):
#     question = CodingQuestion.query.get_or_404(id)
#     return render_template("coding/practice.html", question=question)

@coding_bp.route("/<int:id>")
@login_required
def coding_page(id):
    question = CodingQuestion.query.get_or_404(id)

    # ✅ GET LAST SUBMISSION
    last_submission = (
        Submission.query
        .filter_by(user_id=current_user.id, question_id=id)
        .order_by(Submission.created_at.desc())
        .first()
    )

    return render_template(
        "coding/practice.html",
        question=question,
        last_submission=last_submission   # 🔥 IMPORTANT
    )

# -----------------------------------------------
# Run Code (Sample Input)
# -----------------------------------------------
@coding_bp.route("/run", methods=["POST"])
@login_required
def run_code():
    data = request.get_json()
    language = data.get("language")
    code = data.get("code")
    stdin = data.get("stdin", "")

    if language not in LANGUAGE_CONFIG:
        return jsonify({"error": "Unsupported language"}), 400

    payload = {
        "language_id": LANGUAGE_CONFIG[language]["id"],
        "source_code": code,
        "stdin": stdin
    }
    try:
        result = _runner_request(payload)
        output = _extract_output(result)
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------
# Submit Code (Hidden Test Cases)
# -----------------------------------------------

from app.utils.complexity_analyzer import analyze_time_complexity
import json
from app.models.submission import Submission

@coding_bp.route("/submit", methods=["POST"])
@login_required
def submit_code():
    data = request.get_json()
    language = data.get("language")
    code = data.get("code")
    qid = data.get("question_id")
    solve_time_seconds = float(data.get("solve_time_seconds") or 0)

    question = CodingQuestion.query.get(qid)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    progress = CodingQuestionProgress.query.filter_by(
        user_id=current_user.id,
        question_id=question.id,
    ).first()

    if not progress:
        progress = CodingQuestionProgress(
            user_id=current_user.id,
            question_id=question.id,
        )
        db.session.add(progress)

    test_cases = json.loads(question.test_cases)
    results = []
    passed = 0
    total_case_time_ms = 0.0

    for case in test_cases:
        stdin = case["input"]
        expected_output = case["output"].strip()

        payload = {
            "language_id": LANGUAGE_CONFIG[language]["id"],
            "source_code": code,
            "stdin": stdin
        }

        try:
            case_start = time.perf_counter()
            result = _runner_request(payload)
            case_elapsed_ms = (time.perf_counter() - case_start) * 1000
            total_case_time_ms += case_elapsed_ms
            output = _extract_output(result).strip()

            if output == expected_output:
                passed += 1
                results.append({
                    "input": stdin,
                    "output": output,
                    "status": "Passed",
                    "time_ms": round(case_elapsed_ms, 1)
                })
            else:
                results.append({
                    "input": stdin,
                    "output": output,
                    "expected": expected_output,
                    "status": "Failed",
                    "time_ms": round(case_elapsed_ms, 1)
                })
        except Exception as e:
            case_elapsed_ms = (time.perf_counter() - case_start) * 1000 if "case_start" in locals() else 0
            total_case_time_ms += case_elapsed_ms
            results.append({
                "input": stdin,
                "output": str(e),
                "status": "Error",
                "time_ms": round(case_elapsed_ms, 1)
            })

    # 🔥 CALL GEMINI ONLY ONCE
    complexity = analyze_time_complexity(
        code=code,
        problem=question.description,
        language=language
    )

    avg_case_time_ms = total_case_time_ms / len(test_cases) if test_cases else 0
    performance_rating, performance_summary = _calculate_performance_rating(
        passed=passed,
        total=len(test_cases),
        solve_time_seconds=solve_time_seconds,
        avg_case_time_ms=avg_case_time_ms
    )

    complexity["performance_rating"] = performance_rating
    complexity["performance_summary"] = performance_summary
    complexity["solve_time_seconds"] = round(solve_time_seconds, 1)
    complexity["avg_case_time_ms"] = round(avg_case_time_ms, 1)
    complexity["passed_cases"] = passed
    complexity["total_cases"] = len(test_cases)

    if test_cases and passed == len(test_cases):
        progress.is_completed = True
        if not progress.xp_awarded:
            current_user.xp = (current_user.xp or 0) + CODING_QUESTION_XP
            progress.xp_awarded = True
            progress.solved_at = datetime.utcnow()

    progress.last_attempt_at = datetime.utcnow()

    # ✅ SAVE SUBMISSION HISTORY (MAIN FIX)
    submission = Submission(
        user_id=current_user.id,
        question_id=question.id,
        code=code,
        language=language,

        passed=passed,
        total=len(test_cases),

        # ✅ map correctly
        runtime=avg_case_time_ms,
        solve_time=solve_time_seconds,

        # optional status
        status="Passed" if passed == len(test_cases) else "Failed"
    )

    db.session.add(submission)

    # ✅ Store analysis in session (TEMP)
    from flask import session
    session["last_complexity_analysis"] = complexity
    session["last_question_id"] = qid

    db.session.commit()
    current_user.check_and_award_badges()

    return jsonify({
        "passed": passed,
        "total": len(test_cases),
        "results": results,
        "performance_rating": performance_rating,
        "performance_summary": performance_summary,
        "analysis_ready": True
    })

#  updated
#  from app.models.submission import Submission
# from app.utils.complexity_analyzer import analyze_time_complexity
# from flask import session

# @coding_bp.route("/submit", methods=["POST"])
# @login_required
# def submit_code():
#     data = request.get_json()

#     language = data.get("language")
#     code = data.get("code")
#     qid = data.get("question_id")
#     solve_time_seconds = float(data.get("solve_time_seconds") or 0)

#     question = CodingQuestion.query.get(qid)
#     if not question:
#         return jsonify({"error": "Question not found"}), 404

#     progress = CodingQuestionProgress.query.filter_by(
#         user_id=current_user.id,
#         question_id=question.id,
#     ).first()

#     if not progress:
#         progress = CodingQuestionProgress(
#             user_id=current_user.id,
#             question_id=question.id,
#         )
#         db.session.add(progress)

#     test_cases = json.loads(question.test_cases)

#     results = []
#     passed = 0
#     total_case_time_ms = 0.0

#     for case in test_cases:
#         stdin = case["input"]
#         expected_output = case["output"].strip()

#         payload = {
#             "language_id": LANGUAGE_CONFIG[language]["id"],
#             "source_code": code,
#             "stdin": stdin
#         }

#         try:
#             case_start = time.perf_counter()

#             result = _runner_request(payload)

#             case_elapsed_ms = (time.perf_counter() - case_start) * 1000
#             total_case_time_ms += case_elapsed_ms

#             output = _extract_output(result).strip()

#             if output == expected_output:
#                 passed += 1
#                 status = "Passed"
#             else:
#                 status = "Failed"

#             results.append({
#                 "input": stdin,
#                 "output": output,
#                 "expected": expected_output if status == "Failed" else None,
#                 "status": status,
#                 "time_ms": round(case_elapsed_ms, 1)
#             })

#         except Exception as e:
#             results.append({
#                 "input": stdin,
#                 "output": str(e),
#                 "status": "Error",
#                 "time_ms": 0
#             })

#     # 🔥 AI complexity analysis
#     complexity = analyze_time_complexity(
#         code=code,
#         problem=question.description,
#         language=language
#     )

#     avg_case_time_ms = total_case_time_ms / len(test_cases) if test_cases else 0

#     performance_rating, performance_summary = _calculate_performance_rating(
#         passed=passed,
#         total=len(test_cases),
#         solve_time_seconds=solve_time_seconds,
#         avg_case_time_ms=avg_case_time_ms
#     )

#     # enrich analysis
#     complexity.update({
#         "performance_rating": performance_rating,
#         "performance_summary": performance_summary,
#         "solve_time_seconds": round(solve_time_seconds, 1),
#         "avg_case_time_ms": round(avg_case_time_ms, 1),
#         "passed_cases": passed,
#         "total_cases": len(test_cases)
#     })

#     # ✅ MARK COMPLETION + XP
#     if test_cases and passed == len(test_cases):
#         progress.is_completed = True

#         if not progress.xp_awarded:
#             current_user.xp = (current_user.xp or 0) + CODING_QUESTION_XP
#             progress.xp_awarded = True
#             progress.solved_at = datetime.utcnow()

#     progress.last_attempt_at = datetime.utcnow()

#     # ✅ SAVE SUBMISSION HISTORY (MAIN FIX)
#     submission = Submission(
#         user_id=current_user.id,
#         question_id=question.id,
#         code=code,
#         language=language,
#         passed=passed,
#         total=len(test_cases),
#         performance_rating=performance_rating,
#         performance_summary=performance_summary,
#         avg_case_time_ms=avg_case_time_ms,
#         solve_time_seconds=solve_time_seconds
#     )

#     db.session.add(submission)

#     # ✅ TEMP ANALYSIS STORAGE
#     session["last_complexity_analysis"] = complexity
#     session["last_question_id"] = qid

#     db.session.commit()

#     current_user.check_and_award_badges()

#     return jsonify({
#         "passed": passed,
#         "total": len(test_cases),
#         "results": results,
#         "performance_rating": performance_rating,
#         "performance_summary": performance_summary,
#         "analysis_ready": True
#     })

from flask import session

@coding_bp.route("/analysis/<int:question_id>")
@login_required
def view_analysis(question_id):
    analysis = session.get("last_complexity_analysis")
    qid = session.get("last_question_id")

    if not analysis or qid != question_id:
        return "No analysis found. Please submit code first.", 400

    question = CodingQuestion.query.get_or_404(question_id)

    topic_key = _infer_topic_key(question)
    recommendation_pack = _topic_recommendation_pack(topic_key)
    performance_rating = int(analysis.get("performance_rating") or 0)
    passed_cases = int(analysis.get("passed_cases") or 0)
    total_cases = int(analysis.get("total_cases") or 0)
    solved_cleanly = total_cases > 0 and passed_cases == total_cases and performance_rating > 5

    search_terms = recommendation_pack["search_terms"]
    related_questions_query = CodingQuestion.query.filter(CodingQuestion.id != question.id)

    if search_terms:
        related_conditions = [
            CodingQuestion.title.ilike(f"%{term}%")
            for term in search_terms
        ]
        related_questions_query = related_questions_query.filter(or_(*related_conditions))
    else:
        related_questions_query = related_questions_query.filter(
            CodingQuestion.title.ilike(f"%{topic_key}%")
        )

    related_questions = (
        related_questions_query
        .order_by(
            case(
                (func.lower(CodingQuestion.difficulty) == "easy", 1),
                (func.lower(CodingQuestion.difficulty) == "medium", 2),
                (func.lower(CodingQuestion.difficulty) == "hard", 3),
                else_=4,
            ),
            CodingQuestion.id.asc()
        )
        .limit(4)
        .all()
    )

    return render_template(
        "coding/analysis.html",
        question=question,
        analysis=analysis,
        topic_key=topic_key,
        topic_label=recommendation_pack["label"],
        next_steps=recommendation_pack["next_steps"],
        focus_message=recommendation_pack["focus_message"],
        related_questions=related_questions,
        solved_cleanly=solved_cleanly,
    )

@coding_bp.route("/submissions/<int:question_id>")
@login_required
def submission_history(question_id):
    submissions = (
        Submission.query
        .filter_by(user_id=current_user.id, question_id=question_id)
        .order_by(Submission.created_at.desc())
        .all()
    )

    return render_template(
        "coding/submissions.html",
        submissions=submissions
    )

@coding_bp.route("/delete_submission/<int:submission_id>", methods=["DELETE"])
@login_required
def delete_submission(submission_id):
    sub = Submission.query.get(submission_id)

    if not sub:
        return jsonify({"success": False})

    # security check
    if sub.user_id != current_user.id:
        return jsonify({"success": False})

    db.session.delete(sub)
    db.session.commit()

    return jsonify({"success": True})

# from app.utils.roadmap_generator import generate_user_roadmap

# @coding_bp.route("/roadmap")
# @login_required
# def user_roadmap():
#     roadmap = generate_user_roadmap(current_user.id)

#     return render_template(
#         "coding/roadmap.html",
#         roadmap=roadmap
#     )
