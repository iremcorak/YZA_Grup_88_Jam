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

st.set_page_config(page_title="Bugün Ne Öğrendim?", page_icon="📘")

st.title("📘 Bugün Ne Öğrendim?")
st.markdown("Her gün öğrendiğin bir şeyi yaz, sana özetleyelim, etiketleyelim ve yorumlayalım!")

user_input = st.text_area("Bugün ne öğrendin?")

# Öğrenme Hedefi ve Gelecek Planı
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

    # Günlük kaydına öğrenme hedefi ve gelecek planını da ekle
    log = {
        "tarih": datetime.now().isoformat(),
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
st.subheader("📚 Geçmiş Günlükler")

# Günlük verilerini oku
daily_logs = []
if os.path.exists("gunlukler.jsonl"):
    with open("gunlukler.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            try:
                daily_logs.append(json.loads(line))
            except:
                pass

# Etiketleri topla (filtre için)
etiketler = sorted(set(log.get("etiket", "Genel") for log in daily_logs if "etiket" in log))
selected_etiket = st.selectbox("Etikete göre filtrele:", ["Tümü"] + etiketler)

# Filtrele
if selected_etiket != "Tümü":
    filtered_logs = [log for log in daily_logs if selected_etiket in log.get("etiket", "")]
else:
    filtered_logs = daily_logs

# Arama
arama = st.text_input("Anahtar kelime ara:")
if arama:
    filtered_logs = [log for log in filtered_logs if arama.lower() in log.get("girdi", "").lower()]

# Göster (timeline formatında)
for log in reversed(filtered_logs):
    with st.container():
        st.markdown(f"""
        <div style='border-left: 3px solid #ccc; padding-left: 15px; margin-bottom: 20px;'>
            <strong>🗓️ {log.get("tarih", "")}</strong><br>
            <em>🏷️ {log.get("etiket", "")}</em><br>
            <strong>🧠 Özet:</strong> {log.get("ozet", "")}<br>
            <strong>✍️ Girdi:</strong> {log.get("girdi", "")}<br>
            <small>💬 {log.get("yorum", "")}</small><br>
            <strong>🎯 Öğrenme Hedefi:</strong> {log.get("ogrenme_hedefi", "Belirtilmemiş")}<br>
            <strong>📈 Gelecek Planı:</strong> {log.get("gelecek_planı", "Belirtilmemiş")}
        </div>
        """, unsafe_allow_html=True)

# 📈 Etiket İstatistikleri
detiketler = [log.get("etiket", "") for log in daily_logs]
counter = Counter(detiketler)
most_common = counter.most_common(3)

st.markdown("### 📈 En Sık Öğrenilen 3 Konu:")
for etiket, adet in most_common:
    st.markdown(f"- {etiket}: {adet} kez")

# ☁️ Kelime Bulutu
if daily_logs:
    all_tags_text = " ".join(detiketler)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_tags_text)

    st.markdown("### ☁️ Öğrenilen Konular Kelime Bulutu")
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

# 📊 Öğrenme Süreci Grafiği
if daily_logs:
    etiketler = [log.get("etiket", "") for log in daily_logs]
    counter = Counter(etiketler)
    labels, counts = zip(*counter.items())

    # Grafik oluştur
    fig, ax = plt.subplots()
    ax.bar(labels, counts)
    ax.set_xlabel('Konu Etiketleri')
    ax.set_ylabel('Sıklık')
    ax.set_title('Öğrenilen Konuların Sıklığı')

    st.markdown("### 📊 Öğrenme Süreci Grafiği")
    st.pyplot(fig)

# 📥 JSON Olarak İndir
json_str = json.dumps(filtered_logs, ensure_ascii=False, indent=2)
st.download_button("📥 Günlükleri JSON olarak indir", data=json_str, file_name="gunlukler.json", mime="application/json")

