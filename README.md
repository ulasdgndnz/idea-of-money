# Idea of Money — Opsiyon Analiz Terminali

**Idea of Money**, [yfinance](https://pypi.org/project/yfinance/) üzerinden gerçek zamanlı hisse
senedi ve opsiyon verisi çekip, tek ekranda profesyonel bir opsiyon analiz paneli sunan bir
Streamlit uygulamasıdır. Bir hisse sembolü yazman yeterli — teknik göstergeler, opsiyon zinciri,
piyasa hissiyatı ve max pain analizi saniyeler içinde karşına çıkar.

Yatırım kararı vermeden önce hızlıca "bu hissenin opsiyon piyasası ne söylüyor?" sorusuna cevap
aramak isteyenler için tasarlandı.

## Neler yapabiliyor?

**📊 Temel & teknik veriler**
- Fiyat, günlük değişim, hacim, piyasa değeri, F/K ve PEG oranı, 52 haftalık aralık, beta
- RSI (14) — aşırı alım / aşırı satım / nötr durumunu renkli rozetle gösterir
- SMA 20/50, EMA 20 ve Bollinger Bantları — güncel fiyata göre üstünde mi altında mı olduğunu
  yeşil/kırmızı yön okuyla işaretler

**⛓️ Opsiyon zinciri**
- Her vade tarihi ayrı bir açılır (dropdown) panel olarak listelenir
- Panel başlığında o vadenin özeti: kalan gün, put/call oranı, sentiment, max pain, toplam açık pozisyon
- Panel içinde CALL/PUT tipine ve strike fiyatına göre filtrelenebilir detaylı tablo
- Hem tüm vadeleri tek seferde hem de tek bir vadeyi ayrı ayrı **CSV olarak indirme**

**📈 Piyasa hissiyatı & görselleştirme**
- Put/Call oranı göstergesi (gauge chart) ve genel sentiment etiketi (Çok Bullish → Çok Bearish)
- Strike bazında açık pozisyon (OI) grafiği
- Zımni volatilite (IV) eğrisi
- Vadelere göre açık pozisyon dağılımı
- Call/Put hacim dağılımı (donut chart)

**⚡ Performans**
- `st.cache_data(ttl=300)` ile aynı hissenin verisi 5 dakika boyunca önbellekten gelir,
  gereksiz Yahoo Finance isteği atılmaz.

## Ekran görüntüsü

Uygulamayı çalıştırdıktan sonra bir hisse sembolü (ör. `AAPL`, `TSLA`, `NVDA`) yazıp
**ANALİZ ET** butonuna basman ya da hazır kısayollardan birine tıklaman yeterli.

## Gereksinimler

- Python 3.9 veya üzeri
- İnternet bağlantısı (Yahoo Finance verisine erişim için)

## Kurulum ve localde çalıştırma

```bash
# 1) Projeyi klonla (veya zip olarak indirdiysen klasöre gir)
git clone https://github.com/KULLANICI_ADIN/REPO_ADIN.git
cd REPO_ADIN

# 2) (Önerilir) sanal ortam oluştur
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3) Bağımlılıkları kur
pip install -r requirements.txt

# 4) Uygulamayı başlat
streamlit run app.py
```

Komut çalıştıktan sonra tarayıcında otomatik olarak `http://localhost:8501` açılır. Açılmazsa
terminalde yazan **Local URL**'e manuel olarak gidebilirsin.

Uygulamayı durdurmak için terminalde `Ctrl + C` yeterli.

### Sık karşılaşılan sorunlar

| Sorun | Çözüm |
|---|---|
| `ModuleNotFoundError` | `pip install -r requirements.txt` komutunu tekrar çalıştır, sanal ortamın aktif olduğundan emin ol |
| Veri gelmiyor / boş sonuç | Sembolü kontrol et (`AAPL` gibi ABD borsası sembolleri en stabil çalışır), birkaç saniye bekleyip tekrar dene |
| Yahoo Finance rate-limit hatası | Çok sık istek atıldığında geçici olur; ~30 saniye bekleyip tekrar dene |
| Streamlit üst çubuğu içerikle çakışıyor | Tarayıcı önbelleğini temizleyip sayfayı yenile |

## GitHub'a yükleme

```bash
cd optionsx-streamlit
git init
git add .
git commit -m "Idea of Money — ilk sürüm"
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

Her `git push` yaptığında Streamlit Cloud uygulamayı otomatik olarak günceller. Yeni bir
kütüphane eklersen `requirements.txt`'ye eklemeyi unutma, yoksa deploy hata verir.

## Proje yapısı

```
├── app.py              # Uygulamanın tamamı (veri çekme + arayüz)
├── requirements.txt     # Python bağımlılıkları
└── README.md            # Bu dosya
```

## Notlar

- Veriler [Yahoo Finance](https://finance.yahoo.com/) kaynaklıdır ve yatırım tavsiyesi
  niteliği taşımaz; tamamen bilgilendirme amaçlıdır.
- Yahoo Finance bazen rate-limit uygulayabilir; çok sık istek atılırsa geçici
  hatalar görülebilir, bu durumda birkaç saniye bekleyip tekrar denemek yeterli.
- Opsiyon verisi bulunmayan sembollerde (ör. bazı düşük hacimli hisseler) uygulama
  bilgilendirici bir hata mesajı gösterir.
