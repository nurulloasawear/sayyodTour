import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database

class DashboardView(b.Frame):
    """Foydalanuvchi uchun umumiy boshqaruv paneli, rolga asoslangan integratsiya bilan."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Interfeys elementlarini yaratadi."""
        main_frame = b.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        # Foydalanuvchi ma'lumotlari bo'limi
        user_info_frame = b.LabelFrame(main_frame, text="Foydalanuvchi ma'lumotlari", padding=15, bootstyle=INFO)
        user_info_frame.pack(fill=X, pady=10)

        user = self.controller.current_user or {"full_name": "Noma'lum", "role": "Noma'lum", "phone": "Noma'lum"}
        b.Label(user_info_frame, text=f"Ism: {user['full_name']}", font=("Helvetica", 12)).pack(anchor=W, padx=10, pady=5)
        b.Label(user_info_frame, text=f"Rol: {user['role']}", font=("Helvetica", 12)).pack(anchor=W, padx=10, pady=5)
        b.Label(user_info_frame, text=f"Telefon: {user['phone']}", font=("Helvetica", 12)).pack(anchor=W, padx=10, pady=5)

        # Statistik bo'lim
        stats_frame = b.LabelFrame(main_frame, text="Tizim statistikasi", padding=15, bootstyle=SUCCESS)
        stats_frame.pack(fill=X, pady=10)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM cash_entries")
            cash_entries_count = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM invoices")
            invoices_count = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM customers")
            customers_count = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM products")
            products_count = cursor.fetchone()['count']
            conn.close()
            b.Label(stats_frame, text=f"Kassa yozuvlari: {cash_entries_count}", font=("Helvetica", 11)).pack(anchor=W, padx=10, pady=3)
            b.Label(stats_frame, text=f"Invoyslar: {invoices_count}", font=("Helvetica", 11)).pack(anchor=W, padx=10, pady=3)
            b.Label(stats_frame, text=f"Mijozlar: {customers_count}", font=("Helvetica", 11)).pack(anchor=W, padx=10, pady=3)
            b.Label(stats_frame, text=f"Mahsulotlar: {products_count}", font=("Helvetica", 11)).pack(anchor=W, padx=10, pady=3)
        except Exception as e:
            print(f"Xato: Statistikani olishda xato: {str(e)}")
            b.Label(stats_frame, text="Statistika yuklanmadi", font=("Helvetica", 11), bootstyle=WARNING).pack(anchor=W, padx=10, pady=3)

        # Navigatsiya bo'limi (rolga asoslangan)
        nav_frame = b.LabelFrame(main_frame, text="Navigatsiya", padding=15, bootstyle=PRIMARY)
        nav_frame.pack(fill=BOTH, expand=YES, pady=10)

        role = user['role']
        if role == "OWNER":
            # OWNER uchun hamma panellarga ruxsat
            b.Button(nav_frame, text="Admin paneli (AdminPanelView)", command=lambda: self.controller.show_frame("AdminPanelView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Buxgalteriya paneli (AccountantView)", command=lambda: self.controller.show_frame("AccountantView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Taqqoslash paneli (ReconciliationView)", command=lambda: self.controller.show_frame("ReconciliationView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Invoyslar paneli (InvoicesView)", command=lambda: self.controller.show_frame("InvoicesView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Hisobotlar paneli (ReportsView)", command=lambda: self.controller.show_frame("ReportsView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="CRM paneli (CRMView)", command=lambda: self.controller.show_frame("CRMView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Xodim hisobotlari paneli (WorkerReportView)", command=lambda: self.controller.show_frame("WorkerReportView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Mahsulotlar paneli (ProductsView)", command=lambda: self.controller.show_frame("ProductsView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
        elif role == "ACCOUNTANT":
            # ACCOUNTANT uchun buxgalteriya va invoyslar
            b.Button(nav_frame, text="Buxgalteriya paneli (AccountantView)", command=lambda: self.controller.show_frame("AccountantView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Taqqoslash paneli (ReconciliationView)", command=lambda: self.controller.show_frame("ReconciliationView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Invoyslar paneli (InvoicesView)", command=lambda: self.controller.show_frame("InvoicesView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Hisobotlar paneli (ReportsView)", command=lambda: self.controller.show_frame("ReportsView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
        elif role == "MANAGER":
            # MANAGER uchun CRM, mahsulotlar, xodim hisobotlari
            b.Button(nav_frame, text="CRM paneli (CRMView)", command=lambda: self.controller.show_frame("CRMView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Mahsulotlar paneli (ProductsView)", command=lambda: self.controller.show_frame("ProductsView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Xodim hisobotlari paneli (WorkerReportView)", command=lambda: self.controller.show_frame("WorkerReportView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Hisobotlar paneli (ReportsView)", command=lambda: self.controller.show_frame("ReportsView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
        elif role == "MARKETING":
            # MARKETING uchun CRM va hisobotlar
            b.Button(nav_frame, text="CRM paneli (CRMView)", command=lambda: self.controller.show_frame("CRMView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
            b.Button(nav_frame, text="Hisobotlar paneli (ReportsView)", command=lambda: self.controller.show_frame("ReportsView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
        elif role == "WORKER":
            # WORKER uchun xodim hisobotlari
            b.Button(nav_frame, text="Xodim hisobotlari paneli (WorkerReportView)", command=lambda: self.controller.show_frame("WorkerReportView"), bootstyle=PRIMARY, width=30).pack(fill=X, pady=5)
        else:
            b.Label(nav_frame, text="Ruxsat etilgan panellar mavjud emas.", font=("Helvetica", 11), bootstyle=WARNING).pack(fill=X, pady=5)

        # Chiqish tugmasi
        b.Button(nav_frame, text="Tizimdan chiqish", command=self.logout, bootstyle=DANGER, width=30).pack(fill=X, pady=10)

    def logout(self):
        """Tizimdan chiqish."""
        try:
            self.controller.current_user = None
            self.controller.show_frame("LoginView")
            login_frame = self.controller.frames.get("LoginView")
            if login_frame:
                login_frame.clear_form()
            messagebox.showinfo("Chiqish", "Tizimdan muvaffaqiyatli chiqildi!", parent=self)
        except Exception as e:
            print(f"Xato: Tizimdan chiqishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Tizimdan chiqishda xato: {str(e)}", parent=self)

    def refresh(self, **kwargs):
        """Freymni yangilaydi."""
        try:
            self.destroy()
            self.__init__(self.master, self.controller)
        except Exception as e:
            print(f"Xato: Dashboardni yangilashda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Dashboardni yangilashda xato: {str(e)}", parent=self)
