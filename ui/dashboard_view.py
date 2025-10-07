import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database

class DashboardView(b.Frame):
    """Foydalanuvchi uchun umumiy boshqaruv paneli."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Interfeys elementlarini yaratadi."""
        main_frame = b.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        # Foydalanuvchi ma'lumotlari
        user_info_frame = b.LabelFrame(main_frame, text="Foydalanuvchi ma'lumotlari", padding=10, bootstyle=INFO)
        user_info_frame.pack(fill=X, pady=10)

        user = self.controller.current_user or {"full_name": "Noma'lum", "role": "Noma'lum"}
        b.Label(user_info_frame, text=f"Ism: {user['full_name']}").pack(anchor=W, padx=5, pady=2)
        b.Label(user_info_frame, text=f"Rol: {user['role']}").pack(anchor=W, padx=5, pady=2)

        # Umumiy ma'lumotlar
        stats_frame = b.LabelFrame(main_frame, text="Tizim statistikasi", padding=10, bootstyle=INFO)
        stats_frame.pack(fill=X, pady=10)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM cash_entries")
            cash_entries_count = cursor.fetchone()['count']
            b.Label(stats_frame, text=f"Kassa yozuvlari: {cash_entries_count}").pack(anchor=W, padx=5, pady=2)
            conn.close()
        except Exception as e:
            print(f"Xato: Statistikani olishda xato: {str(e)}")
            b.Label(stats_frame, text="Statistika yuklanmadi").pack(anchor=W, padx=5, pady=2)

        # Navigatsiya tugmalari
        nav_frame = b.Frame(main_frame)
        nav_frame.pack(fill=X, pady=10)

        if user['role'] in ["OWNER", "ACCOUNTANT"]:
            b.Button(nav_frame, text="Buxgalteriya paneli", command=lambda: self.controller.show_frame("AccountantView"), bootstyle=PRIMARY).pack(side=LEFT, padx=5)
            b.Button(nav_frame, text="Taqqoslash paneli", command=lambda: self.controller.show_frame("ReconciliationView"), bootstyle=PRIMARY).pack(side=LEFT, padx=5)
        # Agar ProductsView mavjud bo'lsa, quyidagi tugma qo'shiladi:
        # b.Button(nav_frame, text="Mahsulotlar paneli", command=lambda: self.controller.show_frame("ProductsView"), bootstyle=PRIMARY).pack(side=LEFT, padx=5)

        # Chiqish tugmasi
        b.Button(nav_frame, text="Tizimdan chiqish", command=self.logout, bootstyle=DANGER).pack(side=RIGHT, padx=5)

        # Kengaytirish uchun sozlash
        main_frame.columnconfigure(0, weight=1)

    def logout(self):
        """Tizimdan chiqish."""
        self.controller.current_user = None
        self.controller.show_frame("LoginView")
        login_frame = self.controller.frames.get("LoginView")
        if login_frame:
            login_frame.clear_form()
        messagebox.showinfo("Chiqish", "Tizimdan muvaffaqiyatli chiqildi!", parent=self)