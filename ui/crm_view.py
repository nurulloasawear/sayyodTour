import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox
import database

class CrmView(b.Frame):
    """Mijozlar bilan ishlash (CRM) paneli uchun to'liq dinamik interfeys."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        notebook = b.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.customers_tab = b.Frame(notebook)
        self.deals_tab = b.Frame(notebook)
        self.settings_tab = b.Frame(notebook)

        notebook.add(self.customers_tab, text="👥 Mijozlar")
        notebook.add(self.deals_tab, text="📊 Kelishuvlar (Pipeline)")
        notebook.add(self.settings_tab, text="⚙️ Manbalarni Boshqarish")

        self.create_customers_widgets()
        self.create_deals_widgets()
        self.create_crm_settings_widgets()
        
        self.update_filter_comboboxes()  # Initialize combobox values
        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_data())

    def refresh_data(self):
        """Panelga kerakli barcha dinamik ma'lumotlarni bazadan yangilaydi."""
        print("CRM paneli ma'lumotlari yangilanmoqda...")
        try:
            self.refresh_customers_treeview()
            self.refresh_deals_treeview()
            self.refresh_sources_list()
            self.update_filter_comboboxes()
        except Exception as e:
            messagebox.showerror("Xato", f"Ma'lumotlarni yangilashda xato: {str(e)}")

    # --- 1. Mijozlar Vkladkasi ---
    def create_customers_widgets(self):
        frame = self.customers_tab
        
        top_frame = b.Frame(frame)
        top_frame.pack(fill=X, padx=10, pady=10)
        self.customer_search_var = tk.StringVar()
        self.search_entry = b.Entry(top_frame, textvariable=self.customer_search_var, width=40)
        self.search_entry.pack(side=LEFT, fill=X, expand=YES)
        # Add placeholder text
        self.search_entry.insert(0, "FIO yoki telefon bo'yicha qidirish...")
        self.search_entry.config(foreground='grey')
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_placeholder)
        b.Button(top_frame, text="Qidirish", command=self.refresh_customers_treeview, bootstyle=SECONDARY).pack(side=LEFT, padx=5)
        b.Button(top_frame, text="➕ Yangi Mijoz...", command=self.open_customer_editor, bootstyle=SUCCESS).pack(side=RIGHT)
        
        tree_frame = b.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        columns = ("id", "fio", "telefon", "manba", "sana")
        self.customers_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        
        self.customers_tree.heading("id", text="ID")
        self.customers_tree.heading("fio", text="F.I.O.")
        self.customers_tree.heading("telefon", text="Telefon")
        self.customers_tree.heading("manba", text="Manba")
        self.customers_tree.heading("sana", text="Qo'shilgan sana")
        
        self.customers_tree.column("id", width=50, anchor="center")
        self.customers_tree.column("fio", width=250)
        self.customers_tree.column("telefon", width=150)
        self.customers_tree.column("manba", width=150)
        self.customers_tree.column("sana", width=120, anchor="center")

        scrollbar = b.Scrollbar(tree_frame, orient=VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.customers_tree.pack(fill=BOTH, expand=YES)
        
        action_frame = b.Frame(frame)
        action_frame.pack(fill='x', padx=10, pady=5)
        b.Button(action_frame, text="O'chirish", command=self.delete_selected_customer, bootstyle=DANGER).pack(side=RIGHT)
        b.Button(action_frame, text="Tahrirlash...", command=self.edit_selected_customer, bootstyle=INFO).pack(side=RIGHT, padx=10)
        b.Button(action_frame, text="Hujjatlar...", command=self.open_documents_window, bootstyle=SECONDARY).pack(side=RIGHT)

    def clear_placeholder(self, event):
        """Clear placeholder text when Entry gains focus."""
        if self.search_entry.get() == "FIO yoki telefon bo'yicha qidirish...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground='black')

    def restore_placeholder(self, event):
        """Restore placeholder text if Entry is empty."""
        if not self.search_entry.get():
            self.search_entry.insert(0, "FIO yoki telefon bo'yicha qidirish...")
            self.search_entry.config(foreground='grey')

    def refresh_customers_treeview(self):
        """Mijozlar jadvalini yangilaydi."""
        try:
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
            search_term = self.customer_search_var.get()
            if search_term == "FIO yoki telefon bo'yicha qidirish...":
                search_term = ""
            customers = database.search_customers(search_term)
            for customer in customers:
                self.customers_tree.insert("", END, values=customer)
        except Exception as e:
            messagebox.showerror("Xato", f"Mijozlarni yangilashda xato: {str(e)}")

    def open_customer_editor(self, customer_id=None):
        """Mijoz tahrirlash oynasini ochadi."""
        CustomerEditorWindow(self, self.controller, customer_id, self.refresh_data)

    def edit_selected_customer(self):
        """Tanlangan mijozni tahrirlash uchun oynani ochadi."""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Xatolik", "Tahrirlash uchun mijozni tanlang.")
            return
        customer_id = self.customers_tree.item(selected[0])['values'][0]
        self.open_customer_editor(customer_id)

    def delete_selected_customer(self):
        """Tanlangan mijozni o'chiradi."""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Xatolik", "O'chirish uchun mijozni tanlang.")
            return
        customer_id = self.customers_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Tasdiqlash", f"ID={customer_id} mijozni o'chirishga ishonchingiz komilmi? Bu mijozga bog'liq kelishuvlar ham o'chiriladi."):
            try:
                database.delete_customer(customer_id)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Xato", f"Mijozni o'chirishda xato: {str(e)}")

    def open_documents_window(self):
        """Hujjatlar oynasini ochadi."""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Xatolik", "Hujjat yaratish uchun avval mijozni tanlang.")
            return
        customer_id = self.customers_tree.item(selected[0])['values'][0]
        
        doc_window = tk.Toplevel(self)
        doc_window.title(f"ID={customer_id} - Hujjatlar")
        doc_window.geometry("400x200")
        
        b.Label(doc_window, text=f"Mijoz ID: {customer_id}", font=("Helvetica", 12, "bold")).pack(pady=10)
        b.Button(doc_window, text="Shartnoma generatsiya qilish (PDF)", bootstyle=PRIMARY, command=lambda: messagebox.showinfo("Info", "PDF Shartnoma yaratish funksiyasi chaqirildi.")).pack(pady=5, padx=20, fill='x')
        b.Button(doc_window, text="Hisob-faktura (Invoice) yaratish (PDF)", bootstyle=PRIMARY, command=lambda: messagebox.showinfo("Info", "PDF Invoice yaratish funksiyasi chaqirildi.")).pack(pady=5, padx=20, fill='x')
        b.Button(doc_window, text="Kvitansiya chop etish", bootstyle=PRIMARY, command=lambda: messagebox.showinfo("Info", "Kvitansiya yaratish funksiyasi chaqirildi.")).pack(pady=5, padx=20, fill='x')
        doc_window.grab_set()

    # --- 2. Kelishuvlar Vkladkasi ---
    def create_deals_widgets(self):
        frame = self.deals_tab
        filter_frame = b.LabelFrame(frame, text="Filtrlar", padding=10, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(filter_frame, text="Holati:").grid(row=0, column=0, padx=5, pady=5)
        self.deal_status_filter = b.Combobox(filter_frame, state="readonly", values=["Barchasi", "Yangi", "Taklif yuborildi", "Oldindan to'lov", "To'liq to'lov", "Yakunlandi", "Bekor qilindi"])
        self.deal_status_filter.grid(row=0, column=1, padx=5, pady=5)
        self.deal_status_filter.set("Barchasi")
        
        b.Label(filter_frame, text="Menejer:").grid(row=0, column=2, padx=5, pady=5)
        self.deal_manager_filter = b.Combobox(filter_frame, state="readonly")
        self.deal_manager_filter.grid(row=0, column=3, padx=5, pady=5)
        self.deal_manager_filter.set("Barchasi")
        
        b.Button(filter_frame, text="Filterlash", command=self.refresh_deals_treeview, bootstyle=SECONDARY).grid(row=0, column=4, padx=10, pady=5)

        tree_frame = b.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        columns = ("id", "mijoz", "yonalish", "summa", "holati", "menejer")
        self.deals_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        
        self.deals_tree.heading("id", text="ID")
        self.deals_tree.heading("mijoz", text="Mijoz")
        self.deals_tree.heading("yonalish", text="Yo'nalish")
        self.deals_tree.heading("summa", text="Summa (UZS)")
        self.deals_tree.heading("holati", text="Holati")
        self.deals_tree.heading("menejer", text="Menejer")
        
        self.deals_tree.column("id", width=50, anchor="center")
        self.deals_tree.column("mijoz", width=200)
        self.deals_tree.column("yonalish", width=150)
        self.deals_tree.column("summa", width=120, anchor="e")
        self.deals_tree.column("holati", width=120, anchor="center")
        self.deals_tree.column("menejer", width=150)
        
        scrollbar = b.Scrollbar(tree_frame, orient=VERTICAL, command=self.deals_tree.yview)
        self.deals_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.deals_tree.pack(fill=BOTH, expand=YES)
        
        self.deals_tree.tag_configure('Yakunlandi', background='#2E7D32')
        self.deals_tree.tag_configure('Bekor qilindi', background='#C62828')
        self.deals_tree.tag_configure('Yangi', background='#0277BD')

    def update_filter_comboboxes(self):
        """Menejerlar filtrini yangilaydi."""
        try:
            managers = ["Barchasi"] + [m['full_name'] for m in database.get_users(role='MANAGER')]
            self.deal_manager_filter['values'] = managers
            if "Barchasi" not in self.deal_manager_filter.get():
                self.deal_manager_filter.set("Barchasi")
        except Exception as e:
            messagebox.showerror("Xato", f"Filtrlarni yangilashda xato: {str(e)}")

    def refresh_deals_treeview(self):
        """Kelishuvlar jadvalini yangilaydi."""
        try:
            for item in self.deals_tree.get_children():
                self.deals_tree.delete(item)
            filters = {
                'status': self.deal_status_filter.get() if self.deal_status_filter.get() != "Barchasi" else None,
                'manager_name': self.deal_manager_filter.get() if self.deal_manager_filter.get() != "Barchasi" else None
            }
            deals = database.get_filtered_deals(filters)
            for deal in deals:
                status_tag = deal[4].replace(" ", "")  # e.g., "Bekor qilindi" -> "Bekorqilindi"
                self.deals_tree.insert("", END, values=deal, tags=(status_tag,))
        except Exception as e:
            messagebox.showerror("Xato", f"Kelishuvlarni yangilashda xato: {str(e)}")

    # --- 3. Sozlamalar Vkladkasi ---
    def create_crm_settings_widgets(self):
        frame = self.settings_tab
        container = b.LabelFrame(frame, text="Mijoz Manbalarini Boshqarish", padding=15, bootstyle=INFO)
        container.pack(fill=X, padx=20, pady=20)

        self.sources_listbox = tk.Listbox(container, height=8)
        self.sources_listbox.pack(fill=X, pady=5, expand=YES)
        
        add_frame = b.Frame(container)
        add_frame.pack(fill=X, pady=5)
        self.new_source_var = tk.StringVar()
        self.source_entry = b.Entry(add_frame, textvariable=self.new_source_var)
        self.source_entry.pack(side=LEFT, expand=YES, fill=X)
        self.source_entry.insert(0, "Yangi manba nomini kiriting...")
        self.source_entry.config(foreground='grey')
        self.source_entry.bind("<FocusIn>", self.clear_source_placeholder)
        self.source_entry.bind("<FocusOut>", self.restore_source_placeholder)
        b.Button(add_frame, text="Qo'shish", command=self.add_source, bootstyle=SUCCESS).pack(side=LEFT, padx=(5,0))
        b.Button(container, text="Tanlanganni o'chirish", command=self.delete_source, bootstyle=DANGER).pack(fill=X, pady=5)

    def clear_source_placeholder(self, event):
        """Clear placeholder text for source entry."""
        if self.source_entry.get() == "Yangi manba nomini kiriting...":
            self.source_entry.delete(0, tk.END)
            self.source_entry.config(foreground='black')

    def restore_source_placeholder(self, event):
        """Restore placeholder text for source entry if empty."""
        if not self.source_entry.get():
            self.source_entry.insert(0, "Yangi manba nomini kiriting...")
            self.source_entry.config(foreground='grey')

    def refresh_sources_list(self):
        """Manbalar ro'yxatini yangilaydi."""
        try:
            self.sources_listbox.delete(0, tk.END)
            self.sources_data = database.get_deal_sources()
            for src_id, src_name in self.sources_data:
                self.sources_listbox.insert(tk.END, f"{src_id}: {src_name}")
        except Exception as e:
            messagebox.showerror("Xato", f"Manbalarni yangilashda xato: {str(e)}")

    def add_source(self):
        """Yangi manba qo'shadi."""
        source_name = self.new_source_var.get().strip()
        if source_name == "Yangi manba nomini kiriting...":
            source_name = ""
        if not source_name:
            messagebox.showwarning("Xatolik", "Manba nomi kiritilmadi!")
            return
        try:
            database.add_deal_source(source_name)
            self.new_source_var.set("")
            self.restore_source_placeholder(None)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Xato", f"Manba qo'shishda xato: {str(e)}")

    def delete_source(self):
        """Tanlangan manbani o'chiradi."""
        selected_index = self.sources_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Xatolik", "O'chirish uchun manbani tanlang!")
            return
        source_id = self.sources_data[selected_index[0]][0]
        if messagebox.askyesno("Tasdiqlash", "Bu manbani o'chirishga ishonchingiz komilmi?"):
            try:
                database.delete_deal_source(source_id)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Xato", f"Manbani o'chirishda xato: {str(e)}")

class CustomerEditorWindow(tk.Toplevel):
    """Mijozlarni qo'shish va tahrirlash uchun Toplevel oyna."""
    def __init__(self, parent, controller, customer_id=None, callback=None):
        super().__init__(parent)
        self.controller = controller
        self.customer_id = customer_id
        self.callback = callback

        self.title("Yangi Mijoz Qo'shish" if not customer_id else f"ID={customer_id} Mijozni Tahrirlash")
        self.geometry("500x350")
        
        self.vars = {k: tk.StringVar() for k in ['fio', 'phone', 'source', 'passport', 'interest']}
        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)
        container.columnconfigure(1, weight=1)

        b.Label(container, text="F.I.O.*:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['fio']).grid(row=0, column=1, sticky="ew", padx=5, pady=8)
        b.Label(container, text="Telefon*:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['phone']).grid(row=1, column=1, sticky="ew", padx=5, pady=8)
        b.Label(container, text="Manba:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.source_combo = b.Combobox(container, textvariable=self.vars['source'], state="readonly")
        self.source_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=8)
        b.Label(container, text="Pasport (ixtiyoriy):").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['passport']).grid(row=3, column=1, sticky="ew", padx=5, pady=8)
        b.Label(container, text="Qiziqqan yo'nalish:").grid(row=4, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['interest']).grid(row=4, column=1, sticky="ew", padx=5, pady=8)
        
        btn_frame = b.Frame(container)
        btn_frame.grid(row=5, column=1, sticky="e", pady=20)
        b.Button(btn_frame, text="Saqlash", command=self.save, bootstyle=SUCCESS).pack(side=LEFT)
        b.Button(btn_frame, text="Bekor qilish", command=self.destroy, bootstyle=SECONDARY).pack(side=LEFT, padx=10)
        
        self.populate_form()
        self.grab_set()
    
    def populate_form(self):
        """Forma maydonlarini to'ldiradi."""
        try:
            self.source_combo['values'] = [s[1] for s in database.get_deal_sources()]
            if self.customer_id:
                customer_data = database.get_customer_details(self.customer_id)
                if customer_data:
                    for key in self.vars:
                        self.vars[key].set(customer_data.get(key, ''))
        except Exception as e:
            messagebox.showerror("Xato", f"Forma ma'lumotlarini yuklashda xato: {str(e)}", parent=self)

    def save(self):
        """Mijoz ma'lumotlarini saqlaydi."""
        data = {key: var.get() for key, var in self.vars.items()}
        if not data['fio'] or not data['phone']:
            messagebox.showerror("Xatolik", "F.I.O. va Telefon kiritilishi shart!", parent=self)
            return
        try:
            if self.customer_id:
                database.update_customer(self.customer_id, data)
            else:
                database.add_customer(data)
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Xato", f"Mijoz ma'lumotlarini saqlashda xato: {str(e)}", parent=self)