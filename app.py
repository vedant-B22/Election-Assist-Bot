import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PROJECT_ID = os.environ.get("PROJECT_ID", "election-assist-bot")
LOCATION = os.environ.get("LOCATION", "us-central1")

SYSTEM_PROMPT = """You are ElectionBot, a friendly and neutral election education assistant for India.
Your job is to help citizens understand:
- How elections work step by step
- The timeline of elections (announcement to results)
- How to register as a voter (voter ID, Form 6)
- What happens on election day (EVM machines, VVPAT, booth process)
- The role of Election Commission of India
- Types of elections: Lok Sabha, Rajya Sabha, State Assembly, Local Body
- How votes are counted and results declared
- Common election terms

Rules:
- Always be neutral, never favour any party or candidate
- Give simple, easy-to-understand answers
- Use numbered steps when explaining a process
- If asked about something unrelated to elections, politely redirect
- Keep answers concise but complete"""

QUICK_TOPICS = [
    "How do I register to vote?",
    "What is the election timeline?",
    "How does vote counting work?",
    "What is EVM and VVPAT?",
    "What are Lok Sabha elections?",
    "How is a winner declared?"
]

def get_ai_response(user_message, history):
    import vertexai
    from vertexai.generative_models import GenerativeModel, SafetySetting, HarmCategory, HarmBlockThreshold
    
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    safety_settings = [
        SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
    ]
    
    model = GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    chat_history = []
    for msg in history[-6:]:
        if msg.get("role") in ["user", "model"] and msg.get("content"):
            chat_history.append({
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            })
    
    chat_session = model.start_chat(history=chat_history)
    response = chat_session.send_message(user_message)
    return response.text

@app.route("/")
def index():
    return render_template("index.html", quick_topics=QUICK_TOPICS)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    if len(user_message) > 500:
        return jsonify({"error": "Message too long"}), 400

    history = data.get("history", [])

    try:
        answer = get_ai_response(user_message, history)
        return jsonify({"reply": answer})
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERROR: {error_detail}")
        return jsonify({"error": f"AI error: {str(e)}"}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Election-Assist-Bot"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)