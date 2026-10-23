# My Voice AI

A personal writing assistant that learns from your writing samples and creates new drafts in a similar style.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/cbrawl2011-bit/my-voice-ai)

## Put it online

1. Click **Deploy to Render** above and sign in to Render.
2. Connect the `cbrawl2011-bit/my-voice-ai` repository and approve the Blueprint.
3. During setup, supply your OpenAI API key as `OPENAI_API_KEY`.
4. Choose a private password and set it as `SITE_PASSWORD`.
5. Deploy the service. Render will give you a URL for the website.

The app is configured by `render.yaml`. Keep API keys private: put them in Render's Environment settings, never in HTML, Python source, or GitHub. OpenAI API usage may cost money separately from a ChatGPT subscription.

## Features

- Analyze your writing samples to create a practical writing-style profile.
- Generate drafts for schoolwork, messages, and other writing.
- Save your samples and profile locally in your browser.
- Copy drafts and export the profile to a JSON file.
- Use a site password to protect the AI endpoints on a public deployment.

## Run on your computer

Python 3.12 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in your local environment or a local `.env` file, then run:

```bash
python app.py
```

Open http://127.0.0.1:5000.

## Privacy

Your writing examples and style profile are saved in your browser's local storage. When you analyze or generate text, the relevant text is sent to this site's server and the OpenAI API. The API key remains on the server. The site's shared password is a basic access gate, not a full account system.

Do not add a real `.env` file or API key to GitHub. The checked-in `.env.example` contains placeholders only.
