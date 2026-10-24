from app.utils.gemini_client import get_gemini_client
from app.utils.analytics_service import get_user_context

client = get_gemini_client()

FAST_MODEL = "gemini-3-flash-preview"

PRO_MODEL = "gemini-2.5-pro"

chat_memory = {}


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


def get_memory(user_id):
    return chat_memory.get(user_id, {
        "last_problem": "",
        "last_topic": "",
        "hint_level": 0
    })


def save_memory(user_id, data):
    chat_memory[user_id] = data

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

def concept_teacher(msg):
    prompt = f"""
{SYSTEM_RULES}

Teach clearly:

{msg}

Use intuition + example + where used in interviews.
"""

    return run_gemini(prompt)

def ask_chatbot(user_id, msg):

    text = msg.lower().strip()
    context = get_user_context(user_id)
    mem = get_memory(user_id)

    if "hint" in text or "stuck" in text or "help solve" in text:
        mem["last_problem"] = msg
        save_memory(user_id, mem)
        return hint_engine(user_id, msg)

    if text in ["next hint", "more hint", "another hint"]:
        last = mem.get("last_problem", "")
        if last:
            return hint_engine(user_id, last)
        return "Ask problem first."

    if "review code" in text or "rate code" in text:
        return code_review(msg)

    if "error" in text or "wrong answer" in text or "bug" in text:
        return debugger(msg)

    if "complexity" in text or "optimize" in text:
        return complexity_analyzer(msg)

    if "study plan" in text or "roadmap" in text or "placement ready" in text:
        return personalized_plan(context)

    if "weak" in text:
        return f"Your weak topics are: {context.get('weak_topics', [])}"

    if "what should i study" in text:
        return f"Next best topic: {context.get('next_topic', 'Arrays')}"

    if "what is" in text or "explain" in text:
        return concept_teacher(msg)

    prompt = f"""
{SYSTEM_RULES}

User profile:
{context}

User asked:
{msg}

Give best mentoring response.
"""

    return run_gemini(prompt)

