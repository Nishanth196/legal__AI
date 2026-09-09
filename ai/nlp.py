"""
NLP utilities – entity extraction, keyword extraction, summarization
"""
import re
import os
from flask import current_app

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def _get_model():
    api_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY', '')
    if not api_key or not GEMINI_AVAILABLE:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


def extract_entities(text: str) -> dict:
    """Extract named entities (company, GST, PAN, address, dates, persons)."""
    model = _get_model()
    entities = {
        'companies': [],
        'persons':   [],
        'gst':       [],
        'pan':       [],
        'dates':     [],
        'addresses': [],
    }

    # Regex-based extraction (always runs)
    gst_matches = re.findall(r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}', text)
    pan_matches = re.findall(r'[A-Z]{5}\d{4}[A-Z]', text)
    date_matches = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)

    entities['gst']   = list(set(gst_matches))
    entities['pan']   = list(set(pan_matches))
    entities['dates'] = list(set(date_matches))

    if model:
        try:
            prompt = f"""Extract named entities from this legal text. Return JSON with keys:
companies (list), persons (list), addresses (list).
Text: {text[:2000]}
Return only valid JSON."""
            response = model.generate_content(prompt)
            import json
            text_resp = response.text
            json_match = re.search(r'\{.*\}', text_resp, re.DOTALL)
            if json_match:
                ai_entities = json.loads(json_match.group())
                entities.update({k: v for k, v in ai_entities.items() if isinstance(v, list)})
        except Exception:
            pass

    return entities


def extract_keywords(text: str) -> list:
    """Extract top legal keywords from text."""
    model = _get_model()

    if model:
        try:
            prompt = f"""Extract the top 10 most important legal keywords from this text.
Return only a JSON array of strings.
Text: {text[:2000]}"""
            response = model.generate_content(prompt)
            import json
            match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass

    # Fallback: simple keyword extraction
    legal_terms = [
        'agreement', 'contract', 'compliance', 'registration', 'license',
        'declaration', 'undertaking', 'authorization', 'signatory', 'party',
        'clause', 'section', 'provision', 'regulation', 'authority',
        'certificate', 'application', 'approval', 'penalty', 'liability',
    ]
    words = text.lower().split()
    found = list({w for w in words if w in legal_terms})
    return found[:10]


def summarize_text(text: str) -> str:
    """Summarize a legal document."""
    model = _get_model()

    if model:
        try:
            prompt = f"""Provide a concise 3-4 sentence summary of this legal document, 
highlighting the key parties, purpose, and main obligations.
Text: {text[:3000]}"""
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            pass

    # Fallback: return first 300 chars
    return text[:300].strip() + '...' if len(text) > 300 else text
