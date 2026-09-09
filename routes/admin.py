"""
Admin panel routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from models.user import User, ActivityLog
from models.document import DocumentTemplate, GeneratedDocument
from models.analytics import Analytics

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def index():
    total_users = User.query.count()
    total_docs  = GeneratedDocument.query.count()
    total_templates = DocumentTemplate.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_docs  = GeneratedDocument.query.order_by(GeneratedDocument.created_at.desc()).limit(5).all()
    analytics_rows = Analytics.query.order_by(Analytics.date.desc()).limit(30).all()
    return render_template('admin/index.html',
                           total_users=total_users,
                           total_docs=total_docs,
                           total_templates=total_templates,
                           recent_users=recent_users,
                           recent_docs=recent_docs,
                           analytics_rows=analytics_rows)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page  = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    query = User.query
    if search:
        query = query.filter(User.email.ilike(f'%{search}%') | User.name.ilike(f'%{search}%'))
    users_pg = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users_pg, search=search)


@admin_bp.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_verified = not user.is_verified
    db.session.commit()
    flash(f'User {user.email} status updated.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.email == 'admin@lexregai.com':
        flash('Cannot delete the default admin account.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User deleted.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/documents')
@login_required
@admin_required
def documents():
    page = request.args.get('page', 1, type=int)
    docs = GeneratedDocument.query.order_by(GeneratedDocument.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/documents.html', docs=docs)


@admin_bp.route('/documents/approve/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def approve_doc(doc_id):
    doc = GeneratedDocument.query.get_or_404(doc_id)
    doc.status = 'completed'
    db.session.commit()
    flash(f'Document approved.', 'success')
    return redirect(url_for('admin.documents'))


@admin_bp.route('/documents/reject/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def reject_doc(doc_id):
    doc = GeneratedDocument.query.get_or_404(doc_id)
    doc.status = 'draft'
    db.session.commit()
    flash(f'Document rejected.', 'warning')
    return redirect(url_for('admin.documents'))


@admin_bp.route('/templates')
@login_required
@admin_required
def templates():
    templates = DocumentTemplate.query.all()
    return render_template('admin/templates.html', templates=templates)


@admin_bp.route('/templates/add', methods=['POST'])
@login_required
@admin_required
def add_template():
    name     = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    slug     = name.lower().replace(' ', '_')
    if name and not DocumentTemplate.query.filter_by(slug=slug).first():
        tpl = DocumentTemplate(name=name, category=category, slug=slug, is_active=True)
        db.session.add(tpl)
        db.session.commit()
        flash('Template added.', 'success')
    else:
        flash('Template name already exists or invalid.', 'danger')
    return redirect(url_for('admin.templates'))


@admin_bp.route('/templates/delete/<int:tpl_id>', methods=['POST'])
@login_required
@admin_required
def delete_template(tpl_id):
    tpl = DocumentTemplate.query.get_or_404(tpl_id)
    db.session.delete(tpl)
    db.session.commit()
    flash('Template deleted.', 'info')
    return redirect(url_for('admin.templates'))
