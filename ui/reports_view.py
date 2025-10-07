import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox
from datetime import datetime
import database

class ReportsView(b.Frame):
    """Barcha asosiy hisobotlarni shakllantirish uchun interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        notebook = b.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.sales_tab = b.Frame(notebook)
        self.marketing_tab = b.Frame(notebook)
        self.financial_tab = b.Frame(notebook)

        notebook.add(self.sales_tab, text="📈 Sotuvlar Hisoboti")
        notebook.add(self.marketing_tab, text="📢 Marketing Hisoboti")
        notebook.add(self.financial_tab, text="💰 Moliyaviy Hisobotlar")

        self.create_sales_report_widgets()
        self.create_marketing_report_widgets()
        self.create_financial_report_widgets()

        self.refresh_data()  # Initialize comboboxes

    def refresh_data(self):
        """Panelga kerakli dinamik ma'lumotlarni (filtrlar uchun) yangilaydi."""
        print("Hisobotlar paneli ma'lumotlari yangilanmoqda...")
        try:
            managers = ["Barchasi"] + [m[1] for m in database.get_users(role='manager')]
            sources = ["Barchasi"] + [s[1] for s in database.get_deal_sources()]
            self.sales_manager_filter['values'] = managers
            self.marketing_source_filter['values'] = sources
            if not self.sales_manager_filter.get():
                self.sales_manager_filter.set("Barchasi")
            if not self.marketing_source_filter.get():
                self.marketing_source_filter.set("Barchasi")
        except Exception as e:
            messagebox.showerror("Xato", f"Ma'lumotlarni yangilashda xato: {str(e)}")

    # --- 1. Sotuvlar Hisoboti Vkladkasi ---
    def create_sales_report_widgets(self):
        frame = self.sales_tab
        
        filter_frame = b.LabelFrame(frame, text="Filtrlar", padding=15, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(filter_frame, text="Dan:").grid(row=0, column=0, padx=5, pady=5)
        self.sales_start_date = b.DateEntry(filter_frame, dateformat='%Y-%m-%d')
        self.sales_start_date.grid(row=0, column=1, padx=5, pady=5)
        self.sales_start_date.set_date(datetime.now())
        
        b.Label(filter_frame, text="Gacha:").grid(row=0, column=2, padx=5, pady=5)
        self.sales_end_date = b.DateEntry(filter_frame, dateformat='%Y-%m-%d')
        self.sales_end_date.grid(row=0, column=3, padx=5, pady=5)
        self.sales_end_date.set_date(datetime.now())
        
        b.Label(filter_frame, text="Menejer:").grid(row=0, column=4, padx=(10, 5), pady=5)
        self.sales_manager_filter = b.Combobox(filter_frame, state="readonly")
        self.sales_manager_filter.grid(row=0, column=5, padx=5, pady=5)
        self.sales_manager_filter.set("Barchasi")

        b.Button(filter_frame, text="Hisobotni Shakllantirish", command=self.generate_sales_report, bootstyle=SUCCESS).grid(row=0, column=6, padx=20, pady=5)

        result_frame = b.LabelFrame(frame, text="Natija", padding=10, bootstyle=SUCCESS)
        result_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        
        self.sales_tree = b.Treeview(result_frame, show="headings", bootstyle=DARK)
        self.sales_tree.pack(fill=BOTH, expand=YES)

    def generate_sales_report(self):
        try:
            filters = {
                'start_date': self.sales_start_date.get(),
                'end_date': self.sales_end_date.get(),
                'manager_name': self.sales_manager_filter.get() if self.sales_manager_filter.get() != "Barchasi" else None
            }
            report_data = database.get_sales_report(filters)

            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            if not report_data:
                messagebox.showinfo("Ma'lumot yo'q", "Tanlangan filtrlar bo'yicha sotuvlar topilmadi.")
                return

            columns = list(report_data[0].keys())
            self.sales_tree['columns'] = columns
            column_widths = {
                'manager_name': 200,
                'product_name': 200,
                'deal_count': 100,
                'total_amount': 150
            }
            for col in columns:
                self.sales_tree.heading(col, text=col.replace('_', ' ').title())
                self.sales_tree.column(col, anchor="center", width=column_widths.get(col, 150))
        
            for row in report_data:
                self.sales_tree.insert("", tk.END, values=list(row.values()))
        except Exception as e:
            messagebox.showerror("Xato", f"Sotuvlar hisobotini shakllantirishda xato: {str(e)}")

    # --- 2. Marketing Hisoboti Vkladkasi ---
    def create_marketing_report_widgets(self):
        frame = self.marketing_tab
        
        filter_frame = b.LabelFrame(frame, text="Filtrlar", padding=15, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)

        b.Label(filter_frame, text="Manba:").grid(row=0, column=0, padx=5, pady=5)
        self.marketing_source_filter = b.Combobox(filter_frame, state="readonly")
        self.marketing_source_filter.grid(row=0, column=1, padx=5, pady=5)
        self.marketing_source_filter.set("Barchasi")
        
        b.Button(filter_frame, text="Hisobotni Shakllantirish", command=self.generate_marketing_report, bootstyle=SUCCESS).grid(row=0, column=2, padx=20, pady=5)

        result_frame = b.LabelFrame(frame, text="Natija", padding=10, bootstyle=SUCCESS)
        result_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        
        self.marketing_tree = b.Treeview(result_frame, show="headings", bootstyle=DARK)
        self.marketing_tree.pack(fill=BOTH, expand=YES)
    
    def generate_marketing_report(self):
        try:
            filters = {
                'source_name': self.marketing_source_filter.get() if self.marketing_source_filter.get() != "Barchasi" else None
            }
            report_data = database.get_marketing_report(filters)

            for item in self.marketing_tree.get_children():
                self.marketing_tree.delete(item)
            if not report_data:
                messagebox.showinfo("Ma'lumot yo'q", "Marketing hisoboti uchun ma'lumot topilmadi.")
                return

            columns = list(report_data[0].keys())
            column_widths = {
                'source_name': 200,
                'customer_count': 100,
                'deal_count': 100,
                'total_amount': 150
            }
            self.marketing_tree['columns'] = columns
            for col in columns:
                self.marketing_tree.heading(col, text=col.replace('_', ' ').title())
                self.marketing_tree.column(col, anchor="center", width=column_widths.get(col, 150))
        
            for row in report_data:
                self.marketing_tree.insert("", tk.END, values=list(row.values()))
        except Exception as e:
            messagebox.showerror("Xato", f"Marketing hisobotini shakllantirishda xato: {str(e)}")

    # --- 3. Moliyaviy Hisobotlar Vkladkasi ---
    def create_financial_report_widgets(self):
        frame = self.financial_tab
        
        filter_frame = b.LabelFrame(frame, text="Umumiy Filtrlar", padding=15, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(filter_frame, text="Dan:").pack(side=LEFT, padx=5)
        self.fin_start_date = b.DateEntry(filter_frame, dateformat='%Y-%m-%d')
        self.fin_start_date.pack(side=LEFT, padx=5)
        self.fin_start_date.set_date(datetime.now())
        
        b.Label(filter_frame, text="Gacha:").pack(side=LEFT, padx=5)
        self.fin_end_date = b.DateEntry(filter_frame, dateformat='%Y-%m-%d')
        self.fin_end_date.pack(side=LEFT, padx=5)
        self.fin_end_date.set_date(datetime.now())
        
        btn_frame = b.Frame(frame, padding=10)
        btn_frame.pack(fill=X, padx=5)
        b.Button(btn_frame, text="Pul Oqimi (Cashflow) Hisoboti", command=self.generate_cashflow_report, bootstyle=PRIMARY).pack(side=LEFT, padx=5)
        b.Button(btn_frame, text="Qarzdorlik (AR/AP) Hisoboti", command=self.generate_ar_ap_report, bootstyle=PRIMARY).pack(side=LEFT, padx=5)

        self.fin_text = ScrolledText(frame, wrap="word", font=("Courier New", 10), autohide=True, state="disabled")
        self.fin_text.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        self.fin_text.tag_configure("h1", font=("Courier New", 14, "bold", "underline"))
        self.fin_text.tag_configure("h2", font=("Courier New", 12, "bold"))
        self.fin_text.tag_configure("total", font=("Courier New", 10, "bold"))

    def generate_cashflow_report(self):
        try:
            start, end = self.fin_start_date.get(), self.fin_end_date.get()
            data = database.get_cashflow_data(start, end)
            if not data:
                messagebox.showinfo("Ma'lumot yo'q", "Cashflow uchun ma'lumotlar topilmadi.")
                return
            
            self.fin_text.text.config(state="normal")
            self.fin_text.text.delete("1.0", tk.END)
            self.fin_text.text.insert(tk.END, f"PUL OQIMI (CASHFLOW) HISOBOTI ({start} - {end})\n\n", "h1")
            self.fin_text.text.insert(tk.END, f"{'Boshlang\'ich qoldiq:':<25}{data['opening_balance']:>20,.2f} UZS\n\n")
            self.fin_text.text.insert(tk.END, f"Pul Kirimlari:\n", "h2")
            for item, value in data['inflows'].items():
                self.fin_text.text.insert(tk.END, f"  {item:<23}{value:>20,.2f} UZS\n")
            self.fin_text.text.insert(tk.END, f"{'Jami kirim:':<25}{data['total_inflow']:>20,.2f} UZS\n\n", "total")
            self.fin_text.text.insert(tk.END, f"Pul Chiqimlari:\n", "h2")
            for item, value in data['outflows'].items():
                self.fin_text.text.insert(tk.END, f"  {item:<23}{value:>20,.2f} UZS\n")
            self.fin_text.text.insert(tk.END, f"{'Jami chiqim:':<25}{data['total_outflow']:>20,.2f} UZS\n\n", "total")
            self.fin_text.text.insert(tk.END, f"{'-'*46}\n")
            self.fin_text.text.insert(tk.END, f"{'Yakuniy qoldiq:':<25}{data['closing_balance']:>20,.2f} UZS\n", "total")
            self.fin_text.text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Xato", f"Cashflow hisobotini shakllantirishda xato: {str(e)}")

    def generate_ar_ap_report(self):
        try:
            end_date = self.fin_end_date.get()
            data = database.get_ar_ap_data(end_date)
            if not data:
                messagebox.showinfo("Ma'lumot yo'q", "Qarzdorlik uchun ma'lumotlar topilmadi.")
                return

            self.fin_text.text.config(state="normal")
            self.fin_text.text.delete("1.0", tk.END)
            self.fin_text.text.insert(tk.END, f"QARZDORLIK (AR/AP) HISOBOTI ({end_date} holatiga)\n\n", "h1")
            self.fin_text.text.insert(tk.END, "Mijozlarning Qarzdorligi (Accounts Receivable):\n", "h2")
            if data['accounts_receivable']:
                for row in data['accounts_receivable']:
                    self.fin_text.text.insert(tk.END, f"  - {row['customer_name']:<25} | {row['invoice_amount']:>15,.2f} UZS (Invoice #{row['invoice_id']})\n")
            else:
                self.fin_text.text.insert(tk.END, "  Mijozlardan qarzdorlik mavjud emas.\n")
            
            self.fin_text.text.insert(tk.END, "\nMajburiyatlar (Accounts Payable):\n", "h2")
            if data['accounts_payable']:
                for row in data['accounts_payable']:
                    self.fin_text.text.insert(tk.END, f"  - {row['operator_name']:<25} | {row['expense_amount']:>15,.2f} UZS\n")
            else:
                self.fin_text.text.insert(tk.END, "  Operatorlar oldida majburiyatlar mavjud emas.\n")
            self.fin_text.text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Xato", f"Qarzdorlik hisobotini shakllantirishda xato: {str(e)}")