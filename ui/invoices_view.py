import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from tkcalendar import DateEntry
from tkinter import messagebox
import database

class InvoicesView(b.Frame):
    """Hisob-fakturalarni (Invoyslarni) boshqarish uchun to'liq interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        filter_frame = b.LabelFrame(self, text="Filtrlar", padding=15, bootstyle=INFO)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        b.Label(filter_frame, text="Holati:").pack(side=LEFT, padx=(0, 5))
        self.status_filter = b.Combobox(filter_frame, state="readonly", values=["Barchasi", "Yangi", "Tolanmagan", "Qisman to'langan", "To'langan", "Bekor qilingan"])
        self.status_filter.pack(side=LEFT, padx=5)
        self.status_filter.set("Barchasi")
        
        b.Button(filter_frame, text="Filterlash", command=self.refresh_data, bootstyle=SECONDARY).pack(side=LEFT, padx=10)

        tree_frame = b.LabelFrame(self, text="Barcha Invoyslar", padding=10, bootstyle=SUCCESS)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        
        columns = ("id", "raqam", "mijoz", "summa", "holati", "sana", "tolov_sana")
        self.invoices_tree = b.Treeview(tree_frame, columns=columns, show="headings", bootstyle=DARK)
        self.invoices_tree.heading("id", text="ID")
        self.invoices_tree.heading("raqam", text="Raqami #")
        self.invoices_tree.heading("mijoz", text="Mijoz")
        self.invoices_tree.heading("summa", text="Summa")
        self.invoices_tree.heading("holati", text="Holati")
        self.invoices_tree.heading("sana", text="Yaratilgan sana")
        self.invoices_tree.heading("tolov_sana", text="To'lov sanasi")
        self.invoices_tree.column("id", width=50, anchor="center")
        self.invoices_tree.column("raqam", width=100)
        self.invoices_tree.column("mijoz", width=150)
        self.invoices_tree.column("summa", width=100)
        self.invoices_tree.column("holati", width=100)
        self.invoices_tree.column("sana", width=100)
        self.invoices_tree.column("tolov_sana", width=100)
        self.invoices_tree.tag_configure("To'langan", background="#2E7D32")
        self.invoices_tree.tag_configure("Bekorqilingan", background="#C62828")
        self.invoices_tree.tag_configure("To'lanmagan", background="#FFB300")
        self.invoices_tree.tag_configure("Qismantolangan", background="#FFCA28")
        self.invoices_tree.pack(fill=BOTH, expand=YES)

        action_frame = b.Frame(self)
        action_frame.pack(fill=X, padx=10, pady=5)
        b.Button(action_frame, text="➕ Yangi Invoys...", command=self.open_invoice_editor, bootstyle=SUCCESS).pack(side=LEFT)
        b.Button(action_frame, text="To'lov Kiritish...", command=self.open_payment_recorder, bootstyle=PRIMARY).pack(side=RIGHT, padx=10)
        b.Button(action_frame, text="PDF Yuklab Olish", command=self.generate_pdf, bootstyle=SECONDARY).pack(side=RIGHT)

        self.refresh_data()

    def refresh_data(self):
        """Invoyslar ro'yxatini yangilaydi."""
        try:
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)
            filters = {'status': self.status_filter.get() if self.status_filter.get() != "Barchasi" else None}
            invoices = database.get_filtered_invoices(filters)
            for invoice in invoices:
                status_tag = invoice[4].replace(" ", "")
                self.invoices_tree.insert("", END, values=invoice, tags=(status_tag,))
        except Exception as e:
            messagebox.showerror("Xatolik", f"Invoyslarni yuklashda xato: {str(e)}")

    def open_invoice_editor(self, invoice_id=None):
        """Invoys tahrirlash oynasini ochadi."""
        InvoiceEditorWindow(self, self.controller, invoice_id, self.refresh_data)

    def open_payment_recorder(self):
        """To'lov kiritish oynasini ochadi."""
        selected = self.invoices_tree.selection()
        if not selected:
            return messagebox.showwarning("Xatolik", "To'lov kiritish uchun avval invoysni tanlang.")
        
        values = self.invoices_tree.item(selected[0])['values']
        invoice_id = values[0]
        total_due_str = values[3]  # e.g., "12,000,000 UZS"
        try:
            total_due = float(total_due_str.replace(',', '').split(' ')[0])
        except (ValueError, IndexError):
            total_due = 0.0
            messagebox.showwarning("Ogohlantirish", "Summa noto'g'ri formatda, 0 deb qabul qilindi.")

        RecordPaymentWindow(self, self.controller, invoice_id, total_due, self.refresh_data)

    def generate_pdf(self):
        """Tanlangan invoys uchun PDF yaratadi (mock)."""
        selected = self.invoices_tree.selection()
        if not selected:
            return messagebox.showwarning("Xatolik", "PDF yaratish uchun avval invoysni tanlang.")
        invoice_id = self.invoices_tree.item(selected[0])['values'][0]
        messagebox.showinfo("Info", f"ID={invoice_id} invoys uchun PDF yaratish funksiyasi chaqirildi.\nBu funksiyani alohida modulda yaratish kerak.")

class InvoiceEditorWindow(tk.Toplevel):
    """Invoys qo'shish yoki tahrirlash oynasi."""

    def __init__(self, parent, controller, invoice_id=None, callback=None):
        super().__init__(parent)
        self.invoice_id, self.callback = invoice_id, callback
        self.controller = controller
        self.title("Yangi Invoys" if not invoice_id else f"Invoys #{invoice_id} Tahrirlash")
        self.geometry("500x300")
        
        self.vars = {k: tk.StringVar() for k in ['deal_id', 'amount', 'currency', 'status', 'due_date']}

        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)
        container.columnconfigure(1, weight=1)

        b.Label(container, text="Kelishuv (Deal)*:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.deal_combo = b.Combobox(container, textvariable=self.vars['deal_id'], state="readonly")
        self.deal_combo.grid(row=0, column=1, sticky="ew")
        
        b.Label(container, text="Summa*:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['amount']).grid(row=1, column=1, sticky="ew")
        
        b.Label(container, text="Valyuta:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        b.Combobox(container, textvariable=self.vars['currency'], values=["UZS", "USD"], state="readonly").grid(row=2, column=1, sticky="ew")
        
        b.Label(container, text="Holati:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        b.Combobox(container, textvariable=self.vars['status'], values=["Yangi", "To'lanmagan", "Qisman to'langan", "To'langan", "Bekor qilingan"], state="readonly").grid(row=3, column=1, sticky="ew")
        
        b.Label(container, text="To'lov Sanasi:").grid(row=4, column=0, sticky="w", padx=5, pady=8)
        DateEntry(container, textvariable=self.vars['due_date'], date_pattern='yyyy-mm-dd').grid(row=4, column=1, sticky="ew")

        btn_frame = b.Frame(container)
        btn_frame.grid(row=5, column=1, sticky="e", pady=20)
        b.Button(btn_frame, text="Saqlash", command=self.save, bootstyle=SUCCESS).pack()
        
        self.populate_form()
        self.grab_set()

    def populate_form(self):
        """Forma maydonlarini to'ldiradi."""
        try:
            deals = database.get_deals_for_invoice_form()
            self.deal_map = {f"{d_id}: {c_name}" for d_id, c_name, d_title in deals}
            self.deal_combo['values'] = list(self.deal_map.keys())
            if self.invoice_id:
                invoice = database.get_invoice_by_id(self.invoice_id)
                if invoice:
                    self.deal_combo.set(f"{invoice['deal_id']}: {invoice.get('customer_name', '')}")
                    self.vars['amount'].set(str(invoice['amount']))
                    self.vars['currency'].set(invoice['currency'])
                    self.vars['status'].set(invoice['status'])
                    self.vars['due_date'].set(invoice['due_date'])
        except Exception as e:
            messagebox.showerror("Xatolik", f"Forma ma'lumotlarini yuklashda xato: {str(e)}", parent=self)

    def save(self):
        """Invoysni saqlaydi."""
        try:
            data = {key: var.get() for key, var in self.vars.items()}
            data['deal_id'] = self.deal_map.get(data['deal_id'])
            if not data['deal_id'] or not data['amount']:
                return messagebox.showerror("Xatolik", "Kelishuv va Summa kiritilishi shart!", parent=self)
            data['amount'] = float(data['amount'])
            if self.invoice_id:
                database.update_invoice(self.invoice_id, data)
            else:
                database.add_invoice(data)
            if self.callback:
                self.callback()
            messagebox.showinfo("Muvaffaqiyatli", "Invoys saqlandi.")
            self.destroy()
        except ValueError:
            messagebox.showerror("Xatolik", "Summa maydoniga raqam kiriting!", parent=self)
        except Exception as e:
            messagebox.showerror("Xatolik", f"Invoysni saqlashda xato: {str(e)}", parent=self)

class RecordPaymentWindow(tk.Toplevel):
    """To'lov kiritish oynasi."""

    def __init__(self, parent, controller, invoice_id, total_due, callback):
        super().__init__(parent)
        self.invoice_id, self.total_due, self.callback = invoice_id, total_due, callback
        self.controller = controller
        self.title(f"Invoys #{invoice_id} uchun to'lov")
        self.geometry("400x350")
        
        self.vars = {
            'amount': tk.DoubleVar(),
            'channel': tk.StringVar(),
            'paid_at': tk.StringVar(value=datetime.now().strftime('%Y-%m-%d')),
            'trx_id': tk.StringVar()
        }
        
        container = b.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)
        container.columnconfigure(1, weight=1)

        b.Label(container, text=f"Invoys Raqami: #{self.invoice_id}", font=("", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        b.Label(container, text=f"Jami summa: {self.total_due:,.2f} UZS", bootstyle=INFO).grid(row=1, column=0, columnspan=2, pady=(0, 10))

        b.Label(container, text="To'lov summasi*:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['amount']).grid(row=2, column=1, sticky="ew")
        
        b.Label(container, text="To'lov usuli*:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        b.Combobox(container, textvariable=self.vars['channel'], values=["CASH", "CARD", "BANK"], state="readonly").grid(row=3, column=1, sticky="ew")
        
        b.Label(container, text="To'lov sanasi*:").grid(row=4, column=0, sticky="w", padx=5, pady=8)
        DateEntry(container, textvariable=self.vars['paid_at'], date_pattern='yyyy-mm-dd').grid(row=4, column=1, sticky="ew")

        b.Label(container, text="Tranzaksiya ID (ixtiyoriy):").grid(row=5, column=0, sticky="w", padx=5, pady=8)
        b.Entry(container, textvariable=self.vars['trx_id']).grid(row=5, column=1, sticky="ew")
        
        b.Button(container, text="To'lovni Saqlash", command=self.save_payment, bootstyle=SUCCESS).grid(row=6, column=1, sticky="e", pady=20)
        self.grab_set()

    def save_payment(self):
        """To'lovni saqlaydi."""
        try:
            payment_data = {key: var.get() for key, var in self.vars.items()}
            payment_data['invoice_id'] = self.invoice_id
            if not payment_data['amount'] > 0 or not payment_data['channel']:
                return messagebox.showerror("Xatolik", "Summa va To'lov usuli kiritilishi shart!", parent=self)
            
            database.record_payment_for_invoice(payment_data)
            if self.callback:
                self.callback()
            messagebox.showinfo("Muvaffaqiyatli", "To'lov muvaffaqiyatli saqlandi.")
            self.destroy()
        except tk.TclError:
            messagebox.showerror("Xatolik", "Summa maydoniga raqam kiriting!", parent=self)
        except Exception as e:
            messagebox.showerror("Xatolik", f"To'lovni saqlashda xato: {str(e)}", parent=self)