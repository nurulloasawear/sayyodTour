# ui/products_view.py

import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from tkinter import messagebox, filedialog

# MUHIM: Bu panel ishlashi uchun database.py da ushbu fayl oxirida ko'rsatilgan
# barcha funksiyalarni yaratgan bo'lishingiz SHART.
import database

class ProductsView(b.Frame):
    """Mahsulotlar (Tur Paketlar) va Turoperatorlarni boshqarish uchun interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        notebook = b.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.products_tab = b.Frame(notebook)
        self.operators_tab = b.Frame(notebook)

        notebook.add(self.products_tab, text="✈️ Tur Paketlar (Mahsulotlar)")
        notebook.add(self.operators_tab, text="🏢 Turoperatorlar")

        self.create_products_widgets()
        self.create_operators_widgets()

        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_data())

    def refresh_data(self):
        """Panelga kerakli barcha dinamik ma'lumotlarni bazadan yangilaydi."""
        print("Mahsulotlar paneli ma'lumotlari yangilanmoqda...")
        self.refresh_products_treeview()
        self.refresh_operators_treeview()

    # --- 1. Tur Paketlar Vkladkasi ---
    def create_products_widgets(self):
        frame = self.products_tab
        top_frame = b.Frame(frame)
        top_frame.pack(fill=X, padx=10, pady=10)
        b.Button(top_frame, text="➕ Yangi Tur Paket...", command=self.open_product_editor, bootstyle=SUCCESS).pack(side=RIGHT)
        
        tree_frame = b.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        columns = ("id", "nomi", "davlat", "kunlar", "narx", "operator")
        self.products_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("nomi", text="Tur Nomi")
        self.products_tree.heading("davlat", text="Davlat")
        self.products_tree.heading("kunlar", text="Tunlar")
        self.products_tree.heading("narx", text="Boshlang'ich Narx")
        self.products_tree.heading("operator", text="Turoperator")

        self.products_tree.column("id", width=50, anchor="center")
        self.products_tree.column("kunlar", width=60, anchor="center")
        self.products_tree.column("narx", anchor="e")

        self.products_tree.pack(fill=BOTH, expand=YES)
        
        action_frame = b.Frame(frame)
        action_frame.pack(fill='x', padx=10, pady=5)
        b.Button(action_frame, text="O'chirish", command=self.delete_selected_product, bootstyle=DANGER).pack(side=RIGHT)
        b.Button(action_frame, text="Tahrirlash...", command=self.edit_selected_product, bootstyle=INFO).pack(side=RIGHT, padx=10)

    def refresh_products_treeview(self):
        for item in self.products_tree.get_children(): self.products_tree.delete(item)
        products = database.get_all_products()
        for product in products: self.products_tree.insert("", END, values=product)

    def open_product_editor(self, product_id=None):
        ProductEditorWindow(self, self.controller, product_id, self.refresh_data)

    def edit_selected_product(self):
        selected = self.products_tree.selection()
        if not selected: return messagebox.showwarning("Xatolik", "Tahrirlash uchun tur paketni tanlang.")
        product_id = self.products_tree.item(selected[0])['values'][0]
        self.open_product_editor(product_id)

    def delete_selected_product(self):
        selected = self.products_tree.selection()
        if not selected: return messagebox.showwarning("Xatolik", "O'chirish uchun tur paketni tanlang.")
        product_id = self.products_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Tasdiqlash", f"ID={product_id} tur paketni o'chirishga ishonchingiz komilmi?"):
            database.delete_product(product_id)
            self.refresh_data()

    # --- 2. Turoperatorlar Vkladkasi ---
    def create_operators_widgets(self):
        frame = self.operators_tab
        top_frame = b.Frame(frame)
        top_frame.pack(fill=X, padx=10, pady=10)
        b.Button(top_frame, text="➕ Yangi Operator...", command=self.open_operator_editor, bootstyle=SUCCESS).pack(side=RIGHT)
        
        tree_frame = b.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        columns = ("id", "nomi", "aloqa")
        self.operators_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        self.operators_tree.heading("id", text="ID")
        self.operators_tree.heading("nomi", text="Operator Nomi")
        self.operators_tree.heading("aloqa", text="Aloqa Ma'lumoti")
        self.operators_tree.column("id", width=50, anchor="center")
        self.operators_tree.pack(fill=BOTH, expand=YES)
        
        action_frame = b.Frame(frame)
        action_frame.pack(fill='x', padx=10, pady=5)
        b.Button(action_frame, text="O'chirish", command=self.delete_selected_operator, bootstyle=DANGER).pack(side=RIGHT)
        b.Button(action_frame, text="Tahrirlash...", command=self.edit_selected_operator, bootstyle=INFO).pack(side=RIGHT, padx=10)

    def refresh_operators_treeview(self):
        for item in self.operators_tree.get_children(): self.operators_tree.delete(item)
        operators = database.get_all_operators()
        for operator in operators: self.operators_tree.insert("", END, values=operator)

    def open_operator_editor(self, operator_id=None):
        OperatorEditorWindow(self, self.controller, operator_id, self.refresh_data)

    def edit_selected_operator(self):
        selected = self.operators_tree.selection()
        if not selected: return messagebox.showwarning("Xatolik", "Tahrirlash uchun operatorni tanlang.")
        operator_id = self.operators_tree.item(selected[0])['values'][0]
        self.open_operator_editor(operator_id)
    
    def delete_selected_operator(self):
        selected = self.operators_tree.selection()
        if not selected: return messagebox.showwarning("Xatolik", "O'chirish uchun operatorni tanlang.")
        operator_id = self.operators_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Tasdiqlash", "DIQQAT! Bu operatorga bog'langan barcha tur paketlarda muammo yuzaga kelishi mumkin.\n\nDavom etishni xohlaysizmi?"):
            database.delete_operator(operator_id)
            self.refresh_data()

class ProductEditorWindow(tk.Toplevel):
    def __init__(self, parent, controller, product_id=None, callback=None):
        super().__init__(parent)
        self.product_id, self.callback = product_id, callback
        self.title("Yangi Tur Paket" if not product_id else f"ID={product_id} Tur Paketni Tahrirlash")
        self.geometry("600x500")

        self.vars = {k: tk.StringVar() for k in ['title', 'country', 'operator_name']}
        self.nights_var = tk.IntVar()
        self.price_var = tk.DoubleVar()
        
        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)
        container.columnconfigure(1, weight=1)

        b.Label(container, text="Tur nomi*:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        b.Entry(container, textvariable=self.vars['title']).grid(row=0, column=1, sticky="ew")
        b.Label(container, text="Davlat*:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        b.Entry(container, textvariable=self.vars['country']).grid(row=1, column=1, sticky="ew")
        b.Label(container, text="Tunlar soni*:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        b.Entry(container, textvariable=self.nights_var).grid(row=2, column=1, sticky="ew")
        b.Label(container, text="Boshlang'ich narx (UZS)*:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        b.Entry(container, textvariable=self.price_var).grid(row=3, column=1, sticky="ew")
        b.Label(container, text="Turoperator*:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.operator_combo = b.Combobox(container, textvariable=self.vars['operator_name'], state="readonly")
        self.operator_combo.grid(row=4, column=1, sticky="ew")
        
        b.Label(container, text="Paketga nimalar kiradi:").grid(row=5, column=0, columnspan=2, sticky="w", pady=(10,5))
        self.inclusions_text = ScrolledText(container, height=6, autohide=True)
        self.inclusions_text.grid(row=6, column=0, columnspan=2, sticky="nsew")

        btn_frame = b.Frame(container)
        btn_frame.grid(row=7, column=1, sticky="e", pady=20)
        b.Button(btn_frame, text="Saqlash", command=self.save, bootstyle=SUCCESS).pack(side=LEFT)
        b.Button(btn_frame, text="Bekor qilish", command=self.destroy, bootstyle=SECONDARY).pack(side=LEFT, padx=10)

        self.populate_form()
        self.grab_set()

    def populate_form(self):
        operators = database.get_all_operators()
        self.operator_map = {name: op_id for op_id, name, contact in operators}
        self.operator_combo['values'] = list(self.operator_map.keys())
        if self.product_id:
            product_data = database.get_product_details(self.product_id)
            if product_data:
                self.vars['title'].set(product_data.get('title', ''))
                self.vars['country'].set(product_data.get('country', ''))
                self.nights_var.set(product_data.get('nights', 0))
                self.price_var.set(product_data.get('base_price', 0.0))
                self.vars['operator_name'].set(product_data.get('operator_name', ''))
                self.inclusions_text.insert(END, product_data.get('inclusions', ''))

    def save(self):
        try:
            data = {key: var.get() for key, var in self.vars.items()}
            data['nights'] = self.nights_var.get()
            data['base_price'] = self.price_var.get()
            data['inclusions'] = self.inclusions_text.get("1.0", END).strip()
            data['operator_id'] = self.operator_map.get(data['operator_name'])
        
            if not all([data['title'], data['country'], data['nights'] > 0, data['base_price'] > 0, data['operator_id']]):
                return messagebox.showerror("Xatolik", "Barcha yulduzchali (*) maydonlar to'ldirilishi shart!", parent=self)
        except tk.TclError:
            return messagebox.showerror("Xatolik", "'Tunlar soni' va 'Narx' maydonlariga raqam kiriting!", parent=self)

        if self.product_id: database.update_product(self.product_id, data)
        else: database.add_product(data)
        
        if self.callback: self.callback()
        self.destroy()

class OperatorEditorWindow(tk.Toplevel):
    def __init__(self, parent, controller, operator_id=None, callback=None):
        super().__init__(parent)
        self.operator_id, self.callback = operator_id, callback
        self.title("Yangi Turoperator" if not operator_id else f"ID={operator_id} Operatorni Tahrirlash")
        self.geometry("500x350")
        
        self.name_var = tk.StringVar()
        self.contract_file_var = tk.StringVar()

        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)
        container.columnconfigure(1, weight=1)

        b.Label(container, text="Operator Nomi*:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.name_var).grid(row=0, column=1, sticky="ew")
        
        b.Label(container, text="Aloqa ma'lumotlari:").grid(row=1, column=0, sticky="nw", padx=5, pady=8)
        self.contact_text = tk.Text(container, height=5)
        self.contact_text.grid(row=1, column=1, sticky="ew")
        
        b.Label(container, text="Shartnoma fayli:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        file_frame = b.Frame(container)
        file_frame.grid(row=2, column=1, sticky="ew")
        b.Button(file_frame, text="Fayl tanlash", command=self.select_file, bootstyle=SECONDARY).pack(side=LEFT)
        b.Label(file_frame, textvariable=self.contract_file_var, bootstyle=INFO).pack(side=LEFT, padx=10)

        btn_frame = b.Frame(container)
        btn_frame.grid(row=3, column=1, sticky="e", pady=20)
        b.Button(btn_frame, text="Saqlash", command=self.save, bootstyle=SUCCESS).pack(side=LEFT)
        b.Button(btn_frame, text="Bekor qilish", command=self.destroy, bootstyle=SECONDARY).pack(side=LEFT, padx=10)
        
        if self.operator_id: self.populate_form()
        self.grab_set()

    def select_file(self):
        filepath = filedialog.askopenfilename()
        if filepath: self.contract_file_var.set(filepath)

    def populate_form(self):
        operator_data = database.get_operator_details(self.operator_id)
        if operator_data:
            self.name_var.set(operator_data.get('name', ''))
            self.contact_text.insert(END, operator_data.get('contact', ''))
            self.contract_file_var.set(operator_data.get('contract_file', ''))

    def save(self):
        data = {
            'name': self.name_var.get().strip(),
            'contact': self.contact_text.get("1.0", END).strip(),
            'contract_file': self.contract_file_var.get()
        }
        if not data['name']: return messagebox.showerror("Xatolik", "Operator nomi kiritilishi shart!", parent=self)
        
        if self.operator_id: database.update_operator(self.operator_id, data)
        else: database.add_operator(data)
        
        if self.callback: self.callback()
        self.destroy()