import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database

class UserCreateView(b.Frame):
    """Yangi foydalanuvchi yaratish sahifasi uchun interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Forma elementlarini yaratadi."""
        form_frame = b.LabelFrame(self, text="Yangi foydalanuvchi yaratish", padding=20, bootstyle=INFO)
        form_frame.pack(fill=BOTH, padx=100, pady=100, expand=YES)

        # To'liq ism
        b.Label(form_frame, text="To'liq ism:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.full_name_entry = b.Entry(form_frame)
        self.full_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        self.full_name_entry.focus()

        # Telefon
        b.Label(form_frame, text="Telefon:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.phone_entry = b.Entry(form_frame)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky=EW)

        # Login
        b.Label(form_frame, text="Login:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.login_entry = b.Entry(form_frame)
        self.login_entry.grid(row=2, column=1, padx=5, pady=5, sticky=EW)

        # Parol
        b.Label(form_frame, text="Parol:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.password_entry = b.Entry(form_frame, show="*")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5, sticky=EW)
        self.password_entry.bind("<Return>", lambda event: self.save_user())

        # Rol
        b.Label(form_frame, text="Rol:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.role_combobox = b.Combobox(form_frame, values=["OWNER", "MANAGER", "MARKETING", "ACCOUNTANT", "WORKER"], state="readonly")
        self.role_combobox.grid(row=4, column=1, padx=5, pady=5, sticky=EW)
        self.role_combobox.current(0)  # Birinchi rolni tanlash

        # Tugmalar ramkasi
        button_frame = b.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        # Saqlash tugmasi
        b.Button(button_frame, text="Saqlash", command=self.save_user, bootstyle=PRIMARY).pack(side=LEFT, padx=5)

        # Orqaga tugmasi
        self.back_button = b.Button(button_frame, text="Orqaga", command=lambda: self.controller.show_frame("LoginView"), bootstyle=SECONDARY)
        self.back_button.pack(side=LEFT, padx=5)

        # Forma maydonlarini kengaytirish uchun sozlash
        form_frame.columnconfigure(1, weight=1)

    def save_user(self):
        """Foydalanuvchi ma'lumotlarini saqlaydi."""
        full_name = self.full_name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_combobox.get()

        # Validatsiya
        if not full_name or not login or not password or not role:
            messagebox.showerror("Xatolik", "Barcha maydonlarni to'ldiring!", parent=self)
            return

        try:
            user_data = {
                "full_name": full_name,
                "phone": phone,
                "login": login,
                "password": password,
                "role": role
            }
            database.add_user(user_data)
            messagebox.showinfo("Muvaffaqiyat", f"Foydalanuvchi '{login}' muvaffaqiyatli qo'shildi!", parent=self)
            self.clear_form()
            self.controller.show_frame("LoginView")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Foydalanuvchi qo'shishda xato: {str(e)}", parent=self)

    def clear_form(self):
        """Formani tozalaydi."""
        self.full_name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.login_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_combobox.current(0)
        self.full_name_entry.focus()

    def show_back_button(self, show=True):
        """Orqaga tugmasini ko'rsatadi yoki yashiradi."""
        if show:
            self.back_button.pack(side=LEFT, padx=5)
        else:
            self.back_button.pack_forget()