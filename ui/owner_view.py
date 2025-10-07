import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from ttkbootstrap import DateEntry, Style
from datetime import datetime, timedelta
from tkinter import messagebox
import database

class OwnerView(b.Frame):
    """Rahbar (Owner) paneli uchun to'liq dinamik va funksional interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        notebook = b.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.dashboard_tab = b.Frame(notebook)
        self.kpi_tab = b.Frame(notebook)
        self.pnl_tab = b.Frame(notebook)
        self.audit_tab = b.Frame(notebook)

        notebook.add(self.dashboard_tab, text="📊 Boshqaruv Paneli (Dashboard)")
        notebook.add(self.kpi_tab, text="🏆 Menejerlar KPI")
        notebook.add(self.pnl_tab, text="💰 Moliyaviy Hisobot (P&L)")
        notebook.add(self.audit_tab, text="📜 Audit Jurnali")
        
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.create_dashboard_widgets()
        self.create_kpi_widgets()
        self.create_pnl_widgets()
        self.create_audit_widgets()
    
    def refresh_data(self):
        """Panelga kerakli barcha dinamik ma'lumotlarni bazadan yangilaydi."""
        print("Rahbar paneli ma'lumotlari yangilanmoqda...")
        try:
            self.refresh_dashboard()
            self.refresh_kpi_treeview()
            self.refresh_audit_treeview()
            self.update_audit_user_filter()
        except Exception as e:
            messagebox.showerror("Xato", f"Ma'lumotlarni yangilashda xato: {str(e)}")

    def on_tab_change(self, event):
        """Vkladka almashganda kerakli ma'lumotlarni yangilaydi."""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        try:
            if "Dashboard" in tab_text:
                self.refresh_dashboard()
            elif "KPI" in tab_text:
                self.refresh_kpi_treeview()
            elif "Audit" in tab_text:
                self.refresh_audit_treeview()
        except Exception as e:
            messagebox.showerror("Xato", f"Vkladka ma'lumotlarini yangilashda xato: {str(e)}")

    # --- 1. Boshqaruv Paneli (Dashboard) Vkladkasi ---
    def create_dashboard_widgets(self):
        frame = self.dashboard_tab
        frame.columnconfigure((0, 1), weight=1)

        top_frame = b.Frame(frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        b.Label(top_frame, text="Asosiy Ko'rsatkichlar", font=("Helvetica", 16, "bold")).pack(side=LEFT)
        self.last_updated_label = b.Label(top_frame, text="")
        self.last_updated_label.pack(side=RIGHT)
        b.Button(top_frame, text="🔄 Yangilash", command=self.refresh_dashboard, bootstyle=SECONDARY).pack(side=RIGHT, padx=10)
        
        self.kpi_vars = {
            'today_income': tk.StringVar(value="0 UZS"),
            'today_expense': tk.StringVar(value="0 UZS"),
            'today_profit': tk.StringVar(value="0 UZS"),
            'month_income': tk.StringVar(value="0 UZS"),
            'month_expense': tk.StringVar(value="0 UZS"),
            'month_profit': tk.StringVar(value="0 UZS"),
            'month_leads': tk.StringVar(value="0 ta"),
            'month_deals': tk.StringVar(value="0 ta"),
            'month_conversion': tk.StringVar(value="0.0 %"),
            'active_deals': tk.StringVar(value="0 ta"),
            'total_customers': tk.StringVar(value="0 ta")
        }

        def create_kpi_card(parent, title, data, row, col):
            card = b.LabelFrame(parent, text=title, padding=15, bootstyle=INFO)
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            for i, (label, var_key, style) in enumerate(data):
                b.Label(card, text=label).pack(anchor="w")
                b.Label(card, textvariable=self.kpi_vars[var_key], font=("", 14, "bold"), bootstyle=style).pack(anchor="w", pady=(0, 10))
        
        create_kpi_card(frame, "Bugungi Moliya", [
            ("Kirim:", 'today_income', SUCCESS),
            ("Chiqim:", 'today_expense', DANGER),
            ("Sof Foyda:", 'today_profit', '')
        ], 1, 0)
        create_kpi_card(frame, "Shu Oy Moliya", [
            ("Kirim:", 'month_income', SUCCESS),
            ("Chiqim:", 'month_expense', DANGER),
            ("Sof Foyda:", 'month_profit', '')
        ], 1, 1)
        create_kpi_card(frame, "Marketing (shu oy)", [
            ("Yangi Leadlar:", 'month_leads', ''),
            ("Yopilgan Kelishuvlar:", 'month_deals', ''),
            ("Konversiya:", 'month_conversion', SUCCESS)
        ], 2, 0)
        create_kpi_card(frame, "Umumiy Holat", [
            ("Aktiv Kelishuvlar:", 'active_deals', ''),
            ("Jami Mijozlar:", 'total_customers', '')
        ], 2, 1)

    def refresh_dashboard(self):
        """Dashboard ma'lumotlarini yangilaydi."""
        try:
            stats = database.get_dashboard_stats()
            if not stats:
                messagebox.showinfo("Info", "Dashboard ma'lumotlari topilmadi.")
                return

            today_profit = stats.get('today_income', 0) - stats.get('today_expense', 0)
            month_profit = stats.get('month_income', 0) - stats.get('month_expense', 0)
            conversion = (stats.get('month_deals', 0) / stats.get('month_leads', 1)) * 100 if stats.get('month_leads') else 0

            self.kpi_vars['today_income'].set(f"{stats.get('today_income', 0):,} UZS")
            self.kpi_vars['today_expense'].set(f"{stats.get('today_expense', 0):,} UZS")
            self.kpi_vars['today_profit'].set(f"{today_profit:,} UZS")
            self.kpi_vars['month_income'].set(f"{stats.get('month_income', 0):,} UZS")
            self.kpi_vars['month_expense'].set(f"{stats.get('month_expense', 0):,} UZS")
            self.kpi_vars['month_profit'].set(f"{month_profit:,} UZS")
            self.kpi_vars['month_leads'].set(f"{stats.get('month_leads', 0)} ta")
            self.kpi_vars['month_deals'].set(f"{stats.get('month_deals', 0)} ta")
            self.kpi_vars['month_conversion'].set(f"{conversion:.1f} %")
            self.kpi_vars['active_deals'].set(f"{stats.get('active_deals', 0)} ta")
            self.kpi_vars['total_customers'].set(f"{stats.get('total_customers', 0)} ta")
            self.last_updated_label.config(text=f"Yangilandi: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            messagebox.showerror("Xato", f"Dashboardni yangilashda xato: {str(e)}")

    # --- 2. Menejerlar KPI Vkladkasi ---
    def create_kpi_widgets(self):
        frame = self.kpi_tab
        filter_frame = b.LabelFrame(frame, text="Vaqt Oralig'i", padding=10, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(filter_frame, text="Dan:").pack(side=LEFT, padx=5)
        self.kpi_start_date = DateEntry(filter_frame, dateformat='%Y-%m-%d', width=12)
        self.kpi_start_date.set_date(datetime.now().replace(day=1))
        self.kpi_start_date.pack(side=LEFT, padx=5)
        
        b.Label(filter_frame, text="Gacha:").pack(side=LEFT, padx=5)
        self.kpi_end_date = DateEntry(filter_frame, dateformat='%Y-%m-%d', width=12)
        self.kpi_end_date.pack(side=LEFT, padx=5)
        
        b.Button(filter_frame, text="Ko'rsatish", command=self.refresh_kpi_treeview, bootstyle=SECONDARY).pack(side=LEFT, padx=10)

        tree_frame = b.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        columns = ("menejer", "yangi_lead", "yopilgan_deal", "sotuv_summa", "konversiya")
        self.kpi_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        
        self.kpi_tree.heading("menejer", text="Menejer")
        self.kpi_tree.heading("yangi_lead", text="Yangi Leadlar")
        self.kpi_tree.heading("yopilgan_deal", text="Yopilgan Kelishuvlar")
        self.kpi_tree.heading("sotuv_summa", text="Sotuv Summasi (UZS)")
        self.kpi_tree.heading("konversiya", text="Konversiya %")
        self.kpi_tree.column("yangi_lead", anchor="center")
        self.kpi_tree.column("yopilgan_deal", anchor="center")
        self.kpi_tree.column("sotuv_summa", anchor="e")
        self.kpi_tree.column("konversiya", anchor="center")
        self.kpi_tree.pack(fill=BOTH, expand=YES)

    def refresh_kpi_treeview(self):
        """KPI jadvalini yangilaydi."""
        try:
            for item in self.kpi_tree.get_children():
                self.kpi_tree.delete(item)
            kpi_data = database.get_manager_kpi(self.kpi_start_date.get(), self.kpi_end_date.get())
            for row in kpi_data:
                self.kpi_tree.insert("", END, values=row)
        except Exception as e:
            messagebox.showerror("Xato", f"KPI jadvalini yangilashda xato: {str(e)}")

    # --- 3. Moliyaviy Hisobot (P&L) Vkladkasi ---
    def create_pnl_widgets(self):
        frame = self.pnl_tab
        filter_frame = b.LabelFrame(frame, text="Vaqt Oralig'i", padding=10, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(filter_frame, text="Dan:").pack(side=LEFT, padx=5)
        self.pnl_start_date = DateEntry(filter_frame, dateformat='%Y-%m-%d', width=12)
        self.pnl_start_date.pack(side=LEFT, padx=5)

        b.Label(filter_frame, text="Gacha:").pack(side=LEFT, padx=5)
        self.pnl_end_date = DateEntry(filter_frame, dateformat='%Y-%m-%d', width=12)
        self.pnl_end_date.pack(side=LEFT, padx=5)

        b.Button(filter_frame, text="Hisobotni Shakllantirish", command=self.generate_pnl_report, bootstyle=SUCCESS).pack(side=LEFT, padx=10)

        style = b.Style()
        bg_color = style.colors.bg
        fg_color = style.colors.fg

        self.pnl_text = tk.Text(
            frame,
            wrap="word",
            font=("Courier New", 10),
            height=20,
            relief="flat",
            background=bg_color,
            foreground=fg_color
        )
        self.pnl_text.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        self.pnl_text.tag_configure("h1", font=("Courier New", 14, "bold", "underline"))
        self.pnl_text.tag_configure("h2", font=("Courier New", 12, "bold"))
        self.pnl_text.tag_configure("total", font=("Courier New", 10, "bold"))
        self.pnl_text.config(state="disabled")

    def generate_pnl_report(self):
        """P&L hisobotini shakllantiradi."""
        try:
            pnl_data = database.generate_pnl_report(self.pnl_start_date.get(), self.pnl_end_date.get())
            if not pnl_data:
                messagebox.showinfo("Info", "Hisobot uchun ma'lumot topilmadi.")
                return
            
            self.pnl_text.config(state="normal")
            self.pnl_text.delete("1.0", tk.END)
            
            self.pnl_text.insert(END, f"FOYDA VA ZARARLAR TO'G'RISIDA HISOBOT\n", "h1")
            self.pnl_text.insert(END, f"({pnl_data['start_date']} - {pnl_data['end_date']})\n\n")
            self.pnl_text.insert(END, f"{'Daromad (Revenue)':<30} {pnl_data['revenue']:>20,.2f} UZS\n")
            self.pnl_text.insert(END, f"{'Sotilgan mahsulot tannarxi (COGS)':<30} {pnl_data['cogs']:>20,.2f} UZS\n")
            self.pnl_text.insert(END, f"{'-'*51}\n")
            self.pnl_text.insert(END, f"{'Yalpi foyda':<30} {pnl_data['gross_profit']:>20,.2f} UZS\n\n", "total")
            self.pnl_text.insert(END, f"Operatsion Xarajatlar (OPEX):\n", "h2")
            for item, value in pnl_data['opex'].items():
                self.pnl_text.insert(END, f"  {item:<28} {value:>20,.2f} UZS\n")
            self.pnl_text.insert(END, f"{'Jami OPEX':<30} {pnl_data['total_opex']:>20,.2f} UZS\n\n", "total")
            self.pnl_text.insert(END, f"{'-'*51}\n")
            self.pnl_text.insert(END, f"{'Sof Foyda':<30} {pnl_data['net_profit']:>20,.2f} UZS\n", "total")
            
            self.pnl_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Xato", f"Hisobotni shakllantirishda xato: {str(e)}")

    # --- 4. Audit Jurnali Vkladkasi ---
    def create_audit_widgets(self):
        frame = self.audit_tab
        filter_frame = b.LabelFrame(frame, text="Filtrlar", padding=10, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(filter_frame, text="Foydalanuvchi:").pack(side=LEFT, padx=(0,5))
        self.audit_user_filter = b.Combobox(filter_frame, state="readonly")
        self.audit_user_filter.pack(side=LEFT, padx=5)

        b.Label(filter_frame, text="Harakat bo'yicha izlash:").pack(side=LEFT, padx=(10,5))
        self.audit_action_filter = b.Entry(filter_frame)
        self.audit_action_filter.pack(side=LEFT, padx=5)
        
        b.Button(filter_frame, text="Qidirish", command=self.refresh_audit_treeview, bootstyle=SECONDARY).pack(side=LEFT, padx=10)

        tree_frame = b.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        columns = ("id", "vaqt", "user", "harakat", "obyekt", "obyekt_id", "tafsilot")
        self.audit_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)

        self.audit_tree.heading("id", text="ID")
        self.audit_tree.heading("vaqt", text="Vaqt")
        self.audit_tree.heading("user", text="Foydalanuvchi")
        self.audit_tree.heading("harakat", text="Harakat")
        self.audit_tree.heading("obyekt", text="Obyekt")
        self.audit_tree.heading("obyekt_id", text="Obyekt ID")
        self.audit_tree.heading("tafsilot", text="Tafsilot")
        self.audit_tree.column("id", width=50)
        self.audit_tree.column("vaqt", width=150)
        self.audit_tree.pack(fill=BOTH, expand=YES)

    def update_audit_user_filter(self):
        """Audit foydalanuvchi filtrini yangilaydi."""
        try:
            users = ["Barchasi"] + [u['full_name'] for u in database.get_users()]
            self.audit_user_filter['values'] = users
            self.audit_user_filter.set("Barchasi")
        except Exception as e:
            messagebox.showerror("Xato", f"Foydalanuvchi filtrini yangilashda xato: {str(e)}")

    def refresh_audit_treeview(self):
        """Audit jadvalini yangilaydi."""
        try:
            for item in self.audit_tree.get_children():
                self.audit_tree.delete(item)
            filters = {
                'user_name': self.audit_user_filter.get() if self.audit_user_filter.get() != "Barchasi" else None,
                'action': self.audit_action_filter.get().strip()
            }
            audit_logs = database.get_audit_logs(filters)
            for log in audit_logs:
                self.audit_tree.insert("", END, values=log)
        except Exception as e:
            messagebox.showerror("Xato", f"Audit jadvalini yangilashda xato: {str(e)}")