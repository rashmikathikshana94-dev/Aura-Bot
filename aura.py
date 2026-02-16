import telebot
import requests
import time

# --- CONFIG ---
TELEGRAM_TOKEN = '8325049823:AAEQuwlom3yuncMIQZiY1C9RaqC-qsjKKus'
GEMINI_API_KEY = 'AIzaSyAy3R7JptcqQEeMvHvlL7lNc5tST-67GCM'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_chat_history = {}

def get_aura_ultimate_response(user_id, user_text):
    # Free API වලට වැඩ කරන, පිස්සු කෙළින් නැති සුපිරිම මොඩලය
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp-01-21:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    if user_id not in user_chat_history:
        user_chat_history[user_id] = [
            {
                "role": "user", 
                "parts": [{"text": (
                    "ඔයාගේ නම Aura. ඔයාව නිර්මාණය කළේ (Creator) 'රශ්මික' (Rashmika). "
                    "ඔයා ලෝකයේ සිටින සියලුම දරුවන්ගේ අධ්‍යාපනය වෙනුවෙන් කැපවුණු යාළුවෙක්. "
                    "ළමයින්ට විෂය කරුණු ඉතා සරලව සහ කරුණාවන්තව කියලා දෙන්න. "
                    "හැමවිටම සිංහලෙන් සහ ඉතා බුද්ධිමත් ලෙස පිළිතුරු දෙන්න."
                )}]
            }
        ]
    
    user_chat_history[user_id].append({"role": "user", "parts": [{"text": user_text}]})
    
    # මැසේජ් 50ක් (වැඩිපුර මතකය) තියාගන්න පුළුවන් විදිහට හැදුවා
    if len(user_chat_history[user_id]) > 50:
        system_prompt = user_chat_history[user_id][0]
        recent_history = user_chat_history[user_id][-40:]
        user_chat_history[user_id] = [system_prompt] + recent_history

    payload = {
        "contents": user_chat_history[user_id],
        "generationConfig": {
            "temperature": 0.7, 
            "maxOutputTokens": 4096 # වැඩිපුර විස්තර දීමට ඉඩ ලබා දීම
        }
    }

    for attempt in range(3):
        try:
            # Render නිසා Proxy අවශ්‍ය නැත
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            res = response.json()
            if 'candidates' in res:
                answer = res['candidates'][0]['content']['parts'][0]['text']
                user_chat_history[user_id].append({"role": "model", "parts": [{"text": answer}]})
                return answer
        except:
            time.sleep(2)
            
    return "මචං, පොඩි සර්වර් හිරවීමක්. විනාඩියකින් ආයෙත් අහන්න. ⏳"

@bot.message_handler(func=lambda message: True)
def chat(message):
    print(f"Chat with {message.chat.id}: {message.text}")
    answer = get_aura_ultimate_response(message.chat.id, message.text)
    bot.reply_to(message, answer)

print("Aura AI 2.0 (Thinking Edition) is ONLINE! 🚀🌍")
bot.infinity_polling()
