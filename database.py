import sqlite3
import hashlib
import os
from datetime import datetime

# Konfiguratsiya
class config:
    DB_NAME = 'sayyod_tour.db'

# --- Yordamchi funksiyalar ---

def get_connection():
    """Ma'lumotlar bazasiga ulanish va sozlamalarni ta'minlaydi."""
    conn = sqlite3.connect(config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def _hash_password(password, salt):
    """Berilgan parol va tuz yordamida hash generatsiya qiladi."""
    salted_password = salt.encode('utf-8') + password.encode('utf-8')  # UTF-8 kodlash
    return hashlib.sha256(salted_password).hexdigest()

def _add_audit_log(cursor, user_id, action, entity, entity_id, details=""):
    """Audit jurnaliga yozuv qo'shadi."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO audit_logs (user_id, action, entity, entity_id, details, at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, action, entity, entity_id, details, timestamp))

# --- Dastlabki sozlash ---

def create_all_tables():
    """Barcha kerakli jadvallarni yaratadi (agar mavjud bo'lmasa)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                login TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('OWNER', 'MANAGER', 'MARKETING', 'ACCOUNTANT', 'WORKER')),
                is_active BOOLEAN DEFAULT 1,
                twofa_secret TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                phone TEXT,
                source TEXT,
                interest TEXT,
                passport TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                source TEXT,
                status TEXT DEFAULT 'Yangi',
                assigned_to_id INTEGER,
                contact_date TEXT,
                note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                campaign TEXT,
                interest TEXT,
                temperature TEXT,
                FOREIGN KEY(assigned_to_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                manager_id INTEGER,
                product_id INTEGER,
                stage TEXT,
                amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(id),
                FOREIGN KEY(manager_id) REFERENCES users(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id INTEGER,
                number TEXT,
                amount REAL,
                currency TEXT,
                status TEXT DEFAULT 'Yangi',
                due_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deal_id) REFERENCES deals(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                channel TEXT,
                amount REAL,
                paid_at TEXT,
                trx_id TEXT,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                amount REAL,
                date TEXT,
                payee TEXT,
                note TEXT,
                file TEXT,
                status TEXT DEFAULT "Tolanmagan",
                operator_id INTEGER,
                FOREIGN KEY(category_id) REFERENCES categories(id),
                FOREIGN KEY(operator_id) REFERENCES operators(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cashboxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT DEFAULT 'BANK'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cashbox_id INTEGER,
                direction TEXT,
                amount REAL,
                date TEXT,
                category_id INTEGER,
                note TEXT,
                payee TEXT,
                ref_type TEXT,
                ref_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT,
                FOREIGN KEY(cashbox_id) REFERENCES cashboxes(id),
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                country TEXT,
                nights INTEGER,
                base_price REAL,
                operator_id INTEGER,
                inclusions TEXT,
                FOREIGN KEY(operator_id) REFERENCES operators(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                contact TEXT,
                contract_file TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                entity TEXT,
                entity_id INTEGER,
                details TEXT,
                at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_whitelist (
                ip_address TEXT PRIMARY KEY
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deal_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                report_date TEXT,
                calls INTEGER,
                meetings INTEGER,
                sales_count INTEGER,
                sales_amount REAL,
                expense_amount REAL,
                expense_note TEXT,
                expense_file TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lead_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                user_id INTEGER,
                note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(lead_id) REFERENCES leads(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        print("Barcha jadvallar muvaffaqiyatli yaratildi yoki tekshirildi.")
    except sqlite3.Error as e:
        print(f"Xato: Jadvallarni yaratishda xato yuz berdi: {str(e)}")
        raise
    finally:
        conn.close()

# --- Sozlamalar va Admin funksiyalari ---

def get_setting(key, default_value=None):
    """Berilgan sozlama qiymatini qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else default_value
    except sqlite3.Error as e:
        print(f"Xato: Sozlama olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def update_setting(key, value):
    """Sozlama qiymatini yangilaydi yoki qo'shadi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        print(f"Sozlama '{key}' muvaffaqiyatli yangilandi.")
    except sqlite3.Error as e:
        print(f"Xato: Sozlama yangilashda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_ip_whitelist():
    """IP ruxsatnomasi ro'yxatini qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address FROM ip_whitelist ORDER BY ip_address")
        return [row['ip_address'] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: IP ruxsatnomasini olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def add_ip_to_whitelist(ip):
    """IP manzilni ruxsatnomaga qo'shadi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO ip_whitelist (ip_address) VALUES (?)", (ip,))
        conn.commit()
        print(f"IP '{ip}' ruxsatnomaga qo'shildi.")
    except sqlite3.Error as e:
        print(f"Xato: IP ruxsatnomaga qo'shishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def delete_ip_from_whitelist(ip):
    """IP manzilni ruxsatnomadan o'chiradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ip_whitelist WHERE ip_address = ?", (ip,))
        conn.commit()
        print(f"IP '{ip}' ruxsatnomadan o'chirildi.")
    except sqlite3.Error as e:
        print(f"Xato: IP ruxsatnomadan o'chirishda xato: {str(e)}")
        raise
    finally:
        conn.close()

# --- Foydalanuvchi va autentifikatsiya ---

def verify_user_credentials(username, password):
    """Foydalanuvchi login va parolini tekshiradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE login = ? AND is_active = 1", (username,))
        user = cursor.fetchone()
        if user:
            password_hash = _hash_password(password, user['salt'])
            print(f"Input password: {password}, Salt: {user['salt']}, Generated hash: {password_hash}, Stored hash: {user['password_hash']}")  # Debug
            if password_hash == user['password_hash']:
                user_data = dict(user)
                del user_data['password_hash'], user_data['salt']
                user_data['requires_2fa'] = bool(user_data.get('twofa_secret')) or user_data.get('role') in ['OWNER', 'ACCOUNTANT']
                return user_data
        return None
    except sqlite3.Error as e:
        print(f"Xato: Foydalanuvchi autentifikatsiyasida xato: {str(e)}")
        raise
    finally:
        conn.close()


def check_2fa_code(username, code):
    """Ikki faktorli autentifikatsiya kodini tekshiradi (mock)."""
    return username == "boss" and code == "123456"

def get_all_users():
    """Barcha foydalanuvchilarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, phone, login, role, IIF(is_active, 'Aktiv', 'Bloklangan') AS status FROM users ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Foydalanuvchilarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_users(role=None):
    """Foydalanuvchilarni roliga qarab qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if role:
            cursor.execute("SELECT id, full_name FROM users WHERE role = ? AND is_active = 1", (role,))
        else:
            cursor.execute("SELECT id, full_name FROM users WHERE is_active = 1")
        return [(row['id'], row['full_name']) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Foydalanuvchilarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_user_details(user_id):
    """Foydalanuvchi ma'lumotlarini ID bo'yicha qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, phone, login, role, is_active FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    except sqlite3.Error as e:
        print(f"Xato: Foydalanuvchi ma'lumotlarini olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def add_user(data):
    """Yangi foydalanuvchi qo'shadi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        salt = os.urandom(16).hex()
        password_hash = _hash_password(data['password'], salt)
        print(f"Adding user: {data['login']}, Password: {data['password']}, Salt: {salt}, Hash: {password_hash}")  # Debug
        cursor.execute("""
            INSERT INTO users (full_name, phone, login, password_hash, salt, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['full_name'],
            data.get('phone', ''),
            data['login'],
            password_hash,
            salt,
            data['role'],
            1,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        user_id = cursor.lastrowid
        _add_audit_log(cursor, 1, "CREATE", "USER", user_id, f"Foydalanuvchi qo'shildi: {data['login']}")
        conn.commit()
        print(f"Foydalanuvchi '{data['login']}' qo'shildi.")
    except sqlite3.Error as e:
        print(f"Xato: Foydalanuvchi qo'shishda xato: {str(e)}")
        raise
    finally:
        conn.close()


# --- Invoys funksiyalari ---

def get_filtered_invoices(filters):
    """Filtrlangan invoyslarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT i.id, i.number AS raqam, c.full_name AS mijoz,
                   i.amount || ' ' || i.currency AS summa,
                   i.status AS holati, i.created_at AS sana, i.due_date AS tolov_sana
            FROM invoices i
            JOIN deals d ON i.deal_id = d.id
            JOIN customers c ON d.customer_id = c.id
            WHERE 1=1
        """
        params = []
        if filters.get('status'):
            query += " AND i.status = ?"
            params.append(filters['status'])
        query += " ORDER BY i.created_at DESC"
        cursor.execute(query, params)
        return [(
            row['id'],
            row['raqam'] or f"INV-{row['id']:04d}",
            row['mijoz'],
            row['summa'],
            row['holati'],
            row['sana'],
            row['tolov_sana'] or ""
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Invoyslarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_deals_for_invoice_form():
    """Invoys formasi uchun kelishuvlarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, c.full_name, p.title
            FROM deals d
            JOIN customers c ON d.customer_id = c.id
            JOIN products p ON d.product_id = p.id
            WHERE d.stage NOT IN ('Bekor qilindi')
            ORDER BY d.created_at DESC
        """)
        return [(row['id'], row['full_name'], row['title']) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Kelishuvlarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def add_invoice(data):
    """Yangi invoys qo'shadi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute("""
            INSERT INTO invoices (deal_id, number, amount, currency, status, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['deal_id'],
            number,
            data['amount'],
            data.get('currency', 'UZS'),
            data.get('status', 'Yangi'),
            data['due_date'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        invoice_id = cursor.lastrowid
        _add_audit_log(cursor, 1, "CREATE", "INVOICE", invoice_id, f"Invoys qo'shildi: {number}")
        conn.commit()
        print(f"Invoys '{number}' qo'shildi.")
    except sqlite3.Error as e:
        print(f"Xato: Invoys qo'shishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def update_invoice(invoice_id, data):
    """Invoysni yangilaydi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE invoices
            SET deal_id = ?, amount = ?, currency = ?, status = ?, due_date = ?
            WHERE id = ?
        """, (
            data['deal_id'],
            data['amount'],
            data.get('currency', 'UZS'),
            data.get('status', 'Yangi'),
            data['due_date'],
            invoice_id
        ))
        _add_audit_log(cursor, 1, "UPDATE", "INVOICE", invoice_id, "Invoys ma'lumotlari yangilandi")
        conn.commit()
        print(f"Invoys ID={invoice_id} yangilandi.")
    except sqlite3.Error as e:
        print(f"Xato: Invoysni yangilashda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_invoice_by_id(invoice_id):
    """Invoysni ID bo'yicha qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, i.deal_id, i.number, i.amount, i.currency, i.status, i.due_date, i.created_at,
                   c.full_name AS customer_name
            FROM invoices i
            JOIN deals d ON i.deal_id = d.id
            JOIN customers c ON d.customer_id = c.id
            WHERE i.id = ?
        """, (invoice_id,))
        invoice = cursor.fetchone()
        return dict(invoice) if invoice else None
    except sqlite3.Error as e:
        print(f"Xato: Invoysni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def record_payment_for_invoice(payment_data):
    """Invoys uchun to'lovni qayd etadi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payments (invoice_id, channel, amount, paid_at, trx_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            payment_data['invoice_id'],
            payment_data['channel'],
            payment_data['amount'],
            payment_data['paid_at'],
            payment_data.get('trx_id')
        ))
        payment_id = cursor.lastrowid
        cursor.execute("""
            SELECT SUM(amount) AS total_paid
            FROM payments
            WHERE invoice_id = ?
        """, (payment_data['invoice_id'],))
        total_paid = cursor.fetchone()['total_paid'] or 0.0
        cursor.execute("SELECT amount FROM invoices WHERE id = ?", (payment_data['invoice_id'],))
        invoice_amount = cursor.fetchone()['amount']
        if total_paid >= invoice_amount:
            new_status = "Tolangan"
        elif total_paid > 0:
            new_status = "Qisman tolangan"
        else:
            new_status = "Tolanmagan"
        cursor.execute("UPDATE invoices SET status = ? WHERE id = ?", (new_status, payment_data['invoice_id']))
        _add_audit_log(cursor, 1, "CREATE", "PAYMENT", payment_id, f"Invoys ID={payment_data['invoice_id']} uchun to'lov qayd etildi")
        conn.commit()
        print(f"Invoys ID={payment_data['invoice_id']} uchun to'lov qayd etildi.")
    except sqlite3.Error as e:
        print(f"Xato: To'lovni qayd etishda xato: {str(e)}")
        raise
    finally:
        conn.close()

# --- Mijozlar va kelishuvlar ---

def search_customers(search_term):
    """Mijozlarni ism yoki telefon bo'yicha qidiradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        search_term = f"%{search_term}%"
        cursor.execute("""
            SELECT id, full_name, phone, source, interest, passport, created_at, updated_at
            FROM customers
            WHERE full_name LIKE ? OR phone LIKE ?
            ORDER BY full_name
        """, (search_term, search_term))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Mijozlarni qidirishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def search_customer(customer_id):
    """Mijozni ID bo'yicha qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, phone, source, interest, passport, created_at, updated_at
            FROM customers
            WHERE id = ?
        """, (customer_id,))
        customer = cursor.fetchone()
        return dict(customer) if customer else None
    except sqlite3.Error as e:
        print(f"Xato: Mijozni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_filtered_deals(filters):
    """Filtrlangan kelishuvlarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT d.id, c.full_name AS customer_name, u.full_name AS manager_name,
                   p.title AS product_title, d.stage, d.amount, d.created_at, d.updated_at
            FROM deals d
            JOIN customers c ON d.customer_id = c.id
            JOIN users u ON d.manager_id = u.id
            JOIN products p ON d.product_id = p.id
            WHERE 1=1
        """
        params = []
        if filters.get('stage'):
            query += " AND d.stage = ?"
            params.append(filters['stage'])
        if filters.get('customer_id'):
            query += " AND d.customer_id = ?"
            params.append(filters['customer_id'])
        if filters.get('manager_id'):
            query += " AND d.manager_id = ?"
            params.append(filters['manager_id'])
        query += " ORDER BY d.created_at DESC"
        cursor.execute(query, params)
        return [(
            row['id'],
            row['customer_name'],
            row['manager_name'],
            row['product_title'],
            row['stage'],
            f"{row['amount']:,.2f} UZS",
            row['created_at'],
            row['updated_at'] or ""
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Kelishuvlarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

# --- Yangi funksiyalar ---

def get_deal_sources():
    """Kelishuv manbalarini qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM deal_sources ORDER BY name")
        return [(row['id'], row['name']) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Kelishuv manbalarini olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_dashboard_stats():
    """Boshqaruv paneli uchun statistik ma'lumotlarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) AS total FROM customers")
        stats['total_customers'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM deals WHERE stage NOT IN ('Bekor qilindi', 'Yakunlandi')")
        stats['active_deals'] = cursor.fetchone()['total']
        cursor.execute("SELECT SUM(amount) AS total FROM invoices WHERE status != 'Tolanmagan'")
        stats['total_invoiced'] = cursor.fetchone()['total'] or 0.0
        cursor.execute("SELECT SUM(amount) AS total FROM payments")
        stats['total_paid'] = cursor.fetchone()['total'] or 0.0
        return stats
    except sqlite3.Error as e:
        print(f"Xato: Statistik ma'lumotlarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_cashboxes():
    """Kassa qutilarini qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type FROM cashboxes ORDER BY name")
        return [(row['id'], row['name'], row['type']) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Kassa qutilarini olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_categories():
    """Kategoriyalar ro'yxatini qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        return [(row['id'], row['name']) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Kategoriyalarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_all_products():
    """Barcha mahsulotlarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.title, p.country, p.nights, p.base_price, o.name AS operator_name
            FROM products p
            LEFT JOIN operators o ON p.operator_id = o.id
            ORDER BY p.title
        """)
        return [(
            row['id'],
            row['title'],
            row['country'] or "",
            row['nights'] or 0,
            f"{row['base_price']:,.2f} UZS",
            row['operator_name'] or ""
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Mahsulotlarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_all_operators():
    """Barcha operatorlarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, contact, contract_file
            FROM operators
            ORDER BY name
        """)
        return [(
            row['id'],
            row['name'],
            row['contact'] or "",
            row['contract_file'] or ""
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Operatorlarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_unmatched_cash_entries(direction):
    """Tasdiqlanmagan kirim yoki chiqim yozuvlarini qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT ce.id, ce.date AS sana, ce.amount AS summa, ce.note AS izoh
            FROM cash_entries ce
            WHERE ce.direction = ? AND ce.ref_type IS NULL
            ORDER BY ce.date DESC
        """
        cursor.execute(query, (direction,))
        return [(
            row['id'],
            row['sana'],
            f"{row['summa']:,.2f} UZS",
            row['izoh'] or ""
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Tasdiqlanmagan kassa yozuvlarini olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_unpaid_invoices():
    """Tolanmagan invoyslarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, c.full_name AS mijoz, i.amount AS summa, i.created_at AS sana
            FROM invoices i
            JOIN deals d ON i.deal_id = d.id
            JOIN customers c ON d.customer_id = c.id
            WHERE i.status IN ('Yangi', 'Qisman tolangan')
            ORDER BY i.created_at DESC
        """)
        return [(
            row['id'],
            row['mijoz'],
            f"{row['summa']:,.2f} UZS",
            row['sana']
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Tolanmagan invoyslarni olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_unpaid_operator_expenses():
    """Operatorlarga tolanmagan xarajatlarni qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, o.name AS operator, e.amount AS summa, e.date AS sana
            FROM expenses e
            JOIN operators o ON e.operator_id = o.id
            WHERE e.status IN ('Tolanmagan', 'Qisman tolangan')
            ORDER BY e.date DESC
        """)
        return [(
            row['id'],
            row['operator'],
            f"{row['summa']:,.2f} UZS",
            row['sana']
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Operator xarajatlarini olishda xato: {str(e)}")
        raise
    finally:
        conn.close()

def reconcile_invoice_payment(cash_entry_id, invoice_id):
    """Kassa kirim yozuvini invoys bilan bog'laydi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cash_entries
            SET ref_type = ?, ref_id = ?, updated_at = ?
            WHERE id = ?
        """, (
            'INVOICE',
            invoice_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            cash_entry_id
        ))
        cursor.execute("SELECT amount FROM cash_entries WHERE id = ?", (cash_entry_id,))
        cash_amount = cursor.fetchone()['amount']
        cursor.execute("INSERT INTO payments (invoice_id, channel, amount, paid_at) VALUES (?, ?, ?, ?)",
                       (invoice_id, 'CASH', cash_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        payment_id = cursor.lastrowid
        cursor.execute("SELECT SUM(amount) AS total_paid FROM payments WHERE invoice_id = ?", (invoice_id,))
        total_paid = cursor.fetchone()['total_paid'] or 0.0
        cursor.execute("SELECT amount FROM invoices WHERE id = ?", (invoice_id,))
        invoice_amount = cursor.fetchone()['amount']
        if total_paid >= invoice_amount:
            new_status = "Tolangan"
        elif total_paid > 0:
            new_status = "Qisman tolangan"
        else:
            new_status = "Tolanmagan"
        cursor.execute("UPDATE invoices SET status = ? WHERE id = ?", (new_status, invoice_id))
        _add_audit_log(cursor, 1, "RECONCILE", "INVOICE_PAYMENT", payment_id, f"Kirim ID {cash_entry_id} invoys ID {invoice_id} bilan bog'landi")
        conn.commit()
        print(f"Kirim ID {cash_entry_id} invoys ID {invoice_id} bilan bog'landi.")
    except sqlite3.Error as e:
        print(f"Xato: Invoys bog'lashda xato: {str(e)}")
        raise
    finally:
        conn.close()

def reconcile_expense_payment(cash_entry_id, expense_id):
    """Kassa chiqim yozuvini xarajat bilan bog'laydi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cash_entries
            SET ref_type = ?, ref_id = ?, updated_at = ?
            WHERE id = ?
        """, (
            'EXPENSE',
            expense_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            cash_entry_id
        ))
        cursor.execute("SELECT amount FROM cash_entries WHERE id = ?", (cash_entry_id,))
        cash_amount = cursor.fetchone()['amount']
        cursor.execute("SELECT SUM(amount) AS total_paid FROM cash_entries WHERE ref_type = 'EXPENSE' AND ref_id = ?", (expense_id,))
        total_paid = cursor.fetchone()['total_paid'] or 0.0
        cursor.execute("SELECT amount FROM expenses WHERE id = ?", (expense_id,))
        expense_amount = cursor.fetchone()['amount']
        if total_paid >= expense_amount:
            new_status = "Tolangan"
        elif total_paid > 0:
            new_status = "Qisman tolangan"
        else:
            new_status = "Tolanmagan"
        cursor.execute("UPDATE expenses SET status = ? WHERE id = ?", (new_status, expense_id))
        _add_audit_log(cursor, 1, "RECONCILE", "EXPENSE_PAYMENT", expense_id, f"Chiqim ID {cash_entry_id} xarajat ID {expense_id} bilan bog'landi")
        conn.commit()
        print(f"Chiqim ID {cash_entry_id} xarajat ID {expense_id} bilan bog'landi.")
    except sqlite3.Error as e:
        print(f"Xato: Xarajat bog'lashda xato: {str(e)}")
        raise
    finally:
        conn.close()

def get_cash_journal_entries(filters):
    """Filtrlangan kassa jurnali yozuvlarini qaytaradi."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT ce.id, ce.date AS sana, ce.amount AS summa, ce.direction AS yonalish,
                   cb.name AS kassa, c.name AS kategoriya, ce.note AS izoh
            FROM cash_entries ce
            JOIN cashboxes cb ON ce.cashbox_id = cb.id
            LEFT JOIN categories c ON ce.category_id = c.id
            WHERE 1=1
        """
        params = []
        if filters.get('start_date'):
            query += " AND ce.date >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND ce.date <= ?"
            params.append(filters['end_date'])
        if filters.get('cashbox_id'):
            query += " AND ce.cashbox_id = ?"
            params.append(filters['cashbox_id'])
        if filters.get('category_id'):
            query += " AND ce.category_id = ?"
            params.append(filters['category_id'])
        query += " ORDER BY ce.date DESC"
        cursor.execute(query, params)
        return [(
            row['id'],
            row['sana'],
            f"{row['summa']:,.2f} UZS",
            row['yonalish'],
            row['kassa'],
            row['kategoriya'] or "",
            row['izoh'] or ""
        ) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Xato: Kassa jurnali yozuvlarini olishda xato: {str(e)}")
        raise
    finally:
        conn.close()