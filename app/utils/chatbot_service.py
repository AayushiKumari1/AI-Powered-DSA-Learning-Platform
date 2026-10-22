





# # # ==========================================================
# # # FILE: app/utils/chatbot_service.py
# # #
# # # EduMentor AI — DSA Chatbot powered by Claude (Anthropic)
# # #
# # # FEATURES:
# # #   - Multi-turn conversation memory per user session
# # #   - Progressive 4-level hint engine (pattern → approach → pseudocode → code)
# # #   - Code review with score
# # #   - Smart debugger
# # #   - Big-O complexity analyser
# # #   - Personalised 7-day study roadmap (pulls live DB context)
# # #   - Concept teacher with intuition + interview tips
# # #   - Intent routing (keyword → specialist handler → Claude fallback)
# # #   - Session reset
# # #
# # # SETUP:
# # #   pip install anthropic
# # #   Set ANTHROPIC_API_KEY in your .env file
# # # ==========================================================

# # import os
# # import anthropic
# # from app.utils.analytics_service import get_user_context


# # # ----------------------------------------------------------
# # # CLIENT
# # # ----------------------------------------------------------
# # def _get_client() -> anthropic.Anthropic:
# #     api_key = os.getenv("ANTHROPIC_API_KEY")
# #     if not api_key:
# #         raise RuntimeError("ANTHROPIC_API_KEY is not set in your .env file.")
# #     return anthropic.Anthropic(api_key=api_key)


# # # ----------------------------------------------------------
# # # MODELS
# # #   FAST — everyday Q&A, hints, concepts  (cheap & quick)
# # #   PRO  — code review, debug, roadmap    (smarter)
# # # ----------------------------------------------------------
# # FAST_MODEL = "claude-haiku-4-5"
# # PRO_MODEL  = "claude-sonnet-4-6"


# # # ----------------------------------------------------------
# # # SYSTEM PROMPT  (injected on every API call)
# # # ----------------------------------------------------------
# # SYSTEM_PROMPT = """\
# # You are EduMentor AI — an expert DSA (Data Structures & Algorithms) mentor \
# # built into a student learning platform, like a LeetCode Premium tutor.

# # Personality:
# # - Concise by default: 3–5 lines unless the student needs more depth.
# # - Socratic: guide students to discover answers; never just hand over solutions.
# # - Warm and encouraging, but honest about misconceptions.

# # Capabilities:
# # 1. Hint Engine  — progressive hints (pattern → approach → pseudocode → code).
# # 2. Code Review  — correctness, style, complexity, score /10.
# # 3. Debugger     — root cause + explanation + corrected code.
# # 4. Complexity   — Big-O time & space with optimisation tips.
# # 5. Concept Tutor— intuition, example, complexity, interview tip.
# # 6. Roadmap      — personalised 7-day plan from live student data.

# # Hard rules:
# # - Never reveal the full solution until hint level 4 or if explicitly asked.
# # - Always tag code blocks with the language  (```python, ```java, etc.).
# # - If the question is unrelated to DSA/programming, politely redirect.
# # - Format responses with Markdown so they render nicely in the chat.
# # """


# # # ----------------------------------------------------------
# # # IN-MEMORY SESSION STORE
# # #
# # # Structure per user_id:
# # #   {
# # #     "history":      [{"role": "user"|"assistant", "content": str}, ...],
# # #     "last_problem": str,   # tracks last problem for "next hint"
# # #     "hint_level":   int,   # 0-4
# # #   }
# # #
# # # NOTE: This is intentionally simple (lives in process memory).
# # #       For production, replace _sessions with a Redis/DB store.
# # # ----------------------------------------------------------
# # _sessions: dict = {}


# # def _session(user_id: int) -> dict:
# #     """Return (or create) the session dict for this user."""
# #     if user_id not in _sessions:
# #         _sessions[user_id] = {"history": [], "last_problem": "", "hint_level": 0}
# #     return _sessions[user_id]


# # def _append(user_id: int, role: str, content: str):
# #     """Add a message to history, capping at 20 messages to stay within limits."""
# #     hist = _session(user_id)["history"]
# #     hist.append({"role": role, "content": content})
# #     if len(hist) > 20:
# #         # Drop oldest 2 (one user + one assistant) but keep first greeting if any
# #         _sessions[user_id]["history"] = hist[-20:]


# # # ----------------------------------------------------------
# # # CORE CLAUDE CALL  (always sends full conversation history)
# # # ----------------------------------------------------------
# # def _claude(
# #     user_id: int,
# #     user_message: str,
# #     system: str = None,
# #     use_pro: bool = False,
# #     max_tokens: int = 700,
# # ) -> str:
# #     """
# #     Build messages from history + new user turn, call Claude,
# #     then persist both turns back into history.
# #     """
# #     session  = _session(user_id)
# #     model    = PRO_MODEL if use_pro else FAST_MODEL
# #     system   = system or SYSTEM_PROMPT
# #     messages = session["history"] + [{"role": "user", "content": user_message}]

# #     try:
# #         client   = _get_client()
# #         response = client.messages.create(
# #             model=model,
# #             max_tokens=max_tokens,
# #             system=system,
# #             messages=messages,
# #         )
# #         reply = response.content[0].text.strip()
# #     except Exception as exc:
# #         print(f"[EduMentor Claude ERROR] {exc}")
# #         reply = "⚠️ EduMentor AI is temporarily unavailable. Please try again in a moment."

# #     _append(user_id, "user",      user_message)
# #     _append(user_id, "assistant", reply)
# #     return reply


# # # ----------------------------------------------------------
# # # 1. HINT ENGINE
# # # ----------------------------------------------------------
# # _HINT_GUIDES = {
# #     1: "Identify ONLY the algorithmic pattern (e.g. sliding window, two pointers, BFS). One sentence.",
# #     2: "Describe the high-level approach WITHOUT code. 2–3 sentences maximum.",
# #     3: "Give clean pseudocode showing the key steps. No full code yet.",
# #     4: "Give the complete optimised solution with time & space complexity.",
# # }

# # def hint_engine(user_id: int, problem: str) -> str:
# #     sess = _session(user_id)
# #     sess["hint_level"] = min(sess["hint_level"] + 1, 4)
# #     sess["last_problem"] = problem
# #     level = sess["hint_level"]

# #     prompt = (
# #         f"The student needs help with this problem:\n\n{problem}\n\n"
# #         f"This is **hint level {level}/4**.\n"
# #         f"Instruction for this level: {_HINT_GUIDES[level]}\n\n"
# #         "Stay strictly within the scope of this hint level."
# #     )
# #     return _claude(user_id, prompt)


# # # ----------------------------------------------------------
# # # 2. CODE REVIEW
# # # ----------------------------------------------------------
# # def code_review(user_id: int, msg: str) -> str:
# #     prompt = (
# #         f"Please review the following DSA code:\n\n{msg}\n\n"
# #         "Respond with exactly these sections:\n"
# #         "1. **Logic Issues** — bugs or edge cases missed\n"
# #         "2. **Code Quality** — style, naming, readability tips\n"
# #         "3. **Better Approach** — if a superior algorithm exists\n"
# #         "4. **Time & Space Complexity** — with justification\n"
# #         "5. **Score** — X/10 with one-line justification"
# #     )
# #     return _claude(user_id, prompt, use_pro=True, max_tokens=900)


# # # ----------------------------------------------------------
# # # 3. DEBUGGER
# # # ----------------------------------------------------------
# # def debugger(user_id: int, msg: str) -> str:
# #     prompt = (
# #         f"Debug the following code or problem:\n\n{msg}\n\n"
# #         "Respond with:\n"
# #         "1. **Root Cause** — what exactly is wrong\n"
# #         "2. **Why It Happens** — brief explanation\n"
# #         "3. **Fixed Code** — corrected snippet with the change highlighted"
# #     )
# #     return _claude(user_id, prompt, use_pro=True, max_tokens=800)


# # # ----------------------------------------------------------
# # # 4. COMPLEXITY ANALYSER
# # # ----------------------------------------------------------
# # def complexity_analyser(user_id: int, msg: str) -> str:
# #     prompt = (
# #         f"Analyse the complexity of:\n\n{msg}\n\n"
# #         "Respond with:\n"
# #         "1. **Time Complexity** — Big-O with justification\n"
# #         "2. **Space Complexity** — Big-O with justification\n"
# #         "3. **Theoretical Best** — best possible complexity for this problem\n"
# #         "4. **Optimisation Tip** — one concrete next step"
# #     )
# #     return _claude(user_id, prompt, max_tokens=500)


# # # ----------------------------------------------------------
# # # 5. PERSONALISED ROADMAP
# # # ----------------------------------------------------------
# # def personalised_roadmap(user_id: int, context: dict) -> str:
# #     profile = (
# #         f"- Completed topics : {context.get('completed_topics', 0)} / {context.get('total_topics', 0)}\n"
# #         f"- Avg quiz score   : {context.get('avg_score', 0)}%\n"
# #         f"- Weak topics      : {', '.join(context.get('weak_topics', [])) or 'None identified'}\n"
# #         f"- Next topic       : {context.get('next_topic', 'Arrays')}\n"
# #         f"- Current streak   : {context.get('streak', 0)} days\n"
# #         f"- Slowest topic    : {context.get('slowest', 'N/A')}\n"
# #         f"- XP earned        : {context.get('xp', 0)}\n"
# #     )
# #     prompt = (
# #         f"Here is the student's live profile:\n{profile}\n"
# #         "Create a **personalised 7-day DSA study roadmap**:\n"
# #         "- Prioritise weak topics\n"
# #         "- Specify LeetCode difficulty (Easy/Medium/Hard) per day\n"
# #         "- Include one interview-readiness rating (e.g. 60% ready)\n"
# #         "- End with a short motivational note"
# #     )
# #     return _claude(user_id, prompt, use_pro=True, max_tokens=1000)


# # # ----------------------------------------------------------
# # # 6. CONCEPT TEACHER
# # # ----------------------------------------------------------
# # def concept_teacher(user_id: int, msg: str) -> str:
# #     prompt = (
# #         f"Teach this DSA concept:\n\n{msg}\n\n"
# #         "Structure your answer as:\n"
# #         "**Intuition** → **Example** → **Time/Space** → **Interview Tip**\n"
# #         "Be concise but complete."
# #     )
# #     return _claude(user_id, prompt, max_tokens=700)


# # # ----------------------------------------------------------
# # # 7. SESSION RESET
# # # ----------------------------------------------------------
# # def reset_chat(user_id: int) -> str:
# #     _sessions.pop(user_id, None)
# #     return "🔄 Chat history cleared! Ready to tackle something new? What are you working on?"


# # # ----------------------------------------------------------
# # # MAIN ENTRY POINT
# # # ----------------------------------------------------------
# # def ask_chatbot(user_id: int, msg: str) -> str:
# #     """
# #     Route the user's message to the right specialist handler.
# #     Falls back to a context-enriched general Claude call.
# #     """
# #     text = msg.lower().strip()
# #     sess = _session(user_id)

# #     # ── Session reset ───────────────────────────────────
# #     if text in {"reset", "clear", "start over", "new chat"}:
# #         return reset_chat(user_id)

# #     # ── Continue hint (no new problem needed) ───────────
# #     if text in {"next hint", "more hint", "another hint", "go deeper", "more"}:
# #         last = sess.get("last_problem", "")
# #         return hint_engine(user_id, last) if last else (
# #             "Please describe your problem first, then ask for a hint!"
# #         )

# #     # ── Hint request ────────────────────────────────────
# #     if any(k in text for k in ("hint", "stuck", "help solve", "can't solve", "no idea", "don't know how")):
# #         return hint_engine(user_id, msg)

# #     # ── Code review ─────────────────────────────────────
# #     if any(k in text for k in ("review", "rate my code", "check my code", "evaluate my", "is my code")):
# #         return code_review(user_id, msg)

# #     # ── Debugging ───────────────────────────────────────
# #     if any(k in text for k in ("error", "wrong answer", "bug", "failing", "not working", "fix my", "why is my")):
# #         return debugger(user_id, msg)

# #     # ── Complexity ──────────────────────────────────────
# #     if any(k in text for k in ("complexity", "big o", "big-o", "optimize", "time complexity", "space complexity", "o(n)")):
# #         return complexity_analyser(user_id, msg)

# #     # ── Roadmap / study plan ────────────────────────────
# #     if any(k in text for k in ("roadmap", "study plan", "what should i study", "placement", "interview prep", "7 day", "schedule")):
# #         ctx = get_user_context(user_id)
# #         return personalised_roadmap(user_id, ctx)

# #     # ── Weak topics shortcut ────────────────────────────
# #     if "weak" in text and ("topic" in text or "area" in text):
# #         ctx = get_user_context(user_id)
# #         weak = ctx.get("weak_topics", [])
# #         if weak:
# #             joined = ", ".join(f"**{t}**" for t in weak)
# #             return f"Your weak topics are: {joined}.\n\nFocus on these before moving forward — want a hint or explanation on any of them? 💪"
# #         return "No weak topics identified yet — great job keeping up! Keep practising to uncover any gaps."

# #     # ── Concept / explanation ───────────────────────────
# #     if any(k in text for k in ("what is", "explain", "how does", "how do", "what are", "define", "teach me", "tell me about")):
# #         return concept_teacher(user_id, msg)

# #     # ── General fallback: context-enriched Claude call ──
# #     ctx = get_user_context(user_id)
# #     ctx_note = (
# #         f"[Student snapshot — weak: {ctx.get('weak_topics', [])}, "
# #         f"score: {ctx.get('avg_score', 0)}%, "
# #         f"streak: {ctx.get('streak', 0)} days, "
# #         f"next topic: {ctx.get('next_topic', 'Arrays')}]"
# #     )
# #     full_msg = f"{ctx_note}\n\nStudent message: {msg}"
# #     return _claude(user_id, full_msg)




# # # #  Prior-------------------------------------

# #  ==========================================================
# # FILE: app/utils/chatbot_service.py
# # FULL PRODUCTION READY DSA CHATBOT (LeetCode Style)
# # Features:
# # - Hint Levels
# # - Code Review
# # - Debugging
# # - Complexity Analyzer
# # - Follow-up Memory
# # - Personalized with User Stats
# # ==========================================================

# from app.utils.gemini_client import get_gemini_client
# from app.utils.analytics_service import get_user_context

# client = get_gemini_client()

# FAST_MODEL = "gemini-3-flash-preview"
    
# PRO_MODEL = "gemini-2.5-pro"

# # ----------------------------------------------------------
# # MEMORY STORE (simple in-memory)
# # Replace with DB later
# # ----------------------------------------------------------
# chat_memory = {}


# # ----------------------------------------------------------
# # GEMINI RUNNER
# # ----------------------------------------------------------
# def run_gemini(prompt, use_pro=False):
#     model = PRO_MODEL if use_pro else FAST_MODEL

#     try:
#         res = client.models.generate_content(
#             model=model,
#             contents=prompt
#         )
#         return (res.text or "").strip()

#     except Exception:
#         return "Mentor bot is temporarily unavailable."


# # ----------------------------------------------------------
# # CORE SYSTEM PROMPT
# # ----------------------------------------------------------
# SYSTEM_RULES = """
# You are an expert DSA coding mentor like LeetCode premium mentor.

# Rules:
# - Help user learn, not just give answer
# - Give short answers
# - Max 3 lines normally
# - Be direct and useful
# - No unnecessary explanation
# - If coding doubt: explain steps shortly
# - If hint asked: give only next step
# - If debug asked: tell exact issue + fix
# - If complexity asked: give direct answer
# - If asked deeper, then explain more
# - Detect problem pattern automatically
# - Prefer hints before full solution
# - Explain brute force then optimal
# - Explain time complexity
# - Explain space complexity
# - If code given, review logically
# - If bug given, debug step-by-step
# - Use short clean responses
# - No unnecessary text
# """

# SYSTEM_RULES = """
# You are an expert DSA coding mentor.

# Rules:
# - Give short answers
# - Max 3 lines normally
# - Be direct and useful
# - No unnecessary explanation
# - If coding doubt: explain steps shortly
# - If hint asked: give only next step
# - If debug asked: tell exact issue + fix
# - If complexity asked: give direct answer
# - If asked deeper, then explain more
# """


# # ----------------------------------------------------------
# # MEMORY
# # ----------------------------------------------------------
# def get_memory(user_id):
#     return chat_memory.get(user_id, {
#         "last_problem": "",
#         "last_topic": "",
#         "hint_level": 0
#     })


# def save_memory(user_id, data):
#     chat_memory[user_id] = data


# # ----------------------------------------------------------
# # HINT ENGINE
# # ----------------------------------------------------------
# def hint_engine(user_id, msg):
#     mem = get_memory(user_id)
#     mem["hint_level"] += 1

#     level = mem["hint_level"]

#     prompt = f"""
# {SYSTEM_RULES}

# User asked help for:
# {msg}

# Hint level = {level}

# If level 1:
# - identify pattern only

# If level 2:
# - explain approach

# If level 3:
# - give pseudocode

# If level 4:
# - give optimized code

# Respond based on level.
# """

#     save_memory(user_id, mem)
#     return run_gemini(prompt)


# # ----------------------------------------------------------
# # CODE REVIEW
# # ----------------------------------------------------------
# def code_review(msg):
#     prompt = f"""
# {SYSTEM_RULES}

# Review this code:

# {msg}

# Return:
# 1. Logic issues
# 2. Code quality
# 3. Better approach
# 4. Complexity
# 5. Score out of 10
# """

#     return run_gemini(prompt, use_pro=True)


# # ----------------------------------------------------------
# # DEBUGGER
# # ----------------------------------------------------------
# def debugger(msg):
#     prompt = f"""
# {SYSTEM_RULES}

# Debug this code/problem:

# {msg}

# Return:
# 1. Root issue
# 2. Why happening
# 3. Fix steps
# 4. Corrected logic
# """

#     return run_gemini(prompt, use_pro=True)


# # ----------------------------------------------------------
# # COMPLEXITY ANALYZER
# # ----------------------------------------------------------
# def complexity_analyzer(msg):
#     prompt = f"""
# {SYSTEM_RULES}

# Analyze this code/problem:

# {msg}

# Return:
# 1. Time complexity
# 2. Space complexity
# 3. Better possible complexity
# 4. Optimization tips
# """

#     return run_gemini(prompt)


# # ----------------------------------------------------------
# # ROADMAP / PERSONALIZED
# # ----------------------------------------------------------
# def personalized_plan(context):
#     prompt = f"""
# {SYSTEM_RULES}

# User stats:
# {context}

# Create personalized next learning roadmap:
# - weak topics
# - next topic
# - 7 day plan
# - interview readiness
# """

#     return run_gemini(prompt, use_pro=True)


# # ----------------------------------------------------------
# # GENERAL DSA TEACHER
# # ----------------------------------------------------------
# def concept_teacher(msg):
#     prompt = f"""
# {SYSTEM_RULES}

# Teach clearly:

# {msg}

# Use intuition + example + where used in interviews.
# """

#     return run_gemini(prompt)


# # ----------------------------------------------------------
# # MAIN CHATBOT ENTRY
# # ----------------------------------------------------------
# def ask_chatbot(user_id, msg):

#     text = msg.lower().strip()
#     context = get_user_context(user_id)
#     mem = get_memory(user_id)

#     # --------------------------------------
#     # HINT SYSTEM
#     # --------------------------------------
#     if "hint" in text or "stuck" in text or "help solve" in text:
#         mem["last_problem"] = msg
#         save_memory(user_id, mem)
#         return hint_engine(user_id, msg)

#     # --------------------------------------
#     # NEXT HINT
#     # --------------------------------------
#     if text in ["next hint", "more hint", "another hint"]:
#         last = mem.get("last_problem", "")
#         if last:
#             return hint_engine(user_id, last)
#         return "Ask problem first."

#     # --------------------------------------
#     # CODE REVIEW
#     # --------------------------------------
#     if "review code" in text or "rate code" in text:
#         return code_review(msg)

#     # --------------------------------------
#     # DEBUGGING
#     # --------------------------------------
#     if "error" in text or "wrong answer" in text or "bug" in text:
#         return debugger(msg)

#     # --------------------------------------
#     # COMPLEXITY
#     # --------------------------------------
#     if "complexity" in text or "optimize" in text:
#         return complexity_analyzer(msg)

#     # --------------------------------------
#     # PERSONALIZED ROADMAP
#     # --------------------------------------
#     if "study plan" in text or "roadmap" in text or "placement ready" in text:
#         return personalized_plan(context)

#     # --------------------------------------
#     # WEAK TOPICS
#     # --------------------------------------
#     if "weak" in text:
#         return f"Your weak topics are: {context.get('weak_topics', [])}"

#     # --------------------------------------
#     # WHAT TO STUDY
#     # --------------------------------------
#     if "what should i study" in text:
#         return f"Next best topic: {context.get('next_topic', 'Arrays')}"

#     # --------------------------------------
#     # CONCEPTS
#     # --------------------------------------
#     if "what is" in text or "explain" in text:
#         return concept_teacher(msg)

#     # --------------------------------------
#     # DEFAULT
#     # --------------------------------------
#     prompt = f"""
# {SYSTEM_RULES}

# User profile:
# {context}

# User asked:
# {msg}

# Give best mentoring response.
# """

#     return run_gemini(prompt)






# # ==========================================================
# # DSA CHATBOT SERVICE (FINAL PRODUCTION VERSION)
# # ==========================================================

# from app.utils.gemini_client import get_gemini_client
# from app.utils.analytics_service import get_user_context

# client = get_gemini_client()

# FAST_MODEL = "gemini-3-flash-preview"
# PRO_MODEL = "gemini-2.5-pro"

# # ==========================================================
# # MEMORY STORE (Replace with DB later)
# # ==========================================================
# chat_memory = {}


# def get_memory(user_id):
#     return chat_memory.get(user_id, {
#         "last_problem": "",
#         "hint_level": 0
#     })


# def save_memory(user_id, data):
#     chat_memory[user_id] = data


# # ==========================================================
# # GEMINI SAFE CALL
# # ==========================================================
# def run_gemini(prompt, use_pro=False):
#     model_name = PRO_MODEL if use_pro else FAST_MODEL

#     try:
#         model = client.GenerativeModel(model_name)
#         response = model.generate_content(prompt)

#         if not response.text:
#             return "⚠️ AI returned empty response."

#         return response.text.strip()

#     except Exception as e:
#         print("❌ GEMINI ERROR:", str(e))
#         return "⚠️ AI is temporarily unavailable."


# # ==========================================================
# # SYSTEM PROMPT
# # ==========================================================
# SYSTEM_RULES = """
# You are a strict DSA mentor.

# Rules:
# - Max 3–5 lines
# - No long explanation
# - Help user think
# - Prefer hints over answers
# - If debugging → give exact issue
# - If code → analyze logic
# - If asked deeper → explain more
# """


# # ==========================================================
# # PATTERN DETECTION
# # ==========================================================
# def detect_pattern(code):
#     code = code.lower()

#     if code.count("for") >= 2:
#         return "Nested Loop (Brute Force)"

#     if "while" in code and "left" in code:
#         return "Sliding Window"

#     if "mid" in code:
#         return "Binary Search"

#     if "dp" in code or "memo" in code:
#         return "Dynamic Programming"

#     if "stack" in code:
#         return "Stack"

#     if "queue" in code:
#         return "Queue / BFS"

#     return "Brute Force"


# # ==========================================================
# # COMPLEXITY ESTIMATION
# # ==========================================================
# def estimate_complexity(code):
#     loops = code.count("for") + code.count("while")

#     if loops >= 3:
#         return "O(n^3)"
#     elif loops == 2:
#         return "O(n^2)"
#     elif loops == 1:
#         return "O(n)"
#     return "O(log n) / O(1)"


# # ==========================================================
# # HINT ENGINE
# # ==========================================================
# def smart_hint(user_id, problem):
#     mem = get_memory(user_id)
#     mem["hint_level"] += 1
#     level = mem["hint_level"]

#     if level == 1:
#         hint = "Identify pattern (array, hashmap, two pointers?)"
#     elif level == 2:
#         hint = "Think of optimizing brute force using data structures."
#     elif level == 3:
#         hint = "Break into steps and track values efficiently."
#     elif level == 4:
#         hint = "Use optimal approach (binary search / sliding window / DP)."
#     else:
#         hint = "Try implementing full solution now."

#     save_memory(user_id, mem)
#     return f"Hint {level}: {hint}"


# # ==========================================================
# # DEBUG ENGINE
# # ==========================================================
# def debug_code(code):
#     code = code.lower()

#     if "=" in code and "==" not in code:
#         return "Bug: assignment (=) instead of comparison (==)"

#     if "while true" in code:
#         return "Bug: infinite loop detected"

#     if "index" in code and "-1" in code:
#         return "Bug: possible index out of bounds"

#     return "Check logic using dry run with sample input."


# # ==========================================================
# # ANALYZE CODE
# # ==========================================================
# def analyze_code(code):
#     pattern = detect_pattern(code)
#     complexity = estimate_complexity(code)

#     return f"""
# Pattern: {pattern}
# Estimated Time Complexity: {complexity}
# """


# # ==========================================================
# # AI CODE REVIEW
# # ==========================================================
# def code_review(code):
#     prompt = f"""
# {SYSTEM_RULES}

# Review this code:
# {code}

# Return:
# 1. Mistakes
# 2. Improvements
# 3. Better approach
# 4. Complexity
# """

#     return run_gemini(prompt, use_pro=True)


# # ==========================================================
# # AI CONCEPT TEACHER
# # ==========================================================
# def concept_teacher(msg):
#     prompt = f"""
# {SYSTEM_RULES}

# Explain clearly with example:
# {msg}
# """
#     return run_gemini(prompt)


# # ==========================================================
# # ROADMAP GENERATOR
# # ==========================================================
# def generate_roadmap(context):
#     weak = context.get("weak_topics", [])

#     return f"""
# Your Weak Topics: {weak}

# 7-Day Plan:
# Day 1: Arrays + Hashing
# Day 2: Sliding Window
# Day 3: Recursion
# Day 4: Trees
# Day 5: Graphs
# Day 6: DP Basics
# Day 7: Mock Interview

# Focus on weak areas first.
# """


# # ==========================================================
# # PERSONALIZED RESPONSE
# # ==========================================================
# def personalized_response(context):
#     return f"""
# Weak topics: {context.get('weak_topics', [])}
# Next topic: {context.get('next_topic', 'Arrays')}
# """


# # ==========================================================
# # MAIN CHATBOT FUNCTION
# # ==========================================================
# def ask_chatbot(user_id, msg):

#     text = msg.lower().strip()
#     context = get_user_context(user_id)
#     mem = get_memory(user_id)

#     try:
#         # ---------------- HINT ----------------
#         if any(x in text for x in ["hint", "stuck", "help"]):
#             mem["last_problem"] = msg
#             save_memory(user_id, mem)
#             return smart_hint(user_id, msg)

#         # NEXT HINT
#         if text in ["next hint", "more hint"]:
#             if mem.get("last_problem"):
#                 return smart_hint(user_id, mem["last_problem"])
#             return "Ask a problem first."

#         # ---------------- DEBUG ----------------
#         if any(x in text for x in ["error", "bug", "wrong"]):
#             return debug_code(msg)

#         # ---------------- ANALYSIS ----------------
#         if "complexity" in text or "analyze" in text:
#             return analyze_code(msg)

#         # ---------------- REVIEW ----------------
#         if "review" in text:
#             return code_review(msg)

#         # ---------------- ROADMAP ----------------
#         if "roadmap" in text or "study plan" in text:
#             return generate_roadmap(context)

#         # ---------------- WEAK ----------------
#         if "weak" in text:
#             return f"Weak topics: {context.get('weak_topics', [])}"

#         # ---------------- NEXT TOPIC ----------------
#         if "what should i study" in text:
#             return f"Next topic: {context.get('next_topic', 'Arrays')}"

#         # ---------------- PROGRESS ----------------
#         if "progress" in text:
#             return personalized_response(context)

#         # ---------------- CONCEPT ----------------
#         if any(x in text for x in ["what is", "explain", "how"]):
#             return concept_teacher(msg)

#         # ---------------- DEFAULT (AI) ----------------
#         prompt = f"""
# {SYSTEM_RULES}

# User profile:
# {context}

# User question:
# {msg}
# """

#         return run_gemini(prompt)

#     except Exception as e:
#         print("❌ CHATBOT ERROR:", str(e))
#         return "⚠️ Something went wrong."







#  3.-------------------------------------

#  ==========================================================
# FILE: app/utils/chatbot_service.py
# FULL PRODUCTION READY DSA CHATBOT (LeetCode Style)
# Features:
# - Hint Levels
# - Code Review
# - Debugging
# - Complexity Analyzer
# - Follow-up Memory
# - Personalized with User Stats
# ==========================================================

from app.utils.gemini_client import get_gemini_client
from app.utils.analytics_service import get_user_context

client = get_gemini_client()

FAST_MODEL = "gemini-3-flash-preview"

PRO_MODEL = "gemini-2.5-pro"

# ----------------------------------------------------------
# MEMORY STORE (simple in-memory)
# Replace with DB later
# ----------------------------------------------------------
chat_memory = {}


# ----------------------------------------------------------
# GEMINI RUNNER
# ----------------------------------------------------------
def run_gemini(prompt, use_pro=False):
    model = PRO_MODEL if use_pro else FAST_MODEL

    try:
        res = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return (res.text or "").strip()

    except Exception:
        return "Mentor bot is temporarily unavailable."


# ----------------------------------------------------------
# CORE SYSTEM PROMPT
# ----------------------------------------------------------
SYSTEM_RULES = """
You are an expert DSA coding mentor like LeetCode premium mentor.

Rules:
- Help user learn, not just give answer
- Give short answers
- Max 3 lines normally
- Be direct and useful
- No unnecessary explanation
- If coding doubt: explain steps shortly
- If hint asked: give only next step
- If debug asked: tell exact issue + fix
- If complexity asked: give direct answer
- If asked deeper, then explain more
- Detect problem pattern automatically
- Prefer hints before full solution
- Explain brute force then optimal
- Explain time complexity
- Explain space complexity
- If code given, review logically
- If bug given, debug step-by-step
- Use short clean responses
- No unnecessary text
"""

# SYSTEM_RULES = """
# You are an expert DSA coding mentor.

# Rules:
# - Give short answers
# - Max 3 lines normally
# - Be direct and useful
# - No unnecessary explanation
# - If coding doubt: explain steps shortly
# - If hint asked: give only next step
# - If debug asked: tell exact issue + fix
# - If complexity asked: give direct answer
# - If asked deeper, then explain more
# """


# ----------------------------------------------------------
# MEMORY
# ----------------------------------------------------------
def get_memory(user_id):
    return chat_memory.get(user_id, {
        "last_problem": "",
        "last_topic": "",
        "hint_level": 0
    })


def save_memory(user_id, data):
    chat_memory[user_id] = data


# ----------------------------------------------------------
# HINT ENGINE
# ----------------------------------------------------------
def hint_engine(user_id, msg):
    mem = get_memory(user_id)
    mem["hint_level"] += 1

    level = mem["hint_level"]

    prompt = f"""
{SYSTEM_RULES}

User asked help for:
{msg}

Hint level = {level}

If level 1:
- identify pattern only

If level 2:
- explain approach

If level 3:
- give pseudocode

If level 4:
- give optimized code

Respond based on level.
"""

    save_memory(user_id, mem)
    return run_gemini(prompt)


# ----------------------------------------------------------
# CODE REVIEW
# ----------------------------------------------------------
def code_review(msg):
    prompt = f"""
{SYSTEM_RULES}

Review this code:

{msg}

Return:
1. Logic issues
2. Code quality
3. Better approach
4. Complexity
5. Score out of 10
"""

    return run_gemini(prompt, use_pro=True)


# ----------------------------------------------------------
# DEBUGGER
# ----------------------------------------------------------
def debugger(msg):
    prompt = f"""
{SYSTEM_RULES}

Debug this code/problem:

{msg}

Return:
1. Root issue
2. Why happening
3. Fix steps
4. Corrected logic
"""

    return run_gemini(prompt, use_pro=True)


# ----------------------------------------------------------
# COMPLEXITY ANALYZER
# ----------------------------------------------------------
def complexity_analyzer(msg):
    prompt = f"""
{SYSTEM_RULES}

Analyze this code/problem:

{msg}

Return:
1. Time complexity
2. Space complexity
3. Better possible complexity
4. Optimization tips
"""

    return run_gemini(prompt)


# ----------------------------------------------------------
# ROADMAP / PERSONALIZED
# ----------------------------------------------------------
def personalized_plan(context):
    prompt = f"""
{SYSTEM_RULES}

User stats:
{context}

Create personalized next learning roadmap:
- weak topics
- next topic
- 7 day plan
- interview readiness
"""

    return run_gemini(prompt, use_pro=True)


# ----------------------------------------------------------
# GENERAL DSA TEACHER
# ----------------------------------------------------------
def concept_teacher(msg):
    prompt = f"""
{SYSTEM_RULES}

Teach clearly:

{msg}

Use intuition + example + where used in interviews.
"""

    return run_gemini(prompt)


# ----------------------------------------------------------
# MAIN CHATBOT ENTRY
# ----------------------------------------------------------
def ask_chatbot(user_id, msg):

    text = msg.lower().strip()
    context = get_user_context(user_id)
    mem = get_memory(user_id)

    # --------------------------------------
    # HINT SYSTEM
    # --------------------------------------
    if "hint" in text or "stuck" in text or "help solve" in text:
        mem["last_problem"] = msg
        save_memory(user_id, mem)
        return hint_engine(user_id, msg)

    # --------------------------------------
    # NEXT HINT
    # --------------------------------------
    if text in ["next hint", "more hint", "another hint"]:
        last = mem.get("last_problem", "")
        if last:
            return hint_engine(user_id, last)
        return "Ask problem first."

    # --------------------------------------
    # CODE REVIEW
    # --------------------------------------
    if "review code" in text or "rate code" in text:
        return code_review(msg)

    # --------------------------------------
    # DEBUGGING
    # --------------------------------------
    if "error" in text or "wrong answer" in text or "bug" in text:
        return debugger(msg)

    # --------------------------------------
    # COMPLEXITY
    # --------------------------------------
    if "complexity" in text or "optimize" in text:
        return complexity_analyzer(msg)

    # --------------------------------------
    # PERSONALIZED ROADMAP
    # --------------------------------------
    if "study plan" in text or "roadmap" in text or "placement ready" in text:
        return personalized_plan(context)

    # --------------------------------------
    # WEAK TOPICS
    # --------------------------------------
    if "weak" in text:
        return f"Your weak topics are: {context.get('weak_topics', [])}"

    # --------------------------------------
    # WHAT TO STUDY
    # --------------------------------------
    if "what should i study" in text:
        return f"Next best topic: {context.get('next_topic', 'Arrays')}"

    # --------------------------------------
    # CONCEPTS
    # --------------------------------------
    if "what is" in text or "explain" in text:
        return concept_teacher(msg)

    # --------------------------------------
    # DEFAULT
    # --------------------------------------
    prompt = f"""
{SYSTEM_RULES}

User profile:
{context}

User asked:
{msg}

Give best mentoring response.
"""

    return run_gemini(prompt)

