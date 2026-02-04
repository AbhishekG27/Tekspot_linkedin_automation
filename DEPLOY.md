# Deploy to Streamlit Community Cloud

Follow these steps to get a shareable link (e.g. `https://your-app.streamlit.app`).

---

## 1. Push your code to GitHub

If the project is not in a repo yet:

```bash
cd c:\Users\abhis\OneDrive\Documents\automation
git init
git add .
git commit -m "LinkedIn Content Machine app"
```

Create a new repository on [GitHub](https://github.com/new) (e.g. `linkedin-content-machine`). Then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/linkedin-content-machine.git
git branch -M main
git push -u origin main
```

**Important:** Do **not** commit `.env`. It’s in `.gitignore`; only commit `.env.example`.

---

## 2. Deploy on Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
2. Click **“New app”**.
3. Fill in:
   - **Repository:** `YOUR_USERNAME/linkedin-content-machine` (or your repo name).
   - **Branch:** `main`.
   - **Main file path:** `app.py`.
   - **App URL:** optional (e.g. `linkedin-content-machine` → `https://linkedin-content-machine.streamlit.app`).
4. Click **“Advanced settings”** and open **Secrets**.
5. Add your keys in TOML format:

```toml
GEMINI_API_KEY = "..."
TAVILY_API_KEY = "tvly-..."
```

Replace the placeholders with your real keys. Save.

6. Click **“Deploy!”**.

---

## 3. After deployment

- The first run can take 1–2 minutes (install + start).
- Your app will be at: `https://YOUR_APP_URL.streamlit.app`.
- Share this link (e.g. with your manager) so they can use the app in the browser.
- **Secrets** are only visible to you in the Streamlit Cloud dashboard; others only see the running app.

---

## 4. Optional: Python version

Streamlit Cloud usually picks a suitable Python version. If you need a specific one, add a **runtime.txt** in the repo root, for example:

```
python-3.11
```

Then commit and push; Streamlit will use that version on the next deploy.

---

## Troubleshooting

| Issue | What to do |
|--------|------------|
| “Set GEMINI_API_KEY” / “Set TAVILY_API_KEY” in app | Add both in **App → Settings → Secrets** and redeploy. |
| Build fails | Check **Deploy log** on Streamlit Cloud; fix any missing deps in `requirements.txt` and push. |
| App is slow to start | Normal on free tier; first request after idle may take ~30s. |
