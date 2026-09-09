"""
Document generation, CRUD, history, editor routes
"""
import os
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app, send_file, abort)
from flask_login import login_required, current_user
from app import db
from models.document import DocumentTemplate, GeneratedDocument, Download
from models.user import Notification, ActivityLog
from models.analytics import Analytics

documents_bp = Blueprint('documents', __name__)


def add_notification(user_id, message, ntype='success'):
    n = Notification(user_id=user_id, message=message, type=ntype)
    db.session.add(n)
    db.session.commit()


def log_activity(user_id, action, details=''):
    log = ActivityLog(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Template browser
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/templates')
@login_required
def templates():
    category = request.args.get('category', '')
    query    = DocumentTemplate.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    all_templates = query.order_by(DocumentTemplate.name).all()
    categories = db.session.query(DocumentTemplate.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('documents/templates.html',
                           templates=all_templates,
                           categories=categories,
                           selected_category=category)


# ─────────────────────────────────────────────────────────────────────────────
# Generate document
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Generate document (Step 1: Company Information)
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        # Store form data in session
        from flask import session
        session['company_info'] = {
            'company_name': request.form.get('company_name'),
            'business_type': request.form.get('business_type'),
            'state': request.form.get('state'),
            'registration_type': request.form.get('registration_type'),
            'annual_turnover': request.form.get('annual_turnover'),
            'gst_number': request.form.get('gst_number'),
            'pan_number': request.form.get('pan_number'),
            'cin_number': request.form.get('cin_number'),
            'address': request.form.get('address'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone')
        }
        return redirect(url_for('documents.predict_doc'))

    # GET request: Pre-fill if profile exists
    profile = current_user.profile
    return render_template('documents/company_info.html', profile=profile)

# ─────────────────────────────────────────────────────────────────────────────
# Generate document (Step 2: ML Prediction & Step 3: Generation)
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict_doc():
    from flask import session
    import os
    import joblib
    import numpy as np
    from dl.predict_dl import predict_document_dl

    company_info = session.get('company_info')
    if not company_info:
        flash('Please fill in your company information first.', 'warning')
        return redirect(url_for('documents.generate'))

    ml_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml')
    dl_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dl')
    
    rf_model_path = os.path.join(ml_dir, 'model.pkl')
    dl_model_path = os.path.join(dl_dir, 'dl_model.keras')
    
    # Check models availability
    if not os.path.exists(rf_model_path):
        flash('No trained Machine Learning model found. Please train a model first.', 'error')
        return render_template('documents/ml_prediction.html', error=True, model_err="ML")
        
    if not os.path.exists(dl_model_path):
        flash('No trained Deep Learning model found. Please train a model first.', 'error')
        return render_template('documents/ml_prediction.html', error=True, model_err="DL")

    try:
        # 1. Random Forest prediction
        model = joblib.load(rf_model_path)
        b_encoder = joblib.load(os.path.join(ml_dir, 'business_encoder.pkl'))
        s_encoder = joblib.load(os.path.join(ml_dir, 'state_encoder.pkl'))
        r_encoder = joblib.load(os.path.join(ml_dir, 'registration_encoder.pkl'))
        t_encoder = joblib.load(os.path.join(ml_dir, 'target_encoder.pkl'))
        
        # Safely encode with fallback for unseen labels
        def safe_encode(encoder, val):
            if val in encoder.classes_:
                return encoder.transform([val])[0]
            return 0
            
        b_val = safe_encode(b_encoder, company_info['business_type'])
        s_val = safe_encode(s_encoder, company_info['state'])
        r_val = safe_encode(r_encoder, company_info['registration_type'])
        turnover = float(company_info['annual_turnover'] or 0)
        
        features = np.array([[b_val, s_val, r_val, turnover]])
        
        pred_idx = model.predict(features)[0]
        predicted_doc_ml = t_encoder.inverse_transform([pred_idx])[0]
        proba = model.predict_proba(features)[0]
        confidence_ml = round(proba[pred_idx] * 100, 1)
        
        # 2. Deep Learning prediction
        predicted_doc_dl, confidence_dl = predict_document_dl(
            company_info['business_type'],
            company_info['state'],
            company_info['registration_type'],
            company_info['annual_turnover']
        )
        
        # Compare confidence & select best
        if confidence_dl > confidence_ml:
            best_doc = predicted_doc_dl
            best_model = "Deep Learning"
            best_conf = confidence_dl
        else:
            best_doc = predicted_doc_ml
            best_model = "Random Forest"
            best_conf = confidence_ml
            
    except Exception as e:
        flash(f'Error during prediction: {str(e)}', 'error')
        return render_template('documents/ml_prediction.html', error=True, model_err="prediction")

    if request.method == 'POST':
        # Step 3: Generate Document
        from ai.generator import generate_document
        
        content = generate_document(
            template_name=best_doc,
            company_info=company_info,
            extra_info=""
        )
        
        # Find template ID – case-insensitive search
        from sqlalchemy import func as sqlfunc
        template = DocumentTemplate.query.filter(
            sqlfunc.lower(DocumentTemplate.name) == sqlfunc.lower(best_doc)
        ).first()

        # If still not found, try a partial match (contains)
        if not template:
            template = DocumentTemplate.query.filter(
                DocumentTemplate.name.ilike(f'%{best_doc}%')
            ).first()

        # If no match at all, auto-create the template so it shows correctly
        if not template:
            import re
            slug = re.sub(r'[^a-z0-9]+', '_', best_doc.lower()).strip('_')
            template = DocumentTemplate(
                name=best_doc,
                category='compliance',
                slug=slug,
                is_active=True
            )
            db.session.add(template)
            db.session.commit()

        template_id = template.id
        
        title = f"{best_doc} - {company_info.get('company_name', 'Document')}"
        
        doc = GeneratedDocument(
            user_id=current_user.id,
            template_id=template_id,
            title=title,
            content=content,
            status='generated',
        )
        db.session.add(doc)
        db.session.commit()

        Analytics.increment('total_docs')
        Analytics.increment('api_calls')
        add_notification(current_user.id, f'Document "{title}" generated successfully using {best_model} prediction!', 'success')
        log_activity(current_user.id, 'GENERATE', f'Generated: {title} ({best_model})')

        flash('Document generated successfully!', 'success')
        
        # Clear session
        session.pop('company_info', None)
        
        return redirect(url_for('documents.editor', doc_id=doc.id))

    return render_template('documents/ml_prediction.html', 
                           predicted_doc_ml=predicted_doc_ml, 
                           confidence_ml=confidence_ml,
                           predicted_doc_dl=predicted_doc_dl,
                           confidence_dl=confidence_dl,
                           best_doc=best_doc,
                           best_model=best_model,
                           best_conf=best_conf,
                           error=False)


# ─────────────────────────────────────────────────────────────────────────────
# Editor
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/editor/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def editor(doc_id):
    doc = GeneratedDocument.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        action  = request.form.get('action', 'save')
        content = request.form.get('content', '')
        title   = request.form.get('title', doc.title)

        doc.content = content
        doc.title   = title
        if action == 'finalize':
            doc.status = 'completed'
            add_notification(current_user.id, f'Document "{doc.title}" finalized!', 'success')
        else:
            doc.status = 'generated'
        db.session.commit()
        flash('Document saved successfully!', 'success')
        return redirect(url_for('documents.editor', doc_id=doc.id))

    return render_template('documents/editor.html', doc=doc)


# ─────────────────────────────────────────────────────────────────────────────
# Document history
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/history')
@login_required
def history():
    page    = request.args.get('page', 1, type=int)
    search  = request.args.get('search', '').strip()
    status  = request.args.get('status', '')
    per_page = current_app.config.get('DOCS_PER_PAGE', 10)

    query = GeneratedDocument.query.filter_by(user_id=current_user.id)
    if search:
        query = query.filter(GeneratedDocument.title.ilike(f'%{search}%'))
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(GeneratedDocument.updated_at.desc())
    docs  = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('documents/history.html', docs=docs, search=search, status=status)


# ─────────────────────────────────────────────────────────────────────────────
# Download PDF
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/download/pdf/<int:doc_id>')
@login_required
def download_pdf(doc_id):
    doc = GeneratedDocument.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    profile = current_user.profile

    from pdf.generator import generate_pdf
    pdf_path = generate_pdf(doc, profile)

    doc.pdf_path = pdf_path
    db.session.commit()

    dl = Download(user_id=current_user.id, document_id=doc.id, format='pdf')
    db.session.add(dl)
    Analytics.increment('downloads')
    db.session.commit()

    add_notification(current_user.id, f'PDF downloaded: {doc.title}', 'info')
    log_activity(current_user.id, 'DOWNLOAD_PDF', doc.title)
    return send_file(pdf_path, as_attachment=True,
                     download_name=f"{doc.title.replace(' ', '_')}.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# Download DOCX
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/download/docx/<int:doc_id>')
@login_required
def download_docx(doc_id):
    doc = GeneratedDocument.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    profile = current_user.profile

    from utils.docx_export import generate_docx
    docx_path = generate_docx(doc, profile)

    doc.docx_path = docx_path
    db.session.commit()

    dl = Download(user_id=current_user.id, document_id=doc.id, format='docx')
    db.session.add(dl)
    Analytics.increment('downloads')
    db.session.commit()

    add_notification(current_user.id, f'DOCX downloaded: {doc.title}', 'info')
    log_activity(current_user.id, 'DOWNLOAD_DOCX', doc.title)
    return send_file(docx_path, as_attachment=True,
                     download_name=f"{doc.title.replace(' ', '_')}.docx")


# ─────────────────────────────────────────────────────────────────────────────
# Delete document
# ─────────────────────────────────────────────────────────────────────────────
@documents_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    doc = GeneratedDocument.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    title = doc.title
    db.session.delete(doc)
    db.session.commit()
    flash(f'Document "{title}" deleted.', 'info')
    log_activity(current_user.id, 'DELETE', title)
    return redirect(url_for('documents.history'))


@documents_bp.route('/link-csv', methods=['GET', 'POST'])
@login_required
def link_csv():
    import csv
    import io
    results = []
    headers = []
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(request.url)
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
            csv_reader = csv.reader(stream)
            try:
                headers = next(csv_reader)
            except StopIteration:
                flash('CSV file is empty', 'danger')
                return redirect(request.url)

            # Look for a description column
            desc_col_idx = 0
            for i, h in enumerate(headers):
                if any(x in h.lower() for x in ['desc', 'requirement', 'text', 'purpose', 'need', 'about', 'company', 'info']):
                    desc_col_idx = i
                    break

            from ai.generator import recommend_template
            row_count = 0
            for row in csv_reader:
                if not row or all(not x.strip() for x in row):
                    continue
                row_count += 1
                if row_count > 10:  # Limit processing to avoid API limits
                    break
                
                desc_text = row[desc_col_idx] if len(row) > desc_col_idx else ' '.join(row)
                recommendations = recommend_template(desc_text)
                
                # Fetch templates from DB corresponding to recommended template names
                rec_templates = []
                for name in recommendations:
                    t = DocumentTemplate.query.filter_by(name=name, is_active=True).first()
                    if t:
                        rec_templates.append(t)
                
                results.append({
                    'row': row,
                    'description': desc_text,
                    'recommendations': rec_templates
                })
            flash(f'Successfully parsed CSV and mapped {len(results)} rows with AI recommendations!', 'success')
        else:
            flash('Please upload a valid CSV file.', 'danger')
            
    return render_template('documents/link_csv.html', headers=headers, results=results)
