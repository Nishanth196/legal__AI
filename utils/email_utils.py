"""
Email utilities (Flask-Mail)
"""
from flask_mail import Message
from app import mail


def send_email(to: str, subject: str, body: str, html: str = None):
    """Send an email. Silently fails if mail is not configured."""
    try:
        msg = Message(subject=subject, recipients=[to], body=body, html=html)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Mail] Failed to send to {to}: {e}")
        return False


def send_welcome_email(user):
    send_email(
        to      = user.email,
        subject = 'Welcome to LexReg AI!',
        html    = f"""
        <h2>Welcome, {user.name}!</h2>
        <p>Your LexReg AI account is ready. Start generating professional legal documents in seconds.</p>
        <p><a href="http://localhost:5000/dashboard">Login to Dashboard</a></p>
        <hr/>
        <p style="color:#666;font-size:12px;">LexReg AI – Automated Legal Document Generation</p>
        """
    )


def send_document_ready_email(user, document_title: str):
    send_email(
        to      = user.email,
        subject = f'Document Ready: {document_title}',
        html    = f"""
        <h2>Your document is ready!</h2>
        <p><strong>{document_title}</strong> has been generated successfully.</p>
        <p><a href="http://localhost:5000/documents/history">View & Download</a></p>
        <hr/>
        <p style="color:#666;font-size:12px;">LexReg AI – Automated Legal Document Generation</p>
        """
    )
