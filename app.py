import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
API_KEY = os.environ.get("GOOGLE_API_KEY", "")

SYSTEM_PROMPT = """You are ElectionBot, a friendly and neutral election education assistant for India. Help citizens understand elections, voter registration, EVM machines, election timelines, and related topics. Always be neutral and educational. Give simple numbered steps when explaining processes."""

QUICK_TOPICS = [
    "How do I register to vote?",
    "What is the election timeline?",
    "How does vote counting work?",
    "What is EVM and VVPAT?",
    "What are Lok Sabha elections?",
    "How is a winner declared?"
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
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        last_error = None
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_PROMPT
                )
                response = model.generate_content(user_message)
                return jsonify({"reply": response.text, "model": model_name})
            except Exception as me:
                last_error = me
                continue
        return jsonify({"error": str(last_error)}), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)