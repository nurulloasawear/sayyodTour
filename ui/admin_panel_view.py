import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database
import settings_manager

class AdminPanelView(b.Frame):
    """Admin paneli uchun interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Asosiy vidjetlarni yaratadi."""
        notebook = b.Notebook(self, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.security_frame = b.Frame(notebook)
        self.users_frame = b.Frame(notebook)
        notebook.add(self.security_frame, text="Xavfsizlik")
        notebook.add(self.users_frame, text="Foydalanuvchilar")

        self.create_security_widgets()
        self.create_users_widgets()
        self.refresh_data()

    def create_security_widgets(self):
        """Xavfsizlik sozlamalari uchun vidjetlarni yaratadi."""
        settings_frame = b.LabelFrame(self.security_frame, text="Umumiy sozlamalar", padding=15, bootstyle=INFO)
        settings_frame.pack(fill=X, padx=10, pady=10)

        ip_filter_var = tk.BooleanVar(value=database.get_setting("ip_filtering_enabled", "false") == "true")
        b.Checkbutton(settings_frame, text="IP filtratsiyasini yoqish", variable=ip_filter_var, command=lambda: self.update_ip_filter(ip_filter_var.get())).pack(anchor=W, pady=5)

        telegram_frame = b.LabelFrame(self.security_frame, text="Telegram Bot", padding=15, bootstyle=INFO)
        telegram_frame.pack(fill=X, padx=10, pady=10)
        b.Button(telegram_frame, text="Test xabarini yuborish", command=self.send_test_telegram, bootstyle=PRIMARY).pack(anchor=W)

        ip_frame = b.LabelFrame(self.security_frame, text="IP ruxsatnomasi", padding=10, bootstyle=SUCCESS)
        ip_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        add_frame = b.Frame(ip_frame)
        add_frame.pack(fill=X, pady=5)
        self.new_ip_var = tk.StringVar()
        
        # Placeholder effektini yaratish
        def on_entry_focus_in(event):
            if self.new_ip_var.get() == "Yangi IP manzil (masalan, 192.168.1.1)":
                self.new_ip_var.set("")
                ip_entry.configure(foreground='black')
        
        def on_entry_focus_out(event):
            if not self.new_ip_var.get():
                self.new_ip_var.set("Yangi IP manzil (masalan, 192.168.1.1)")
                ip_entry.configure(foreground='grey')
        
        ip_entry = b.Entry(add_frame, textvariable=self.new_ip_var)
        ip_entry.pack(side=LEFT, expand=YES, fill=X, padx=(0, 5))
        self.new_ip_var.set("Yangi IP manzil (masalan, 192.168.1.1)")
        ip_entry.configure(foreground='grey')
        ip_entry.bind("<FocusIn>", on_entry_focus_in)
        ip_entry.bind("<FocusOut>", on_entry_focus_out)
        
        b.Button(add_frame, text="IP qo'shish", command=self.add_ip, bootstyle=PRIMARY).pack(side=LEFT)

        columns = ("ip_address",)
        self.ip_tree = b.Treeview(ip_frame, columns=columns, show="headings", bootstyle=DARK)
        self.ip_tree.heading("ip_address", text="IP manzil")
        self.ip_tree.pack(fill=BOTH, expand=YES)
        b.Button(ip_frame, text="Tanlangan IPni o'chirish", command=self.delete_selected_ip, bootstyle=DANGER).pack(anchor=W, pady=5)

    def create_users_widgets(self):
        """Foydalanuvchilar sozlamalari uchun vidjetlarni yaratadi."""
        add_user_frame = b.LabelFrame(self.users_frame, text="Yangi foydalanuvchi qo'shish", padding=15, bootstyle=INFO)
        add_user_frame.pack(fill=X, padx=10, pady=10)

        b.Label(add_user_frame, text="Ism:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.full_name_var = tk.StringVar()
        b.Entry(add_user_frame, textvariable=self.full_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=EW)

        b.Label(add_user_frame, text="Telefon:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.phone_var = tk.StringVar()
        b.Entry(add_user_frame, textvariable=self.phone_var).grid(row=1, column=1, padx=5, pady=5, sticky=EW)

        b.Label(add_user_frame, text="Login:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.login_var = tk.StringVar()
        b.Entry(add_user_frame, textvariable=self.login_var).grid(row=2, column=1, padx=5, pady=5, sticky=EW)

        b.Label(add_user_frame, text="Parol:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.password_var = tk.StringVar()
        b.Entry(add_user_frame, textvariable=self.password_var, show="*").grid(row=3, column=1, padx=5, pady=5, sticky=EW)

        b.Label(add_user_frame, text="Rol:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.role_var = tk.StringVar(value="WORKER")
        roles = ["OWNER", "MANAGER", "MARKETING", "ACCOUNTANT", "WORKER"]
        b.Combobox(add_user_frame, textvariable=self.role_var, values=roles, state="readonly").grid(row=4, column=1, padx=5, pady=5, sticky=EW)

        b.Button(add_user_frame, text="Foydalanuvchi qo'shish", command=self.add_user, bootstyle=PRIMARY).grid(row=5, column=0, columnspan=2, pady=10)

        users_frame = b.LabelFrame(self.users_frame, text="Foydalanuvchilar ro'yxati", padding=10, bootstyle=SUCCESS)
        users_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        columns = ("id", "full_name", "phone", "login", "role", "status")
        self.user_tree = b.Treeview(users_frame, columns=columns, show="headings", bootstyle=DARK)
        self.user_tree.heading("id", text="ID")
        self.user_tree.heading("full_name", text="Ism")
        self.user_tree.heading("phone", text="Telefon")
        self.user_tree.heading("login", text="Login")
        self.user_tree.heading("role", text="Rol")
        self.user_tree.heading("status", text="Holati")
        self.user_tree.column("id", width=50)
        self.user_tree.pack(fill=BOTH, expand=YES)

    def update_ip_filter(self, enabled):
        """IP filtratsiyasini yoqadi yoki o'chiradi."""
        try:
            database.update_setting("ip_filtering_enabled", "true" if enabled else "false")
            messagebox.showinfo("Muvaffaqiyat", f"IP filtratsiyasi {"yoqildi" if enabled else "ochirild"}.")
        except Exception as e:
            messagebox.showerror("Xatolik", f"IP filtratsiyasini yangilashda xato: {str(e)}")

    def send_test_telegram(self):
        """Telegram test xabarini yuboradi."""
        try:
            settings_manager.load_settings()
            messagebox.showinfo("Muvaffaqiyat", "Test xabari Telegramga yuborildi.")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Telegram xabarini yuborishda xato: {str(e)}")

    def add_ip(self):
        """Yangi IP manzilni qo'shadi."""
        ip = self.new_ip_var.get()
        if ip and ip != "Yangi IP manzil (masalan, 192.168.1.1)":
            try:
                database.add_ip_to_whitelist(ip)
                self.new_ip_var.set("")
                self.refresh_ip_list()
                messagebox.showinfo("Muvaffaqiyat", f"IP manzil '{ip}' qo'shildi.")
            except Exception as e:
                messagebox.showerror("Xatolik", f"IP qo'shishda xato: {str(e)}")
        else:
            messagebox.showwarning("Xato", "Iltimos, to'g'ri IP manzil kiriting.")

    def delete_selected_ip(self):
        """Tanlangan IP manzilni o'chiradi."""
        selected = self.ip_tree.selection()
        if selected:
            ip = self.ip_tree.item(selected[0])['values'][0]
            try:
                database.delete_ip_from_whitelist(ip)
                self.refresh_ip_list()
                messagebox.showinfo("Muvaffaqiyat", f"IP manzil '{ip}' o'chirildi.")
            except Exception as e:
                messagebox.showerror("Xatolik", f"IP o'chirishda xato: {str(e)}")
        else:
            messagebox.showwarning("Xato", "Iltimos, o'chirish uchun IP manzilni tanlang.")

    def add_user(self):
        """Yangi foydalanuvchi qo'shadi."""
        data = {
            "full_name": self.full_name_var.get(),
            "phone": self.phone_var.get(),
            "login": self.login_var.get(),
            "password": self.password_var.get(),
            "role": self.role_var.get()
        }
        if not all([data['full_name'], data['login'], data['password']]):
            messagebox.showwarning("Xato", "Iltimos, barcha maydonlarni to'ldiring.")
            return
        try:
            database.add_user(data)
            self.full_name_var.set("")
            self.phone_var.set("")
            self.login_var.set("")
            self.password_var.set("")
            self.role_var.set("WORKER")
            self.refresh_users()
            messagebox.showinfo("Muvaffaqiyat", "Foydalanuvchi muvaffaqiyatli qo'shildi.")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Foydalanuvchi qo'shishda xato: {str(e)}")

    def refresh_data(self):
        """Ma'lumotlarni yangilaydi."""
        self.refresh_ip_list()
        self.refresh_users()

    def refresh_ip_list(self):
        """IP ruxsatnomasi ro'yxatini yangilaydi."""
        try:
            for item in self.ip_tree.get_children():
                self.ip_tree.delete(item)
            ip_list = database.get_ip_whitelist()
            for ip in ip_list:
                self.ip_tree.insert("", tk.END, values=(ip,))
        except Exception as e:
            messagebox.showerror("Xatolik", f"IP ro'yxatini yangilashda xato: {str(e)}")

    def refresh_users(self):
        """Foydalanuvchilar ro'yxatini yangilaydi."""
        try:
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            users = database.get_all_users()
            for user in users:
                self.user_tree.insert("", tk.END, values=(
                    user['id'],
                    user['full_name'],
                    user['phone'],
                    user['login'],
                    user['role'],
                    user['status']
                ))
        except Exception as e:
            messagebox.showerror("Xatolik", f"Foydalanuvchilar ro'yxatini yangilashda xato: {str(e)}")