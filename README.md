# LexReg AI – Automated Legal Document Generation

> AI-powered web application for generating, editing, and downloading professional legal & regulatory documents.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

---

### 1. Clone / Navigate to Project

```bash
cd LexReg_AI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database

Open MySQL and run:
```sql
CREATE DATABASE lexreg_db;
```

Then import the schema:
```bash
mysql -u root -p lexreg_db < database.sql
```

### 5. Configure Settings

Edit `config.py` and update:
```python
DB_USER     = 'root'       # your MySQL username
DB_PASSWORD = ''           # your MySQL password
DB_NAME     = 'lexreg_db'
```

**Or** set environment variables:
```bash
set DB_USER=root
set DB_PASSWORD=yourpassword
set GEMINI_API_KEY=your_gemini_api_key
```

### 6. Run the App

```bash
python app.py
```

Open: **http://localhost:5000**

---

## 🔑 Demo Login Credentials

| Role  | Email                           | Password  |
|-------|---------------------------------|-----------|
| User  | nishanth@novaspheretech.com     | Demo@123  |
| Admin | admin@lexregai.com              | Admin@123 |

> Note: The app auto-creates tables and seeds demo data on first run.

---

## 🤖 AI Setup (Google Gemini)

1. Get a free API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Log in → **Settings** → paste your **Gemini API Key**
3. OR set environment variable: `GEMINI_API_KEY=AIza...`

> The app works **without** an API key using built-in fallback document templates.

---

## 📁 Project Structure

```
LexReg_AI/
├── app.py              ← Flask app factory
├── config.py           ← Configuration
├── requirements.txt    ← Python dependencies
├── database.sql        ← MySQL schema + seed data
├── models/             ← SQLAlchemy models
├── routes/             ← Flask blueprints
├── ai/                 ← Gemini AI integration
├── pdf/                ← ReportLab PDF generator
├── utils/              ← DOCX export, email, security
├── templates/          ← Jinja2 HTML templates
├── static/
│   ├── css/            ← CSS theme
│   ├── js/             ← JavaScript modules
│   ├── images/
│   └── uploads/        ← User uploaded files
└── README.md
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 Auth | Login, Register, Forgot Password, Session management |
| 📄 AI Generator | Generate 20+ legal documents using Google Gemini |
| ✏️ Editor | Rich text editor with bold/italic/tables/alignment |
| 📑 PDF Export | Professional PDF with logo, watermark, QR code, page numbers |
| 📝 DOCX Export | Editable Word documents |
| 🤖 AI Chatbot | Legal assistant for compliance & regulatory queries |
| 🧠 NLP | Entity extraction, keyword analysis, summarization |
| 📊 Analytics | Charts for document usage, template popularity |
| 🛡️ Admin Panel | Manage users, templates, approve/reject documents |
| 🏢 Company Profile | Pre-filled NovaSphere demo data |
| 🔔 Notifications | Real-time in-app notifications |
| 🌙 Dark Mode | Toggle between light and dark themes |

---

## 🗄️ Database Tables

- `users` – User accounts with roles
- `company_profile` – Company details (GST, PAN, CIN)
- `document_templates` – 20 legal document templates
- `generated_documents` – User documents with status tracking
- `notifications` – In-app notifications
- `activity_logs` – User activity audit trail
- `chat_history` – AI chatbot conversation history
- `analytics` – Daily usage statistics
- `downloads` – Download tracking
- `settings` – Per-user settings (API key, dark mode)

---

## 🏢 Demo Company

**NovaSphere Technologies Private Limited**
- Owner: Nishanth S (Managing Director)
- GST: 33ABCDE1234F1Z5
- PAN: ABCDE1234F
- CIN: U72900TZ2025PTC123456
- Address: No.18, Innovation Park, Coimbatore, Tamil Nadu – 641021

---

## 🔒 Security

- Passwords: bcrypt hashing
- Forms: CSRF protection (Flask-WTF)
- Sessions: HTTPOnly, SameSite cookies
- SQL: SQLAlchemy ORM (parameterized queries)
- Files: Secure filename + extension validation
- Access: Role-based (user / admin)

---

## 📄 License

MIT License – Free for personal and commercial use.

---

*Built with ❤️ using Flask, MySQL, Bootstrap 5, and Google Gemini AI*
