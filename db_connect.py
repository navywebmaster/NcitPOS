import mysql.connector
from mysql.connector import Error
import pyodbc
import sqlite3

class ConnectSQLite:
    def __init__(self, db_path="prismadb.db"):
        self.db_path = db_path
        self.conn = None

    def open(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("เชื่อมต่อ SQLite สำเร็จ")
            return True
        except Exception as e:
            print(f"เชื่อมต่อ SQLite ล้มเหลว: {e}")
            return False

    def get_cursor(self):
        if self.conn:
            return self.conn.cursor()
        return None

    def close(self):
        if self.conn:
            self.conn.close()
            print("ปิดการเชื่อมต่อแล้ว")
            self.conn = None

    def get_connection(self):
        return self.conn

    def commit(self):
        if self.conn:
            self.conn.commit()

class ConnectSQLServer:
    def __init__(self, host='localhost', user='sa', password='C15e082542', database='prismadb', port=1433, driver="ODBC Driver 18 for SQL Server"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.driver = driver
        self.conn = None

    def open(self):
        try:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password};"
                "TrustServerCertificate=yes;"   # ป้องกัน SSL Error
            )
            self.conn = pyodbc.connect(conn_str, timeout=5)
            return True
        except Exception as e:
            print(f"เชื่อมต่อ SQL Server ล้มเหลว: {e}")
            return False

    def get_cursor(self):
        if self.conn:
            return self.conn.cursor()
        return None

    def close(self):
        if self.conn:
            self.conn.close()

class Connect:
    def __init__(self, host='localhost', user='root', password='virus', database='prismadb', port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def open(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.conn.is_connected():
                print ("เชื่อมต่อฐานข้อมูลเรียบร้อย")
                return True
            else:
                return False
        except Error as e:
            print(f"เชื่อมต่อฐานข้อมูลล้มเหลว: {e}")
            return False

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def get_cursor(self):
        if self.conn and self.conn.is_connected():
            return self.conn.cursor()
        else:
            return None

    # ตัวอย่างฟังก์ชัน query ข้อมูล
    def get_tables(self):
        tables = []
        if self.open():
            cursor = self.get_cursor()
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            self.close()
        return tables