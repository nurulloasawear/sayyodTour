import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from ttkbootstrap import DateEntry, ScrolledText
from datetime import datetime
from tkinter import messagebox, filedialog
import database

class WorkerReportView(b.Frame):
    """Xodimning kunlik hisobotlari va vazifalari uchun to'liq dinamik interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        notebook = b.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        self.report_tab = b.Frame(notebook)
        self.tasks_tab = b.Frame(notebook)
        
        notebook.add(self.report_tab, text="📝 Kunlik Hisobot")
        notebook.add(self.tasks_tab, text="📌 Mening Vazifalarim")

        self.create_report_widgets()
        self.create_tasks_widgets()

        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_data())

    def get_current_user(self):
        """Controllerdan joriy foydalanuvchi ma'lumotlarini oladi."""
        return self.controller.current_user if hasattr(self.controller, 'current_user') and self.controller.current_user else None

    def refresh_data(self):
        """Panelga kerakli barcha dinamik ma'lumotlarni bazadan yangilaydi."""
        print("Xodim panelining ma'lumotlari yangilanmoqda...")
        user = self.get_current_user()
        if not user:
            messagebox.showerror("Xatolik", "Joriy foydalanuvchi aniqlanmadi. Qaytadan tizimga kiring.")
            return
        
        user_id = user.get('id')
        try:
            self.refresh_report_history(user_id)
            self.refresh_tasks_treeview(user_id)
        except Exception as e:
            messagebox.showerror("Xato", f"Ma'lumotlarni yangilashda xato: {str(e)}")

    # --- 1. Kunlik Hisobot Vkladkasi ---
    def create_report_widgets(self):
        frame = self.report_tab
        
        form_frame = b.LabelFrame(frame, text="Yangi hisobot ma'lumotlari", padding=15, bootstyle=PRIMARY)
        form_frame.pack(fill=X, padx=10, pady=10)
        form_frame.columnconfigure((1, 3), weight=1)

        self.calls_var = tk.IntVar(value=0)
        self.meetings_var = tk.IntVar(value=0)
        self.sales_count_var = tk.IntVar(value=0)
        self.sales_amount_var = tk.DoubleVar(value=0.0)
        self.expense_amount_var = tk.DoubleVar(value=0.0)
        self.expense_note_var = tk.StringVar()
        self.expense_file_var = tk.StringVar()

        b.Label(form_frame, text="Hisobot sanasi:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.report_date_entry = DateEntry(form_frame, dateformat='%Y-%m-%d', width=12)
        self.report_date_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.report_date_entry.set_date(datetime.now())
        
        b.Label(form_frame, text="Qo'ng'iroqlar soni:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        b.Entry(form_frame, textvariable=self.calls_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        b.Label(form_frame, text="Uchrashuvlar soni:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        b.Entry(form_frame, textvariable=self.meetings_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        b.Label(form_frame, text="Sotuvlar soni (dona):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        b.Entry(form_frame, textvariable=self.sales_count_var).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        b.Label(form_frame, text="Jami sotuv summasi (UZS):").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        b.Entry(form_frame, textvariable=self.sales_amount_var).grid(row=2, column=3, sticky="ew", padx=5, pady=5)

        expense_frame = b.LabelFrame(form_frame, text="Kunlik Xarajatlar", padding=10, bootstyle=SECONDARY)
        expense_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        expense_frame.columnconfigure(1, weight=1)

        b.Label(expense_frame, text="Xarajat summasi:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        b.Entry(expense_frame, textvariable=self.expense_amount_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        b.Label(expense_frame, text="Izohi:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        b.Entry(expense_frame, textvariable=self.expense_note_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        b.Button(expense_frame, text="Chek/Foto yuklash...", command=self.select_expense_file, bootstyle=OUTLINE + SECONDARY).grid(row=2, column=0, padx=5, pady=5)
        b.Label(expense_frame, textvariable=self.expense_file_var, bootstyle=INFO).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        b.Button(form_frame, text="Hisobotni Saqlash", command=self.save_report, bootstyle=SUCCESS).grid(row=4, column=3, sticky="e", pady=10)

        history_frame = b.LabelFrame(frame, text="Mening oxirgi 10 ta hisobotim", padding=10, bootstyle=INFO)
        history_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        columns = ("id", "sana", "qongiroqlar", "uchrashuvlar", "sotuvlar_soni", "sotuvlar_summa", "xarajat_summa", "xarajat_izoh")
        self.history_tree = b.Treeview(history_frame, columns=columns, show="headings", height=8, bootstyle=DARK)
        self.history_tree.heading("id", text="ID")
        self.history_tree.heading("sana", text="Sana")
        self.history_tree.heading("qongiroqlar", text="Qo'ng'iroqlar")
        self.history_tree.heading("uchrashuvlar", text="Uchrashuvlar")
        self.history_tree.heading("sotuvlar_soni", text="Sotuvlar Soni")
        self.history_tree.heading("sotuvlar_summa", text="Sotuvlar Summasi (UZS)")
        self.history_tree.heading("xarajat_summa", text="Xarajat Summasi (UZS)")
        self.history_tree.heading("xarajat_izoh", text="Xarajat Izohi")
        self.history_tree.column("id", width=50, anchor="center")
        self.history_tree.column("sana", width=100, anchor="center")
        self.history_tree.column("qongiroqlar", width=100, anchor="center")
        self.history_tree.column("uchrashuvlar", width=100, anchor="center")
        self.history_tree.column("sotuvlar_soni", width=100, anchor="center")
        self.history_tree.column("sotuvlar_summa", width=150, anchor="e")
        self.history_tree.column("xarajat_summa", width=150, anchor="e")
        self.history_tree.column("xarajat_izoh", width=200)
        self.history_tree.pack(fill=BOTH, expand=YES)

    def select_expense_file(self):
        """Fayl tanlash oynasini ochadi."""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("Rasm fayllari", "*.png *.jpg *.jpeg"), ("Barcha fayllar", "*.*")]
            )
            if filepath:
                self.expense_file_var.set(filepath)
        except Exception as e:
            messagebox.showerror("Xato", f"Fayl tanlashda xato: {str(e)}")

    def save_report(self):
        """Hisobotni bazaga saqlaydi."""
        user = self.get_current_user()
        if not user:
            messagebox.showerror("Xatolik", "Foydalanuvchi aniqlanmadi. Qaytadan tizimga kiring.")
            return
        try:
            report_data = {
                "user_id": user.get('id'),
                "report_date": self.report_date_entry.get(),
                "calls": self.calls_var.get(),
                "meetings": self.meetings_var.get(),
                "sales_count": self.sales_count_var.get(),
                "sales_amount": self.sales_amount_var.get(),
                "expense_amount": self.expense_amount_var.get(),
                "expense_note": self.expense_note_var.get(),
                "expense_file": self.expense_file_var.get() or None
            }
            database.add_daily_report(report_data)
            messagebox.showinfo("Muvaffaqiyatli", "Kunlik hisobot saqlandi!")
            self.refresh_report_history(user.get('id'))
            for var in [self.calls_var, self.meetings_var, self.sales_count_var]:
                var.set(0)
            for var in [self.sales_amount_var, self.expense_amount_var]:
                var.set(0.0)
            for var in [self.expense_note_var, self.expense_file_var]:
                var.set("")
        except tk.TclError:
            messagebox.showerror("Xatolik", "Iltimos, sonli maydonlarga faqat raqam kiriting!")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Hisobotni saqlashda xato: {str(e)}")

    def refresh_report_history(self, user_id):
        """Oxirgi 10 ta hisobotni yangilaydi."""
        try:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            reports = database.get_reports_for_user(user_id, limit=10)
            for report in reports:
                self.history_tree.insert("", END, values=(
                    report['id'],
                    report['report_date'],
                    report['calls'],
                    report['meetings'],
                    report['sales_count'],
                    f"{report['sales_amount']:,.2f}",
                    f"{report['expense_amount']:,.2f}",
                    report['expense_note'] or ""
                ))
        except Exception as e:
            messagebox.showerror("Xato", f"Hisobotlarni yangilashda xato: {str(e)}")

    # --- 2. Mening Vazifalarim (Leadlar) Vkladkasi ---
    def create_tasks_widgets(self):
        frame = self.tasks_tab
        top_frame = b.Frame(frame)
        top_frame.pack(fill='x', padx=10, pady=10)
        b.Label(top_frame, text="Menga biriktirilgan aktiv leadlar", font=("", 12, "bold")).pack(side=LEFT)
        b.Button(top_frame, text="🔄 Ro'yxatni yangilash", command=self.refresh_data, bootstyle=OUTLINE + SECONDARY).pack(side=RIGHT)

        tree_frame = b.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        columns = ("id", "ism", "telefon", "holati", "qayta_aloqa_sana", "izoh")
        self.tasks_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        self.tasks_tree.heading("id", text="ID")
        self.tasks_tree.heading("ism", text="Ism")
        self.tasks_tree.heading("telefon", text="Telefon")
        self.tasks_tree.heading("holati", text="Holati")
        self.tasks_tree.heading("qayta_aloqa_sana", text="Qayta Aloqa Sanasi")
        self.tasks_tree.heading("izoh", text="Izoh")
        self.tasks_tree.column("id", width=50, anchor="center")
        self.tasks_tree.column("ism", width=150)
        self.tasks_tree.column("telefon", width=120)
        self.tasks_tree.column("holati", width=120, anchor="center")
        self.tasks_tree.column("qayta_aloqa_sana", width=120, anchor="center")
        self.tasks_tree.column("izoh", width=200)
        self.tasks_tree.pack(fill=BOTH, expand=YES)
        
        action_frame = b.Frame(frame)
        action_frame.pack(fill='x', padx=10, pady=5)
        b.Button(action_frame, text="Izoh qo'shish / Ko'rish...", command=self.manage_lead_notes, bootstyle=SECONDARY).pack(side=RIGHT)
        b.Button(action_frame, text="Holatini o'zgartirish...", command=self.change_lead_status, bootstyle=INFO).pack(side=RIGHT, padx=10)

    def refresh_tasks_treeview(self, user_id):
        """Leadlar jadvalini yangilaydi."""
        try:
            for item in self.tasks_tree.get_children():
                self.tasks_tree.delete(item)
            leads = database.get_leads_for_user(user_id)
            for lead in leads:
                self.tasks_tree.insert("", END, values=(
                    lead['id'],
                    lead['full_name'],
                    lead['phone'],
                    lead['status'],
                    lead['next_contact_date'] or "",
                    lead['notes'] or ""
                ))
        except Exception as e:
            messagebox.showerror("Xato", f"Leadlarni yangilashda xato: {str(e)}")

    def get_selected_lead_id(self):
        """Tanlangan leadning ID'sini qaytaradi."""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Ogohlantirish", "Avval ro'yxatdan leadni tanlang!")
            return None
        return self.tasks_tree.item(selected[0])['values'][0]

    def change_lead_status(self):
        """Lead holatini o'zgartirish oynasini ochadi."""
        lead_id = self.get_selected_lead_id()
        if not lead_id:
            return
        LeadStatusEditorWindow(self, self.controller, lead_id, self.refresh_data)

    def manage_lead_notes(self):
        """Lead izohlarini boshqarish oynasini ochadi."""
        lead_id = self.get_selected_lead_id()
        if not lead_id:
            return
        LeadNoteEditorWindow(self, self.controller, lead_id)

class LeadStatusEditorWindow(tk.Toplevel):
    """Lead holatini o'zgartirish uchun oyna."""

    def __init__(self, parent, controller, lead_id, callback):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.lead_id = lead_id
        self.callback = callback

        self.title(f"ID={lead_id} Lead holatini o'zgartirish")
        self.geometry("350x200")
        
        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)

        b.Label(container, text="Yangi holatni tanlang:").pack(padx=10, pady=(0,5), anchor='w')
        self.status_var = tk.StringVar()
        status_combo = b.Combobox(
            container,
            textvariable=self.status_var,
            state="readonly",
            values=["Jarayonda", "Uchrashuv belgilandi", "Muvaffaqiyatli", "Muvaffaqiyatsiz", "Qayta aloqa kerak"]
        )
        status_combo.pack(padx=10, fill='x')

        b.Button(container, text="Saqlash", command=self.save_status, bootstyle=SUCCESS).pack(pady=20)
        self.grab_set()

    def save_status(self):
        """Yangi holatni saqlaydi."""
        new_status = self.status_var.get()
        user = self.parent.get_current_user()
        if not user:
            messagebox.showerror("Xatolik", "Foydalanuvchi aniqlanmadi.", parent=self)
            return
        if not new_status:
            messagebox.showwarning("Ogohlantirish", "Holat tanlanmadi!", parent=self)
            return
        try:
            database.update_lead_status(self.lead_id, new_status, user.get('id'))
            messagebox.showinfo("Muvaffaqiyatli", "Lead holati yangilandi.", parent=self)
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Xato", f"Holatni yangilashda xato: {str(e)}", parent=self)

class LeadNoteEditorWindow(tk.Toplevel):
    """Lead izohlarini boshqarish uchun oyna."""

    def __init__(self, parent, controller, lead_id):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.lead_id = lead_id

        self.title(f"ID={lead_id} Lead uchun izohlar")
        self.geometry("450x400")

        container = b.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=YES)
        
        history_frame = b.LabelFrame(container, text="Mavjud izohlar", bootstyle=INFO, padding=5)
        history_frame.pack(padx=10, pady=5, fill=BOTH, expand=YES)
        
        self.history_text = ScrolledText(history_frame, height=10, autohide=True)
        self.history_text.pack(fill=BOTH, expand=YES)
        self.history_text.config(state="disabled")

        add_frame = b.LabelFrame(container, text="Yangi izoh qo'shish", bootstyle=PRIMARY, padding=5)
        add_frame.pack(padx=10, pady=10, fill=X)
        self.new_note_text = tk.Text(add_frame, height=4)
        self.new_note_text.pack(pady=5, padx=5, fill=X)
        b.Button(add_frame, text="Izohni qo'shish", command=self.add_note, bootstyle=SUCCESS).pack(pady=5, padx=5, anchor='e')
        
        self.load_notes()
        self.grab_set()

    def load_notes(self):
        """Lead izohlarini yuklaydi."""
        try:
            self.history_text.config(state="normal")
            self.history_text.delete("1.0", tk.END)
            notes = database.get_lead_notes(self.lead_id)
            if not notes:
                self.history_text.insert(tk.END, "Hozircha izohlar mavjud emas.")
            else:
                for timestamp, user_name, note_text in notes:
                    header = f"--- {user_name} ({timestamp}) ---\n"
                    self.history_text.insert(tk.END, header)
                    self.history_text.insert(tk.END, f"{note_text}\n\n")
            self.history_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Xato", f"Izohlarni yuklashda xato: {str(e)}", parent=self)

    def add_note(self):
        """Yangi izoh qo'shadi."""
        user = self.parent.get_current_user()
        if not user:
            messagebox.showerror("Xatolik", "Foydalanuvchi aniqlanmadi.", parent=self)
            return
        
        note = self.new_note_text.get("1.0", tk.END).strip()
        if not note:
            messagebox.showwarning("Ogohlantirish", "Izoh kiritilmadi!", parent=self)
            return
        
        try:
            database.add_lead_note(self.lead_id, note, user.get('id'))
            self.new_note_text.delete("1.0", tk.END)
            self.load_notes()
            messagebox.showinfo("Muvaffaqiyatli", "Yangi izoh qo'shildi.", parent=self)
        except Exception as e:
            messagebox.showerror("Xato", f"Izoh qo'shishda xato: {str(e)}", parent=self)