# import ollama

# MODEL = "qwen2.5:7b"

# def ask_ollama(prompt):

#     try:

#         response = ollama.chat(
#             model=MODEL,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ]
#         )

#         return response["message"]["content"]

#     except Exception as e:

#         print("OLLAMA ERROR:", e)

#         return "AI is temporarily unavailable."