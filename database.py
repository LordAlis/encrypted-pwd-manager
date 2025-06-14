import sqlite3
import json
import base64
import os
from encryption_utils import derive_key, encrypt, decrypt

class Database:
    def __init__(self, db_file='vault.db', master_password_file='master_pass.json'):
        self.db_file = db_file
        self.master_password_file = master_password_file
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                ciphertext TEXT NOT NULL,
                salt TEXT NOT NULL,
                iv TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

    def load_master_password_data(self):
        if os.path.exists(self.master_password_file):
            try:
                with open(self.master_password_file, 'r') as f:
                    data = json.load(f)
                    data['hashed_password'] = base64.b64decode(data['hashed_password'])
                    data['salt'] = base64.b64decode(data['salt'])
                    return data
            except (json.JSONDecodeError, KeyError) as e:
                raise Exception("Master password file corrupted. Please delete 'master_pass.json' and restart.")
        return None

    def save_master_password_data(self, hashed_password_bytes, salt_bytes):
        data = {
            'hashed_password': base64.b64encode(hashed_password_bytes).decode('utf-8'),
            'salt': base64.b64encode(salt_bytes).decode('utf-8')
        }
        with open(self.master_password_file, 'w') as f:
            json.dump(data, f)
        return data

    def load_vault_entries(self):
        entries = []
        try:
            self.cursor.execute('SELECT id, site, username, ciphertext, salt, iv FROM entries')
            rows = self.cursor.fetchall()
            for row in rows:
                db_id, site, username, ciphertext, salt, iv = row
                entries.append({
                    'id': db_id,
                    'site': site,
                    'username': username,
                    'password_enc': {
                        'ciphertext': ciphertext,
                        'salt': salt,
                        'iv': iv
                    }
                })
            return entries
        except sqlite3.Error as e:
            raise Exception(f"Failed to load entries from database: {e}")

    def save_entry(self, site, username, encrypted_data):
        try:
            self.cursor.execute(
                'INSERT INTO entries (site, username, ciphertext, salt, iv) VALUES (?, ?, ?, ?, ?)',
                (site, username, encrypted_data['ciphertext'], encrypted_data['salt'], encrypted_data['iv'])
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Failed to save entry: {e}")

    def update_entry(self, entry_id, site, username, encrypted_data):
        try:
            self.cursor.execute(
                'UPDATE entries SET site = ?, username = ?, ciphertext = ?, salt = ?, iv = ? WHERE id = ?',
                (site, username, encrypted_data['ciphertext'], encrypted_data['salt'], encrypted_data['iv'], entry_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Failed to update entry: {e}")

    def delete_entry(self, entry_id):
        try:
            self.cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Failed to delete entry: {e}") 