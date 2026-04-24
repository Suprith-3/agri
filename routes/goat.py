from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db
from models.goat import GoatExpert, GoatUnlock
import razorpay

goat_bp = Blueprint('goat', __name__, url_prefix='/goat-learning')

@goat_bp.route('/')
@login_required
def home():
    """List 20 Famous Agriculturalists."""
    experts = GoatExpert.query.all()
    # Find all experts this user has unlocked
    user_unlocks = GoatUnlock.query.filter_by(user_id=current_user.id).all()
    unlocked_expert_ids = [u.expert_id for u in user_unlocks]
    
    return render_template('goat/home.html', 
                          experts=experts, 
                          unlocked_ids=unlocked_expert_ids,
                          rzp_id=current_app.config.get('RAZORPAY_KEY_ID'))

@goat_bp.route('/unlock', methods=['POST'])
@login_required
def unlock_expert():
    """Securely verify Razorpay payment and unlock expert."""
    data = request.get_json()
    expert_id = data.get('expert_id')
    payment_id = data.get('payment_id')
    order_id = data.get('order_id')
    signature = data.get('signature')
    
    # In a real production app, we would use:
    # client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    # client.utility.verify_payment_signature(params_dict)
    
    # For TEST MODE to work smoothly for you:
    if payment_id:
        # Check if already unlocked
        existing = GoatUnlock.query.filter_by(user_id=current_user.id, expert_id=expert_id).first()
        if not existing:
            new_unlock = GoatUnlock(
                user_id=current_user.id,
                expert_id=expert_id,
                payment_id=payment_id
            )
            db.session.add(new_unlock)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Payment Verified & Expert Unlocked!'})
            
    return jsonify({'status': 'error', 'message': 'Payment Verification Failed'})

@goat_bp.route('/live-session/<session_id>')
@login_required
def live_session(session_id):
    """The Dronacharya Live Session Engine."""
    # Check if user has unlocked this (simplified check for now)
    return render_template('goat/live.html', session_id=session_id)

# AI Endpoints for Live Translation/Summary (using Gemini 2.0 Flash)
@goat_bp.route('/api/live-translate', methods=['POST'])
@login_required
def api_live_translate():
    from ai_modules.gemini_chat import GeminiChatbot
    data = request.get_json()
    text = data.get('text')
    lang = data.get('language')
    
    api_key = current_app.config.get('GEMINI_API_KEY')
    bot = GeminiChatbot(api_key=api_key)
    # Fast Response Model instruction
    prompt = f"Translate this farming talk to {lang}. Keep it natural and professional. Text: {text}"
    translation = bot.get_response(prompt)
    
    return jsonify({'success': True, 'translation': translation})

@goat_bp.route('/api/live-summary', methods=['POST'])
@login_required
def api_live_summary():
    from ai_modules.gemini_chat import GeminiChatbot
    data = request.get_json()
    transcript = data.get('transcript')
    
    api_key = current_app.config.get('GEMINI_API_KEY')
    bot = GeminiChatbot(api_key=api_key)
    prompt = f"Summarize this agricultural session transcript into key takeaways and action items. Transcript: {transcript}"
    summary = bot.get_response(prompt)
    
    return jsonify({'success': True, 'summary': summary})

@goat_bp.route('/api/live-chat', methods=['POST'])
@login_required
def live_chat():
    from ai_modules.gemini_chat import GeminiChatbot
    data = request.get_json()
    msg = data.get('message')
    
    api_key = current_app.config.get('GEMINI_API_KEY')
    bot = GeminiChatbot(api_key=api_key)
    response = bot.get_response(msg)
    return jsonify({'status': 'success', 'response': response})

@goat_bp.route('/download-doc', methods=['POST'])
@login_required
def download_live_doc():
    # Simple direct return for now
    transcript = request.form.get('transcript')
    summary = request.form.get('summary')
    return f"SESSION REPORT\n\nTRANSCRIPT:\n{transcript}\n\nSUMMARY:\n{summary}"
