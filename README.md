# My Voice AI

A personal writing assistant that studies examples of your writing, builds a style profile, and creates new drafts in a similar voice.

## Deploy on Render

1. Sign in to Render and choose **New → Blueprint**.
2. Connect this GitHub repository: https://github.com/cbrawl2011-bit/my-voice-ai
3. Render reads `render.yaml` and creates the web service.
4. In the service environment settings, add:
   - `OPENAI_API_KEY`: your OpenAI API key
   - `SITE_PASSWORD`: choose a private password for your website
   - `OPENAI_MODEL`: defaults to `gpt-5.5`; change it if your API account uses another model
5. Deploy and open the Render URL. Enter your site password to use the AI.

Never put your API key in frontend code or commit it to GitHub. API usage may cost money separately from a ChatGPT subscription.

## Run locally

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in your environment, then run:

```bash
python app.py
```

Open http://127.0.0.1:5000.

## Privacy

Your writing examples and style profile are saved in your browser's local storage. When you analyze or generate text, the relevant inputs are sent to the server and the OpenAI API. The API key stays on the server. The shared site password is a simple access gate, not a full user-account system.
