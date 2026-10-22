# # from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# # from app.extensions import db
# # from app.models.coding_question import CodingQuestion
# # import json

# # admin_coding_bp = Blueprint("admin_coding", __name__, url_prefix="/admin/coding")

# # # Check admin login
# # def admin_logged_in():
# #     return session.get("admin_logged_in")

# # # --------------------------------------------------
# # # Show all coding questions
# # # --------------------------------------------------
# # @admin_coding_bp.route("/")
# # def dashboard():
# #     if not admin_logged_in():
# #         return redirect(url_for("admin.admin_login"))
# #     questions = CodingQuestion.query.all()
# #     return render_template("admin/coding_dashboard.html", questions=questions)

# # # --------------------------------------------------
# # # Add new coding question
# # # --------------------------------------------------
# # @admin_coding_bp.route("/add", methods=["GET", "POST"])
# # def add_question():
# #     if not admin_logged_in():
# #         return redirect(url_for("admin.admin_login"))

# #     if request.method == "POST":
# #         title = request.form.get("title")
# #         description = request.form.get("description")
# #         sample_input = request.form.get("sample_input")
# #         sample_output = request.form.get("sample_output")
# #         difficulty = request.form.get("difficulty")
# #         test_cases = request.form.get("test_cases")

# #         # Validate JSON format for test cases
# #         try:
# #             json.loads(test_cases)
# #         except Exception as e:
# #             flash("❌ Invalid JSON format in test cases!", "danger")
# #             return redirect(url_for("admin_coding.add_question"))

# #         new_q = CodingQuestion(
# #             title=title,
# #             description=description,
# #             sample_input=sample_input,
# #             sample_output=sample_output,
# #             difficulty=difficulty,
# #             test_cases=test_cases
# #         )
# #         db.session.add(new_q)
# #         db.session.commit()
# #         flash("✅ Coding question added successfully!", "success")
# #         return redirect(url_for("admin_coding.dashboard"))

# #     return render_template("admin/add_coding.html")

# # # --------------------------------------------------
# # # Delete question
# # # --------------------------------------------------
# # @admin_coding_bp.route("/delete/<int:id>")
# # def delete_question(id):
# #     if not admin_logged_in():
# #         return redirect(url_for("admin.admin_login"))

# #     q = CodingQuestion.query.get_or_404(id)
# #     db.session.delete(q)
# #     db.session.commit()
# #     flash("🗑️ Question deleted.", "info")
# #     return redirect(url_for("admin_coding.dashboard"))



# from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# from app.extensions import db
# from app.models.coding_question import CodingQuestion
# import json

# admin_coding_bp = Blueprint("admin_coding", __name__, url_prefix="/admin/coding")

# # Check admin login
# def admin_logged_in():
#     return session.get("admin_logged_in")

# # --------------------------------------------------
# # Show all coding questions
# # --------------------------------------------------
# @admin_coding_bp.route("/")
# def dashboard():
#     if not admin_logged_in():
#         return redirect(url_for("admin.admin_login"))
#     questions = CodingQuestion.query.all()
#     return render_template("admin/coding_dashboard.html", questions=questions)

# # --------------------------------------------------
# # Add new coding question
# # --------------------------------------------------
# @admin_coding_bp.route("/add", methods=["GET", "POST"])
# def add_question():
#     if not admin_logged_in():
#         return redirect(url_for("admin.admin_login"))

#     if request.method == "POST":
#         title = request.form.get("title")
#         description = request.form.get("description")
#         sample_input = request.form.get("sample_input")
#         sample_output = request.form.get("sample_output")
#         difficulty = request.form.get("difficulty")
#         test_cases = request.form.get("test_cases")

#         # Validate JSON format for test cases
#         try:
#             json.loads(test_cases)
#         except Exception as e:
#             flash("❌ Invalid JSON format in test cases!", "danger")
#             return redirect(url_for("admin_coding.add_question"))

#         new_q = CodingQuestion(
#             title=title,
#             description=description,
#             sample_input=sample_input,
#             sample_output=sample_output,
#             difficulty=difficulty,
#             test_cases=test_cases
#         )
#         db.session.add(new_q)
#         db.session.commit()
#         flash("✅ Coding question added successfully!", "success")
#         return redirect(url_for("admin_coding.dashboard"))

#     return render_template("admin/add_coding.html")

# # --------------------------------------------------
# # Delete question
# # --------------------------------------------------
# @admin_coding_bp.route("/delete/<int:id>")
# def delete_question(id):
#     if not admin_logged_in():
#         return redirect(url_for("admin.admin_login"))

#     q = CodingQuestion.query.get_or_404(id)
#     db.session.delete(q)
#     db.session.commit()
#     flash("🗑️ Question deleted.", "info")
#     return redirect(url_for("admin_coding.dashboard"))

# #-----------------------------------------------------

# # import csv
# # import json

# # @admin_coding_bp.route("/upload_csv", methods=["POST"])
# # def upload_csv():

# #     if not admin_logged_in():
# #         return redirect(url_for("admin.admin_login"))

# #     file = request.files.get("file")

# #     if not file:
# #         flash("❌ No CSV file uploaded", "danger")
# #         return redirect(url_for("admin_coding.add_question"))

# #     try:
# #         stream = file.stream.read().decode("UTF-8").splitlines()

# #         reader = csv.DictReader(stream)

# #         count = 0

# #         for row in reader:

# #             try:
# #                 # -----------------------------
# #                 # REQUIRED FIELDS
# #                 # -----------------------------
# #                 title = row.get("title", "").strip()
# #                 description = row.get("description", "").strip()
# #                 sample_input = row.get("sample_input", "").strip()
# #                 sample_output = row.get("sample_output", "").strip()
# #                 difficulty = row.get("difficulty", "Easy").strip()

# #                 test_cases_raw = row.get("test_cases", "[]").strip()

# #                 # -----------------------------
# #                 # VALIDATE JSON
# #                 # -----------------------------
# #                 json.loads(test_cases_raw)

# #                 question = CodingQuestion(
# #                     title=title,
# #                     description=description,
# #                     sample_input=sample_input,
# #                     sample_output=sample_output,
# #                     difficulty=difficulty,
# #                     test_cases=test_cases_raw
# #                 )

# #                 db.session.add(question)

# #                 count += 1

# #             except Exception as row_error:
# #                 print("ROW ERROR:")
# #                 print(row)
# #                 print(row_error)

# #         db.session.commit()

# #         flash(f"✅ {count} questions uploaded successfully!", "success")

# #     except Exception as e:
# #         print(e)
# #         flash("❌ CSV upload failed!", "danger")

# #     return redirect(url_for("admin_coding.add_question"))


# #  ---------

# @admin_coding_bp.route("/upload_csv", methods=["POST"])
# def upload_csv():

#     if not admin_logged_in():
#         return redirect(url_for("admin.admin_login"))

#     # =========================
#     # CHECK FILE
#     # =========================

#     if "file" not in request.files:
#         flash("❌ No file selected", "danger")
#         return redirect(url_for("admin_coding.add_question"))

#     file = request.files["file"]

#     if file.filename == "":
#         flash("❌ Please select a CSV file", "danger")
#         return redirect(url_for("admin_coding.add_question"))

#     # =========================
#     # VALIDATE FILE TYPE
#     # =========================

#     if not file.filename.endswith(".csv"):
#         flash("❌ Only CSV files are allowed", "danger")
#         return redirect(url_for("admin_coding.add_question"))

#     try:

#         # =========================
#         # READ CSV FILE
#         # =========================

#         stream = io.StringIO(
#             file.stream.read().decode("UTF8"),
#             newline=None
#         )

#         reader = csv.DictReader(stream)

#         required_columns = [
#             "title",
#             "description",
#             "sample_input",
#             "sample_output",
#             "difficulty",
#             "test_cases",
#         ]

#         # =========================
#         # VALIDATE CSV HEADERS
#         # =========================

#         csv_headers = reader.fieldnames

#         if not csv_headers:
#             flash("❌ CSV file is empty", "danger")
#             return redirect(url_for("admin_coding.add_question"))

#         missing_columns = []

#         for col in required_columns:
#             if col not in csv_headers:
#                 missing_columns.append(col)

#         if missing_columns:
#             flash(
#                 f"❌ Missing columns: {', '.join(missing_columns)}",
#                 "danger"
#             )
#             return redirect(url_for("admin_coding.add_question"))

#         # =========================
#         # PROCESS ROWS
#         # =========================

#         success_count = 0
#         failed_count = 0

#         for row_number, row in enumerate(reader, start=2):

#             try:

#                 title = (row.get("title") or "").strip()
#                 description = (row.get("description") or "").strip()
#                 sample_input = (row.get("sample_input") or "").strip()
#                 sample_output = (row.get("sample_output") or "").strip()
#                 difficulty = (row.get("difficulty") or "Easy").strip()
#                 test_cases = (row.get("test_cases") or "").strip()

#                 # =========================
#                 # SKIP EMPTY TITLE
#                 # =========================

#                 if not title:
#                     failed_count += 1
#                     print(f"Row {row_number}: Missing title")
#                     continue

#                 # =========================
#                 # VALIDATE JSON
#                 # =========================

#                 parsed_test_cases = json.loads(test_cases)

#                 if not isinstance(parsed_test_cases, list):
#                     failed_count += 1
#                     print(f"Row {row_number}: Test cases not list")
#                     continue

#                 # =========================
#                 # SAVE QUESTION
#                 # =========================

#                 question = CodingQuestion(
#                     title=title,
#                     description=description,
#                     sample_input=sample_input,
#                     sample_output=sample_output,
#                     difficulty=difficulty,
#                     test_cases=json.dumps(parsed_test_cases)
#                 )

#                 db.session.add(question)

#                 success_count += 1

#             except Exception as row_error:

#                 failed_count += 1

#                 print(
#                     f"Error in row {row_number}:",
#                     str(row_error)
#                 )

#         # =========================
#         # COMMIT DATABASE
#         # =========================

#         db.session.commit()

#         flash(
#             f"✅ {success_count} Questions Uploaded Successfully | ❌ {failed_count} Failed",
#             "success"
#         )

#     except Exception as e:

#         db.session.rollback()

#         flash(
#             f"❌ CSV Upload Failed: {str(e)}",
#             "danger"
#         )

#     return redirect(url_for("admin_coding.add_question"))





# #  ----------

# # @admin_coding_bp.route("/upload_csv", methods=["POST"])
# # def upload_csv():
# #     if not admin_logged_in():
# #         return redirect(url_for("admin.admin_login"))

# #     file = request.files.get("file")

# #     if not file:
# #         flash("❌ No file uploaded", "danger")
# #         return redirect(url_for("admin_coding.add_question"))

# #     import csv
# #     stream = file.stream.read().decode("UTF-8").splitlines()
# #     reader = csv.DictReader(stream)

# #     count = 0

# #     for row in reader:
# #         try:
# #             q = CodingQuestion(
# #                 title=row["title"],
# #                 description=row["description"],
# #                 sample_input=row["sample_input"],
# #                 sample_output=row["sample_output"],
# #                 difficulty=row["difficulty"],
# #                 test_cases=row["test_cases"]
# #             )
# #             db.session.add(q)
# #             count += 1
# #         except Exception as e:
# #             print("Error in row:", row)

# #     db.session.commit()

# #     flash(f"✅ {count} questions uploaded successfully!", "success")
# #     return redirect(url_for("admin_coding.add_question"))


























from flask import Blueprint, render_template, request, redirect, url_for, flash, session 

from app.extensions import db 

from app.models.coding_question import CodingQuestion 

import json 

 

admin_coding_bp = Blueprint("admin_coding", __name__, url_prefix="/admin/coding") 

 

# Check admin login 

def admin_logged_in(): 

    return session.get("admin_logged_in") 

 

# -------------------------------------------------- 

# Show all coding questions 

# -------------------------------------------------- 

@admin_coding_bp.route("/") 

def dashboard(): 

    if not admin_logged_in(): 

        return redirect(url_for("admin.admin_login")) 

    questions = CodingQuestion.query.all() 

    return render_template("admin/coding_dashboard.html", questions=questions) 

 

# -------------------------------------------------- 

# Add new coding question 

# -------------------------------------------------- 

@admin_coding_bp.route("/add", methods=["GET", "POST"]) 

def add_question(): 

    if not admin_logged_in(): 

        return redirect(url_for("admin.admin_login")) 

 

    if request.method == "POST": 

        title = request.form.get("title") 

        description = request.form.get("description") 

        sample_input = request.form.get("sample_input") 

        sample_output = request.form.get("sample_output") 

        difficulty = request.form.get("difficulty") 

        test_cases = request.form.get("test_cases") 

 

        # Validate JSON format for test cases 

        try: 

            json.loads(test_cases) 

        except Exception as e: 

            flash("❌ Invalid JSON format in test cases!", "danger") 

            return redirect(url_for("admin_coding.add_question")) 

 

        new_q = CodingQuestion( 

            title=title, 

            description=description, 

            sample_input=sample_input, 

            sample_output=sample_output, 

            difficulty=difficulty, 

            test_cases=test_cases 

        ) 

        db.session.add(new_q) 

        db.session.commit() 

        flash("✅ Coding question added successfully!", "success") 

        return redirect(url_for("admin_coding.dashboard")) 

 

    return render_template("admin/add_coding.html") 

 

# -------------------------------------------------- 

# Delete question 

# -------------------------------------------------- 

@admin_coding_bp.route("/delete/<int:id>") 

def delete_question(id): 

    if not admin_logged_in(): 

        return redirect(url_for("admin.admin_login")) 

 

    q = CodingQuestion.query.get_or_404(id) 

    db.session.delete(q) 

    db.session.commit() 

    flash("🗑️ Question deleted.", "info") 

    return redirect(url_for("admin_coding.dashboard")) 

 

##---------------------------- 

 

@admin_coding_bp.route("/upload_csv", methods=["POST"]) 

def upload_csv(): 

    if not admin_logged_in(): 

        return redirect(url_for("admin.admin_login")) 

 

    file = request.files.get("file") 

 

    if not file: 

        flash("❌ No file uploaded", "danger") 

        return redirect(url_for("admin_coding.add_question")) 

 

    import csv 

    stream = file.stream.read().decode("UTF-8").splitlines() 

    reader = csv.DictReader(stream) 

 

    count = 0 

 

    for row in reader: 

        try: 

            q = CodingQuestion( 

                title=row["title"], 

                description=row["description"], 

                sample_input=row["sample_input"], 

                sample_output=row["sample_output"], 

                difficulty=row["difficulty"], 

                test_cases=row["test_cases"] 

            ) 

            db.session.add(q) 

            count += 1 

        except Exception as e: 

            print("Error in row:", row) 

 

    db.session.commit() 

 

    flash(f"✅ {count} questions uploaded successfully!", "success") 

    return redirect(url_for("admin_coding.add_question")) 