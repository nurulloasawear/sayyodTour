import customtkinter as ctk
from tkinter import messagebox
import os

# UI sahifalar importi
from ui.login_view import LoginView as LoginPage
from ui.user_create_view import UserCreateView  as SignUpPage
from ui.dashboard_view import DashboardView as DashboardPage
from ui.invoices_view import InvoicesView as InvoicesPage
from ui.reconciliation_view import ReconciliationView as ReconciliationPage
from ui.admin_panel_view import AdminPanelView as AdminPanelPage
from ui.accountant_view import AccountantView as AccountantPage
from ui.settings_view import SettingsView as SettingsPage


class MainApp(ctk.CTk):
    """Sayyod Tour CRM — CustomTkinter asosidagi bosh oynasi"""

    def __init__(self):
        super().__init__()
        self.title("Sayyod Tour CRM")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")

        # --- Dastur holatlari ---
        self.current_user = None
        self.frames = {}
        self.sidebar = None

        # --- Boshlang‘ich sahifani ochish ---
        self.show_auth_page()

    # -------------------------
    # 🔹 Kirish/ro‘yxatdan o‘tish oynasi
    # -------------------------
    def show_auth_page(self):
        """Login yoki SignUp oynasini ko‘rsatadi"""
        if self.sidebar:
            self.sidebar.destroy()

        self.auth_frame = ctk.CTkFrame(self, fg_color="#1E1E1E")
        self.auth_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.auth_frame,
            text="Sayyod Tour CRM tizimiga xush kelibsiz 👋",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=40)

        ctk.CTkButton(
            self.auth_frame,
            text="🔐 Kirish (Login)",
            width=200,
            height=50,
            fg_color="#3498db",
            command=self.open_login_page,
        ).pack(pady=10)

        ctk.CTkButton(
            self.auth_frame,
            text="🧾 Ro‘yxatdan o‘tish (Sign Up)",
            width=200,
            height=50,
            fg_color="#2ecc71",
            command=self.open_signup_page,
        ).pack(pady=10)

    def open_login_page(self):
        """Login sahifasiga o‘tish"""
        self.auth_frame.destroy()
        LoginPage(self, self.on_login_success)

    def open_signup_page(self):
        """SignUp sahifasiga o‘tish"""
        self.auth_frame.destroy()
        SignUpPage(self, self.on_signup_success)

    def on_login_success(self, user_data):
        """Login muvaffaqiyatli bo‘lganda"""
        self.current_user = user_data
        self.show_main_interface()

    def on_signup_success(self, user_data):
        """Ro‘yxatdan o‘tishdan so‘ng login sahifasiga qaytish"""
        messagebox.showinfo("Muvaffaqiyatli", "Foydalanuvchi yaratildi, endi tizimga kiring.")
        self.show_auth_page()

    # -------------------------
    # 🔹 Asosiy dastur interfeysi
    # -------------------------
    def show_main_interface(self):
        """Login muvaffaqiyatli bo‘lganda asosiy sahifani ochish"""
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar (navigatsiya)
        self.sidebar = ctk.CTkFrame(self, fg_color="#1E1E1E", width=230)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Foydalanuvchi ismi
        ctk.CTkLabel(
            self.sidebar,
            text=f"👤 {self.current_user.get('username', 'Foydalanuvchi')}",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=20)

        # Tugmalar
        self.create_nav_button("🏠 Dashboard", self.show_dashboard, 1)
        self.create_nav_button("📄 Invoices", self.show_invoices, 2)
        self.create_nav_button("📊 Reconciliation", self.show_reconciliation, 3)
        self.create_nav_button("🛠 Admin Panel", self.show_admin_panel, 4)
        self.create_nav_button("💰 Accountant", self.show_accountant, 5)
        self.create_nav_button("⚙️ Settings", self.show_settings, 6)

        ctk.CTkButton(
            self.sidebar, text="🚪 Chiqish", fg_color="#e74c3c", command=self.logout
        ).grid(row=9, column=0, padx=20, pady=30, sticky="s")

        # Kontent maydoni
        self.content_frame = ctk.CTkFrame(self, fg_color="#2C2C2C")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Dastlab Dashboard ochiladi
        self.show_dashboard()

    # -------------------------
    # 🔹 Navigatsion tugmalar
    # -------------------------
    def create_nav_button(self, text, command, row):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            fg_color="transparent",
            hover_color="#2E86C1",
            text_color="#ECF0F1",
            anchor="w",
            command=command,
        )
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")

    def clear_content(self):
        """Hozirgi sahifani tozalaydi"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # -------------------------
    # 🔹 Sahifalar
    # -------------------------
    def show_dashboard(self):
        self.clear_content()
        DashboardPage(self.content_frame)

    def show_invoices(self):
        self.clear_content()
        InvoicesPage(self.content_frame)

    def show_reconciliation(self):
        self.clear_content()
        ReconciliationPage(self.content_frame)

    def show_admin_panel(self):
        self.clear_content()
        AdminPanelPage(self.content_frame)

    def show_accountant(self):
        self.clear_content()
        AccountantPage(self.content_frame)

    def show_settings(self):
        self.clear_content()
        SettingsPage(self.content_frame)

    def logout(self):
        """Tizimdan chiqish"""
        confirm = messagebox.askyesno("Chiqish", "Tizimdan chiqmoqchimisiz?")
        if confirm:
            self.current_user = None
            self.show_auth_page()


# -------------------------
# 🔹 Asosiy ishga tushirish
# -------------------------
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
