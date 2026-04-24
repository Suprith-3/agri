from flask import Blueprint, request, jsonify, session, render_template, current_app
from flask_login import login_required, current_user
from models import db
from models.prediction import ChatHistory
from ai_modules.gemini_chat import GeminiChatbot

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/')
@login_required
def chat():
    """Render chatbot UI."""
    return render_template('chatbot/chat.html')

@chatbot_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    """AJAX endpoint for chatbot interaction."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'No input provided.'}), 400
        
    user_message = data['message']
    
    # Init history in session if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []
        
    # Get response from logic
    try:
        api_key = current_app.config.get('GROQ_API_KEY')
        model = current_app.config.get('GROQ_MODEL')
        chatbot = GeminiChatbot(api_key=api_key, model=model)
        
        bot_response = chatbot.get_response(user_message, history=session['chat_history'])
        
        # Save to session
        history = session['chat_history']
        history.append({'role': 'user', 'content': user_message})
        history.append({'role': 'model', 'content': bot_response})
        
        # Keep only last 20 messages (10 pairs)
        if len(history) > 20:
            history = history[-20:]
        session['chat_history'] = history
        session.modified = True
        
        # Save to DB
        chat_record = ChatHistory(
            user_id=current_user.id,
            user_message=user_message,
            bot_response=bot_response
        )
        db.session.add(chat_record)
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'response': bot_response
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@chatbot_bp.route('/clear', methods=['POST'])
@login_required
def clear():
    """Clear session chat history."""
    session.pop('chat_history', None)
    return jsonify({'status': 'success'})
