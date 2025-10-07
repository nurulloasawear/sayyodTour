import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database

class LoginView(b.Frame):
    """Login sahifasi uchun interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Login formasini yaratadi."""
        # Markaziy forma ramkasi
        form_frame = b.LabelFrame(self, text="Tizimga kirish", padding=20, bootstyle=INFO)
        form_frame.pack(fill=BOTH, padx=100, pady=100, expand=YES)

        # Login maydoni
        b.Label(form_frame, text="Login:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.username_entry = b.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        self.username_entry.focus()

        # Parol maydoni
        b.Label(form_frame, text="Parol:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.password_entry = b.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        self.password_entry.bind("<Return>", lambda event: self.attempt_login())

        # Kirish tugmasi
        b.Button(form_frame, text="Kirish", command=self.attempt_login, bootstyle=PRIMARY).grid(row=2, column=0, columnspan=2, pady=10, sticky=EW)

        # Yangi foydalanuvchi yaratish tugmasi
        self.create_user_button = b.Button(form_frame, text="Yangi foydalanuvchi yaratish", 
                                          command=lambda: self.controller.show_frame("UserCreateView"), 
                                          bootstyle=SECONDARY)
        self.create_user_button.grid(row=3, column=0, columnspan=2, pady=5, sticky=EW)
        self.update_create_user_button()

        # Forma maydonlarini kengaytirish uchun sozlash
        form_frame.columnconfigure(1, weight=1)

    def attempt_login(self):
        """Login jarayonini boshlaydi."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        print(f"Login attempt: username={username}, password={password}")  # Debug
        if not username or not password:
            messagebox.showerror("Xatolik", "Login va parolni kiriting!", parent=self)
            return
        try:
            user_data = self.controller.attempt_login(username, password)
            if user_data:
                self.clear_form()
        except Exception as e:
            messagebox.showerror("Xatolik", f"Login qilishda xato: {str(e)}", parent=self)

    def update_create_user_button(self):
        """Yangi foydalanuvchi tugmasini foydalanuvchilar soniga qarab yangilaydi."""
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM users")
            user_count = cursor.fetchone()['count']
            conn.close()
            if user_count > 0:
                self.create_user_button.grid()
            else:
                self.create_user_button.grid_remove()
        except Exception as e:
            print(f"Xato: Foydalanuvchilarni tekshirishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Foydalanuvchilarni tekshirishda xato: {str(e)}", parent=self)

    def clear_form(self):
        """Formani tozalaydi."""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()