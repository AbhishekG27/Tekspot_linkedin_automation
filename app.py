"""
LinkedIn Content Machine — AI-powered pipeline:
1. Tavily + Gemini: suggest trending topics → Excel + list
2. Human: select topic or search again
3. Gemini: generate LinkedIn post (strategist prompt)
4. Gemini Imagen: generate image → human approval / regenerate
"""
import streamlit as st
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ensure_dirs, TOPICS_EXCEL, GEMINI_API_KEY, TAVILY_API_KEY
from services.topics import search_trending_topics
from services.excel_store import save_topics_to_excel, load_topics_from_excel
from services.content import generate_linkedin_content
from services.image_gen import generate_post_image

ensure_dirs()

st.set_page_config(
    page_title="LinkedIn Content Machine",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("📄 LinkedIn Content Machine")
st.caption("Topics (Tavily web search) → Select → Generate post & image → Approve")

# Session state
if "topics" not in st.session_state:
    st.session_state.topics = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "content" not in st.session_state:
    st.session_state.content = ""
if "image_path" not in st.session_state:
    st.session_state.image_path = None
if "image_approved" not in st.session_state:
    st.session_state.image_approved = False

# --- Step 1: Trending topics (Tavily web search + Excel) ---
st.header("1️⃣ Trending topics (Tavily + web search)")
DEFAULT_NICHES = "Talent Acquisition, Employee Management, Workforce Management, Staffing Solutions, IT Recruitment Challenges, Skills Shaping Tomorrow's Workforce, Talent Transformation"
niche = st.text_input("Niche / industry for trends", value=DEFAULT_NICHES, key="niche")
count = st.number_input("Number of topics", min_value=5, max_value=20, value=10, key="count")
recency = st.selectbox(
    "Recency (filter by publish/update date)",
    ["day", "week", "month"],
    index=2,
    format_func=lambda x: {"day": "Today", "week": "This week", "month": "This month"}[x],
    key="recency",
)

if st.button("🔍 Search trending topics", type="primary"):
    if not TAVILY_API_KEY:
        st.error("Set TAVILY_API_KEY in .env")
    else:
        with st.spinner("Searching web for recent topics…"):
            try:
                topics = search_trending_topics(niche=niche, count=int(count), recency=recency)
                st.session_state.topics = topics
                save_topics_to_excel(topics)
                st.success(f"Found {len(topics)} topics (recent: {recency}). Saved to {TOPICS_EXCEL}")
            except Exception as e:
                st.exception(e)

if not st.session_state.topics and TOPICS_EXCEL.exists():
    st.session_state.topics = load_topics_from_excel()
    if st.session_state.topics:
        st.info(f"Loaded {len(st.session_state.topics)} topics from Excel.")

if st.session_state.topics:
    st.subheader("Topics (saved in Excel)")
    for t in st.session_state.topics:
        idx = t.get("index", t.get("title", ""))
        title = t.get("title", str(t))
        reason = t.get("reason", "")
        summary = t.get("summary", "")
        with st.expander(f"**{idx}. {title[:80]}**"):
            if reason:
                st.caption(f"Why trending: {reason}")
            if summary:
                st.write(summary)
    st.download_button(
        "📥 Download topics (Excel)",
        data=Path(TOPICS_EXCEL).read_bytes() if TOPICS_EXCEL.exists() else b"",
        file_name=TOPICS_EXCEL.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# --- Step 2: Select topic ---
st.header("2️⃣ Select a topic")
options = ["— Select or search again —"] + [
    f"{t.get('index', i)}. {t.get('title', str(t))[:60]}"
    for i, t in enumerate(st.session_state.topics, 1)
]
choice = st.selectbox("Pick a topic for your post", options, key="topic_choice")
if choice and choice != "— Select or search again —":
    idx = int(choice.split(".")[0]) if choice[0].isdigit() else 1
    selected = next(
        (t for t in st.session_state.topics if t.get("index") == idx or str(t.get("title", "")) in choice),
        st.session_state.topics[0] if st.session_state.topics else None,
    )
    if selected:
        st.session_state.selected_topic = selected.get("title", str(selected))
        st.info(f"Selected: **{st.session_state.selected_topic}**")
else:
    st.session_state.selected_topic = None
    st.caption("Search again above if none of the topics fit.")

# --- Step 3: Generate content (Gemini — strategist prompt) ---
st.header("3️⃣ LinkedIn post (Gemini)")
if st.session_state.selected_topic:
    if st.button("✨ Generate post"):
        if not GEMINI_API_KEY:
            st.error("Set GEMINI_API_KEY in .env")
        else:
            with st.spinner("Generating post…"):
                try:
                    st.session_state.content = generate_linkedin_content(st.session_state.selected_topic)
                except Exception as e:
                    st.exception(e)
    if st.session_state.content:
        st.text_area("Post text", value=st.session_state.content, height=280, key="content_display")
else:
    st.caption("Select a topic first.")

# --- Step 4: Image (Gemini Imagen, approve / regenerate) ---
st.header("4️⃣ Post image (Gemini Imagen)")
if st.session_state.selected_topic:
    with st.expander("🖼️ Image template (optional)", expanded=False):
        st.caption("Describe the layout/style you want. The image will match your content but follow this template.")
        image_template = st.text_area(
            "Template description",
            placeholder="e.g. Minimal slide: white background, bold headline at top center, one simple icon in the middle, corporate blue accent.",
            key="image_template",
            height=80,
        )
        hero_for_image = st.text_input(
            "HERO headline for image (optional)",
            placeholder="Paste the HERO Copy from the caption above to show on the image.",
            key="hero_for_image",
        )
    if st.button("🖼️ Generate image"):
        with st.spinner("Generating image…"):
            path, err = generate_post_image(
                st.session_state.selected_topic,
                template_description=image_template.strip() or None,
                hero_copy=hero_for_image.strip() or None,
            )
            if err:
                st.error(err)
            else:
                st.session_state.image_path = path
                st.session_state.image_approved = False
    if st.session_state.image_path and Path(st.session_state.image_path).exists():
        st.image(str(st.session_state.image_path), use_container_width=True)
        a, b = st.columns(2)
        with a:
            if st.button("✅ Approve image"):
                st.session_state.image_approved = True
                st.success("Image approved.")
        with b:
            if st.button("🔄 Regenerate image"):
                st.session_state.image_path = None
                st.rerun()
else:
    st.caption("Select a topic first.")

# --- Summary ---
st.header("✅ Summary")
if st.session_state.selected_topic:
    st.write("**Topic:**", st.session_state.selected_topic)
if st.session_state.content:
    preview = st.session_state.content[:300] + "…" if len(st.session_state.content) > 300 else st.session_state.content
    st.write("**Post:**", preview)
if st.session_state.image_path:
    st.write("**Image:**", str(st.session_state.image_path))

with st.expander("Setup (API keys)"):
    st.code("""
# Copy .env.example to .env and set:
GEMINI_API_KEY=...      # Topics, LinkedIn post, and images (Gemini)
TAVILY_API_KEY=tvly-... # Web search for recent topics (day/week/month)
    """)
    st.caption("Topics are stored in data/topics.xlsx. Run: streamlit run app.py")
