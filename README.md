# ElectionBot — Election Process Education Assistant

An interactive AI-powered assistant that helps citizens understand how elections work in India. Built for the PromptWars Hackathon (Challenge: Election Process Education).

## What It Does

- **Chat**: Ask any question about Indian elections — get clear, neutral answers powered by Google Vertex AI (Gemini)
- **Timeline**: Visual step-by-step timeline of the entire election process
- **Quiz**: Test your election knowledge with an interactive quiz
- **Glossary**: Quick reference for common election terms

## Chosen Vertical
Election Process Education — helping voters understand the full process from announcement to government formation.

## Approach & Logic

The assistant uses a carefully designed system prompt that keeps responses neutral, educational and India-specific. It uses Gemini 1.5 Flash via Vertex AI for fast, accurate responses. Chat history (last 3 exchanges) is sent with each request so the bot remembers context within a session.

## How It Works

1. User types a question in the chat interface
2. Frontend sends the question + recent history to the Flask `/chat` endpoint
3. Flask builds a Vertex AI chat session with the election-focused system prompt
4. Gemini generates a response which is returned as JSON
5. Frontend displays the answer with a typing animation

## Assumptions Made

- Questions are about Indian elections (the bot redirects off-topic questions)
- Users are citizens wanting to learn, not seeking political advice
- Responses are kept concise (under ~300 words) for readability

## Tech Stack

- **Backend**: Python 3.11, Flask
- **AI**: Google Vertex AI — Gemini 1.5 Flash
- **Deployment**: Google Cloud Run (containerised with Docker)
- **Frontend**: Vanilla HTML/CSS/JS (no framework, fast load, accessible)
- **Testing**: pytest with mocking

## Evaluation Criteria Addressed

| Criteria | How |
|---|---|
| Code Quality | Clean separation of concerns, validated inputs, environment variables for config |
| Security | No hardcoded secrets, input length limits, safety settings on AI model |
| Efficiency | Gemini Flash model (fast), limited history window (6 messages), single worker |
| Testing | pytest suite covers routes, validation, and mocked AI responses |
| Accessibility | ARIA labels, semantic HTML, keyboard navigation, screen-reader support |
| Google Services | Vertex AI (Gemini), Cloud Run deployment |

## Local Setup

```bash
git clone https://github.com/vedant-B22/Election-Assist-Bot
cd Election-Assist-Bot
pip install -r requirements.txt
# Create .env with your PROJECT_ID and LOCATION
python app.py
```

## Running Tests

```bash
pip install pytest
pytest tests/
```

## Deployment

Deployed on Google Cloud Run. See Dockerfile for container config.