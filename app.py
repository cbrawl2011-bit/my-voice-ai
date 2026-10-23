import os
import hmac
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1_000_000
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

def client():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise EnvironmentError("The site owner needs to add OPENAI_API_KEY in the hosting settings.")
    return OpenAI(api_key=key)

def model_text(instructions, content):
    response = client().responses.create(model=MODEL, instructions=instructions, input=content)
    answer = (response.output_text or "").strip()
    if not answer:
        raise RuntimeError("The AI returned an empty answer. Please try again.")
    return answer

def error(message, status=400):
    return jsonify({"error": message}), status

def deployed():
    return os.getenv("RENDER", "").lower() == "true"

def authorize():
    if not deployed():
        return None
    expected = os.getenv("SITE_PASSWORD", "").strip()
    if not expected:
        return error("The site owner needs to set SITE_PASSWORD in the hosting settings.", 503)
    supplied = request.headers.get("X-Site-Password", "")
    if not hmac.compare_digest(supplied, expected):
        return error("Enter the website password to continue.", 401)
    return None

@app.get("/")
def home():
    return render_template("index.html", model=MODEL)

@app.get("/api/status")
def status():
    return jsonify({
        "ready": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "protected": deployed(),
        "password_configured": bool(os.getenv("SITE_PASSWORD", "").strip()),
        "model": MODEL
    })

@app.post("/api/auth")
def auth():
    if not deployed():
        return jsonify({"ok": True})
    expected = os.getenv("SITE_PASSWORD", "").strip()
    if not expected:
        return error("The site owner needs to set SITE_PASSWORD in the hosting settings.", 503)
    if not hmac.compare_digest(request.headers.get("X-Site-Password", ""), expected):
        return error("That password is not correct.", 401)
    return jsonify({"ok": True})

@app.post("/api/analyze")
def analyze():
    denied = authorize()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    samples = str(data.get("samples", "")).strip()
    notes = str(data.get("notes", "")).strip()[:2000]
    if len(samples) < 80:
        return error("Add a few more of your own messages first (at least 80 characters).")
    if len(samples) > 30000:
        return error("Please keep your writing examples under 30,000 characters.")
    instructions = """You analyze writing samples to create a practical style profile. Describe observable habits, not guesses about identity or personality. Cover tone, sentence length, vocabulary, common phrasing, grammar, punctuation, capitalization, spelling patterns only when clearly supported, directness, formatting, and how the style changes by context. Separate strong observations from uncertain patterns. Do not invent word-frequency statistics, judge the author, or exaggerate errors. Return a useful concise profile with headings."""
    try:
        profile = model_text(instructions, "WRITING SAMPLES:\n" + samples + "\n\nAUTHOR NOTES:\n" + (notes or "None"))
        return jsonify({"profile": profile})
    except EnvironmentError as exc:
        return error(str(exc), 503)
    except AuthenticationError:
        return error("The API key was rejected. Check OPENAI_API_KEY in the hosting settings.", 401)
    except RateLimitError:
        return error("The API limit or available credits were reached. Check your API account.", 429)
    except APIError as exc:
        app.logger.exception("OpenAI API error")
        return error("The AI service returned an error. Please try again later.", 502)
    except Exception:
        app.logger.exception("Unexpected style-analysis error")
        return error("Something went wrong while analyzing your examples. Please try again.", 500)

@app.post("/api/write")
def write():
    denied = authorize()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    profile = str(data.get("profile", "")).strip()[:20000]
    samples = str(data.get("samples", "")).strip()[:30000]
    context = str(data.get("context", "")).strip()[:4000]
    style = str(data.get("style", "natural")).lower()
    length = str(data.get("length", "short")).lower()
    if not prompt:
        return error("Tell the AI what you want it to write.")
    if len(prompt) > 8000:
        return error("Your request is too long. Keep it under 8,000 characters.")
    styles = {
        "natural": "Use the author's normal style for this situation.",
        "school": "For schoolwork, use simple, clear, student-like wording. Keep it natural, not overly polished. Follow the task and do not invent facts.",
        "message": "For a text message, keep it conversational, direct, and natural. Avoid formal openings.",
        "detailed": "Include enough detail to complete the task while keeping the author's voice. Do not make it unnecessarily fancy."
    }
    lengths = {
        "tiny": "Use one or two sentences unless the task requires another format.",
        "short": "Keep it brief and to the point unless the task needs more.",
        "medium": "Use a few clear paragraphs or points where helpful. Avoid padding.",
        "long": "Give a complete answer while preserving the author's natural wording and rhythm."
    }
    instructions = f"""You write new content in the general writing style of the author below. Do not merely copy old messages.

STYLE PROFILE:
{profile or "No formal profile yet. Carefully infer observable patterns from the examples."}

WRITING EXAMPLES:
{samples or "No samples provided."}

RULES:
- Match the author's natural tone, vocabulary, sentence rhythm, directness, and formatting where appropriate.
- Use simple words if that matches the samples. Avoid generic chatbot, corporate, or overly formal wording unless the task calls for it.
- Do not deliberately insert spelling mistakes or overdo slang.
- Follow the requested task, format, and length. Do not add unnecessary introductions.
- Do not invent facts or claim personal experiences the author has not supplied.

STYLE FOR THIS REQUEST: {styles.get(style, styles["natural"])}
LENGTH: {lengths.get(length, lengths["short"])}
EXTRA CONTEXT: {context or "None"}
Return only the requested draft."""
    try:
        draft = model_text(instructions, "Write this in my style:\n" + prompt)
        return jsonify({"draft": draft})
    except EnvironmentError as exc:
        return error(str(exc), 503)
    except AuthenticationError:
        return error("The API key was rejected. Check OPENAI_API_KEY in the hosting settings.", 401)
    except RateLimitError:
        return error("The API limit or available credits were reached. Check your API account.", 429)
    except APIError:
        app.logger.exception("OpenAI API error")
        return error("The AI service returned an error. Please try again later.", 502)
    except Exception:
        app.logger.exception("Unexpected writing error")
        return error("Something went wrong while generating the draft. Please try again.", 500)

@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "This request is too large. Please shorten your text."}), 413

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
