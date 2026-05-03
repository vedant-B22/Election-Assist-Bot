import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
PROJECT_ID = os.environ.get("PROJECT_ID", "election-assist-bot")
LOCATION = os.environ.get("LOCATION", "us-central1")

SYSTEM_PROMPT = """You are ElectionBot, a friendly and neutral election education assistant for India. Help citizens understand elections, voter registration, EVM machines, election timelines, and related topics. Always be neutral and educational. Give simple numbered steps when explaining processes."""

QUICK_TOPICS = [
    "How do I register to vote?",
    "What is the election timeline?",
    "How does vote counting work?",
    "What is EVM and VVPAT?",
    "What are Lok Sabha elections?",
    "How is a winner declared?"
]

def get_access_token():
    resp = requests.get(
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"},
        timeout=5
    )
    return resp.json()["access_token"]

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
        token = get_access_token()
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/gemini-2.0-flash-001:generateContent"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": user_message}]}]
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        reply = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": reply})
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