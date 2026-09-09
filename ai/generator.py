"""
AI Document Generator using Google Gemini API
"""
import os
import re
from flask import current_app

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def _get_client():
    """Initialize Gemini client with API key."""
    api_key = (
        current_app.config.get('GEMINI_API_KEY') or
        os.environ.get('GEMINI_API_KEY', '')
    )
    if not api_key or not GEMINI_AVAILABLE:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash'))


def _fallback_content(template_name: str, company_info: dict) -> str:
    """Return a rich fallback document when Gemini is unavailable."""
    company = company_info.get('company_name', 'NovaSphere Technologies Private Limited')
    owner   = company_info.get('owner_name',   'Nishanth S')
    gst     = company_info.get('gst_number',   '33ABCDE1234F1Z5')
    pan     = company_info.get('pan_number',   'ABCDE1234F')
    addr    = company_info.get('address',      'No.18, Innovation Park, Coimbatore, Tamil Nadu – 641021')
    date_   = '15-04-2025'

    return f"""<h2>{template_name.upper()}</h2>

<p><strong>Date:</strong> {date_}</p>
<p><strong>Reference No:</strong> LEXREG/{template_name[:3].upper()}/2025/001</p>

<hr/>

<h3>PARTY DETAILS</h3>
<table class="table table-bordered">
  <tr><td><strong>Company Name</strong></td><td>{company}</td></tr>
  <tr><td><strong>Owner / MD</strong></td><td>{owner}</td></tr>
  <tr><td><strong>GST Number</strong></td><td>{gst}</td></tr>
  <tr><td><strong>PAN Number</strong></td><td>{pan}</td></tr>
  <tr><td><strong>Address</strong></td><td>{addr}</td></tr>
</table>

<h3>1. INTRODUCTION</h3>
<p>This document pertains to the <strong>{template_name}</strong> as required under the applicable laws and regulations of India. {company}, a duly incorporated company, hereby submits this document in accordance with the prescribed format and regulations.</p>

<h3>2. DECLARATION</h3>
<p>I, <strong>{owner}</strong>, Managing Director of <strong>{company}</strong>, hereby declare that all information provided herein is true, accurate, and complete to the best of my knowledge and belief. The company is in full compliance with all applicable regulations as on the date of this document.</p>

<h3>3. REGULATORY COMPLIANCE</h3>
<p>The company confirms compliance with:</p>
<ul>
  <li>The Companies Act, 2013</li>
  <li>The Goods and Services Tax Act, 2017</li>
  <li>The Income Tax Act, 1961</li>
  <li>All applicable state and central regulations</li>
</ul>

<h3>4. UNDERTAKING</h3>
<p>The company undertakes to notify the relevant authority within 30 days of any change in the information provided herein. All requisite fees and charges have been duly paid as prescribed.</p>

<h3>5. AUTHORIZED SIGNATORY</h3>
<p>This document is duly authorized and executed by:</p>
<p><strong>Name:</strong> {owner}<br/>
<strong>Designation:</strong> Managing Director<br/>
<strong>Company:</strong> {company}</p>

<br/><br/>
<p>________________________<br/>
<strong>Authorized Signatory</strong><br/>
{owner}<br/>
{company}</p>
"""


def generate_document(template_name: str, company_info: dict, extra_info: str = '') -> str:
    """Generate a professional legal document using Gemini AI."""
    client = _get_client()

    if not client:
        return _fallback_content(template_name, company_info)

    company = company_info.get('company_name', 'Company')
    prompt  = f"""You are a senior Indian legal expert and document drafter. Generate a complete, professional, and legally accurate {template_name} document for the following company.

Company Details:
- Company Name: {company_info.get('company_name', 'N/A')}
- Business Type: {company_info.get('business_type', 'N/A')}
- Owner/MD: {company_info.get('owner_name', 'N/A')}
- Designation: {company_info.get('designation', 'N/A')}
- Email: {company_info.get('email', 'N/A')}
- Phone: {company_info.get('phone', 'N/A')}
- Address: {company_info.get('address', 'N/A')}
- PAN: {company_info.get('pan_number', 'N/A')}
- GST: {company_info.get('gst_number', 'N/A')}
- CIN: {company_info.get('cin_number', 'N/A')}
- Registration Date: {company_info.get('registration_date', 'N/A')}
- Authorized Signatory: {company_info.get('authorized_signatory', 'N/A')}

Additional Information: {extra_info if extra_info else 'None'}

Requirements:
1. Generate a full, complete {template_name} document in HTML format
2. Use proper legal structure with numbered sections and sub-sections
3. Include all mandatory legal clauses and compliance statements
4. Add a proper header with document reference number, date, and all company details
5. Include declaration, undertaking, and authorized signatory section
6. Format using HTML tags (h2, h3, p, ul, li, table, strong, em)
7. Use professional legal language appropriate for Indian regulatory submissions
8. Include relevant Indian laws, acts, and regulatory references
9. Make the document comprehensive with at least 8-10 sections

Generate the complete HTML document now:"""

    try:
        response = client.generate_content(prompt)
        content  = response.text
        # Strip markdown code fences if present
        content  = re.sub(r'^```html\n?', '', content, flags=re.MULTILINE)
        content  = re.sub(r'\n?```$', '', content, flags=re.MULTILINE)
        return content
    except Exception as e:
        current_app.logger.error(f"Gemini error: {e}")
        return _fallback_content(template_name, company_info)



# ── Keyword-based ML template classifier (works without API key) ──────────────
_TEMPLATE_KEYWORDS = {
    'GST Registration':           ['gst', 'goods', 'services tax', 'gstin', 'gst registration', 'tax registration'],
    'Business License':           ['business license', 'shop act', 'trade permit', 'gumasta', 'business permit'],
    'Trade License':              ['trade license', 'trade permit', 'local body', 'municipal', 'shop'],
    'Import Export License':      ['import', 'export', 'iec', 'dgft', 'customs', 'foreign trade', 'fema'],
    'Company Registration':       ['company registration', 'mca', 'incorporate', 'pvt ltd', 'private limited', 'llp', 'opc'],
    'Partnership Agreement':      ['partnership', 'partner', 'firm', 'deed', 'profit sharing'],
    'Non Disclosure Agreement':   ['nda', 'non disclosure', 'confidential', 'secrecy', 'proprietary'],
    'Privacy Policy':             ['privacy', 'data protection', 'gdpr', 'personal data', 'user data'],
    'Terms and Conditions':       ['terms', 'conditions', 'tnc', 'terms of service', 'user agreement'],
    'Employee Agreement':         ['employee', 'employment', 'service agreement', 'appointment', 'hr contract'],
    'Offer Letter':               ['offer letter', 'job offer', 'appointment letter', 'hiring', 'onboarding'],
    'Vendor Agreement':           ['vendor', 'supplier', 'procurement', 'purchase agreement', 'outsource'],
    'Compliance Report':          ['compliance', 'audit', 'regulatory report', 'annual return', 'filing'],
    'Regulatory Submission':      ['regulatory', 'submission', 'application', 'filing', 'approval', 'government'],
    'Tax Declaration':            ['tax', 'income tax', 'itr', 'declaration', 'return', 'tds', 'pan'],
    'Environmental Clearance':    ['environment', 'noc', 'pollution', 'clearance', 'green', 'eia'],
    'Factory License':            ['factory', 'manufacturing', 'industrial', 'plant', 'production license'],
    'ISO Compliance':             ['iso', 'quality management', 'certification', 'standard', '9001', '27001'],
    'MSME Registration':          ['msme', 'udyam', 'small enterprise', 'medium enterprise', 'udyog aadhaar'],
    'Startup India Registration': ['startup', 'dpiit', 'innovation', 'incubator', 'startup india', 'seed fund'],
}


def _ml_classify(description: str) -> list:
    """Keyword-based TF-IDF-style scoring classifier for template matching."""
    desc_lower = description.lower()
    scores = {}
    for template, keywords in _TEMPLATE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in desc_lower:
                # Longer keyword matches score higher
                score += len(kw.split())
        scores[template] = score
    # Sort by score descending, return top 5
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    # Return templates with score > 0, or top 5 if none matched
    matched = [t for t, s in ranked if s > 0]
    return matched[:5] if matched else [t for t, _ in ranked[:5]]


def recommend_template(description: str) -> list:
    """Recommend document templates based on user description.
    Uses Gemini LLM if API key is configured, else falls back to keyword ML classifier.
    """
    # Try Gemini LLM first
    client = _get_client()
    templates_list = list(_TEMPLATE_KEYWORDS.keys())

    if client:
        prompt = f"""Based on this description: "{description}"
Recommend the top 5 most relevant legal document templates from this list:
{', '.join(templates_list)}
Return ONLY a JSON array of template names, e.g.: ["Template 1", "Template 2"]"""
        try:
            response = client.generate_content(prompt)
            import json
            text = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if text:
                return json.loads(text.group())
        except Exception:
            pass

    # Keyword-based ML fallback
    return _ml_classify(description)
