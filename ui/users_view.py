# ui/users_view.py

import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox

# MUHIM: Bu panel ishlashi uchun database.py da ushbu fayl oxirida ko'rsatilgan
# barcha funksiyalarni yaratgan bo'lishingiz SHART.
import database

class UsersView(b.Frame):
    """Foydalanuvchilarni boshqarish uchun to'liq dinamik interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        top_frame = b.Frame(self)
        top_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(top_frame, text="Foydalanuvchilarni Boshqarish", font=("Helvetica", 16, "bold")).pack(side=LEFT)
        b.Button(top_frame, text="➕ Yangi Foydalanuvchi...", command=self.open_user_editor, bootstyle=SUCCESS).pack(side=RIGHT)
        
        tree_frame = b.Frame(self)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        columns = ("id", "fio", "telefon", "login", "rol", "holati")
        self.users_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("fio", text="F.I.O.")
        self.users_tree.heading("telefon", text="Telefon")
        self.users_tree.heading("login", text="Login")
        self.users_tree.heading("rol", text="Rol")
        self.users_tree.heading("holati", text="Holati")
        
        self.users_tree.column("id", width=50, anchor="center")
        self.users_tree.column("fio", width=250)
        self.users_tree.column("holati", anchor="center")

        scrollbar = b.Scrollbar(tree_frame, orient=VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.users_tree.pack(fill=BOTH, expand=YES)

        action_frame = b.Frame(self)
        action_frame.pack(fill='x', padx=10, pady=5)
        b.Button(action_frame, text="O'chirish", command=self.delete_selected_user, bootstyle=DANGER).pack(side=RIGHT)
        b.Button(action_frame, text="Tahrirlash...", command=self.edit_selected_user, bootstyle=INFO).pack(side=RIGHT, padx=10)
        b.Button(action_frame, text="Parolni Tiklash...", command=self.reset_user_password, bootstyle=SECONDARY).pack(side=RIGHT)

    def refresh_data(self):
        """Panel ma'lumotlarini yangilaydi."""
        print("Foydalanuvchilar paneli ma'lumotlari yangilanmoqda...")
        for item in self.users_tree.get_children(): self.users_tree.delete(item)
        users = database.get_all_users()
        for user in users: self.users_tree.insert("", END, values=user)

    def open_user_editor(self, user_id=None):
        UserEditorWindow(self, self.controller, user_id, self.refresh_data)

    def get_selected_user_info(self):
        """Jadvaldan tanlangan foydalanuvchi ID va loginini oladi."""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Xatolik", "Amalni bajarish uchun avval foydalanuvchini tanlang.")
            return None, None
        
        selected_user_values = self.users_tree.item(selected[0])['values']
        user_id = selected_user_values[0]
        user_login = selected_user_values[3]
        return user_id, user_login

    def edit_selected_user(self):
        user_id, _ = self.get_selected_user_info()
        if user_id:
            self.open_user_editor(user_id)

    def delete_selected_user(self):
        user_id, user_login = self.get_selected_user_info()
        if not user_id: return
        
        current_user_id = self.controller.current_user.get('id')
        if user_id == current_user_id:
            messagebox.showerror("Xatolik", "Siz o'zingizni o'chira olmaysiz.")
            return

        if messagebox.askyesno("Tasdiqlash", f"'{user_login}' loginli foydalanuvchini o'chirishga ishonchingiz komilmi?"):
            database.delete_user(user_id)
            self.refresh_data()
    
    def reset_user_password(self):
        user_id, user_login = self.get_selected_user_info()
        if user_id:
            PasswordResetWindow(self, user_id, user_login)


class UserEditorWindow(tk.Toplevel):
    """Foydalanuvchilarni qo'shish va tahrirlash uchun Toplevel oyna."""
    def __init__(self, parent, controller, user_id=None, callback=None):
        super().__init__(parent)
        self.user_id = user_id
        self.callback = callback
        self.title("Yangi Foydalanuvchi" if not user_id else f"ID={user_id} Foydalanuvchini Tahrirlash")
        self.geometry("450x450")

        self.vars = {k: tk.StringVar() for k in ['full_name', 'phone', 'login', 'role']}
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        self.is_active_var = tk.BooleanVar(value=True)

        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)
        container.columnconfigure(1, weight=1)

        b.Label(container, text="F.I.O.*:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['full_name']).grid(row=0, column=1, sticky="ew")
        b.Label(container, text="Telefon:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['phone']).grid(row=1, column=1, sticky="ew")
        b.Label(container, text="Login*:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['login']).grid(row=2, column=1, sticky="ew")
        
        b.Label(container, text="Rol*:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        roles = ["OWNER", "MANAGER", "MARKETING", "ACCOUNTANT", "WORKER"]
        b.Combobox(container, textvariable=self.vars['role'], values=roles, state="readonly").grid(row=3, column=1, sticky="ew")

        # Parol maydonlari faqat yangi foydalanuvchi qo'shishda ko'rinadi
        if not self.user_id:
            b.Label(container, text="Parol*:").grid(row=4, column=0, sticky="w", padx=5, pady=8)
            b.Entry(container, textvariable=self.password_var, show="*").grid(row=4, column=1, sticky="ew")
            b.Label(container, text="Parolni tasdiqlang*:").grid(row=5, column=0, sticky="w", padx=5, pady=8)
            b.Entry(container, textvariable=self.confirm_password_var, show="*").grid(row=5, column=1, sticky="ew")
        
        b.Checkbutton(container, text="Aktiv", variable=self.is_active_var, bootstyle=SUCCESS).grid(row=6, column=1, sticky="w", pady=10)

        btn_frame = b.Frame(container)
        btn_frame.grid(row=7, column=1, sticky="e", pady=20)
        b.Button(btn_frame, text="Saqlash", command=self.save, bootstyle=SUCCESS).pack(side=LEFT)
        b.Button(btn_frame, text="Bekor qilish", command=self.destroy, bootstyle=SECONDARY).pack(side=LEFT, padx=10)
        
        if self.user_id: self.populate_form()
        self.grab_set()

    def populate_form(self):
        user_data = database.get_user_details(self.user_id)
        if user_data:
            for key in self.vars: self.vars[key].set(user_data.get(key, ''))
            self.is_active_var.set(user_data.get('is_active', True))

    def save(self):
        data = {key: var.get() for key, var in self.vars.items()}
        data['is_active'] = self.is_active_var.get()
        
        if not all([data['full_name'], data['login'], data['role']]):
            return messagebox.showerror("Xatolik", "F.I.O., Login va Rol kiritilishi shart!", parent=self)

        if self.user_id:
            database.update_user(self.user_id, data)
        else:
            password = self.password_var.get()
            confirm_password = self.confirm_password_var.get()
            if not password or password != confirm_password:
                return messagebox.showerror("Xatolik", "Parollar mos kelmadi yoki kiritilmadi!", parent=self)
            data['password'] = password
            database.add_user(data)
        
        if self.callback: self.callback()
        self.destroy()

class PasswordResetWindow(tk.Toplevel):
    """Foydalanuvchi parolini tiklash uchun oyna."""
    def __init__(self, parent, user_id, user_login):
        super().__init__(parent)
        self.user_id = user_id
        self.title(f"'{user_login}' parolini tiklash")
        self.geometry("400x200")

        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)
        
        b.Label(container, text="Yangi parol:").pack(anchor="w")
        b.Entry(container, textvariable=self.new_password_var, show="*").pack(fill=X, pady=(0,10))
        b.Label(container, text="Yangi parolni tasdiqlang:").pack(anchor="w")
        b.Entry(container, textvariable=self.confirm_password_var, show="*").pack(fill=X)

        b.Button(container, text="Parolni Yangilash", command=self.save_password, bootstyle=SUCCESS).pack(side=BOTTOM, pady=20)
        self.grab_set()

    def save_password(self):
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()

        if not new_password or new_password != confirm_password:
            return messagebox.showerror("Xatolik", "Parollar mos kelmadi yoki kiritilmadi!", parent=self)
        
        database.update_user_password(self.user_id, new_password)
        messagebox.showinfo("Muvaffaqiyatli", "Foydalanuvchi paroli muvaffaqiyatli yangilandi.", parent=self)
        self.destroy()