import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkcalendar import DateEntry
from tkinter import messagebox
import database

class AccountantView(b.Frame):
    """Buxgalter paneli uchun interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Asosiy vidjetlarni yaratadi."""
        notebook = b.Notebook(self, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.journal_frame = b.Frame(notebook)
        notebook.add(self.journal_frame, text="Kassa Jurnali")

        self.create_journal_widgets()
        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_data())

    def create_journal_widgets(self):
        """Kassa jurnali vidjetlarini yaratadi."""
        frame = self.journal_frame  # journal_tab o'rniga journal_frame

        filter_frame = b.LabelFrame(frame, text="Filtrlar", padding=10, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)

        b.Label(filter_frame, text="Boshlanish sanasi:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.journal_start_date = b.DateEntry(filter_frame, dateformat="%Y-%m-%d")
        self.journal_start_date.grid(row=0, column=1, padx=5, pady=5, sticky=EW)

        b.Label(filter_frame, text="Tugash sanasi:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.journal_end_date = b.DateEntry(filter_frame, dateformat="%Y-%m-%d")
        self.journal_end_date.grid(row=0, column=3, padx=5, pady=5, sticky=EW)

        b.Label(filter_frame, text="Kassa:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.cashbox_var = tk.StringVar()
        cashboxes = database.get_cashboxes()
        cashbox_options = ["Barchasi"] + [name for _, name, _ in cashboxes]
        b.Combobox(filter_frame, textvariable=self.cashbox_var, values=cashbox_options, state="readonly").grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        self.cashbox_var.set("Barchasi")

        b.Label(filter_frame, text="Kategoriya:").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.category_var = tk.StringVar()
        categories = database.get_categories()
        category_options = ["Barchasi"] + [name for _, name in categories]
        b.Combobox(filter_frame, textvariable=self.category_var, values=category_options, state="readonly").grid(row=1, column=3, padx=5, pady=5, sticky=EW)
        self.category_var.set("Barchasi")

        b.Button(filter_frame, text="Filtrlash", command=self.refresh_journal_treeview, bootstyle=PRIMARY).grid(row=2, column=0, columnspan=4, pady=10)

        journal_pane = b.LabelFrame(frame, text="Kassa Yozuvlari", padding=10, bootstyle=SUCCESS)
        journal_pane.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        columns = ("id", "sana", "summa", "yo'nalish", "kassa", "kategoriya", "izoh")
        self.journal_tree = b.Treeview(journal_pane, columns=columns, show="headings", bootstyle=DARK)
        self.journal_tree.heading("id", text="ID")
        self.journal_tree.heading("sana", text="Sana")
        self.journal_tree.heading("summa", text="Summa")
        self.journal_tree.heading("yo'nalish", text="Yo'nalish")
        self.journal_tree.heading("kassa", text="Kassa")
        self.journal_tree.heading("kategoriya", text="Kategoriya")
        self.journal_tree.heading("izoh", text="Izoh")
        self.journal_tree.column("id", width=50, anchor="center")
        self.journal_tree.column("sana", width=100)
        self.journal_tree.column("summa", width=120, anchor="e")
        self.journal_tree.column("yo'nalish", width=80)
        self.journal_tree.column("kassa", width=120)
        self.journal_tree.column("kategoriya", width=120)
        self.journal_tree.column("izoh", width=200)
        self.journal_tree.pack(fill=BOTH, expand=YES)

    def refresh_data(self):
        """Ma'lumotlarni yangilaydi."""
        self.refresh_journal_treeview()

    def refresh_journal_treeview(self):
        """Jurnal yozuvlarini yangilaydi."""
        try:
            for item in self.journal_tree.get_children():
                self.journal_tree.delete(item)
            filters = {
                'start_date': self.journal_start_date.entry.get(),
                'end_date': self.journal_end_date.entry.get(),
                'cashbox_id': None if self.cashbox_var.get() == "Barchasi" else [cb[0] for cb in database.get_cashboxes() if cb[1] == self.cashbox_var.get()][0],
                'category_id': None if self.category_var.get() == "Barchasi" else [cat[0] for cat in database.get_categories() if cat[1] == self.category_var.get()][0]
            }
            entries = database.get_cash_journal_entries(filters)
            for entry in entries:
                self.journal_tree.insert("", tk.END, values=entry)
        except Exception as e:
            messagebox.showerror("Xatolik", f"Jurnal yozuvlarini yangilashda xato: {str(e)}")
            raise

    def delete_entry(self):
        if not self.selected_journal_id:
            messagebox.showwarning("Xatolik", "O'chirish uchun yozuvni tanlang.")
            return
        if messagebox.askyesno("Tasdiqlash", f"ID={self.selected_journal_id} operatsiyani o'chirishga ishonchingiz komilmi?"):
            try:
                database.delete_entry(self.selected_journal_id)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Xato", f"Yozuvni o'chirishda xato: {str(e)}")

    def edit_entry(self):
        if not self.selected_journal_id:
            messagebox.showwarning("Xatolik", "Tahrirlash uchun yozuvni tanlang.")
            return
        try:
            entry_data = database.get_entry_by_id(self.selected_journal_id)
            if not entry_data:
                messagebox.showerror("Xatolik", "Yozuv topilmadi.")
                return
            self.clear_transaction_form()
            self.editing_entry_id = entry_data.get('id')
            self.trans_direction_var.set(entry_data.get('direction', ''))
            self.trans_cashbox_var.set(entry_data.get('cashbox_name', ''))
            self.trans_amount_var.set(entry_data.get('amount', 0.0))
            self.trans_date_entry.set_date(datetime.strptime(entry_data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'))
            self.trans_category_var.set(entry_data.get('category_name', ''))
            self.trans_payee_var.set(entry_data.get('payee', ''))
            self.trans_note_text.insert("1.0", entry_data.get('note', ''))
            self.trans_file_var.set(entry_data.get('file', ''))
            self.notebook.select(self.transaction_tab)
        except Exception as e:
            messagebox.showerror("Xato", f"Yozuvni tahrirlashda xato: {str(e)}")

    # --- 2. Kirim / Chiqim Vkladkasi ---
    def create_transaction_widgets(self):
        frame = self.transaction_tab
        container = b.LabelFrame(frame, text="Operatsiya ma'lumotlari", padding=20, bootstyle=PRIMARY)
        container.pack(padx=20, pady=20, fill=X)
        container.columnconfigure(1, weight=1)

        self.trans_direction_var = tk.StringVar()
        self.trans_cashbox_var = tk.StringVar()
        self.trans_amount_var = tk.DoubleVar()
        self.trans_category_var = tk.StringVar()
        self.trans_payee_var = tk.StringVar()
        self.trans_file_var = tk.StringVar()
        
        b.Label(container, text="Yo'nalish:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.direction_combobox = b.Combobox(container, textvariable=self.trans_direction_var, values=["Kirim", "Chiqim"], state="readonly")
        self.direction_combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=8)

        b.Label(container, text="Hisob:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.cashbox_combobox = b.Combobox(container, textvariable=self.trans_cashbox_var, state="readonly")
        self.cashbox_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=8)

        b.Label(container, text="Summa:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.trans_amount_var).grid(row=2, column=1, sticky="ew", padx=5, pady=8)
        
        b.Label(container, text="Sana:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        self.trans_date_entry = b.DateEntry(container, dateformat='%Y-%m-%d')
        self.trans_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=8)
        self.trans_date_entry.set_date(datetime.now())
        
        b.Label(container, text="Kategoriya:").grid(row=4, column=0, sticky="w", padx=5, pady=8)
        self.category_combobox = b.Combobox(container, textvariable=self.trans_category_var, state="readonly")
        self.category_combobox.grid(row=4, column=1, sticky="ew", padx=5, pady=8)
        
        b.Label(container, text="Kimga/Kimdan:").grid(row=5, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.trans_payee_var).grid(row=5, column=1, sticky="ew", padx=5, pady=8)

        b.Label(container, text="Izoh:").grid(row=6, column=0, sticky="nw", padx=5, pady=8)
        self.trans_note_text = tk.Text(container, height=4)
        self.trans_note_text.grid(row=6, column=1, sticky="ew", padx=5, pady=8)
        
        b.Label(container, text="Fayl:").grid(row=7, column=0, sticky="w", padx=5, pady=8)
        file_frame = b.Frame(container)
        file_frame.grid(row=7, column=1, sticky="ew")
        b.Button(file_frame, text="Fayl tanlash", command=self.select_transaction_file, bootstyle=SECONDARY).pack(side=LEFT)
        b.Label(file_frame, textvariable=self.trans_file_var, bootstyle=INFO).pack(side=LEFT, padx=10)

        btn_frame = b.Frame(container)
        btn_frame.grid(row=8, column=1, sticky="e", pady=20)
        b.Button(btn_frame, text="Saqlash", command=self.save_transaction, bootstyle=SUCCESS).pack(side=LEFT)
        b.Button(btn_frame, text="Bekor qilish", command=self.clear_transaction_form, bootstyle=SECONDARY).pack(side=LEFT, padx=10)

    def select_transaction_file(self):
        try:
            filepath = filedialog.askopenfilename(filetypes=[("Barcha fayllar", "*.*")])
            if filepath:
                self.trans_file_var.set(filepath)
        except Exception as e:
            messagebox.showerror("Xato", f"Fayl tanlashda xato: {str(e)}")

    def update_transaction_form_comboboxes(self):
        try:
            self.cashbox_combobox['values'] = [c[1] for c in database.get_cashboxes()]
            if not self.trans_cashbox_var.get() and self.cashbox_combobox['values']:
                self.trans_cashbox_var.set(self.cashbox_combobox['values'][0])
            self.category_combobox['values'] = [c[1] for c in database.get_categories()]
            if not self.trans_category_var.get() and self.category_combobox['values']:
                self.trans_category_var.set(self.category_combobox['values'][0])
        except Exception as e:
            messagebox.showerror("Xato", f"Komboboxlarni yangilashda xato: {str(e)}")

    def save_transaction(self):
        try:
            data = {
                'direction': self.trans_direction_var.get(),
                'cashbox_name': self.trans_cashbox_var.get(),
                'amount': self.trans_amount_var.get(),
                'date': self.trans_date_entry.get(),
                'category_name': self.trans_category_var.get(),
                'payee': self.trans_payee_var.get(),
                'note': self.trans_note_text.get("1.0", tk.END).strip(),
                'file': self.trans_file_var.get() or None
            }
            if not all([data['direction'], data['cashbox_name'], data['amount'] > 0, data['date'], data['category_name']]):
                messagebox.showerror("Xatolik", "Barcha asosiy maydonlarni to'ldiring!")
                return
            
            if self.editing_entry_id:
                database.update_cash_entry(self.editing_entry_id, data)
                messagebox.showinfo("Muvaffaqiyatli", "Operatsiya yangilandi!")
            else:
                database.add_cash_entry(data)
                messagebox.showinfo("Muvaffaqiyatli", "Yangi operatsiya qo'shildi!")
            
            self.clear_transaction_form()
            self.refresh_data()
            self.notebook.select(self.journal_tab)
        except tk.TclError:
            messagebox.showerror("Xatolik", "Summa maydoniga faqat raqam kiriting!")
        except Exception as e:
            messagebox.showerror("Xato", f"Operatsiyani saqlashda xato: {str(e)}")

    def clear_transaction_form(self):
        self.editing_entry_id = None
        self.trans_direction_var.set('')
        self.trans_cashbox_var.set('')
        self.trans_amount_var.set(0.0)
        self.trans_date_entry.set_date(datetime.now())
        self.trans_category_var.set('')
        self.trans_payee_var.set('')
        self.trans_file_var.set('')
        self.trans_note_text.delete("1.0", tk.END)

    # --- 3. Kategoriya va Hisoblarni Boshqarish Vkladkasi ---
    def create_management_widgets(self):
        frame = self.management_tab
        frame.columnconfigure((0, 1), weight=1)
        
        cat_frame = b.LabelFrame(frame, text="Xarajat/Daromad Kategoriyalari", padding=15, bootstyle=INFO)
        cat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cat_listbox = tk.Listbox(cat_frame, height=10)
        self.cat_listbox.pack(fill=X, pady=5, expand=YES)
        
        add_cat_frame = b.Frame(cat_frame)
        add_cat_frame.pack(fill=X, pady=5)
        self.new_cat_var = tk.StringVar()
        self.cat_entry = b.Entry(add_cat_frame, textvariable=self.new_cat_var)
        self.cat_entry.pack(side=LEFT, expand=YES, fill=X)
        self.cat_entry.insert(0, "Yangi kategoriya nomini kiriting...")
        self.cat_entry.configure(foreground="grey")
        self.cat_entry.bind("<FocusIn>", self.clear_cat_placeholder)
        self.cat_entry.bind("<FocusOut>", self.restore_cat_placeholder)
        b.Button(add_cat_frame, text="Qo'shish", command=self.add_category, bootstyle=SUCCESS).pack(side=LEFT, padx=(5,0))
        b.Button(cat_frame, text="Tanlanganni o'chirish", command=self.delete_category, bootstyle=DANGER).pack(fill=X)

        acc_frame = b.LabelFrame(frame, text="Kassa va Bank Hisoblari", padding=15, bootstyle=INFO)
        acc_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.acc_listbox = tk.Listbox(acc_frame, height=10)
        self.acc_listbox.pack(fill=X, pady=5, expand=YES)
        
        add_acc_frame = b.Frame(acc_frame)
        add_acc_frame.pack(fill=X, pady=5)
        self.new_acc_var = tk.StringVar()
        self.acc_entry = b.Entry(add_acc_frame, textvariable=self.new_acc_var)
        self.acc_entry.pack(side=LEFT, expand=YES, fill=X)
        self.acc_entry.insert(0, "Yangi hisob nomini kiriting...")
        self.acc_entry.configure(foreground="grey")
        self.acc_entry.bind("<FocusIn>", self.clear_acc_placeholder)
        self.acc_entry.bind("<FocusOut>", self.restore_acc_placeholder)
        b.Button(add_acc_frame, text="Qo'shish", command=self.add_cashbox, bootstyle=SUCCESS).pack(side=LEFT, padx=(5,0))
        b.Button(acc_frame, text="Tanlanganni o'chirish", command=self.delete_cashbox, bootstyle=DANGER).pack(fill=X)

    def clear_cat_placeholder(self, event):
        if self.new_cat_var.get() == "Yangi kategoriya nomini kiriting...":
            self.new_cat_var.set("")
            self.cat_entry.configure(foreground="black")

    def restore_cat_placeholder(self, event):
        if not self.new_cat_var.get():
            self.new_cat_var.set("Yangi kategoriya nomini kiriting...")
            self.cat_entry.configure(foreground="grey")

    def clear_acc_placeholder(self, event):
        if self.new_acc_var.get() == "Yangi hisob nomini kiriting...":
            self.new_acc_var.set("")
            self.acc_entry.configure(foreground="black")

    def restore_acc_placeholder(self, event):
        if not self.new_acc_var.get():
            self.new_acc_var.set("Yangi hisob nomini kiriting...")
            self.acc_entry.configure(foreground="grey")

    def refresh_management_lists(self):
        try:
            self.cat_listbox.delete(0, tk.END)
            self.categories_data = database.get_categories()
            for cat_id, cat_name in self.categories_data:
                self.cat_listbox.insert(tk.END, f"{cat_id}: {cat_name}")
            
            self.acc_listbox.delete(0, tk.END)
            self.cashboxes_data = database.get_cashboxes()
            for acc_id, acc_name in self.cashboxes_data:
                self.acc_listbox.insert(tk.END, f"{acc_id}: {acc_name}")
        except Exception as e:
            messagebox.showerror("Xato", f"Kategoriya va hisoblarni yangilashda xato: {str(e)}")

    def add_category(self):
        new_cat_name = self.new_cat_var.get().strip()
        if not new_cat_name or new_cat_name == "Yangi kategoriya nomini kiriting...":
            messagebox.showwarning("Xatolik", "Kategoriya nomi kiritilmadi!")
            return
        try:
            database.add_category(new_cat_name)
            self.new_cat_var.set("")
            self.restore_cat_placeholder(None)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Xato", f"Kategoriyani qo'shishda xato: {str(e)}")

    def delete_category(self):
        selected_index = self.cat_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Xatolik", "O'chirish uchun kategoriyani tanlang!")
            return
        cat_id_to_delete = self.categories_data[selected_index[0]][0]
        if messagebox.askyesno("Tasdiqlash", "Kategoriyani o'chirishga ishonchingiz komilmi?"):
            try:
                database.delete_category(cat_id_to_delete)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Xato", f"Kategoriyani o'chirishda xato: {str(e)}")

    def add_cashbox(self):
        new_acc_name = self.new_acc_var.get().strip()
        if not new_acc_name or new_acc_name == "Yangi hisob nomini kiriting...":
            messagebox.showwarning("Xatolik", "Hisob nomi kiritilmadi!")
            return
        try:
            database.add_cashbox(new_acc_name, "BANK")  # Type can be customized later
            self.new_acc_var.set("")
            self.restore_acc_placeholder(None)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Xato", f"Hisobni qo'shishda xato: {str(e)}")

    def delete_cashbox(self):
        selected_index = self.acc_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Xatolik", "O'chirish uchun hisobni tanlang!")
            return
        acc_id_to_delete = self.cashboxes_data[selected_index[0]][0]
        if messagebox.askyesno("Tasdiqlash", "Hisobni o'chirishga ishonchingiz komilmi?"):
            try:
                database.delete_cashbox(acc_id_to_delete)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Xato", f"Hisobni o'chirishda xato: {str(e)}")

    # --- 4. Eksport Vkladkasi ---
    def create_export_widgets(self):
        frame = self.export_tab
        container = b.LabelFrame(frame, text="Ma'lumotlarni eksport qilish", padding=20, bootstyle=SUCCESS)
        container.pack(padx=20, pady=20, fill=X)
        
        b.Label(container, text="Boshlanish sanasi:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.export_start_date = b.DateEntry(container, dateformat='%Y-%m-%d', width=15)
        self.export_start_date.grid(row=0, column=1, padx=5, pady=10)
        self.export_start_date.set_date(datetime.now())
        
        b.Label(container, text="Tugash sanasi:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.export_end_date = b.DateEntry(container, dateformat='%Y-%m-%d', width=15)
        self.export_end_date.grid(row=1, column=1, padx=5, pady=10)
        self.export_end_date.set_date(datetime.now())

        self.export_format_var = tk.StringVar(value="Excel (.xlsx)")
        b.Label(container, text="Format:").grid(row=2, column=0, sticky="w", padx=5, pady=10)
        b.Combobox(container, textvariable=self.export_format_var, values=["Excel (.xlsx)", "CSV (.csv)"], state="readonly").grid(row=2, column=1, sticky="w", padx=5)
        
        b.Button(container, text="Eksport Qilish", command=self.export_data, bootstyle=PRIMARY).grid(row=3, column=1, sticky="e", pady=20)
        
    def export_data(self):
        try:
            start_date = self.export_start_date.get()
            end_date = self.export_end_date.get()
            file_format = self.export_format_var.get()
            data_to_export = database.get_entries_for_export(start_date, end_date)
            if not data_to_export:
                messagebox.showinfo("Ma'lumot yo'q", "Eksport uchun ma'lumot topilmadi.")
                return

            if "Excel" in file_format:
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel fayllari", "*.xlsx")])
                if file_path:
                    self.export_to_excel(file_path, data_to_export)
            else:
                file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV fayllari", "*.csv")])
                if file_path:
                    self.export_to_csv(file_path, data_to_export)
        except Exception as e:
            messagebox.showerror("Xato", f"Eksport qilishda xato: {str(e)}")

    def export_to_excel(self, file_path, data):
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Buxgalteriya Hisoboti"
            headers = list(data[0].keys())
            sheet.append(headers)
            for row_data in data:
                sheet.append(list(row_data.values()))
            workbook.save(file_path)
            messagebox.showinfo("Muvaffaqiyatli", f"Ma'lumotlar '{file_path}' fayliga eksport qilindi.")
        except Exception as e:
            messagebox.showerror("Xato", f"Excel faylga yozishda xato: {str(e)}")

    def export_to_csv(self, file_path, data):
        try:
            headers = list(data[0].keys())
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            messagebox.showinfo("Muvaffaqiyatli", f"Ma'lumotlar '{file_path}' fayliga eksport qilindi.")
        except Exception as e:
            messagebox.showerror("Xato", f"CSV faylga yozishda xato: {str(e)}")