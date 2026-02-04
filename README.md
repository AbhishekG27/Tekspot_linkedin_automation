# LinkedIn Content Machine

Automate your LinkedIn content pipeline with **Gemini only**:

1. **Tavily + Gemini** — Suggest trending, high-engagement topics (Talent Acquisition, Workforce Management, Staffing, IT Recruitment, Talent Transformation), list them, and store in Excel.
2. **Human** — Select a topic from the list or trigger a new search.
3. **Gemini** — Generate LinkedIn post using the strategist prompt (scroll-stopping hooks, punchy content, hashtags; authority/community growth; no C-level or company names).
4. **Gemini Imagen** — Generate image; you approve or regenerate.

Fully runnable locally or deployable (Streamlit Cloud, Docker, etc.).

## Setup

### 1. Clone / open project

```bash
cd automation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. API key (`.env`)

Copy `.env.example` to `.env` and set:

| Variable | Where to get |
|----------|--------------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) — topics, LinkedIn post, and images |
| `TAVILY_API_KEY` | [Tavily](https://app.tavily.com) — web search for recent topics |

Optional: `GEMINI_CHAT_MODEL=gemini-3-flash-preview` (default). Optional: `GEMINI_IMAGE_MODEL=imagen-4.0-generate-001` (default).

### 4. Run the app

```bash
streamlit run app.py
```

- **Step 1:** Niche defaults to Talent Acquisition, Workforce Management, Staffing Solutions, IT Recruitment, Talent Transformation. Click **Search trending topics**. Results are saved to `data/topics.xlsx`.
- **Step 2:** Pick a topic (or search again).
- **Step 3:** Click **Generate post** — content follows the strategist prompt (hooks, main content, hashtags; audience senior leaders; goal authority/community; no C-level or company names).
- **Step 4:** Click **Generate image** (Gemini Imagen). Approve or **Regenerate**.

## Deploy

### Streamlit Community Cloud (recommended)

1. **Push this repo to GitHub** (don’t commit `.env`).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → sign in with GitHub → **New app**.
3. Choose your repo, branch `main`, main file **`app.py`**.
4. Open **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "..."
   TAVILY_API_KEY = "tvly-..."
   ```
5. Click **Deploy**. You’ll get a link like `https://your-app.streamlit.app` to share.

See **[DEPLOY.md](DEPLOY.md)** for step-by-step and troubleshooting.

### Docker

```bash
docker build -t linkedin-content-machine .
docker run -p 8501:8501 --env-file .env linkedin-content-machine
```

### Railway / Render

- Web Service: build `pip install -r requirements.txt`, start `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
- Set `GEMINI_API_KEY` and `TAVILY_API_KEY`.

## Project layout

```
automation/
├── app.py              # Streamlit UI
├── config.py           # Paths and Gemini config
├── requirements.txt
├── .env.example
├── data/
│   └── topics.xlsx     # Saved topics
├── output/             # Generated images
└── services/
    ├── topics.py       # Gemini topic suggestions (Tavily + Gemini)
    ├── excel_store.py  # Excel read/write
    ├── content.py      # Gemini LinkedIn post (strategist prompt)
    └── image_gen.py    # Gemini Imagen image generation
```

## Content prompt (built-in)

The post generator acts as a top-tier social media strategist:

- **Niches:** Talent Acquisition, Employee Management, Workforce Management, Staffing Solutions, IT Recruitment, Skills Shaping Tomorrow's Workforce, Talent Transformation
- **Format:** Headline/Hook (first 2 lines) → Main content (short, punchy, skimmable) → Relevant hashtags
- **Tone:** Relatable, bold, conversation-driven; curiosity/authority/emotional triggers
- **Audience:** Senior decision-makers; goal authority and community growth
- **Rules:** No mention of C-level or external company names
