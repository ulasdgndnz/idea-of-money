# OPTIONSx — Opsiyon Analiz Terminali (Streamlit)

`yfinance` üzerinden gerçek zamanlı hisse ve opsiyon verisi çeken, RSI/MACD/Bollinger/ATR gibi
teknik göstergeler ile opsiyon zinciri (call/put OI, IV, max pain, put/call oranı) gösteren
Streamlit uygulaması.

## Yerel çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tarayıcıda otomatik olarak `http://localhost:8501` açılır.

## GitHub'a yükleme

```bash
cd optionsx-streamlit
git init
git add .
git commit -m "OPTIONSx Streamlit ilk sürüm"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/REPO_ADIN.git
git push -u origin main
```

> `KULLANICI_ADIN/REPO_ADIN` kısmını GitHub'da oluşturduğun reponun adresiyle değiştir.
> Önce github.com üzerinde boş bir repo oluşturman gerekiyor (README eklemeden).

## Streamlit Community Cloud'a deploy

1. https://share.streamlit.io adresine git, GitHub hesabınla giriş yap.
2. **New app** butonuna tıkla.
3. Repository olarak yukarıda push ettiğin repoyu seç.
4. Branch: `main`, Main file path: `app.py`.
5. **Deploy** butonuna tıkla — birkaç dakika içinde uygulamanın linki hazır olur
   (ör. `https://senin-repo-adın.streamlit.app`).

Her `git push` yaptığında Streamlit Cloud uygulamayı otomatik olarak günceller.

## Notlar

- `st.cache_data(ttl=300)` sayesinde aynı hisse için veriler 5 dakika boyunca
  önbellekten gelir, gereksiz `yfinance` isteklerini azaltır.
- Yahoo Finance bazen rate-limit uygulayabilir; çok sık istek atılırsa geçici
  hatalar görülebilir, bu durumda birkaç saniye bekleyip tekrar denemek yeterli.
