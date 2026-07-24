# Katılım Belgesi Doğrulama Sayfası

Advanced Operation Security eğitimi için belge doğrulama sistemi.
GitHub Pages üzerinde ücretsiz çalışır, sunucu gerektirmez.

---

## Nasıl çalışıyor

Katılımcı listesi hiçbir zaman açık biçimde yayımlanmaz.

Her kayıt, kendi belge numarası anahtar olarak kullanılarak **AES-256-GCM** ile
şifrelenir. Doğrulama sayfası yalnızca doğru numarayı girdiğinizde ilgili kaydı
çözebilir. Yayımlanan `belgeler.json` dosyasını indiren biri katılımcı listesini
göremez — dosyada isim, e-posta veya okunabilir hiçbir veri yoktur.

Belge numaralarının sonundaki 5 rastgele karakter (`AOS-2026-0001-K7M2X`) sıra
numarasından deneme yaparak kayıt bulunmasını engeller. PBKDF2 ile 150.000 tur
anahtar türetme, toplu deneme saldırısını ayrıca yavaşlatır.

Doğrulama tamamen tarayıcıda yapılır; girilen numara hiçbir sunucuya gitmez.

---

## Kurulum (tek seferlik)

### 1. Depoyu oluşturun

GitHub'da yeni bir **public** depo açın. Adı `dogrula` olabilir.

### 2. Dosyaları yükleyin

Depoya `index.html` dosyasını koyun. (`belgeler.json` bir sonraki adımda gelecek.)

### 3. GitHub Pages'i açın

Depo → **Settings** → **Pages** → Source: `Deploy from a branch` →
Branch: `main` / `root` → Save.

Birkaç dakika içinde sayfanız yayında olur:

```
https://KULLANICI-ADINIZ.github.io/dogrula/
```

Bu adresi sözleşme metnindeki `[DOĞRULAMA_URL]` alanına yazın.

---

## Her eğitim sonrası yapılacaklar

### 1. Katılımcı listesini hazırlayın

Zoom katılım raporundan, eğitime gerçekten katılanları alıp `katilimcilar.csv`
dosyası oluşturun:

```csv
ad_soyad
Ayşe Yılmaz
Mehmet Demir
Zeynep Öztürk
```

Ad-soyadı, katılımcının başvuru formunda "belgede görünecek ad-soyad" alanına
yazdığı şekilde alın.

### 2. Belgeleri üretin

```bash
pip install cryptography
python3 belge-uret.py katilimcilar.csv
```

İki dosya çıkar:

| Dosya | Ne yapacaksınız |
|---|---|
| `belgeler.json` | GitHub deposuna yükleyin (`index.html` ile aynı klasöre) |
| `belgeler.csv` | Google Sheets'e alın, Autocrat ile belgeleri üretin |

> ⚠️ `belgeler.csv` belge numaralarını **açık biçimde** içerir. Bu dosyayı
> GitHub'a yüklemeyin. Yalnızca kendi bilgisayarınızda ve Drive'da tutun.

### 3. Belgeleri üretip gönderin

`belgeler.csv` içeriğini Google Sheets'e yapıştırın. Autocrat şablonunuzda
`<<ad_soyad>>` ve `<<belge_no>>` yer tutucularını kullanın.

Belge alt bilgisine doğrulama adresini yazın:

```
Belge No: <<belge_no>>
Doğrulama: https://KULLANICI-ADINIZ.github.io/dogrula/
```

### 4. Yeni eğitim eklerken

`belge-uret.py` dosyasının başındaki ayarları güncelleyin:

```python
EGITIM_ADI    = "Advanced Operation Security"
EGITIM_TARIHI = "10 Ağustos 2026"
EGITIM_SURESI = "1 saat 30 dakika"
BELGE_ONEKI   = "AOS-2026"
```

`index.html` içindeki başlığı da (`<h1>`) yeni eğitim adına göre değiştirin.

---

## Birden fazla eğitimi aynı sayfada toplamak

Şu anki kurulum her çalıştırmada `belgeler.json` dosyasını sıfırdan yazar —
yani eski eğitimlerin kayıtları silinir.

Eğitimleri biriktirmek isterseniz iki yol var:

**Basit yol:** Her eğitim için ayrı klasör açın.

```
dogrula/aos-2026-08/index.html + belgeler.json
dogrula/xyz-2026-11/index.html + belgeler.json
```

**Birleşik yol:** `belge-uret.py` içinde `belgeler.json` varsa okuyup
`kayitlar` sözlüğüne ekleme yapacak şekilde değiştirin. Bu durumda `salt`
değerinin sabit kalması gerekir — her eğitimde yeniden üretilmemeli.

---

## Kolaylık: doğrudan bağlantı

Sayfa, adres satırındaki numarayı otomatik doğrular:

```
https://KULLANICI-ADINIZ.github.io/dogrula/?no=AOS-2026-0001-K7M2X
```

Belgeye QR kod koyacaksanız bu adresi kullanın — kişi QR'ı okuttuğunda
doğrudan sonucu görür, numara yazmak zorunda kalmaz.

QR kodu Autocrat şablonunda otomatik üretmek için Google Sheets'te:

```
=IMAGE("https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" &
  ENCODEURL("https://KULLANICI-ADINIZ.github.io/dogrula/?no=" & B2))
```

---

## KVKK notu

Bu sayfa üzerinden yayımlanan tek veri, doğru belge numarasını bilen kişiye
gösterilen ad-soyad, eğitim adı, tarih ve süredir. Aydınlatma metninizde bu
saklama şu şekilde geçiyor:

> Katılım belgesinin doğrulanabilirliği için belge numarası, ad-soyad, eğitim
> adı, tarih ve süre bilgileri daha uzun süre saklanabilir.

Bir katılımcı kaydının silinmesini talep ederse, `belgeler.json` içinden ilgili
satırı silip dosyayı yeniden yükleyin. Bu durumda belgesi doğrulanamaz hâle
gelir; talebi alırken bunu bildirin.

---

## Bakım

- `belgeler.json` dosyasının yedeğini Drive'da tutun. Kaybederseniz eski
  belgeler doğrulanamaz hâle gelir — kayıtlar yalnızca bu dosyada.
- `katilimcilar.csv` ve `belgeler.csv` dosyalarını depoya **koymayın**.
  `.gitignore` dosyası bunu engelliyor.
