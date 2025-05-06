import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Yüklemeler
load_dotenv()
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

st.set_page_config(page_title="BrainDrop", page_icon="🧠")

st.title("🧠 BrainDrop")
st.markdown("Her gün öğrendiğin bir bilgiyi bırak, biz senin için özetleyelim, etiketleyelim ve motive edelim!")

user_input = st.text_area("Bugün ne öğrendin?")

learning_goal = st.text_input("Bugün için öğrenme hedefiniz nedir? (Opsiyonel)")
future_plan = st.text_area("Öğrendiklerini nasıl uygulayacağınızı planlıyorsunuz? (Opsiyonel)")

if st.button("Gönder") and user_input.strip() != "":
    with st.spinner("Yapay zeka düşünürken biraz bekleyelim..."):
        prompt = f"""
        Kullanıcı bugün şöyle yazdı:
        "{user_input}"

        Aşağıdakileri yap:
        1. Bu girdiyi özetle (1 cümle).
        2. Konu etiketi üret (sadece 1-2 kelime).
        3. Motive edici kısa bir geri bildirim ver.
        Sonucu şu formatta ver:
        Özet: ...
        Etiket: ...
        Yorum: ...
        """
        response = model.generate_content(prompt)

    lines = response.text.strip().split("\n")
    summary = next((l for l in lines if l.startswith("Özet:")), "Özet: Bulunamadı")
    topic = next((l for l in lines if l.startswith("Etiket:")), "Etiket: Bulunamadı")
    comment = next((l for l in lines if l.startswith("Yorum:")), "Yorum: Bulunamadı")

    st.subheader("🎯 Özet")
    st.success(summary.replace("Özet:", "").strip())

    st.subheader("🏷️ Etiket")
    st.info(topic.replace("Etiket:", "").strip())

    st.subheader("💬 Yorum")
    st.warning(comment.replace("Yorum:", "").strip())

    log = {
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "girdi": user_input,
        "ozet": summary.replace("Özet:", "").strip(),
        "etiket": topic.replace("Etiket:", "").strip(),
        "yorum": comment.replace("Yorum:", "").strip(),
        "ogrenme_hedefi": learning_goal.strip() if learning_goal else None,
        "gelecek_planı": future_plan.strip() if future_plan else None
    }

    with open("gunlukler.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

# -------------------------------------
# 📚 GEÇMİŞ GÜNLÜKLERİ GÖSTER
# -------------------------------------

st.markdown("---")
st.subheader("📚 Geçmiş Kayıtlar")

daily_logs = []
if os.path.exists("gunlukler.jsonl"):
    with open("gunlukler.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            try:
                daily_logs.append(json.loads(line))
            except:
                pass

etiketler = sorted(set(log.get("etiket", "Genel") for log in daily_logs if "etiket" in log))
selected_etiket = st.selectbox("Etikete göre filtrele:", ["Tümü"] + etiketler)

filtered_logs = daily_logs
if selected_etiket != "Tümü":
    filtered_logs = [log for log in filtered_logs if selected_etiket in log.get("etiket", "")]

arama = st.text_input("Anahtar kelime ara:")
if arama:
    filtered_logs = [log for log in filtered_logs if arama.lower() in log.get("girdi", "").lower()]

for log in reversed(filtered_logs):
    tarih_str = log.get("tarih", "")
    st.markdown(f"""
    <div style='border-left: 3px solid #ccc; padding-left: 15px; margin-bottom: 20px;'>
        <strong>🗓️ {tarih_str}</strong><br>
        <em>🏷️ {log.get("etiket", "")}</em><br>
        <strong>🧠 Özet:</strong> {log.get("ozet", "")}<br>
        <strong>✍️ Girdi:</strong> {log.get("girdi", "")}<br>
        <small>💬 {log.get("yorum", "")}</small><br>
        <strong>🎯 Hedef:</strong> {log.get("ogrenme_hedefi", "Belirtilmemiş")}<br>
        <strong>📈 Plan:</strong> {log.get("gelecek_planı", "Belirtilmemiş")}
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------
# 📊 İSTATİSTİKSEL GÖRSELLEŞTİRME
# -------------------------------------

st.markdown("---")
st.subheader("📈 En Sık Öğrenilen Konular")

etiket_sayilari = Counter(log.get("etiket", "Bilinmiyor") for log in daily_logs)
if etiket_sayilari:
    en_sik = etiket_sayilari.most_common(5)
    etiketler, sayilar = zip(*en_sik)

    fig, ax = plt.subplots()
    ax.barh(etiketler, sayilar, color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel("Gün Sayısı")
    ax.set_title("En Sık Öğrenilen Konular")
    st.pyplot(fig)
else:
    st.info("Henüz istatistik gösterilecek kadar kayıt yok.")

# -------------------------------------
# ☁️ KELİME BULUTU
# -------------------------------------

st.markdown("---")
st.subheader("☁️ Öğrenilen Bilgilerden Kelime Bulutu")

tum_girdiler = " ".join(log.get("girdi", "") for log in daily_logs)
if tum_girdiler.strip():
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(tum_girdiler)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.info("Kelime bulutu oluşturmak için yeterli veri yok.")
