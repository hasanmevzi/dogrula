#!/usr/bin/env python3
"""
Katılım belgesi numaralarını üretir ve doğrulama sayfası için
şifreli kayıt dosyasını (belgeler.json) oluşturur.

Kullanım:
    python3 belge-uret.py katilimcilar.csv

katilimcilar.csv formatı (ilk satır başlık):
    ad_soyad
    Ayşe Yılmaz
    Mehmet Demir

Çıktılar:
    belgeler.json   -> doğrulama sayfasının okuduğu şifreli veri
    belgeler.csv    -> her katılımcının belge numarası (Autocrat için)
"""

import base64
import csv
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------------------------------------------------------------
# Eğitim bilgileri — her yeni eğitimde burayı güncelleyin
# ---------------------------------------------------------------
EGITIM_ADI = "Advanced Operation Security"
EGITIM_TARIHI = "10 Ağustos 2026"
EGITIM_SURESI = "1 saat 30 dakika"
EGITMEN = "Hasan Mevzi"
BELGE_ONEKI = "AOS-2026"

# PBKDF2 tur sayısı. Artırmak güvenliği yükseltir, sayfayı yavaşlatır.
ITERASYON = 150_000

# Karışması kolay karakterler (0/O, 1/I/L) çıkarıldı
ALFABE = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
RASTGELE_UZUNLUK = 5


def belge_no_uret(sira: int) -> str:
    rastgele = "".join(secrets.choice(ALFABE) for _ in range(RASTGELE_UZUNLUK))
    return f"{BELGE_ONEKI}-{sira:04d}-{rastgele}"


def arama_anahtari(belge_no: str, salt_hex: str) -> str:
    ham = f"{belge_no}:{salt_hex}".encode("utf-8")
    return hashlib.sha256(ham).hexdigest()[:32]


def sifrele(belge_no: str, salt: bytes, veri: dict) -> str:
    anahtar = hashlib.pbkdf2_hmac(
        "sha256", belge_no.encode("utf-8"), salt, ITERASYON, dklen=32
    )
    iv = os.urandom(12)
    sifreli = AESGCM(anahtar).encrypt(
        iv, json.dumps(veri, ensure_ascii=False).encode("utf-8"), None
    )
    return base64.b64encode(iv + sifreli).decode("ascii")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    girdi = Path(sys.argv[1])
    if not girdi.exists():
        print(f"Dosya bulunamadı: {girdi}")
        return 1

    with girdi.open(encoding="utf-8-sig", newline="") as f:
        satirlar = [r for r in csv.DictReader(f) if r.get("ad_soyad", "").strip()]

    if not satirlar:
        print("CSV boş ya da 'ad_soyad' sütunu yok.")
        return 1

    salt = os.urandom(16)
    salt_hex = salt.hex()

    kayitlar: dict[str, str] = {}
    liste: list[dict[str, str]] = []

    for i, satir in enumerate(satirlar, start=1):
        ad = satir["ad_soyad"].strip()
        belge_no = belge_no_uret(i)

        kayitlar[arama_anahtari(belge_no, salt_hex)] = sifrele(
            belge_no,
            salt,
            {
                "ad": ad,
                "egitim": EGITIM_ADI,
                "tarih": EGITIM_TARIHI,
                "sure": EGITIM_SURESI,
                "egitmen": EGITMEN,
            },
        )
        liste.append({"ad_soyad": ad, "belge_no": belge_no})

    Path("belgeler.json").write_text(
        json.dumps(
            {
                "v": 1,
                "salt": salt_hex,
                "iter": ITERASYON,
                "kayitlar": kayitlar,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    with Path("belgeler.csv").open("w", encoding="utf-8-sig", newline="") as f:
        yazici = csv.DictWriter(f, fieldnames=["ad_soyad", "belge_no"])
        yazici.writeheader()
        yazici.writerows(liste)

    print(f"{len(liste)} belge üretildi.\n")
    print("  belgeler.json  -> doğrulama sayfasının yanına koyun")
    print("  belgeler.csv   -> Google Sheets'e alıp Autocrat ile birleştirin\n")
    print("UYARI: belgeler.csv belge numaralarını açık biçimde içerir.")
    print("Yayımlamayın; yalnızca belge üretiminde kullanın.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
