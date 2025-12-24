import pandas as pd
import random

# Kilis Gerçek Eczane ve Adres Listesi
eczane_listesi = [
    ("Polat Eczanesi", "Cumhuriyet Cad."), ("Pazar Eczanesi", "Sabah Pazarı Cad."),
    ("Özkeleş Eczanesi", "Cumhuriyet Cad."), ("Şiltelioğlu Eczanesi", "Ali Metin Dirim Cad."),
    ("Efe Eczanesi", "İnönü Bulvarı"), ("Erdem Eczanesi", "Ekrem Çetin Mah."),
    ("Uygur Eczanesi", "Av. Mehmet Abdi Bulut Cad."), ("Ömür Eczanesi", "Şörhabil Cad.")
]
ilaclar = ["Parol", "Arveles", "Augmentin", "Majezik", "Coraspin", "Dolorex", "Apranax"]

# Her eczanenin nöbet durumunu bir kez belirleyelim (Mantık Hatasını Önler)
nobet_durumlari = {e[0]: random.choice(["Evet", "Hayır"]) for e in eczane_listesi}

veriler = []
for _ in range(500):
    eczane_ad, adres = random.choice(eczane_listesi)
    veriler.append({
        "Eczane_Adi": eczane_ad,
        "Adres": adres,
        "Ilac_Adi": random.choice(ilaclar),
        "Stok_Sayisi": random.randint(0, 50),
        "Nobetci_Mi": nobet_durumlari[eczane_ad] # Eczanenin genel durumu neyse o gelir
    })

df = pd.DataFrame(veriler)
df.to_csv("kilis_eczane_stok.csv", index=False, encoding="utf-16")
print("✅ Veri seti ve nöbetçi mantığı başarıyla güncellendi!")