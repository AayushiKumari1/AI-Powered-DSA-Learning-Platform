import json
from app.utils.gemini_client import get_gemini_client

client = get_gemini_client()

def analyze_time_complexity(code, problem, language):
    prompt = f"""
You are a DSA expert.

Analyze the following code and determine:
1. Time Complexity used by the code
2. Best possible time complexity for this problem

Respond ONLY in valid JSON. No markdown.
    
JSON format:
{{
  "used": "O(...)",
  "best": "O(...)",
  "explanation": "short explanation"
}}

Problem:
{problem}

Language:
{language}

Code:
{code}
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    raw = (response.text or "").strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)   
    except Exception as e:
        return {
            "used": "Unknown",
            "best": "Unknown",
            "explanation": f"AI parsing failed: {str(e)}"
        }





# 2.
 
# import re
# import math
# import json

# # ====================================
# # HELPERS
# # ====================================

# def count_loops(code):
#     lines = code.split("\n")
#     levels = []
#     current_depth = 0
#     max_depth = 0

#     for line in lines:
#         stripped = line.strip().lower()

#         if stripped.startswith("for ") or stripped.startswith("while "):
#             indent = len(line) - len(line.lstrip())
#             depth = indent // 4 + 1
#             max_depth = max(max_depth, depth)

#     return max_depth


# def detect_recursion(code):
#     funcs = re.findall(r"def\s+(\w+)\(", code)
#     for fn in funcs:
#         if f"{fn}(" in code.split(":", 1)[-1]:
#             return True
#     return False


# def detect_binary_search(code):
#     keywords = ["mid =", "low <=", "high =", "left <=", "right ="]
#     return any(k in code.lower() for k in keywords)


# def detect_sorting(code):
#     keywords = ["sort(", "sorted(", ".sort("]
#     return any(k in code.lower() for k in keywords)


# def detect_hashmap(code):
#     keywords = ["dict(", "{}", "map[", "unordered_map", "hashmap"]
#     return any(k in code.lower() for k in keywords)


# def detect_array_storage(code):
#     keywords = ["append(", "push_back(", "list(", "vector<"]
#     return any(k in code.lower() for k in keywords)


# # ====================================
# # TIME COMPLEXITY
# # ====================================

# def analyze_time(code):
#     depth = count_loops(code)
#     recursive = detect_recursion(code)

#     if detect_binary_search(code):
#         return "O(log n)", "Binary search pattern detected."

#     if recursive:
#         if "2*" in code or code.count("(") > 5:
#             return "O(2^n)", "Multiple recursive branching detected."
#         return "O(n)", "Single recursion detected."

#     if depth == 3:
#         return "O(n³)", "Triple nested loops detected."

#     if depth == 2:
#         return "O(n²)", "Nested loops detected."

#     if depth == 1:
#         if detect_sorting(code):
#             return "O(n log n)", "Loop + sorting detected."
#         return "O(n)", "Single loop detected."

#     if detect_sorting(code):
#         return "O(n log n)", "Sorting operation detected."

#     return "O(1)", "No loops found."


# # ====================================
# # SPACE COMPLEXITY
# # ====================================

# def analyze_space(code):
#     if detect_array_storage(code):
#         return "O(n)", "Extra list/array storage detected."

#     if detect_hashmap(code):
#         return "O(n)", "HashMap / Dictionary storage detected."

#     if detect_recursion(code):
#         return "O(n)", "Recursion call stack detected."

#     return "O(1)", "No major extra memory used."


# # ====================================
# # BEST POSSIBLE
# # ====================================

# def estimate_best(problem):
#     p = problem.lower()

#     if "search" in p:
#         return "O(log n)"
#     if "sort" in p:
#         return "O(n log n)"
#     if "pair" in p or "sum" in p:
#         return "O(n)"
#     if "graph" in p:
#         return "O(V + E)"
#     if "tree" in p:
#         return "O(n)"

#     return "Depends on constraints"


# # ====================================
# # TLE RISK
# # ====================================

# def tle_risk(tc):
#     if "n³" in tc or "2^n" in tc:
#         return "HIGH 🔴"

#     if "n²" in tc:
#         return "MEDIUM 🟠"

#     return "LOW 🟢"


# # ====================================
# # OPTIMIZATION SUGGESTIONS
# # ====================================

# def suggestions(tc, code):
#     tips = []

#     if "O(n²)" in tc:
#         tips.append("Try HashMap / Two Pointer / Sliding Window to reduce nested loops.")

#     if "O(n³)" in tc:
#         tips.append("Use preprocessing or optimized data structures.")

#     if "2^n" in tc:
#         tips.append("Use Dynamic Programming / Memoization.")

#     if "O(n)" in tc and detect_sorting(code):
#         tips.append("If sorting unnecessary, avoid sort to reduce cost.")

#     if not tips:
#         tips.append("Current approach looks efficient.")

#     return tips


# # ====================================
# # MAIN FUNCTION
# # ====================================

# def analyze_time_complexity(code, problem="", language="Python"):

#     used_tc, tc_reason = analyze_time(code)
#     used_sc, sc_reason = analyze_space(code)
#     best_tc = estimate_best(problem)
#     risk = tle_risk(used_tc)
#     tips = suggestions(used_tc, code)

#     return {
#         "used_time": used_tc,
#         "used_space": used_sc,
#         "best_possible": best_tc,
#         "tle_risk": risk,
#         "time_reason": tc_reason,
#         "space_reason": sc_reason,
#         "optimization_tips": tips,
#         "source": "Hybrid Static Analyzer v2"
#     }







