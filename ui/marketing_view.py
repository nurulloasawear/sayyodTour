# ui/marketing_view.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import csv
from datetime import datetime

# database.py faylidan kerakli funksiyalarni import qilish kerak bo'ladi.
# Hozircha, bu funksiyalar mavjud deb hisoblaymiz.
# import database 

class MarketingView(ttk.Frame):
    """Marketing bo'limi uchun to'liq funksional interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.selected_lead_id = None

        # Asosiy vkladkalar (Notebook)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Vkladkalarni yaratish
        self.leads_list_tab = ttk.Frame(notebook)
        self.add_lead_tab = ttk.Frame(notebook)
        self.import_tab = ttk.Frame(notebook)

        notebook.add(self.leads_list_tab, text=" Leads Ro'yxati")
        notebook.add(self.add_lead_tab, text="➕ Yangi Lead Qo'shish")
        notebook.add(self.import_tab, text="⬆️ Ommaviy Import")

        # Har bir vkladka uchun interfeys elementlarini chizish
        self.create_leads_list_widgets()
        self.create_add_lead_widgets()
        self.create_import_widgets()

    # --- 1. Leadlar Ro'yxati Vkladkasi ---
    def create_leads_list_widgets(self):
        frame = self.leads_list_tab
        
        # Filtrlar paneli
        filter_frame = ttk.LabelFrame(frame, text="Filtrlar", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Menejer:").grid(row=0, column=0, padx=5, pady=5)
        # self.lead_manager_filter = ttk.Combobox(filter_frame, values=["Barchasi"] + database.get_managers_list())
        self.lead_manager_filter = ttk.Combobox(filter_frame, values=["Barchasi", "Alisher Valiev", "Ziyoda Karimova"])
        self.lead_manager_filter.grid(row=0, column=1, padx=5, pady=5)
        self.lead_manager_filter.set("Barchasi")

        ttk.Label(filter_frame, text="Holati:").grid(row=0, column=2, padx=5, pady=5)
        self.lead_status_filter = ttk.Combobox(filter_frame, values=["Barchasi", "Yangi", "Jarayonda", "Muvaffaqiyatli", "Bekor qilingan"])
        self.lead_status_filter.grid(row=0, column=3, padx=5, pady=5)
        self.lead_status_filter.set("Barchasi")

        ttk.Button(filter_frame, text="Filterlash", command=self.refresh_leads_treeview).grid(row=0, column=4, padx=10, pady=5)

        # Leadlar ro'yxati (jadval)
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "ism", "telefon", "manba", "holati", "menejer", "qayta_aloqa")
        self.leads_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.leads_tree.heading("id", text="ID")
        self.leads_tree.heading("ism", text="Ism")
        self.leads_tree.heading("telefon", text="Telefon")
        self.leads_tree.heading("manba", text="Manba")
        self.leads_tree.heading("holati", text="Holati")
        self.leads_tree.heading("menejer", text="Menejer")
        self.leads_tree.heading("qayta_aloqa", text="Qayta aloqa sanasi")
        
        self.leads_tree.column("id", width=50, anchor="center")
        self.leads_tree.column("ism", width=200)
        # qolgan ustunlar kengligi avtomatik

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.leads_tree.yview)
        self.leads_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.leads_tree.pack(fill="both", expand=True)
        
        self.leads_tree.bind('<<TreeviewSelect>>', self.on_lead_select)
        
        # Amallar paneli
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(action_frame, text="Tanlanganni o'chirish", command=self.delete_selected_lead).pack(side='right')
        ttk.Button(action_frame, text="Menejerga biriktirish...", command=self.assign_lead_to_manager).pack(side='right', padx=10)

        self.refresh_leads_treeview()

    def refresh_leads_treeview(self):
        for item in self.leads_tree.get_children():
            self.leads_tree.delete(item)
        
        # leads = database.get_filtered_leads(manager_filter, status_filter)
        leads = [ # Simulyatsiya
            (1, "Sardor Komilov", "+998901112233", "Instagram", "Yangi", "Biriktirilmagan", "-"),
            (2, "Dilnoza Alimova", "+998934445566", "Facebook", "Jarayonda", "Alisher Valiev", "2025-10-08"),
            (3, "Farrux Zokirov", "+998978889900", "Tavsiya", "Muvaffaqiyatli", "Ziyoda Karimova", "2025-10-05"),
        ]
        for lead in leads:
            self.leads_tree.insert("", "end", values=lead)
            
    def on_lead_select(self, event):
        try:
            selected_item = self.leads_tree.selection()[0]
            self.selected_lead_id = self.leads_tree.item(selected_item)['values'][0]
        except IndexError:
            self.selected_lead_id = None

    def delete_selected_lead(self):
        if not self.selected_lead_id:
            return messagebox.showwarning("Ogohlantirish", "O'chirish uchun avval leadni tanlang!")
        if messagebox.askyesno("Tasdiqlash", f"ID={self.selected_lead_id} bo'lgan leadni o'chirishga ishonchingiz komilmi?"):
            # database.delete_lead(self.selected_lead_id)
            print(f"Lead o'chirildi: ID={self.selected_lead_id}")
            self.refresh_leads_treeview()

    def assign_lead_to_manager(self):
        if not self.selected_lead_id:
            return messagebox.showwarning("Ogohlantirish", "Biriktirish uchun avval leadni tanlang!")

        win = tk.Toplevel(self)
        win.title("Menejerga biriktirish")
        
        ttk.Label(win, text=f"Lead ID: {self.selected_lead_id}", font=("", 10, "bold")).pack(pady=10, padx=20)
        
        ttk.Label(win, text="Menejerni tanlang:").pack(padx=20, anchor="w")
        # manager_list = database.get_managers_list()
        manager_list = ["Alisher Valiev", "Ziyoda Karimova"]
        manager_var = tk.StringVar()
        ttk.Combobox(win, textvariable=manager_var, values=manager_list).pack(padx=20, pady=5, fill="x")
        
        ttk.Label(win, text="Qayta aloqa sanasini belgilang:").pack(padx=20, anchor="w")
        date_entry = DateEntry(win, date_pattern='yyyy-mm-dd')
        date_entry.pack(padx=20, pady=5, fill="x")

        def on_save():
            manager = manager_var.get()
            contact_date = date_entry.get()
            if not manager:
                return messagebox.showerror("Xatolik", "Iltimos, menejerni tanlang!", parent=win)
            
            # database.assign_lead(self.selected_lead_id, manager, contact_date)
            print(f"Lead ID={self.selected_lead_id} {manager}ga biriktirildi. Qayta aloqa: {contact_date}")
            self.refresh_leads_treeview()
            win.destroy()

        ttk.Button(win, text="Saqlash", command=on_save).pack(pady=15, padx=20)

    # --- 2. Yangi Lead Qo'shish Vkladkasi ---
    def create_add_lead_widgets(self):
        frame = self.add_lead_tab
        container = ttk.LabelFrame(frame, text="Yangi lead ma'lumotlari", padding=20)
        container.pack(padx=20, pady=20)

        # O'zgaruvchilar
        self.new_lead_vars = {
            'name': tk.StringVar(), 'phone': tk.StringVar(), 'source': tk.StringVar(),
            'campaign': tk.StringVar(), 'interest': tk.StringVar(), 'manager': tk.StringVar(),
            'contact_date': tk.StringVar(value=datetime.now().strftime('%Y-%m-%d')),
            'temperature': tk.StringVar()
        }

        # Maydonlar
        ttk.Label(container, text="Ism:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(container, textvariable=self.new_lead_vars['name'], width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(container, text="Telefon:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(container, textvariable=self.new_lead_vars['phone']).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(container, text="Manba:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(container, textvariable=self.new_lead_vars['source'], values=["Instagram", "Facebook", "Telegram", "Tavsiya"]).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(container, text="Kampaniya (ixtiyoriy):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(container, textvariable=self.new_lead_vars['campaign']).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(container, text="Qiziqqan yo'nalish/byudjet:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(container, textvariable=self.new_lead_vars['interest']).grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(container, text="Issiqligi:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(container, textvariable=self.new_lead_vars['temperature'], values=["Issiq", "Iliq", "Sovuq"]).grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(container, text="Izoh:").grid(row=6, column=0, sticky="nw", padx=5, pady=5)
        self.new_lead_note = tk.Text(container, height=4)
        self.new_lead_note.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Button(container, text="Saqlash", command=self.save_new_lead).grid(row=7, column=1, sticky="e", pady=20)
        container.columnconfigure(1, weight=1)

    def save_new_lead(self):
        name = self.new_lead_vars['name'].get()
        phone = self.new_lead_vars['phone'].get()
        if not name or not phone:
            return messagebox.showerror("Xatolik", "Ism va Telefon kiritilishi shart!")
        
        data = {k: v.get() for k, v in self.new_lead_vars.items()}
        data['note'] = self.new_lead_note.get("1.0", tk.END).strip()
        
        # new_lead_id = database.add_lead(data)
        print("Yangi lead saqlanmoqda:", data)
        messagebox.showinfo("Muvaffaqiyatli", "Yangi lead muvaffaqiyatli saqlandi!")
        
        # Maydonlarni tozalash
        for var in self.new_lead_vars.values(): var.set("")
        self.new_lead_vars['contact_date'].set(datetime.now().strftime('%Y-%m-%d'))
        self.new_lead_note.delete("1.0", tk.END)
        self.refresh_leads_treeview()


    # --- 3. Ommaviy Import Vkladkasi ---
    def create_import_widgets(self):
        frame = self.import_tab
        container = ttk.LabelFrame(frame, text="CSV/Excel fayldan leadlarni import qilish", padding=20)
        container.pack(padx=20, pady=20, fill="x")

        self.import_file_path = tk.StringVar()
        ttk.Button(container, text="Fayl tanlash...", command=self.select_import_file).grid(row=0, column=0, padx=5, pady=10)
        ttk.Label(container, textvariable=self.import_file_path, foreground="blue").grid(row=0, column=1, padx=5, pady=10)
        
        info_text = "DIQQAT: Fayl ustunlari quyidagi tartibda bo'lishi kerak:\nIsm, Telefon, Manba, Kampaniya, Qiziqish"
        ttk.Label(container, text=info_text, justify="left").grid(row=1, column=0, columnspan=2, pady=10, sticky="w")
        
        self.import_button = ttk.Button(container, text="Importni Boshlash", command=self.start_import, state="disabled")
        self.import_button.grid(row=2, column=1, sticky="e", pady=10)
        
        # Progress bar va status
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(container, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        self.import_status_label = ttk.Label(container, text="")
        self.import_status_label.grid(row=4, column=0, columnspan=2, sticky="w")
        
    def select_import_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV fayllar", "*.csv"), ("Excel fayllar", "*.xlsx")])
        if path:
            self.import_file_path.set(path)
            self.import_button.config(state="normal")
            self.import_status_label.config(text="")
            self.progress_var.set(0)

    def start_import(self):
        file_path = self.import_file_path.get()
        if not file_path: return

        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader) # Sarlavhani o'tkazib yuborish
                    leads_to_import = list(reader)
                
                total_leads = len(leads_to_import)
                if total_leads == 0:
                    return messagebox.showinfo("Info", "Fayl bo'sh.")

                success_count = 0
                for i, row in enumerate(leads_to_import):
                    # Ustunlar soni to'g'riligini tekshirish
                    if len(row) >= 3:
                        lead_data = {'name': row[0], 'phone': row[1], 'source': row[2], 
                                     'campaign': row[3] if len(row) > 3 else '', 
                                     'interest': row[4] if len(row) > 4 else ''}
                        # database.add_lead(lead_data, status='Yangi')
                        success_count += 1
                    
                    # Progress barni yangilash
                    progress = (i + 1) / total_leads * 100
                    self.progress_var.set(progress)
                    self.import_status_label.config(text=f"{i+1}/{total_leads} qayta ishlandi...")
                    self.update_idletasks() # Interfeysni yangilash
                
                messagebox.showinfo("Muvaffaqiyatli", f"{total_leads} ta qatordan {success_count} tasi muvaffaqiyatli import qilindi.")
                self.refresh_leads_treeview()
            
            elif file_path.endswith('.xlsx'):
                messagebox.showinfo("Kechirasiz", "Excel importi keyingi versiyalarda qo'shiladi. Hozircha CSV formatidan foydalaning.")
                
        except Exception as e:
            messagebox.showerror("Xatolik", f"Import qilishda xatolik yuz berdi:\n{e}")
        finally:
            self.progress_var.set(0)
            self.import_status_label.config(text="Jarayon yakunlandi.")