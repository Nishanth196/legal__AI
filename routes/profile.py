"""
Profile and Settings routes
"""
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from models.company import CompanyProfile
from models.user import Setting

profile_bp = Blueprint('profile', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@profile_bp.route('/company', methods=['GET', 'POST'])
@login_required
def company():
    profile = current_user.profile or CompanyProfile(user_id=current_user.id)

    if request.method == 'POST':
        profile.company_name         = request.form.get('company_name', '').strip()
        profile.business_type        = request.form.get('business_type', '').strip()
        profile.owner_name           = request.form.get('owner_name', '').strip()
        profile.designation          = request.form.get('designation', '').strip()
        profile.email                = request.form.get('email', '').strip()
        profile.phone                = request.form.get('phone', '').strip()
        profile.website              = request.form.get('website', '').strip()
        profile.address              = request.form.get('address', '').strip()
        profile.pan_number           = request.form.get('pan_number', '').strip()
        profile.gst_number           = request.form.get('gst_number', '').strip()
        profile.cin_number           = request.form.get('cin_number', '').strip()
        profile.registration_date    = request.form.get('registration_date', '').strip()
        profile.authorized_signatory = request.form.get('authorized_signatory', '').strip()

        # Handle logo upload
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo and logo.filename and allowed_file(logo.filename):
                from werkzeug.utils import secure_filename
                filename = secure_filename(logo.filename)
                logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                logo.save(logo_path)
                profile.logo_path = f'uploads/{filename}'

        if not profile.id:
            db.session.add(profile)
        db.session.commit()
        flash('Company profile updated successfully!', 'success')
        return redirect(url_for('profile.company'))

    return render_template('profile/company.html', profile=profile)


@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        gemini_key = request.form.get('gemini_api_key', '').strip()
        dark_mode  = request.form.get('dark_mode', '0')

        for key, value in [('gemini_api_key', gemini_key), ('dark_mode', dark_mode)]:
            s = Setting.query.filter_by(user_id=current_user.id, key=key).first()
            if s:
                s.value = value
            else:
                db.session.add(Setting(user_id=current_user.id, key=key, value=value))
        db.session.commit()
        flash('Settings saved.', 'success')

    settings_dict = {s.key: s.value for s in
                     Setting.query.filter_by(user_id=current_user.id).all()}
    return render_template('profile/settings.html', settings=settings_dict)
