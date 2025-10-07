import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database

class DashboardView(b.Frame):
    """Foydalanuvchilar uchun umumiy boshqaruv paneli."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Dashboard interfeysini yaratadi."""
        main_frame = b.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        # Sarlavha
        b.Label(main_frame, text="Sayyod Tour - Boshqaruv Paneli", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Foydalanuvchi ma'lumotlari
        user_info = self.controller.current_user
        if user_info:
            user_label = b.Label(
                main_frame,
                text=f"Xush kelibsiz, {user_info['full_name']} ({user_info['role']})",
                font=("Helvetica", 12)
            )
            user_label.pack(pady=10)

        # Navigatsiya tugmalari
        button_frame = b.Frame(main_frame)
        button_frame.pack(fill=X, pady=10)

        # Rolga qarab tugmalar
        if user_info and user_info['role'] in ['MANAGER', 'MARKETING', 'WORKER']:
            b.Button(
                button_frame,
                text="Kassa Jurnali",
                command=lambda: self.controller.show_frame("AccountantView"),
                bootstyle=PRIMARY
            ).pack(side=LEFT, padx=5)
            b.Button(
                button_frame,
                text="Taqqoslash",
                command=lambda: self.controller.show_frame("ReconciliationView"),
                bootstyle=PRIMARY
            ).pack(side=LEFT, padx=5)
            # Agar ProductsView mavjud bo'lsa, qo'shiladi
            # b.Button(
            #     button_frame,
            #     text="Mahsulotlar",
            #     command=lambda: self.controller.show_frame("ProductsView"),
            #     bootstyle=PRIMARY
            # ).pack(side=LEFT, padx=5)

        # Chiqish tugmasi
        b.Button(
            main_frame,
            text="Tizimdan chiqish",
            command=self.logout,
            bootstyle=DANGER
        ).pack(pady=20)

        # Test ma'lumotlari (masalan, kassa jurnali umumiy ko'rinishi)
        try:
            entries = database.get_cash_journal_entries({
                'start_date': '2025-01-01',
                'end_date': '2025-12-31'
            })
            summary_label = b.Label(
                main_frame,
                text=f"Kassa yozuvlari soni: {len(entries)}",
                font=("Helvetica", 10)
            )
            summary_label.pack(pady=5)
        except Exception as e:
            print(f"Xato: Kassa yozuvlarini olishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Ma'lumotlarni yuklashda xato: {str(e)}", parent=self)

    def logout(self):
        """Foydalanuvchini tizimdan chiqaradi."""
        try:
            self.controller.current_user = None
            self.controller.show_frame("LoginView")
            self.controller.frames["LoginView"].clear_form()
            print("Foydalanuvchi tizimdan chiqdi.")
        except Exception as e:
            print(f"Xato: Chiqishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Chiqishda xato: {str(e)}", parent=self)