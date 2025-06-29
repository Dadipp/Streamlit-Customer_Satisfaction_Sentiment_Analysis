import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Customer Satisfaction Dashboard",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fungsi Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/final_review_sentiment_nps_ces_csat.csv")
    return df

df = load_data()

# --- Sidebar ---
st.sidebar.header("🎛️ Filter Panel")

# Filter tanggal
df["date_of_survey"] = pd.to_datetime(df["date_of_survey"], errors='coerce')
min_date = df["date_of_survey"].min().date()
max_date = df["date_of_survey"].max().date()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date_filter = pd.to_datetime(date_range[0])
    end_date_filter = pd.to_datetime(date_range[1])
    filtered_df = df[
        (df["date_of_survey"] >= start_date_filter) & (df["date_of_survey"] <= end_date_filter)
    ]
else:
    filtered_df = df.copy()

# Filter ticket system
ticket_options = df["ticket_system"].dropna().unique().tolist()
selected_tickets = st.sidebar.multiselect("Pilih Ticket System:", options=ticket_options, default=ticket_options)

filtered_df = filtered_df[filtered_df["ticket_system"].isin(selected_tickets)]

# --- Judul Halaman ---
st.title("📊 Customer Satisfaction Sentiment Analysis")
st.markdown("""
Dashboard ini menampilkan analisis sentimen dan kepuasan pelanggan berdasarkan survey support system seperti Zendesk, Zoho Desk, OTRS.
Metrik yang dianalisis: **CSAT**, **NPS**, **CES**, dan **sentimen review pelanggan**.
""")

# --- Metrics Ringkasan ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Overall Rating", f"{filtered_df['overall_rating'].mean():.2f}")
col2.metric("Avg Ease of Use", f"{filtered_df['ease_of_use'].mean():.2f}")
col3.metric("Avg Service Rating", f"{filtered_df['customer_service'].mean():.2f}")
col4.metric("Avg Value for Money", f"{filtered_df['value_for_money'].mean():.2f}")

st.markdown("---")

# --- Visualisasi Sentimen Pie ---
st.subheader("📌 Distribusi Sentimen Review")
sentiment_count = filtered_df["sentiment"].value_counts().reset_index()
sentiment_count.columns = ["sentiment", "count"]
fig_sentiment = px.pie(sentiment_count, names="sentiment", values="count", title="Distribusi Sentimen Pelanggan", hole=0.3)
st.plotly_chart(fig_sentiment, use_container_width=True)

# --- CSAT dan NPS ---
colA, colB = st.columns(2)
with colA:
    st.subheader("💡 CSAT Category")
    fig_csat = px.pie(filtered_df, names="csat_category", title="Customer Satisfaction (CSAT)", hole=0.4)
    st.plotly_chart(fig_csat, use_container_width=True)

with colB:
    st.subheader("📣 NPS Category")
    fig_nps = px.histogram(filtered_df, x="nps_category", color="sentiment", barmode="group", title="Distribusi NPS dan Sentimen")
    st.plotly_chart(fig_nps, use_container_width=True)


# --- Sentimen per Ticket System ---
st.subheader("🏷️ Sentimen Berdasarkan Ticket System")
fig_ticket_sentiment = px.histogram(
    filtered_df,
    x="ticket_system",
    color="sentiment",
    barmode="group",
    title="Distribusi Sentimen per Ticket System"
)
st.plotly_chart(fig_ticket_sentiment, use_container_width=True)



# --- Ringkasan Jumlah Review per Sentimen ---
st.subheader("🔢 Jumlah Review per Sentimen")
sentiment_summary = filtered_df["sentiment"].value_counts().reset_index()
sentiment_summary.columns = ["Sentimen", "Jumlah Review"]
st.dataframe(sentiment_summary)

# --- Time Series Value & Review Trend ---
st.subheader("📈 Tren Rata-rata Value for Money")
trend_df = filtered_df.groupby(filtered_df['date_of_survey'].dt.date).agg({
    "value_for_money": "mean",
    "sentiment": "count"
}).reset_index().rename(columns={
    "date_of_survey": "tanggal",
    "value_for_money": "rata_value",
    "sentiment": "jumlah_review"
})

fig_value = px.line(trend_df, x="tanggal", y="rata_value", title="Rata-rata Value for Money Harian", markers=True)
st.plotly_chart(fig_value, use_container_width=True)

st.subheader("📈 Jumlah Review Harian")
fig_review = px.line(trend_df, x="tanggal", y="jumlah_review", title="Jumlah Review Harian", markers=True)
st.plotly_chart(fig_review, use_container_width=True)

# --- Raw Data ---
st.markdown("---")
st.subheader("🧾 Data Final Review Sentiment")
st.dataframe(filtered_df)

# --- Insight Bisnis ---
st.markdown("""
### 📌 Insight & Rekomendasi Bisnis

- Mayoritas sentimen pelanggan bersifat **positif**, namun terdapat peluang untuk mengkonversi review **netral dan negatif** menjadi positif melalui follow-up.
- Sistem seperti **OTRS dan Zoho Desk** menunjukkan variasi besar dalam sentimen dan rating, perlu dilakukan evaluasi internal.
- **Ease of Use** memiliki korelasi tinggi dengan **Overall Rating** – peningkatan pengalaman pengguna dapat berdampak langsung terhadap kepuasan.
- **Value for Money** cenderung meningkat, namun jumlah review tidak stabil – evaluasi strategi campaign atau komunikasi perlu diperkuat.
- Kombinasi **CSAT**, **NPS**, dan **CES** bisa digunakan sebagai framework pengukuran loyalitas pelanggan dan churn risk.
""")
