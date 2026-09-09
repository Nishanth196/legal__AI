"""
Chatbot route – serves the AI Legal Assistant page
"""
from flask import Blueprint, render_template
from flask_login import login_required

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/')
@login_required
def assistant():
    return render_template('chatbot/assistant.html')
