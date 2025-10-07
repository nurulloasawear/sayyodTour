import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database
import os
from ui.admin_panel_view import AdminPanelView
from ui.accountant_view import AccountantView
from ui.reconciliation_view import ReconciliationView
from ui.user_create_view import UserCreateView
from ui.login_view import LoginView
from ui.dashboard_view import DashboardView
from ui.invoices_view import InvoicesView
# Taxminiy panellar (agar mavjud bo'lsa, keyin import qilinadi)
# from ui.reports_view import ReportsView
# from ui.crm_view import CRMView
# from ui.worker_report_view import WorkerReportView
# from ui.products_view import ProductsView

class App(b.Window):
    """Asosiy ilova oynasi, barcha panellarga yo'naltirish."""

    def __init__(self):
        super().__init__(title="Sayyod Tour", themename="darkly")
        self.geometry("1200x800")
        self.current_user = None
        self.current_frame = None
        print("Dastur sozlamalari ishga tushirilmoqda...")
        self.initialize_database()
        print("Sozlamalar yuklanmoqda...")
        self.load_settings()
        print("Sozlamalar tayyor.")

        self.container = b.Frame(self)
        self.container.pack(fill=BOTH, expand=YES)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.initialize_frames()
        self.check_initial_user()

    def initialize_database(self):
        """Ma'lumotlar bazasini boshlaydi."""
        try:
            database.create_all_tables()
            print("Ma'lumotlar bazasi muvaffaqiyatli boshlandi.")
        except Exception as e:
            print(f"Xato: Ma'lumotlar bazasini boshlashda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Ma'lumotlar bazasini boshlashda xato: {str(e)}")
            self.destroy()

    def load_settings(self):
        """Sozlamalarni yuklaydi."""
        try:
            ip_filtering = database.get_setting("ip_filtering_enabled", "false")
            print("Sozlamalar muvaffaqiyatli yuklandi.")
        except Exception as e:
            print(f"Xato: Sozlamalarni yuklashda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Sozlamalarni yuklashda xato: {str(e)}")
            self.destroy()

    def initialize_frames(self):
        """Barcha panellarni ro'yxatga oladi."""
        try:
            frame_classes = [
                LoginView,
                UserCreateView,
                AccountantView,
                ReconciliationView,
                DashboardView,
                AdminPanelView,
                InvoicesView,
                # Agar mavjud bo'lsa, quyidagilarni qo'shing:
                # ReportsView,
                # CRMView,
                # WorkerReportView,
                # ProductsView,
            ]
            for F in frame_classes:
                frame = F(self.container, self)
                self.frames[F.__name__] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            print("Barcha panellar muvaffaqiyatli boshlandi.")
        except Exception as e:
            print(f"Xato: Panellarni boshlashda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Panellarni boshlashda xato: {str(e)}")
            self.destroy()

    def check_initial_user(self):
        """Birinchi foydalanuvchi mavjudligini tekshiradi."""
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM users")
            user_count = cursor.fetchone()['count']
            conn.close()
            if user_count == 0:
                print("Birinchi foydalanuvchi yaratilishi kerak.")
                self.show_frame("UserCreateView")
                self.frames["UserCreateView"].show_back_button(False)
            else:
                print("Foydalanuvchilar mavjud, login sahifasiga o'tilmoqda.")
                self.show_frame("LoginView")
        except Exception as e:
            print(f"Xato: Foydalanuvchilarni tekshirishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Foydalanuvchilarni tekshirishda xato: {str(e)}")
            self.destroy()

    def show_frame(self, frame_name, **kwargs):
        """Berilgan freymni ko'rsatadi."""
        try:
            frame = self.frames.get(frame_name)
            if frame:
                if self.current_frame:
                    self.current_frame.grid_forget()
                self.current_frame = frame
                self.current_frame.grid(row=0, column=0, sticky="nsew")
                print(f"{frame_name} ko'rsatilmoqda...")
                if hasattr(frame, "refresh"):
                    frame.refresh(**kwargs)
            else:
                print(f"Xato: {frame_name} topilmadi.")
                messagebox.showerror("Xatolik", f"Panel topilmadi: {frame_name}")
        except Exception as e:
            print(f"Xato: Freymni ko'rsatishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Freymni ko'rsatishda xato: {str(e)}")

    def show_login_page(self):
        """Login sahifasini ko'rsatadi."""
        self.geometry("600x400")
        self.show_frame("LoginView")

    def show_user_create_page(self):
        """Foydalanuvchi yaratish sahifasini ko'rsatadi."""
        self.geometry("600x400")
        self.show_frame("UserCreateView")

    def show_dashboard(self, user_data):
        """Dashboard sahifasini ko'rsatadi."""
        self.geometry("1200x800")
        self.current_user = user_data
        self.show_frame("DashboardView", user_data=user_data)

    def attempt_login(self, username, password):
        """Foydalanuvchi loginini tekshiradi."""
        try:
            print(f"Attempting login for username: {username}")
            user_data = database.verify_user_credentials(username, password)
            if user_data:
                print(f"Login successful for {username}, role: {user_data['role']}")
                if user_data.get('requires_2fa'):
                    messagebox.showinfo("2FA Talab qilinadi", "Ikki faktorli autentifikatsiya kodi kerak.", parent=self.frames["LoginView"])
                    return user_data
                else:
                    self.show_dashboard(user_data)
                    return user_data
            else:
                print(f"Login failed for {username}: Invalid credentials")
                messagebox.showerror("Xatolik", "Noto'g'ri login yoki parol!", parent=self.frames["LoginView"])
                return None
        except Exception as e:
            print(f"Xato: Login qilishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Login qilishda xato: {str(e)}", parent=self.frames["LoginView"])
            return None

if __name__ == "__main__":
    # Kerakli papkalarni yaratish
    for folder in ["ui", "backend", "utils"]:
        os.makedirs(folder, exist_ok=True)
    
    app = App()
    app.mainloop()