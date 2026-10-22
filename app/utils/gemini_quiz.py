import json
from app.utils.gemini_client import get_gemini_client

client = get_gemini_client()

def generate_mcq_quiz(topic_title):
    """
    Returns:
    [
      {
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "correct_index": 1
      }
    ]
    """

    prompt = f"""
You are a computer science instructor.

Generate EXACTLY 5 multiple choice questions for the topic:
"{topic_title}"

Rules:
- Difficulty: Medium
- Each question must have 4 options
- Only ONE correct option
- Return ONLY valid JSON
- No markdown
- No explanations

JSON format:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_index": 0
  }}
]
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    raw = (response.text or "").strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    quiz = json.loads(raw)

    # Basic validation
    if not isinstance(quiz, list) or len(quiz) != 5:
        raise ValueError("Invalid quiz format from Gemini")

    return quiz
