"""
AI Legal Assistant Chatbot
"""
import os
import re
from flask import current_app

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

SYSTEM_CONTEXT = """You are LexReg AI Legal Assistant – an expert in Indian business law, compliance, taxation, and regulatory procedures. You assist businesses with:
- Legal document explanations
- GST, PAN, TAN, and tax queries
- Company registration procedures (MCA, ROC)
- MSME, Startup India registrations
- Import/Export (DGFT, IEC) procedures
- Environmental and factory clearances
- ISO compliance
- Employment and HR compliance
- Contract and agreement guidance
- Regulatory submissions

Always provide accurate, practical, and legally sound advice specific to India. Be professional yet approachable. Format responses with clear structure using bullet points and numbered lists where appropriate."""

FALLBACK_RESPONSES = {
    'gst': """**GST (Goods and Services Tax) – Key Information:**

• **Full Form:** Goods and Services Tax
• **Introduced:** 1st July 2017 (India)
• **Governing Body:** GST Council

**GST Registration:**
1. Mandatory if annual turnover exceeds ₹40 Lakhs (₹20L for services)
2. Apply on GST Portal: www.gst.gov.in
3. Documents needed: PAN, Aadhaar, bank account, business address proof

**GST Slabs:** 0%, 5%, 12%, 18%, 28%

**Returns:** GSTR-1 (monthly/quarterly), GSTR-3B (monthly)

Would you like help generating a GST Registration document?""",

    'pan': """**PAN (Permanent Account Number) – Key Information:**

• **Issued by:** Income Tax Department, India
• **Format:** ABCDE1234F (10 characters)
• **Purpose:** Tax identity, financial transactions

**When is PAN needed?**
- Income Tax Returns filing
- Bank accounts & investments
- Property transactions above ₹10 lakhs
- All business registrations

**How to apply:** NSDL or UTIITSL portal online

Need help with Tax Declaration documents?""",

    'company': """**Company Registration in India:**

**Types of Companies:**
1. **Private Limited (Pvt Ltd)** – Most popular for startups
2. **Public Limited** – For larger businesses
3. **OPC (One Person Company)** – Single owner
4. **LLP** – Limited Liability Partnership

**Registration Process (Pvt Ltd):**
1. Obtain DSC (Digital Signature Certificate)
2. Apply for DIN (Director Identification Number)
3. Reserve company name via RUN (Reserve Unique Name)
4. File SPICe+ form on MCA portal
5. Receive Certificate of Incorporation

**Required Documents:** PAN, Aadhaar, address proof, utility bill

Shall I generate a Company Registration document for you?""",

    'default': """I'm your **LexReg AI Legal Assistant**! I can help you with:

📋 **Document Generation** – GST, Business License, Agreements
⚖️ **Legal Explanations** – Clauses, compliance, regulations  
🏢 **Company Law** – Registration, MCA filings, compliance
💰 **Tax Guidance** – GST, Income Tax, TDS
📜 **Regulatory Procedures** – MSME, Startup India, IEC

Please ask your specific legal or compliance question, and I'll provide detailed guidance!"""
}


def get_chatbot_response(message: str, user_id: int = None) -> str:
    """Get AI chatbot response for legal queries."""
    api_key = (
        current_app.config.get('GEMINI_API_KEY') or
        os.environ.get('GEMINI_API_KEY', '')
    )

    if not api_key or not GEMINI_AVAILABLE:
        return _fallback_response(message)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash'),
            system_instruction=SYSTEM_CONTEXT
        )
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        current_app.logger.error(f"Chatbot Gemini error: {e}")
        return _fallback_response(message)


def _fallback_response(message: str) -> str:
    msg_lower = message.lower()
    for keyword, response in FALLBACK_RESPONSES.items():
        if keyword in msg_lower:
            return response
    return FALLBACK_RESPONSES['default']
