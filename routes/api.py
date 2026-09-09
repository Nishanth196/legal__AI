"""
API routes (AJAX endpoints for chatbot, notifications, NLP)
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models.user import Notification
from models.document import ChatHistory

api_bp = Blueprint('api', __name__)


@api_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """AI Legal Assistant chatbot endpoint."""
    data    = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Empty message'}), 400

    from ai.chatbot import get_chatbot_response
    response = get_chatbot_response(message, current_user.id)

    # Save to history
    history = ChatHistory(user_id=current_user.id, message=message, response=response)
    db.session.add(history)
    db.session.commit()

    return jsonify({'response': response})


@api_bp.route('/notifications')
@login_required
def notifications():
    notifs = (Notification.query
              .filter_by(user_id=current_user.id, is_read=False)
              .order_by(Notification.created_at.desc())
              .limit(10).all())
    return jsonify([{
        'id':      n.id,
        'message': n.message,
        'type':    n.type,
        'time':    n.created_at.strftime('%H:%M'),
    } for n in notifs])


@api_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})


@api_bp.route('/nlp/analyze', methods=['POST'])
@login_required
def nlp_analyze():
    """NLP analysis: entity extraction, keywords, summary."""
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'No text'}), 400

    from ai.nlp import extract_entities, extract_keywords, summarize_text
    entities = extract_entities(text)
    keywords = extract_keywords(text)
    summary  = summarize_text(text)

    return jsonify({
        'entities': entities,
        'keywords': keywords,
        'summary':  summary,
    })


@api_bp.route('/recommend', methods=['POST'])
@login_required
def recommend():
    """ML document recommendation."""
    data        = request.get_json() or {}
    description = data.get('description', '').strip()
    if not description:
        return jsonify({'error': 'No description'}), 400

    from ai.generator import recommend_template
    recommendations = recommend_template(description)
    return jsonify({'recommendations': recommendations})


@api_bp.route('/chat/history')
@login_required
def chat_history():
    history = (ChatHistory.query
               .filter_by(user_id=current_user.id)
               .order_by(ChatHistory.created_at.desc())
               .limit(20).all())
    return jsonify([{
        'message':  h.message,
        'response': h.response,
        'time':     h.created_at.strftime('%Y-%m-%d %H:%M'),
    } for h in history])
