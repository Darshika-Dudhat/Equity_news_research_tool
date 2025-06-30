# app.py
import streamlit as st
from langchain_config import llm_chain, get_summary, llm
from news_utils import get_news_articles, summarize_articles
from login_config import USER_CREDENTIALS
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime, timedelta

# ---Page Configuration ---
st.set_page_config(page_title="News Research Tool", layout="wide")

# --- Initialize session ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user' not in st.session_state:
    st.session_state.user = "User"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- Header ---
if st.session_state.logged_in:
    st.markdown(f"""
        <h2 style='color:#4CAF50;'>🧠 Equity Research News Tool</h2>
        <p>Welcome, <b>{st.session_state.user}</b>! Ask your question below to get summarized insights using Groq LLM + NewsAPI.</p>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <h2 style='color:#4CAF50;'>🧠 Equity Research News Tool</h2>
        <p>Please log in to use the tool.</p>
    """, unsafe_allow_html=True)

def login():
    st.title(" 🔐 login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if USER_CREDENTIALS.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.user = username  # Save the logged-in user
            st.success("✅ Login sucessful! Reloading...")
            # print("Loaded Credentials:", USER_CREDENTIALS)
            # print("Entered:", username, password)
            st.rerun()
        else:
            st.error(" ❌ Invalid Credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.title("🔍 Navigation")
    if st.session_state.logged_in:
        st.write(f"👤 Logged in as: {st.session_state.user}")
        if st.button("🚪 Logout"):
            #st.session_state.history.clear()
            st.session_state.logged_in =False
            st.session_state.user = None
            st.rerun()
        if st.button("🔄 Reset Session"):
            st.session_state.history.clear()
            st.rerun()
    else:
        st.write("🔐 Please log in")

# --- Initialize session history ---
if 'history' not in st.session_state:
    st.session_state.history = []

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", size=12)
        self.cell(0, 10, "News Summary", ln=True)

# --- PDF generation function ---
def create_pdf(query, response):
    pdf = PDF()

    # Full path to the font inside your structure
    font_path = os.path.join(
        os.path.dirname(__file__), "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans.ttf"
    )
    # Register the font BEFORE using it
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")
    # Debug print (optional)
    # print("Font file found:", os.path.exists(font_path))  # Should be True

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.add_page()
    pdf.set_font("DejaVu", size=12)

    pdf.multi_cell(0, 10, f"Query: {query}\n\nResponse:\n{response}")
    #Convert to bytes before returning
    return pdf.output(dest="S")

# --- Query form ---
st.write(" ✍️ Enter your Query")
with st.form("query_form"):
    col1, col2 = st.columns([4,1])
    with col1:
        query = st.text_input("Ask your question or news query:")
    with col2:
        submitted = st.form_submit_button("🚀 Get News Summary")

if submitted and query.strip():
    with st.spinner("⏳ Fetching and summarizing news..."):

        direct_starts = ('who', 'what', 'when', 'where', 'why', 'how', 'is', 'are', 'does', 'can')
        is_direct = query.strip().lower().startswith(direct_starts)

        if is_direct:
            # prompt = f"Answer the following question concisely and accurately:\n\n{query}"
            # response = llm.invoke(prompt)

            detailed_prompt = f"""
                        You are a knowledgeable AI assistant. Please provide a detailed, well-structured answer to the following question, including:
                        - Relevant facts, names, dates, and statistics
                        - Context or background if useful
                        - Clear and precise language

                        Question:
                        {query}
                        """
            response = llm_chain.invoke({'query': detailed_prompt, 'summaries': ''})
            # answer = response.content 
            # print("Inside Groq")
            # response = llm_chain.invoke({'query': query, 'summaries': ''})
            # print(answer)
            st.markdown("### 🤖 AI Answer:")
            st.success(response)

            st.session_state.history.append({
                                'query': query,
                                'response': response
                            })
        else:
            days_back = st.slider("Search news from the past (days)", 1, 30, 7)
            articles = get_news_articles(query, days_back=days_back)
            # articles = get_news_articles(query)
            # print(articles)

            if articles:
                # Frequency Chart
                dates = [article['publishedAt'][:10] for article in articles if 'publishedAt' in article]
                if dates:
                    # Define full date range (e.g., past 7 days)
                    end_date = datetime.today().date()
                    start_date = end_date - timedelta(days=6)
                    full_range = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d')

                    # Count actual article dates
                    date_series = pd.Series(dates)
                    counts = date_series.value_counts()

                    # Build full date count dictionary with zeros by default
                    date_counts = {date: 0 for date in full_range}
                    date_counts.update(counts.to_dict())  # Update with real counts

                    # Sort by date
                    sorted_counts = pd.Series(date_counts).sort_index()

                    st.markdown("### 🗓️ Article Frequency Over Time (Full Week)")
                    st.bar_chart(sorted_counts)

                article_summaries = summarize_articles(articles)
                detailed_prompt = f"""
                    You are a news analyst. Read the following summaries and provide a **detailed, informative, and engaging summary** of the topic: **{query}**.
                    Make sure to:
                    - Mention specific names, places, events, and dates.
                    - Include outcomes and implications if possible.
                    - Use clear, paragraph-style explanations.

                    Summaries:
                    {article_summaries}
                    """
                # response = llm_chain.invoke({'query':f"Provide a detailed and thorough summary of the following topic: {query}", 
                #                              'summaries':article_summaries})
                response = llm_chain.invoke({'query': detailed_prompt, 'summaries': article_summaries})
                st.markdown("### AI Summary:")
                st.success(response)

                pdf_data = create_pdf(query, response)
                st.download_button(
                    label="Download as PDF",
                    data=bytes(pdf_data),
                    file_name="news_summary.pdf",
                    mime="application/pdf"
                )

                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                st.markdown(f"[🔗Search more on Google]({search_url})")

                with st.expander("📄 Source Articles:"):
                    for article in articles:
                        st.markdown(f"- [{article['title']}]({article['url']}) — *{article['source']['name']}*")

                # Save to session history
                st.session_state.history.append({
                    'query': query,
                    'response': response
                })
            else:
                st.warning("⚠️ No relevant news articles found.")

# --- History Viewer ---
if st.session_state.history:
    st.markdown('### 📜 Query History')
    for i, item in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"{i}. {item['query']}"):
            st.markdown(item['response'])
