"""
app.py

Flask backend for AdmitBot.

Routes:
    GET  /       -> serves the chat UI (templates/index.html)
    POST /chat   -> receives {"message": "..."} and returns {"response": "..."}
    POST /clear  -> resets the current session's conversation context

Session/context handling:
    Flask's built-in signed-cookie session is used to store the
    conversation context (rank, category, branch, stage) for the
    current user's browser session. This is sufficient for a
    mini-project - no database is needed for this.
"""

from flask import Flask, jsonify, render_template, request, session

import chatbot

app = Flask(__name__)

# Needed for Flask's session cookie to be signed. For a real deployment
# this should come from an environment variable, not be hardcoded.
app.secret_key = "admitbot-dev-secret-key-change-in-production"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str):
        return jsonify({"response": "Invalid message format."}), 400

    context = session.get("context")
    if context is None:
        context = chatbot.default_context()

    response_text, updated_context = chatbot.get_response(message, context)

    session["context"] = updated_context
    session.modified = True

    return jsonify({"response": response_text})


@app.route("/clear", methods=["POST"])
def clear():
    session["context"] = chatbot.default_context()
    session.modified = True
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
