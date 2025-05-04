import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")

# API anahtarını oku
genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

st.set_page_config(page_title="Bugün Ne Öğrendim?", page_icon="📘")

st.title("📘 Bugün Ne Öğrendim?")
st.markdown("Her gün öğrendiğin bir şeyi yaz, sana özetleyelim, etiketleyelim ve yorumlayalım!")

user_input = st.text_area("Bugün ne öğrendin?")

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

    # Çıktıyı ayır
    lines = response.text.strip().split("\n")
    summary = next((l for l in lines if l.startswith("Özet:")), "Özet: Bulunamadı")
    topic = next((l for l in lines if l.startswith("Etiket:")), "Etiket: Bulunamadı")
    comment = next((l for l in lines if l.startswith("Yorum:")), "Yorum: Bulunamadı")

    # Göster
    st.subheader("🎯 Özet")
    st.success(summary.replace("Özet:", "").strip())

    st.subheader("🏷️ Etiket")
    st.info(topic.replace("Etiket:", "").strip())

    st.subheader("💬 Yorum")
    st.warning(comment.replace("Yorum:", "").strip())


    log = {
        "tarih": "2025-05-04",
        "girdi": user_input,
        "ozet": response.text.split("Özet:")[1].split("Etiket:")[0].strip(),
        "etiket": response.text.split("Etiket:")[1].split("Yorum:")[0].strip(),
        "yorum": response.text.split("Yorum:")[1].strip()
    }

    with open("gunluk_kayitlar.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")


    log = {
        "tarih": datetime.now().isoformat(),
        "girdi": user_input,
        "ozet": summary,
        "etiket": topic,
        "yorum": comment
    }

    with open("gunlukler.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")



