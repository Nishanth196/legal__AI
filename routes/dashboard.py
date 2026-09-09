"""
Dashboard routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from models.document import GeneratedDocument, DocumentTemplate
from models.user import Notification, ActivityLog
from models.analytics import Analytics

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/index')
@login_required
def index():
    # Stats
    total_docs     = GeneratedDocument.query.filter_by(user_id=current_user.id).count()
    completed_docs = GeneratedDocument.query.filter_by(user_id=current_user.id, status='completed').count()
    draft_docs     = GeneratedDocument.query.filter_by(user_id=current_user.id, status='draft').count()
    generated_docs = GeneratedDocument.query.filter_by(user_id=current_user.id, status='generated').count()

    # Recent activity
    recent_docs = (GeneratedDocument.query
                   .filter_by(user_id=current_user.id)
                   .order_by(GeneratedDocument.updated_at.desc())
                   .limit(5).all())

    # Notifications
    notifications = (Notification.query
                     .filter_by(user_id=current_user.id, is_read=False)
                     .order_by(Notification.created_at.desc())
                     .limit(5).all())

    # Recent activities
    activities = (ActivityLog.query
                  .filter_by(user_id=current_user.id)
                  .order_by(ActivityLog.created_at.desc())
                  .limit(8).all())

    # Template categories
    templates = DocumentTemplate.query.filter_by(is_active=True).all()

    Analytics.increment('total_docs', 0)   # ensure today's row exists

    return render_template(
        'dashboard/index.html',
        total_docs     = total_docs,
        completed_docs = completed_docs,
        draft_docs     = draft_docs,
        generated_docs = generated_docs,
        recent_docs    = recent_docs,
        notifications  = notifications,
        activities     = activities,
        templates      = templates,
    )


@dashboard_bp.route('/analytics')
@login_required
def analytics():
    from sqlalchemy import func
    # Check config for database-agnostic date formatting
    from flask import current_app
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite') or 'sqlite' in db_uri:
        month_func = func.strftime('%Y-%m', GeneratedDocument.created_at)
    else:
        month_func = func.date_format(GeneratedDocument.created_at, '%Y-%m')

    # Monthly doc counts (last 6 months)
    monthly = (db.session.query(
        month_func.label('month'),
        func.count(GeneratedDocument.id).label('count')
    ).filter_by(user_id=current_user.id)
     .group_by(month_func)
     .order_by(month_func)
     .limit(6).all())

    # Template usage
    template_usage = (db.session.query(
        DocumentTemplate.name,
        func.count(GeneratedDocument.id).label('count')
    ).join(GeneratedDocument, GeneratedDocument.template_id == DocumentTemplate.id)
     .filter(GeneratedDocument.user_id == current_user.id)
     .group_by(DocumentTemplate.id)
     .order_by(func.count(GeneratedDocument.id).desc())
     .limit(8).all())

    # Convert tuples to serializable lists for Chart.js
    monthly_data = [[row[0] or 'Unknown', row[1]] for row in monthly]
    template_data = [[row[0] or 'Unknown', row[1]] for row in template_usage]

    return render_template(
        'dashboard/analytics.html',
        monthly=monthly_data,
        template_usage=template_data
    )
