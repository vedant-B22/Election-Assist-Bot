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

MODELS_TO_TRY = [
    "gemini-2.0-flash-001",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro-002",
    "gemini-1.0-pro-002",
    "gemini-1.0-pro-001",
]

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

    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=PROJECT_ID, location=LOCATION)

        last_error = None
        for model_name in MODELS_TO_TRY:
            try:
                model = GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_PROMPT
                )
                response = model.generate_content(user_message)
                return jsonify({
                    "reply": response.text,
                    "model_used": model_name
                })
            except Exception as model_err:
                last_error = model_err
                err_str = str(model_err)
                if "404" in err_str or "not found" in err_str.lower() or "does not have access" in err_str.lower():
                    continue
                else:
                    return jsonify({"error": f"Model error: {err_str}"}), 500

        return jsonify({"error": f"No model available. Last error: {str(last_error)}"}), 500

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "Election-Assist-Bot",
        "models_configured": MODELS_TO_TRY
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)