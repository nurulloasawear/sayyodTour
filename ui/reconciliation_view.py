# ui/reconciliation_view.py

import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkinter import messagebox

# MUHIM: Bu panel ishlashi uchun database.py da ushbu fayl oxirida ko'rsatilgan
# barcha funksiyalarni yaratgan bo'lishingiz SHART.
import database

class ReconciliationView(b.Frame):
    """Moliyaviy taqqoslash (Matching) uchun maxsus interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Tanlangan elementlarni saqlash uchun
        self.selected_inflow_id = None
        self.selected_invoice_id = None
        self.selected_outflow_id = None
        self.selected_expense_id = None

        notebook = b.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.customer_tab = b.Frame(notebook)
        self.operator_tab = b.Frame(notebook)

        notebook.add(self.customer_tab, text="📥 Mijoz To'lovlari")
        notebook.add(self.operator_tab, text="📤 Operator To'lovlari")

        self.create_customer_payment_widgets()
        self.create_operator_payment_widgets()

        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_data())

    def refresh_data(self):
        """Panelga kerakli barcha dinamik ma'lumotlarni bazadan yangilaydi."""
        print("Taqqoslash paneli ma'lumotlari yangilanmoqda...")
        self.refresh_customer_tab_views()
        self.refresh_operator_tab_views()
    
    def _create_treeview_pane(self, parent, title, columns_config):
        """Yordamchi funksiya: Taqqoslash uchun oyna (pane) yaratadi."""
        pane = b.LabelFrame(parent, text=title, padding=10, bootstyle=INFO)
        pane.pack(side=LEFT, fill=BOTH, expand=YES, padx=10, pady=10)
        
        columns = [key for key, val in columns_config.items()]
        tree = b.Treeview(pane, columns=columns, show="headings", bootstyle=DARK, height=15)
        
        for key, val in columns_config.items():
            tree.heading(key, text=val['text'])
            tree.column(key, width=val['width'], anchor=val.get('anchor', 'w'))
            
        tree.pack(fill=BOTH, expand=YES)
        return tree

    # --- 1. Mijoz To'lovlarini Taqqoslash Vkladkasi ---
    def create_customer_payment_widgets(self):
        frame = self.customer_tab

        inflow_cols = {
            "id": {"text": "ID", "width": 40, "anchor": "center"}, "sana": {"text": "Sana", "width": 90},
            "summa": {"text": "Summa", "width": 120, "anchor": "e"}, "izoh": {"text": "Izoh", "width": 250}
        }
        self.inflow_tree = self._create_treeview_pane(frame, "Tasdiqlanmagan Kirimlar (Bank/Kassa)", inflow_cols)
        self.inflow_tree.bind('<<TreeviewSelect>>', self.on_inflow_select)

        action_pane = b.Frame(frame)
        action_pane.pack(side=LEFT, fill=Y, padx=10, pady=10)
        self.match_button_customer = b.Button(action_pane, text="✅\nBog'lash\n(Match)", command=self.match_payment_to_invoice, bootstyle=SUCCESS, state="disabled")
        self.match_button_customer.pack(expand=YES, pady=20)
        self.customer_selection_label = b.Label(action_pane, text="Kirim: Tanlanmagan\nInvoys: Tanlanmagan", justify=LEFT)
        self.customer_selection_label.pack(expand=YES)

        invoice_cols = {
            "id": {"text": "Invoys ID", "width": 80, "anchor": "center"}, "mijoz": {"text": "Mijoz", "width": 180},
            "summa": {"text": "Summa", "width": 120, "anchor": "e"}, "sana": {"text": "Sana", "width": 90}
        }
        self.invoice_tree = self._create_treeview_pane(frame, "To'lanmagan Invoyslar", invoice_cols)
        self.invoice_tree.bind('<<TreeviewSelect>>', self.on_invoice_select)

    def refresh_customer_tab_views(self):
        for item in self.inflow_tree.get_children(): self.inflow_tree.delete(item)
        inflows = database.get_unmatched_cash_entries('Kirim')
        for inflow in inflows: self.inflow_tree.insert("", END, values=inflow)

        for item in self.invoice_tree.get_children(): self.invoice_tree.delete(item)
        invoices = database.get_unpaid_invoices()
        for invoice in invoices: self.invoice_tree.insert("", END, values=invoice)
        
        self.selected_inflow_id = None
        self.selected_invoice_id = None
        self.update_customer_match_button_state()

    def on_inflow_select(self, event):
        selected = self.inflow_tree.selection()
        if selected: self.selected_inflow_id = self.inflow_tree.item(selected[0])['values'][0]
        self.update_customer_match_button_state()

    def on_invoice_select(self, event):
        selected = self.invoice_tree.selection()
        if selected: self.selected_invoice_id = self.invoice_tree.item(selected[0])['values'][0]
        self.update_customer_match_button_state()
        
    def update_customer_match_button_state(self):
        self.customer_selection_label.config(text=f"Kirim ID: {self.selected_inflow_id or '...'}\nInvoys ID: {self.selected_invoice_id or '...'}")
        self.match_button_customer.config(state="normal" if self.selected_inflow_id and self.selected_invoice_id else "disabled")

    def match_payment_to_invoice(self):
        if not (self.selected_inflow_id and self.selected_invoice_id): return
        if messagebox.askyesno("Tasdiqlash", f"Kirim ID {self.selected_inflow_id} ni Invoys ID {self.selected_invoice_id} bilan bog'lashni tasdiqlaysizmi?"):
            try:
                database.reconcile_invoice_payment(self.selected_inflow_id, self.selected_invoice_id)
                messagebox.showinfo("Muvaffaqiyatli", "Operatsiya muvaffaqiyatli bog'landi!")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Xatolik", f"Bog'lashda xatolik yuz berdi: {e}")

    # --- 2. Operator To'lovlarini Taqqoslash Vkladkasi ---
    def create_operator_payment_widgets(self):
        frame = self.operator_tab

        outflow_cols = {
            "id": {"text": "ID", "width": 40, "anchor": "center"}, "sana": {"text": "Sana", "width": 90},
            "summa": {"text": "Summa", "width": 120, "anchor": "e"}, "izoh": {"text": "Izoh", "width": 250}
        }
        self.outflow_tree = self._create_treeview_pane(frame, "Tasdiqlanmagan Chiqimlar (Bank/Kassa)", outflow_cols)
        self.outflow_tree.bind('<<TreeviewSelect>>', self.on_outflow_select)

        action_pane = b.Frame(frame)
        action_pane.pack(side=LEFT, fill=Y, padx=10, pady=10)
        self.match_button_operator = b.Button(action_pane, text="✅\nBog'lash\n(Match)", command=self.match_payment_to_expense, bootstyle=SUCCESS, state="disabled")
        self.match_button_operator.pack(expand=YES, pady=20)
        self.operator_selection_label = b.Label(action_pane, text="Chiqim: Tanlanmagan\nXarajat: Tanlanmagan", justify=LEFT)
        self.operator_selection_label.pack(expand=YES)

        expense_cols = {
            "id": {"text": "Xarajat ID", "width": 80, "anchor": "center"}, "operator": {"text": "Operator", "width": 180},
            "summa": {"text": "Summa", "width": 120, "anchor": "e"}, "sana": {"text": "Sana", "width": 90}
        }
        self.expense_tree = self._create_treeview_pane(frame, "Operatorlarga To'lovlar", expense_cols)
        self.expense_tree.bind('<<TreeviewSelect>>', self.on_expense_select)

    def refresh_operator_tab_views(self):
        for item in self.outflow_tree.get_children(): self.outflow_tree.delete(item)
        outflows = database.get_unmatched_cash_entries('Chiqim')
        for outflow in outflows: self.outflow_tree.insert("", END, values=outflow)

        for item in self.expense_tree.get_children(): self.expense_tree.delete(item)
        expenses = database.get_unpaid_operator_expenses()
        for expense in expenses: self.expense_tree.insert("", END, values=expense)

        self.selected_outflow_id = None
        self.selected_expense_id = None
        self.update_operator_match_button_state()

    def on_outflow_select(self, event):
        selected = self.outflow_tree.selection()
        if selected: self.selected_outflow_id = self.outflow_tree.item(selected[0])['values'][0]
        self.update_operator_match_button_state()
        
    def on_expense_select(self, event):
        selected = self.expense_tree.selection()
        if selected: self.selected_expense_id = self.expense_tree.item(selected[0])['values'][0]
        self.update_operator_match_button_state()
        
    def update_operator_match_button_state(self):
        self.operator_selection_label.config(text=f"Chiqim ID: {self.selected_outflow_id or '...'}\nXarajat ID: {self.selected_expense_id or '...'}")
        self.match_button_operator.config(state="normal" if self.selected_outflow_id and self.selected_expense_id else "disabled")

    def match_payment_to_expense(self):
        if not (self.selected_outflow_id and self.selected_expense_id): return
        if messagebox.askyesno("Tasdiqlash", f"Chiqim ID {self.selected_outflow_id} ni Xarajat ID {self.selected_expense_id} bilan bog'lashni tasdiqlaysizmi?"):
            try:
                database.reconcile_expense_payment(self.selected_outflow_id, self.selected_expense_id)
                messagebox.showinfo("Muvaffaqiyatli", "Operatsiya muvaffaqiyatli bog'landi!")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Xatolik", f"Bog'lashda xatolik yuz berdi: {e}")