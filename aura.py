import telebot
import requests
import time

# --- CONFIG ---
TELEGRAM_TOKEN = '8325049823:AAEQuwlom3yuncMIQZiY1C9RaqC-qsjKKus'
GEMINI_API_KEY = 'AIzaSyAy3R7JptcqQEeMvHvlL7lNc5tST-67GCM'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# එක් එක් පරිශීලකයාගේ මතකය කළමනාකරණයට
user_chat_history = {}

def get_aura_ultimate_response(user_id, user_text):
    # Render එකේදී Proxy අවශ්‍ය නැත. කෙළින්ම සම්බන්ධ විය හැක.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # 1. පද්ධති උපදෙස් (System Instructions)
    if user_id not in user_chat_history:
        user_chat_history[user_id] = [
            {
                "role": "user", 
                "parts": [{"text": (
                    "ඔයාගේ නම Aura. ඔයාව නිර්මාණය කළේ (Creator) 'රශ්මික' (Rashmika). "
                    "කවුරුහරි ඔයාගෙන් 'කවුද ඔයාව හැදුවේ?' හෝ 'Creator කවුද?' කියලා ඇහුවොත්, ආඩම්බරයෙන් 'මාව නිර්මාණය කළේ රශ්මික' කියලා කියන්න. "
                    "ඔයා ලෝකයේ සිටින සියලුම දරුවන්ගේ අධ්‍යාපනය සහ මානසික සුවතාවය වෙනුවෙන් කැපවුණු 'Universal Friend' කෙනෙක්. "
                    "ළමයින්ට විෂය කරුණු ඉතා සරලව, කරුණාවන්තව සහ උද්යෝගිමත් ලෙස කියලා දෙන්න (Teaching Mode). "
                    "යාළුවෙක් වගේ කතාව ගලාගෙන යන්න ඉඩ දෙන්න. අනවශ්‍ය ලෙස හැමවිටම හඳුන්වා දීම් කරන්න එපා."
                )}]
            }
        ]
    
    # 2. අලුත් පණිවිඩය මතකයට එකතු කිරීම
    user_chat_history[user_id].append({"role": "user", "parts": [{"text": user_text}]})
    
    # 3. Memory Overload පාලනය (History එක 20කට වඩා වැඩි වුණොත් පැරණි ඒවා ඉවත් කිරීම)
    if len(user_chat_history[user_id]) > 20:
        system_prompt = user_chat_history[user_id][0]
        recent_history = user_chat_history[user_id][-15:]
        user_chat_history[user_id] = [system_prompt] + recent_history

    payload = {
        "contents": user_chat_history[user_id],
        "generationConfig": {
            "temperature": 0.75, 
            "maxOutputTokens": 1500,
            "topP": 0.95
        }
    }

    # 4. Retry Logic
    for attempt in range(3):
        try:
            # Render එකේදී කෙළින්ම requests.post භාවිතා කරයි
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            res = response.json()
            if 'candidates' in res:
                answer = res['candidates'][0]['content']['parts'][0]['text']
                user_chat_history[user_id].append({"role": "model", "parts": [{"text": answer}]})
                return answer
            if response.status_code == 429:
                time.sleep(5)
                continue
        except:
            time.sleep(2)
            
    return "මචං, පොඩි සර්වර් හිරවීමක්. විනාඩියකින් ආයෙත් අහන්න. ⏳"

@bot.message_handler(func=lambda message: True)
def chat(message):
    print(f"Chat with {message.chat.id}: {message.text}")
    answer = get_aura_ultimate_response(message.chat.id, message.text)
    bot.reply_to(message, answer)

print("Aura AI 22.0 (Ultimate Service Edition) is ONLINE! 🌍🎓")
bot.infinity_polling()
