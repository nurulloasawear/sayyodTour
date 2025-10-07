# ui/settings_view.py

import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import shutil
from datetime import datetime

# MUHIM: Bu panel ishlashi uchun database.py, settings_manager.py va config.py
# fayllari mavjud va to'g'ri sozланган bo'lishi SHART.
import database
import settings_manager
import config # DB_NAME ni olish uchun

class SettingsView(b.Frame):
    """Dastur sozlamalarini boshqarish uchun to'liq funksional interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        # Barcha sozlama o'zgaruvchilarini saqlash uchun lug'at
        self.settings_vars = {}

        # Asosiy vkladkalar (Notebook)
        notebook = b.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=(10, 0))

        self.company_tab = b.Frame(notebook)
        self.integrations_tab = b.Frame(notebook)
        self.database_tab = b.Frame(notebook)

        notebook.add(self.company_tab, text="🏢 Kompaniya Rekvizitlari")
        notebook.add(self.integrations_tab, text="🔌 Integratsiyalar")
        notebook.add(self.database_tab, text="🗄️ Ma'lumotlar Bazasi")

        # Har bir vkladka uchun interfeys elementlarini chizish
        self.create_company_widgets()
        self.create_integrations_widgets()
        self.create_database_widgets()

        # Barcha o'zgarishlarni saqlash uchun umumiy tugma
        save_button_frame = b.Frame(self)
        save_button_frame.pack(fill='x', padx=10, pady=10)
        b.Button(
            save_button_frame, 
            text="✅ Barcha o'zgarishlarni saqlash", 
            command=self.save_all_settings,
            bootstyle=SUCCESS
        ).pack(side=RIGHT)
        
        # Dastlabki qiymatlarni yuklash
        self.load_all_settings()

    def _create_setting_entry(self, parent, key, label_text, row, is_password=False):
        """Yordamchi funksiya: sozlama uchun label va entry yaratadi."""
        b.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=8)
        
        var = tk.StringVar()
        self.settings_vars[key] = var
        
        entry_options = {'textvariable': var, 'width': 60}
        if is_password:
            entry_options['show'] = "*"
            
        entry = b.Entry(parent, **entry_options)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=8)

    # --- 1. Kompaniya Rekvizitlari Vkladkasi ---
    def create_company_widgets(self):
        frame = self.company_tab
        container = b.LabelFrame(frame, text="Asosiy ma'lumotlar", padding=20, bootstyle=INFO)
        container.pack(fill=X, padx=20, pady=20)
        container.columnconfigure(1, weight=1)

        self._create_setting_entry(container, 'company_name', "Kompaniya nomi:", 0)
        self._create_setting_entry(container, 'company_stir', "STIR (INN):", 1)
        self._create_setting_entry(container, 'company_address', "Manzil:", 2)
        self._create_setting_entry(container, 'company_phone', "Telefon:", 3)
        self._create_setting_entry(container, 'company_bank', "Bank nomi:", 4)
        self._create_setting_entry(container, 'company_mfo', "Hisob raqam (MFO):", 5)

    # --- 2. Integratsiyalar Vkladkasi ---
    def create_integrations_widgets(self):
        frame = self.integrations_tab
        
        telegram_frame = b.LabelFrame(frame, text="Telegram Xabarnomalari", padding=20, bootstyle=INFO)
        telegram_frame.pack(fill=X, padx=20, pady=20)
        telegram_frame.columnconfigure(1, weight=1)

        self._create_setting_entry(telegram_frame, 'telegram_token', "Bot Token:", 0, is_password=True)
        self._create_setting_entry(telegram_frame, 'telegram_chat_id', "Chat ID:", 1)
        
        email_frame = b.LabelFrame(frame, text="Email (SMTP) Sozlamalari (keyingi versiyada)", padding=20, bootstyle=SECONDARY)
        email_frame.pack(fill=X, padx=20, pady=(0, 20))
        b.Label(email_frame, text="Hozircha aktiv emas.").pack()

    # --- 3. Ma'lumotlar Bazasi Vkladkasi ---
    def create_database_widgets(self):
        frame = self.database_tab
        container = b.LabelFrame(frame, text="Baza Boshqaruvi", padding=20, bootstyle=PRIMARY)
        container.pack(fill=X, padx=20, pady=20)

        b.Button(container, text="Zaxira nusxasini yaratish (Backup)", command=self.backup_database, bootstyle=SUCCESS).pack(fill='x', pady=5)
        b.Label(container, text="Dasturning barcha ma'lumotlari bitta faylda saqlanadi. Muhim ma'lumotlarni yo'qotmaslik uchun vaqti-vaqti bilan zaxira nusxasini yaratib turing.", wraplength=500).pack(pady=5)
        
        b.Separator(container, orient='horizontal').pack(fill='x', pady=15)
        
        b.Button(container, text="Zaxira nusxadan tiklash (Restore)...", command=self.restore_database, bootstyle=DANGER).pack(fill='x', pady=5)
        b.Label(container, text="DIQQAT! Bu amal joriy ma'lumotlarni tanlangan fayldagi ma'lumotlar bilan almashtiradi. Bu jarayonni bekor qilib bo'lmaydi.", wraplength=500, bootstyle=DANGER).pack(pady=5)

    def backup_database(self):
        try:
            today_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
            backup_filename = f"sayyodtour_backup_{today_str}.db"
            
            save_path = filedialog.asksaveasfilename(
                initialfile=backup_filename,
                defaultextension=".db",
                filetypes=[("Database Files", "*.db")]
            )
            
            if save_path:
                shutil.copyfile(config.DB_NAME, save_path)
                messagebox.showinfo("Muvaffaqiyatli", f"Ma'lumotlar bazasining zaxira nusxasi muvaffaqiyatli yaratildi!\n\nJoylashuv: {save_path}")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Zaxira nusxasi yaratishda xatolik yuz berdi:\n{e}")

    def restore_database(self):
        if not messagebox.askyesno("Tasdiqlash", "DIQQAT! Joriy ma'lumotlar o'chiriladi va tanlangan fayldan qayta tiklanadi.\n\nDasturni qayta ishga tushirishingiz kerak bo'ladi.\n\nDavom etishni xohlaysizmi?", title="Qayta tiklashni tasdiqlang", alert=True):
            return
            
        try:
            restore_path = filedialog.askopenfilename(
                title="Zaxira faylini tanlang",
                filetypes=[("Database Files", "*.db")]
            )
            
            if restore_path:
                shutil.copyfile(restore_path, config.DB_NAME)
                messagebox.showinfo("Muvaffaqiyatli", "Ma'lumotlar bazasi muvaffaqiyatli tiklandi!\n\nDasturdagi o'zgarishlar kuchga kirishi uchun uni qayta ishga tushiring.")
                self.controller.destroy() # O'zgarishlar kuchga kirishi uchun dasturni yopish
        except Exception as e:
            messagebox.showerror("Xatolik", f"Ma'lumotlarni tiklashda xatolik yuz berdi:\n{e}")


    # --- Umumiy funksiyalar ---
    def load_all_settings(self):
        """Barcha sozlamalarni bazadan o'qib, interfeysga yuklaydi."""
        print("Sozlamalar oynasi uchun qiymatlar yuklanmoqda...")
        for key, var in self.settings_vars.items():
            value = database.get_setting(key, default_value="")
            var.set(value)

    def save_all_settings(self):
        """Interfeysdagi barcha sozlamalarni bazaga saqlaydi."""
        try:
            for key, var in self.settings_vars.items():
                database.update_setting(key, var.get())
            
            # Global sozlamalarni yangilash
            settings_manager.load_settings()
            
            messagebox.showinfo("Muvaffaqiyatli", "Barcha o'zgarishlar muvaffaqiyatli saqlandi!")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Sozlamalarni saqlashda xatolik yuz berdi:\n{e}")