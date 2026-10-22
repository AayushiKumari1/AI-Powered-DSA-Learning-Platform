from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.extensions import db
from app.models.flash_note import FlashNote

flash_notes_bp = Blueprint("flash_notes", __name__, url_prefix="/notes")


@flash_notes_bp.route("/", methods=["GET"])
@login_required
def index():
    query_text = (request.args.get("q") or "").strip()
    subject_filter = (request.args.get("subject") or "").strip()

    notes_query = FlashNote.query.filter_by(user_id=current_user.id)

    if query_text:
        like_pattern = f"%{query_text}%"
        notes_query = notes_query.filter(
            or_(
                FlashNote.subject.ilike(like_pattern),
                FlashNote.title.ilike(like_pattern),
                FlashNote.content.ilike(like_pattern),
            )
        )

    if subject_filter:
        notes_query = notes_query.filter(FlashNote.subject == subject_filter)

    notes = notes_query.order_by(FlashNote.updated_at.desc(), FlashNote.id.desc()).all()

    subjects = (
        db.session.query(FlashNote.subject)
        .filter_by(user_id=current_user.id)
        .distinct()
        .order_by(FlashNote.subject.asc())
        .all()
    )
    subject_options = [s[0] for s in subjects]

    return render_template(
        "notes/index.html",
        notes=notes,
        query_text=query_text,
        subject_filter=subject_filter,
        subject_options=subject_options,
    )


@flash_notes_bp.route("/create", methods=["POST"])
@login_required
def create():
    subject = (request.form.get("subject") or "").strip()
    title = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()

    if not subject or not title or not content:
        flash("Subject, title and short content are required.", "warning")
        return redirect(url_for("flash_notes.index"))

    note = FlashNote(
        user_id=current_user.id,
        subject=subject,
        title=title,
        content=content,
    )
    db.session.add(note)
    db.session.commit()
    flash("Flash note saved.", "success")
    return redirect(url_for("flash_notes.index"))


@flash_notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(note_id):
    note = FlashNote.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        subject = (request.form.get("subject") or "").strip()
        title = (request.form.get("title") or "").strip()
        content = (request.form.get("content") or "").strip()

        if not subject or not title or not content:
            flash("Subject, title and short content are required.", "warning")
            return render_template("notes/edit.html", note=note)

        note.subject = subject
        note.title = title
        note.content = content
        db.session.commit()
        flash("Flash note updated.", "success")
        return redirect(url_for("flash_notes.index"))

    return render_template("notes/edit.html", note=note)


@flash_notes_bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required
def delete(note_id):
    note = FlashNote.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    flash("Flash note deleted.", "info")
    return redirect(url_for("flash_notes.index"))
