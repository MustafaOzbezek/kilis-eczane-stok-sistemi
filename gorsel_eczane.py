import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

# ----------------------------
# Akademik UI Ayarları
# ----------------------------
ctk.set_appearance_mode("dark")         # "light" istersen değiştir
ctk.set_default_color_theme("blue")     # temayı sade tutuyoruz

APP_W, APP_H = 980, 680

# Renkler (kurumsal koyu tema)
BG = "#121417"
SURFACE = "#171A1F"
CARD = "#1E232B"
BORDER = "#2B3240"
TEXT = "#E8EDF6"
MUTED = "#AEB7C6"

ACCENT = "#3B82F6"      # kurumsal mavi
GOOD = "#16A34A"        # nöbetçi EVET
BAD = "#94A3B8"         # nöbetçi HAYIR (pasif)
WARN = "#F59E0B"        # stok düşük


def normalize_query(s: str) -> str:
    """Kullanıcının yazdığı ilacı veriyle eşleştir (Parol, ARVELES, parol...)."""
    s = (s or "").strip()
    if not s:
        return ""
    return s[:1].upper() + s[1:].lower()


class EczaneApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kilis Eczane Stok Sistemi")
        self.geometry(f"{APP_W}x{APP_H}")
        self.minsize(900, 640)

        self.configure(fg_color=BG)

        try:
            self.df = pd.read_csv("kilis_eczane_stok.csv", encoding="utf-16")
        except Exception:
            messagebox.showerror("Hata", "kilis_eczane_stok.csv bulunamadı. Önce veri_olusturucu.py çalıştır.")
            self.df = pd.DataFrame()

        self._build_layout()

    def _build_layout(self):
        # Üst bar (başlık alanı)
        header = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=14)
        header.pack(fill="x", padx=18, pady=(18, 10))

        title = ctk.CTkLabel(
            header,
            text="Kilis Eczane Stok Sorgulama Sistemi",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT
        )
        title.pack(anchor="w", padx=18, pady=(14, 0))

        subtitle = ctk.CTkLabel(
            header,
            text="İlaç adına göre eczane stoklarını listeleyin ve nöbetçi durumunu görüntüleyin.",
            font=("Segoe UI", 12),
            text_color=MUTED
        )
        subtitle.pack(anchor="w", padx=18, pady=(2, 12))

        # Arama alanı (giriş + buton)
        search_row = ctk.CTkFrame(self, fg_color=BG)
        search_row.pack(fill="x", padx=18, pady=(8, 8))

        self.entry = ctk.CTkEntry(
            search_row,
            placeholder_text="İlaç adı giriniz (örn: Parol)",
            height=44,
            font=("Segoe UI", 13),
            fg_color=SURFACE,
            border_color=BORDER,
            text_color=TEXT
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.btn = ctk.CTkButton(
            search_row,
            text="SORGULA",
            height=44,
            width=140,
            font=("Segoe UI", 13, "bold"),
            fg_color=ACCENT,
            hover_color="#2F6FE0",
            command=self.ara
        )
        self.btn.pack(side="left")

        # Enter ile arama
        self.entry.bind("<Return>", lambda e: self.ara())

        # Bilgi satırı
        info_row = ctk.CTkFrame(self, fg_color=BG)
        info_row.pack(fill="x", padx=18, pady=(0, 8))

        self.result_label = ctk.CTkLabel(
            info_row,
            text="Hazır. Bir ilaç adı girip sorgulayın.",
            font=("Segoe UI", 12),
            text_color=MUTED
        )
        self.result_label.pack(anchor="w")

        # Sonuç listesi
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )
        self.scroll.pack(fill="both", expand=True, padx=18, pady=(8, 18))

        # Boş durum
        self.empty_state = ctk.CTkLabel(
            self.scroll,
            text="Sonuçlar burada görüntülenecek.",
            font=("Segoe UI", 13),
            text_color=MUTED
        )
        self.empty_state.pack(pady=22)

    def _clear_results(self):
        for w in self.scroll.winfo_children():
            w.destroy()

    def _badge(self, parent, text, kind="neutral"):
        # Kurumsal küçük etiket (badge)
        if kind == "good":
            fg, bc, tc = "#0F1F15", GOOD, GOOD
        elif kind == "warn":
            fg, bc, tc = "#241A07", WARN, WARN
        elif kind == "bad":
            fg, bc, tc = "#202530", BAD, BAD
        else:
            fg, bc, tc = "#1B2230", BORDER, MUTED

        wrap = ctk.CTkFrame(parent, fg_color=fg, corner_radius=10, border_width=1, border_color=bc)
        lab = ctk.CTkLabel(wrap, text=text, font=("Segoe UI", 11, "bold"), text_color=tc)
        lab.pack(padx=10, pady=6)
        return wrap

    def _card(self, row):
        card = ctk.CTkFrame(self.scroll, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=14, pady=8)

        # Sol (eczane adı + adres)
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=16, pady=14)

        name = ctk.CTkLabel(left, text=row["Eczane_Adi"], font=("Segoe UI", 15, "bold"), text_color=TEXT)
        name.pack(anchor="w")

        addr = ctk.CTkLabel(left, text=row["Adres"], font=("Segoe UI", 12), text_color=MUTED)
        addr.pack(anchor="w", pady=(4, 0))

        # Sağ (stok + nöbetçi badge)
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=16, pady=14)

        stok = int(row["Stok_Sayisi"])
        nobet = str(row["Nobetci_Mi"]).upper()

        # Stok badge kuralı
        if stok == 0:
            stok_badge = self._badge(right, f"Stok: {stok} (YOK)", kind="bad")
        elif stok <= 15:
            stok_badge = self._badge(right, f"Stok: {stok} (DÜŞÜK)", kind="warn")
        else:
            stok_badge = self._badge(right, f"Stok: {stok}", kind="neutral")

        stok_badge.pack(side="left", padx=(0, 10))

        # Nöbetçi badge
        if nobet == "EVET":
            nobet_badge = self._badge(right, "Nöbetçi: EVET", kind="good")
        else:
            nobet_badge = self._badge(right, "Nöbetçi: HAYIR", kind="bad")

        nobet_badge.pack(side="left")

    def ara(self):
        if self.df.empty:
            messagebox.showerror("Hata", "Veri yok. Önce veri_olusturucu.py çalıştırıp CSV oluştur.")
            return

        query = normalize_query(self.entry.get())
        self._clear_results()

        if not query:
            self.result_label.configure(text="Lütfen bir ilaç adı giriniz.")
            empty = ctk.CTkLabel(self.scroll, text="Boş arama yapıldı. Lütfen ilaç adı girin.",
                                font=("Segoe UI", 13), text_color=MUTED)
            empty.pack(pady=22)
            return

        # Filtre + her eczaneden tek kayıt (kesin)
        res = (
            self.df[self.df["Ilac_Adi"] == query]
            .sort_values(["Nobetci_Mi", "Stok_Sayisi"], ascending=[False, False])
            .groupby("Eczane_Adi", as_index=False)
            .first()
        )

        if res.empty:
            self.result_label.configure(text=f"'{query}' için kayıt bulunamadı.")
            empty = ctk.CTkLabel(self.scroll, text="Sonuç bulunamadı.",
                                font=("Segoe UI", 13, "bold"), text_color=TEXT)
            empty.pack(pady=(22, 6))
            hint = ctk.CTkLabel(self.scroll, text="İpucu: Parol, Arveles, Augmentin, Majezik, Coraspin, Dolorex, Apranax",
                                font=("Segoe UI", 12), text_color=MUTED)
            hint.pack(pady=(0, 18))
            return

        # Bilgi satırı
        self.result_label.configure(text=f"'{query}' için {len(res)} eczane listelendi.")

        # Kartlar
        for _, row in res.iterrows():
            self._card(row)


if __name__ == "__main__":
    app = EczaneApp()
    app.mainloop()
