import tkinter as tk
import ttkbootstrap as b
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox
import database

class InvoicesView(b.Frame):
    """Invoyslarni boshqarish uchun interfeys."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Interfeys elementlarini yaratadi."""
        main_frame = b.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        # Filtrlash bo'limi
        filter_frame = b.LabelFrame(main_frame, text="Filtrlash", padding=10, bootstyle=INFO)
        filter_frame.pack(fill=X, pady=10)

        b.Label(filter_frame, text="Mijoz ID:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.customer_id_entry = b.Entry(filter_frame)
        self.customer_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)

        b.Label(filter_frame, text="Status:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.status_combobox = b.Combobox(filter_frame, values=["ALL", "PAID", "UNPAID"], state="readonly")
        self.status_combobox.grid(row=0, column=3, padx=5, pady=5, sticky=EW)
        self.status_combobox.current(0)

        b.Button(filter_frame, text="Filtrlash", command=self.refresh_data, bootstyle=PRIMARY).grid(row=0, column=4, padx=5, pady=5)

        # Invoyslar ro'yxati
        tree_frame = b.Frame(main_frame)
        tree_frame.pack(fill=BOTH, expand=YES, pady=10)

        self.tree = b.Treeview(tree_frame, columns=("ID", "Mijoz", "Miqdor", "Sana", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Mijoz", text="Mijoz")
        self.tree.heading("Miqdor", text="Miqdor")
        self.tree.heading("Sana", text="Sana")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=BOTH, expand=YES)

        # Tugmalar
        button_frame = b.Frame(main_frame)
        button_frame.pack(fill=X, pady=10)

        b.Button(button_frame, text="Yangi invoys", command=lambda: self.open_invoice_editor(None), bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        b.Button(button_frame, text="Tahrirlash", command=lambda: self.open_invoice_editor(self.get_selected_invoice()), bootstyle=PRIMARY).pack(side=LEFT, padx=5)
        b.Button(button_frame, text="O'chirish", command=self.delete_invoice, bootstyle=DANGER).pack(side=LEFT, padx=5)
        b.Button(button_frame, text="Orqaga", command=lambda: self.controller.show_frame("DashboardView"), bootstyle=SECONDARY).pack(side=RIGHT, padx=5)

        self.refresh_data()

    def refresh_data(self):
        """Invoyslar ro'yxatini yangilaydi."""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            customer_id = self.customer_id_entry.get().strip()
            status = self.status_combobox.get()
            invoices = database.get_filtered_invoices(customer_id=customer_id if customer_id else None, status=status if status != "ALL" else None)
            for invoice in invoices:
                self.tree.insert("", tk.END, values=(
                    invoice['id'],
                    invoice['customer_name'],
                    invoice['amount'],
                    invoice['due_date'],
                    invoice['status']
                ))
        except Exception as e:
            print(f"Xato: Invoyslarni yangilashda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Invoyslarni yangilashda xato: {str(e)}", parent=self)

    def get_selected_invoice(self):
        """Tanlangan invoys ID sini qaytaradi."""
        selected = self.tree.selection()
        if selected:
            return self.tree.item(selected[0])['values'][0]
        return None

    def open_invoice_editor(self, invoice_id):
        """Invoys tahrirlash oynasini ochadi."""
        try:
            InvoiceEditorWindow(self, self.controller, invoice_id, self.refresh_data)
        except Exception as e:
            print(f"Xato: Invoys tahrirlash oynasini ochishda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Invoys tahrirlash oynasini ochishda xato: {str(e)}", parent=self)

    def delete_invoice(self):
        """Tanlangan invoysni o'chiradi."""
        invoice_id = self.get_selected_invoice()
        if invoice_id:
            try:
                database.delete_invoice(invoice_id)
                messagebox.showinfo("Muvaffaqiyat", "Invoys muvaffaqiyatli o'chirildi!", parent=self)
                self.refresh_data()
            except Exception as e:
                print(f"Xato: Invoysni o'chirishda xato: {str(e)}")
                messagebox.showerror("Xatolik", f"Invoysni o'chirishda xato: {str(e)}", parent=self)
        else:
            messagebox.showwarning("Xatolik", "Iltimos, o'chirish uchun invoys tanlang!", parent=self)

class InvoiceEditorWindow(b.Toplevel):
    """Invoys tahrirlash yoki qo'shish uchun oyna."""

    def __init__(self, parent, controller, invoice_id=None, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.invoice_id = invoice_id
        self.refresh_callback = refresh_callback
        self.title("Invoys tahrirlash" if invoice_id else "Yangi invoys")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()
        self.create_widgets()

    def create_widgets(self):
        """Interfeys elementlarini yaratadi."""
        container = b.Frame(self)
        container.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        self.vars = {}
        labels = ["Mijoz ID:", "Miqdor:", "Sana:", "Status:"]
        fields = ["customer_id", "amount", "due_date", "status"]

        for i, (label, field) in enumerate(zip(labels, fields)):
            b.Label(container, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=W)
            if field == "due_date":
                self.vars[field] = tk.StringVar()
                b.Entry(container, textvariable=self.vars[field]).grid(row=i, column=1, sticky="ew")

            elif field == "status":
                self.vars[field] = tk.StringVar()
                b.Combobox(container, textvariable=self.vars[field], values=["PAID", "UNPAID"], state="readonly").grid(row=i, column=1, sticky="ew")
            else:
                self.vars[field] = tk.StringVar()
                b.Entry(container, textvariable=self.vars[field]).grid(row=i, column=1, sticky="ew")

        if self.invoice_id:
            self.load_invoice_data()

        button_frame = b.Frame(container)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)
        b.Button(button_frame, text="Saqlash", command=self.save_invoice, bootstyle=PRIMARY).pack(side=LEFT, padx=5)
        b.Button(button_frame, text="Bekor qilish", command=self.destroy, bootstyle=SECONDARY).pack(side=LEFT, padx=5)

        container.columnconfigure(1, weight=1)

    def load_invoice_data(self):
        """Invoys ma'lumotlarini yuklaydi."""
        try:
            invoice = database.get_invoice_by_id(self.invoice_id)
            if invoice:
                self.vars['customer_id'].set(invoice['customer_id'])
                self.vars['amount'].set(invoice['amount'])
                self.vars['due_date'].set(invoice['due_date'])
                self.vars['status'].set(invoice['status'])
        except Exception as e:
            print(f"Xato: Invoys ma'lumotlarini yuklashda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Invoys ma'lumotlarini yuklashda xato: {str(e)}", parent=self)

    def save_invoice(self):
        """Invoysni saqlaydi."""
        try:
            data = {field: var.get() for field, var in self.vars.items()}
            if not all(data.values()):
                messagebox.showerror("Xatolik", "Barcha maydonlarni to'ldiring!", parent=self)
                return
            if self.invoice_id:
                database.update_invoice(self.invoice_id, data)
            else:
                database.add_invoice(data)
            messagebox.showinfo("Muvaffaqiyat", "Invoys muvaffaqiyatli saqlandi!", parent=self)
            if self.refresh_callback:
                self.refresh_callback()
            self.destroy()
        except Exception as e:
            print(f"Xato: Invoysni saqlashda xato: {str(e)}")
            messagebox.showerror("Xatolik", f"Invoysni saqlashda xato: {str(e)}", parent=self)