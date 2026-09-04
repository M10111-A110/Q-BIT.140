"""
The web "front door" for the AI tutor.

ask.py already knows HOW to answer a question (it just needs to be run).
This file's only job is to let your WEBSITE ask it a question over the
internet and get the answer back — same shape as how your frontend
already talks to Supabase, just talking to this Python server instead.
"""

import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from ask import ask_question

app = Flask(__name__)

# CORS = "allow requests from a different address than this server's own."
# Your website and this server are two different addresses, and browsers
# block that kind of cross-address request by default unless the server
# explicitly says it's okay — this line says "it's okay."
CORS(app)


def clean_ai_response(text):
    """
    Belt-and-suspenders cleanup: the AI is TOLD not to use LaTeX/markdown
    in its instructions, but models don't always obey style instructions
    perfectly, especially for math-heavy topics. This strips common
    LaTeX/markdown symbols no matter what the AI actually outputs, so
    the chat never shows broken symbol soup like \\alpha or ### again.
    """
    if not text:
        return text

    # \frac{a}{b} -> (a/b), before stripping other LaTeX
    text = re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}', r'(\1/\2)', text)

    # Strip LaTeX math delimiters
    for delim in ['\\[', '\\]', '\\(', '\\)']:
        text = text.replace(delim, '')

    # Common LaTeX symbols -> plain text equivalents
    symbol_map = {
        '\\alpha': 'alpha', '\\beta': 'beta', '\\gamma': 'gamma',
        '\\psi': 'psi', '\\rangle': '>', '\\langle': '<',
        '\\quad': '  ', '\\qquad': '   ', '\\,': ' ', '\\;': ' ',
    }
    for latex, plain in symbol_map.items():
        text = text.replace(latex, plain)

    # Convert markdown bullet lines ("* item") to a plain dash BEFORE
    # touching italics below — otherwise a stray "*" that starts one
    # bullet line can accidentally pair up with the next bullet's "*"
    # and swallow everything in between.
    text = re.sub(r'^\*\s+', '- ', text, flags=re.MULTILINE)

    # Strip markdown bold/italic markers, keeping the text inside
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)

    # Strip markdown headers (###, ##, #) at the start of a line
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # ^{2} -> ^2 (simplify leftover LaTeX-style exponents)
    text = re.sub(r'\^\{(\w+)\}', r'^\1', text)

    # Collapse extra spaces/blank lines left behind by removed symbols
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


@app.route("/", methods=["GET"])
def health_check():
    # Visiting this in a browser just confirms the server is alive —
    # useful for a quick sanity check before wiring up the real frontend.
    return jsonify({"status": "AI tutor server is running"})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        raw_answer = ask_question(question)
        # The frontend now renders Markdown (marked.js) and LaTeX (KaTeX)
        # properly, so we send the answer through as-is instead of
        # stripping it to plain text — that's what let symbols outside
        # clean_ai_response's small symbol_map leak through unrendered.
        return jsonify({"answer": raw_answer})
    except Exception as e:
        # If Groq's API call fails (bad key, network issue, etc.), send
        # back a real error instead of the server just crashing silently.
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


if __name__ == "__main__":
    # host="0.0.0.0" makes this reachable from other devices on the same
    # WiFi (not just this laptop) — find your laptop's local IP with
    # `ipconfig` (Windows) and share http://THAT-IP:5000 with teammates.
    app.run(host="0.0.0.0", port=5000, debug=True)
