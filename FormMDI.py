import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMdiArea, QMdiSubWindow,
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStatusBar, QTableWidget, QTableWidgetItem, QAbstractItemView, 
    QLineEdit, QDialog, QGroupBox, QButtonGroup, QRadioButton, QComboBox, QTextEdit, QSpinBox, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QDate, QTime, QTimer
from button_style import *
from db_connect import Connect, ConnectSQLServer, ConnectSQLite
from datetime import datetime
import sqlite3

class CustomerForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ค้นหาข้อมูลลูกค้า")
        self.setFixedSize(620, 680)
        layout = QVBoxLayout()

        # ----- กลุ่ม Radio -----
        group1 = QGroupBox("เลือกชนิดการค้นหา")
        group1_layout = QHBoxLayout()
        radio_options = [
            "ค้นหาตามรหัสลูกค้า",
            "ค้นหาตามชื่อ-นามสกุลลูกค้า",
            "ค้นหาตามอีเมล",
            "ค้นหาข้อมูลตามหมายเลขโทรศัพท์"
        ]
        self.radiobuttons = []
        self.radio_group = QButtonGroup(self)
        for option in radio_options:
            rb = QRadioButton(option, self)
            self.radiobuttons.append(rb)
            self.radio_group.addButton(rb)
            if option == "ค้นหาตามรหัสลูกค้า":
                rb.setChecked(True)
            group1_layout.addWidget(rb)
        group1.setLayout(group1_layout)
        layout.addWidget(group1)

        # ----- ช่องกรอกข้อมูล & ปุ่ม -----
        hbox_search = QHBoxLayout()
        self.txtCustomerSearch = QLineEdit(self)
        self.txtCustomerSearch.setPlaceholderText("กรอกข้อมูลลูกค้าที่ต้องการค้นหา...")
        self.txtCustomerSearch.setFixedHeight(45)
        self.txtCustomerSearch.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtCustomerSearch.setFocus()
        self.btnSearch = QPushButton(QIcon("icons/Hopstarter-Soft-Scraps-Zoom.256.png"), "ค้นหาข้อมูล")
        self.btnSearch.setIconSize(QSize(24, 24))
        self.btnSearch.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnSearch.setStyleSheet(btnSearch_style)
        self.btnSearch.clicked.connect(self.search_customer)
        hbox_search.addWidget(self.txtCustomerSearch)
        hbox_search.addWidget(self.btnSearch)
        layout.addLayout(hbox_search)

        # ----- ตาราง/แถวข้อมูล -----
        layout.addLayout(self.create_table_row())

        # ----- กลุ่มเพิ่มข้อมูลใหม่ -----
        group2 = QGroupBox("เพิ่มข้อมูลใหม่")
        group2_layout = QVBoxLayout()

        # ชื่อ-นามสกุลลูกค้า
        label_name = QLabel("ชื่อ-นามสกุลลูกค้า :", self)
        label_name.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtCustomerName = QLineEdit(self)
        self.txtCustomerName.setFixedHeight(40)
        self.txtCustomerName.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtCustomerName.setEnabled(False)
        label_email = QLabel("อีเมลลูกค้า :", self)
        label_email.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtEmail = QLineEdit(self)
        self.txtEmail.setFixedHeight(40)
        self.txtEmail.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtEmail.setEnabled(False)
        label_Telephone = QLabel("หมายเลขโทรศัพท์ลูกค้า :", self)
        label_Telephone.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtTelephone = QLineEdit(self)
        self.txtTelephone.setFixedHeight(40)
        self.txtTelephone.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtTelephone.setEnabled(False)
        group2_layout.addWidget(label_name)
        group2_layout.addWidget(self.txtCustomerName)
        group2_layout.addWidget(label_email)
        group2_layout.addWidget(self.txtEmail)
        group2_layout.addWidget(label_Telephone)
        group2_layout.addWidget(self.txtTelephone)

        hbox_button_group = QHBoxLayout()
        self.btnAdd = QPushButton(QIcon("icons/Oxygen-Icons.org-Oxygen-Actions-list-add.256.png"), "เพิ่ม")
        self.btnAdd.setIconSize(QSize(24, 24))
        self.btnAdd.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnAdd.setStyleSheet(btnSearch_style)
        self.btnAdd.clicked.connect(self.add_customer)

        self.btnSave = QPushButton(QIcon("icons/Custom-Icon-Design-Pretty-Office-7-Save-as.256.png"), "บันทึก")
        self.btnSave.setIconSize(QSize(24, 24))
        self.btnSave.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnSave.setStyleSheet(btnSearch_style)
        self.btnSave.setEnabled(False)
        self.btnSave.clicked.connect(self.save_customer)

        self.btnDelete = QPushButton(QIcon("icons/Hopstarter-Sleek-Xp-Basic-Close-2.256.png"), "ลบ")
        self.btnDelete.setIconSize(QSize(24, 24))
        self.btnDelete.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnDelete.setStyleSheet(btnSearch_style)
        self.btnDelete.setEnabled(False)
        self.btnDelete.clicked.connect(self.delete_customer)

        self.btnClear = QPushButton(QIcon("icons/Gartoon-Team-Gartoon-Action-Edit-clear-broom.256.png"), "เคลียร์")
        self.btnClear.setIconSize(QSize(24, 24))
        self.btnClear.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnClear.setStyleSheet(btnSearch_style)
        self.btnClear.clicked.connect(self.clear_fields)

        self.btnClose = QPushButton(QIcon("icons/Visualpharm-Must-Have-Log-Out.256.png"), "ปิด")
        self.btnClose.setIconSize(QSize(24, 24))
        self.btnClose.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnClose.setStyleSheet(btnSearch_style)
        self.btnClose.clicked.connect(self.close)
    
        hbox_button_group.addWidget(self.btnAdd)
        hbox_button_group.addWidget(self.btnSave)
        hbox_button_group.addWidget(self.btnDelete)
        hbox_button_group.addWidget(self.btnClear)
        hbox_button_group.addWidget(self.btnClose)
        group2_layout.addLayout(hbox_button_group)

        group2.setLayout(group2_layout)
        layout.addWidget(group2)

        self.setLayout(layout)

    def search_customer(self):
        keyword = self.txtCustomerSearch.text().strip()
        search_mode = None
        for rb in self.radiobuttons:
            if rb.isChecked():
                search_mode = rb.text()
                break

        sql = "SELECT id, name, email, tel FROM customer"
        params = []

        if not keyword:
            # ถ้าไม่ใส่อะไร ให้แสดงทั้งหมด
            pass
        elif search_mode == "ค้นหาตามรหัสลูกค้า":
            sql += " WHERE id = ?"
            params.append(keyword)
        elif search_mode == "ค้นหาตามชื่อ-นามสกุลลูกค้า":
            sql += " WHERE name LIKE ?"
            params.append(f"%{keyword}%")
        elif search_mode == "ค้นหาตามอีเมล":
            sql += " WHERE email LIKE ?"
            params.append(f"%{keyword}%")
        elif search_mode == "ค้นหาข้อมูลตามหมายเลขโทรศัพท์":
            sql += " WHERE tel = ?"
            params.append(keyword)
        else:
            # fallback
            pass

        db = ConnectSQLite()
        rows = []
        if db.open():
            cursor = db.get_cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
            db.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def save_customer(self):
        name = self.txtCustomerName.text()
        email = self.txtEmail.text()
        telephone = self.txtTelephone.text()
        now = datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S") + f".{int(now.microsecond/1000):03d}"
        updated_at = created_at

        if not name:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อลูกค้าด้วยค่ะ !")
            return
        
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                if hasattr(self, "current_customer_id") and self.current_customer_id is not None:
                    # ----- Update -----
                    sql = "UPDATE customer SET name=?, email=?, tel=?, updatedAdd=? WHERE id=?"
                    cursor.execute(sql, (name, email, telephone, created_at, updated_at, self.current_customer_id))
                    QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลลูกค้าเรียบร้อยแล้ว")
                else:
                    # ----- Add -----
                    sql = "INSERT INTO customer (name, email, tel, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?)"
                    cursor.execute(sql, (name, email, telephone, created_at, updated_at))
                    QMessageBox.information(self, "สำเร็จ", "เพิ่มข้อมูลสินค้าเรียบร้อยแล้ว")
                self.current_customer_id = None
                db.commit()
                cursor.close()
                db.close()
                self.refresh_table()
                self.clear_and_disable_fields()
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "เกิดข้อผิดพลาด", f"ไม่สามารถเพิ่มข้อมูลได้ (ข้อมูลซ้ำหรือข้อผิดพลาด):\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ผิดพลาด: {e}")

    def add_customer(self):
        self.btnAdd.setEnabled(False)
        self.btnSave.setEnabled(True)
        self.btnDelete.setEnabled(True)
        self.txtCustomerName.setEnabled(True)
        self.txtEmail.setEnabled(True)
        self.txtTelephone.setEnabled(True)

    def delete_customer(self):
        if not hasattr(self, "current_customer_id") or self.current_customer_id is None:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกรายการรายชื่อลูกค้าที่ต้องการลบ")
            return

        reply = QMessageBox.question(self, "ยืนยันการลบ", "คุณต้องการลบรายชื่อลูกค้านี้จริงหรือไม่?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        db = ConnectSQLite()
        try:
            if db.open():
                cursor = db.get_cursor()
                sql = "DELETE FROM customer WHERE id = ?"
                cursor.execute(sql, (self.current_customer_id,))
                db.conn.commit()
                cursor.close()
                db.close()
                QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลลูกค้าเรียบร้อยแล้ว")
                self.refresh_table()
                self.clear_and_disable_fields()
                self.current_customer_id = None
            else:
                QMessageBox.critical(self, "ผิดพลาด", "เชื่อมต่อฐานข้อมูลไม่สำเร็จ")
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ผิดพลาด: {e}")

    def clear_fields(self):
        self.txtCustomerName.clear()
        self.txtEmail.clear()
        self.txtTelephone.clear()

    def clear_and_disable_fields(self):
        self.txtCustomerName.clear()
        self.txtCustomerName.setEnabled(False)

        self.txtEmail.clear()
        self.txtEmail.setEnabled(False)

        self.txtTelephone.clear()
        self.txtTelephone.setEnabled(False)

        self.btnAdd.setEnabled(True)
        self.btnSave.setEnabled(False)
        self.btnDelete.setEnabled(False)

    def create_table_row(self):
        hbox = QHBoxLayout()
        self.table = QTableWidget()
        rows = self.get_customer_rows()
        self.table.setFixedSize(600, 150)
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["รหัสลูกค้า", "ชื่อ-นามสกุลลูกค้า", "อีเมลติดต่อ", "หมายเลขโทรศัพท์"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.doubleClicked)
        hbox.addWidget(self.table)
        hbox.addStretch()
        return hbox
    
    def get_customer_rows(self):
        rows = []
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                cursor.execute("SELECT id, name, email, tel FROM customer;")
                rows = cursor.fetchall()
                cursor.close()
                db.close()
            else:
                print("เชื่อมต่อไม่สำเร็จ!")
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            rows = []
        return rows

    def doubleClicked(self, index):
        row = index.row()
        customer_id = int(self.table.item(row, 0).text())
        self.current_customer_id = customer_id

        db = ConnectSQLite()
        if db.open():
            cursor = db.get_cursor()
            cursor.execute("SELECT name, email, tel FROM customer WHERE id = ?", (customer_id,))
            data = cursor.fetchone()
            cursor.close()
            db.close()
            if data:
                self.txtCustomerName.setText(data[0])
                self.txtEmail.setText(data[1])
                self.txtTelephone.setText(data[2])
                
                # enable ทุกฟิลด์ให้แก้ไขได้
                self.txtCustomerName.setEnabled(True)
                self.txtEmail.setEnabled(True)
                self.txtTelephone.setEnabled(True)
                self.btnSave.setEnabled(True)
                self.btnDelete.setEnabled(True)
                self.btnAdd.setEnabled(False)
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสินค้านี้")

    def refresh_table(self):
        rows = self.get_customer_rows()
        self.table.setRowCount(len(rows))
        # ลบข้อมูลเก่า (ถ้ามี) และเติมใหม่
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

class ProductForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ค้นหาสินค้า")
        self.setFixedSize(600, 680)
        layout = QVBoxLayout()

        # ----- กลุ่ม Radio -----
        group1 = QGroupBox("เลือกชนิดการค้นหา")
        group1_layout = QHBoxLayout()
        radio_options = [
            "ค้นหาตามรหัสสินค้า",
            "ค้นหาตามชื่อสินค้า",
            "ค้นหาตามบาร์โค้ด",
            "ค้นหาข้อมูลตามหมวดหมู่"
        ]
        self.radiobuttons = []
        self.radio_group = QButtonGroup(self)
        for option in radio_options:
            rb = QRadioButton(option, self)
            self.radiobuttons.append(rb)
            self.radio_group.addButton(rb)
            if option == "ค้นหาตามบาร์โค้ด":
                rb.setChecked(True)
            group1_layout.addWidget(rb)
        group1.setLayout(group1_layout)
        layout.addWidget(group1)

        # ----- ช่องกรอกข้อมูล & ปุ่ม -----
        hbox_search = QHBoxLayout()
        self.txtSearchProduct = QLineEdit(self)
        self.txtSearchProduct.setPlaceholderText("กรอกข้อมูลสินค้าที่ต้องการค้นหา...")
        self.txtSearchProduct.setFixedHeight(45)
        self.txtSearchProduct.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtSearchProduct.setFocus()
        self.btnSearch = QPushButton(QIcon("icons/Hopstarter-Soft-Scraps-Zoom.256.png"), "ค้นหาข้อมูล")
        self.btnSearch.setIconSize(QSize(24, 24))
        self.btnSearch.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnSearch.setStyleSheet(btnSearch_style)
        self.btnSearch.clicked.connect(self.search_product)
        hbox_search.addWidget(self.txtSearchProduct)
        hbox_search.addWidget(self.btnSearch)
        layout.addLayout(hbox_search)

        # ----- ตาราง/แถวข้อมูล -----
        layout.addLayout(self.create_table_row())

        # ----- กลุ่มเพิ่มข้อมูลใหม่ -----
        group2 = QGroupBox("เพิ่มข้อมูลใหม่")
        group2_layout = QVBoxLayout()
        # แถวเลือกหมวดหมู่
        hbox_category = QHBoxLayout()
        label_category = QLabel("หมวดหมู่สินค้า : ", self)
        label_category.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.combobox = QComboBox(self)
        rows = self.get_category_rows()
        if rows:
            self.combobox.clear()              # (optional) เคลียร์ก่อน
            for row in rows:
                self.combobox.addItem(row[1], row[0])  # name, id
        else:
            print("ไม่มีข้อมูลประเภทสินค้าในฐานข้อมูล")
        self.combobox.setFixedHeight(40)
        self.combobox.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.combobox.setEnabled(False)
        hbox_category.addWidget(label_category)
        hbox_category.addWidget(self.combobox)
        group2_layout.addLayout(hbox_category)
        # แถวรหัสบาร์โค้ด + ชื่อสินค้า
        hbox_id_name = QHBoxLayout()
        label_barcode = QLabel("รหัสบาร์โค้ด :", self)
        label_barcode.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtBarcode = QLineEdit(self)
        self.txtBarcode.setFixedHeight(40)
        self.txtBarcode.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtBarcode.setEnabled(False)
        label_name = QLabel("ชื่อสินค้า :", self)
        label_name.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtProductName = QLineEdit(self)
        self.txtProductName.setFixedHeight(40)
        self.txtProductName.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtProductName.setEnabled(False)
        hbox_id_name.addWidget(label_barcode)
        hbox_id_name.addWidget(self.txtBarcode)
        hbox_id_name.addWidget(label_name)
        hbox_id_name.addWidget(self.txtProductName)
        group2_layout.addLayout(hbox_id_name)
        
        label_description = QLabel("รายละเอียดสินค้า :", self)
        label_description.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        group2_layout.addWidget(label_description)
        self.textedit = QTextEdit(self)
        self.textedit.setFixedSize(557, 70)
        self.textedit.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.textedit.setEnabled(False)
        group2_layout.addWidget(self.textedit)
        group2.setLayout(group2_layout)
        layout.addWidget(group2)

        hbox_price_stock = QHBoxLayout()
        label_price = QLabel("ราคาสินค้า :", self)
        label_price.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.spinPrice = QSpinBox(self)
        self.spinPrice.setMinimum(0)
        self.spinPrice.setMaximum(10000)
        self.spinPrice.setSingleStep(1)
        self.spinPrice.setSuffix(" บาท")
        self.spinPrice.setFixedHeight(40)
        self.spinPrice.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.spinPrice.setEnabled(False)
        label_stock = QLabel("จำนวนสินค้าคงคลัง :", self)
        label_stock.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.spinStock = QSpinBox(self)
        self.spinStock.setMinimum(0)
        self.spinStock.setMaximum(10000)
        self.spinStock.setSingleStep(1)
        self.spinStock.setSuffix(" ชิ้น")
        self.spinStock.setFixedHeight(40)
        self.spinStock.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.spinStock.setEnabled(False)
        hbox_price_stock.addWidget(label_price)
        hbox_price_stock.addWidget(self.spinPrice)
        hbox_price_stock.addWidget(label_stock)
        hbox_price_stock.addWidget(self.spinStock)
        group2_layout.addLayout(hbox_price_stock)

        hbox_cost = QHBoxLayout()
        label_cost = QLabel("ราคาทุนสินค้า :", self)
        label_cost.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.spinCost = QSpinBox(self)
        self.spinCost.setMinimum(0)
        self.spinCost.setMaximum(10000)
        self.spinCost.setSingleStep(1)
        self.spinCost.setSuffix(" บาท")
        self.spinCost.setFixedHeight(40)
        self.spinCost.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.spinCost.setEnabled(False)
        hbox_cost.addWidget(label_cost)
        hbox_cost.addWidget(self.spinCost)
        group2_layout.addLayout(hbox_cost)

        hbox_button_group = QHBoxLayout()
        self.btnAdd = QPushButton(QIcon("icons/Oxygen-Icons.org-Oxygen-Actions-list-add.256.png"), "เพิ่ม")
        self.btnAdd.setIconSize(QSize(24, 24))
        self.btnAdd.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnAdd.setStyleSheet(btnSearch_style)
        self.btnAdd.clicked.connect(self.add_data)

        self.btnSave = QPushButton(QIcon("icons/Custom-Icon-Design-Pretty-Office-7-Save-as.256.png"), "บันทึก")
        self.btnSave.setIconSize(QSize(24, 24))
        self.btnSave.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnSave.setStyleSheet(btnSearch_style)
        self.btnSave.setEnabled(False)
        self.btnSave.clicked.connect(self.save_data)

        self.btnDelete = QPushButton(QIcon("icons/Hopstarter-Sleek-Xp-Basic-Close-2.256.png"), "ลบ")
        self.btnDelete.setIconSize(QSize(24, 24))
        self.btnDelete.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnDelete.setStyleSheet(btnSearch_style)
        self.btnDelete.setEnabled(False)
        self.btnDelete.clicked.connect(self.delete_product)

        self.btnClear = QPushButton(QIcon("icons/Gartoon-Team-Gartoon-Action-Edit-clear-broom.256.png"), "เคลียร์")
        self.btnClear.setIconSize(QSize(24, 24))
        self.btnClear.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnClear.setStyleSheet(btnSearch_style)
        self.btnClear.clicked.connect(self.clear_fields)

        self.btnClose = QPushButton(QIcon("icons/Visualpharm-Must-Have-Log-Out.256.png"), "ปิด")
        self.btnClose.setIconSize(QSize(24, 24))
        self.btnClose.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnClose.setStyleSheet(btnSearch_style)
        self.btnClose.clicked.connect(self.close)
        
        # hbox1.addStretch()
        hbox_button_group.addWidget(self.btnAdd)
        hbox_button_group.addWidget(self.btnSave)
        hbox_button_group.addWidget(self.btnDelete)
        hbox_button_group.addWidget(self.btnClear)
        hbox_button_group.addWidget(self.btnClose)
        group2_layout.addLayout(hbox_button_group)

        self.setLayout(layout)

    def search_product(self):
        keyword = self.txtSearchProduct.text().strip()
        search_mode = None
        for rb in self.radiobuttons:
            if rb.isChecked():
                search_mode = rb.text()
                break

        sql = "SELECT id, barcode, name, price, stock FROM product"
        params = []

        if not keyword:
            # ถ้าไม่ใส่อะไร ให้แสดงทั้งหมด
            pass
        elif search_mode == "ค้นหาตามรหัสสินค้า":
            sql += " WHERE id = ?"
            params.append(keyword)
        elif search_mode == "ค้นหาตามชื่อสินค้า":
            sql += " WHERE name LIKE ?"
            params.append(f"%{keyword}%")
        elif search_mode == "ค้นหาตามบาร์โค้ด":
            sql += " WHERE barcode LIKE ?"
            params.append(f"%{keyword}%")
        elif search_mode == "ค้นหาข้อมูลตามหมวดหมู่":
            sql += " WHERE categoryId = ?"
            params.append(keyword)
        else:
            # fallback
            pass

        db = ConnectSQLite()
        rows = []
        if db.open():
            cursor = db.get_cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
            db.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def save_data(self):
        name = self.txtProductName.text()
        description = self.textedit.toPlainText()
        price = self.spinPrice.value()
        stock = self.spinStock.value()
        category_id = self.combobox.currentData()  # ใช้ currentData() ถ้า addItem(row[1], row[0])
        now = datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S") + f".{int(now.microsecond/1000):03d}"
        updated_at = created_at
        barcode = self.txtBarcode.text()
        cost = self.spinCost.value()        

        if not name or not barcode:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกชื่อสินค้าและบาร์โค้ด")
            return
        
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                if hasattr(self, "current_product_id") and self.current_product_id is not None:
                    # ----- Update -----
                    sql = """
                        UPDATE product
                        SET name=?, description=?, price=?, stock=?, categoryId=?, updatedAt=?, barcode=?, cost=?
                        WHERE id=?
                    """
                    cursor.execute(sql, (
                        name, description, price, stock, category_id, updated_at, barcode, cost, self.current_product_id
                    ))
                    QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลสินค้าเรียบร้อยแล้ว")
                else:
                    # ----- Add -----
                    sql = """
                        INSERT INTO product
                            (name, description, price, stock, categoryId, createdAt, updatedAt, barcode, cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(sql, (
                        name, description, price, stock, category_id, created_at, updated_at, barcode, cost
                    ))
                    QMessageBox.information(self, "สำเร็จ", "เพิ่มข้อมูลสินค้าเรียบร้อยแล้ว")
                self.current_product_id = None
                db.commit()
                cursor.close()
                db.close()
                self.refresh_table()
                self.clear_and_disable_fields()
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "เกิดข้อผิดพลาด", f"ไม่สามารถเพิ่มข้อมูลได้ (ข้อมูลซ้ำหรือข้อผิดพลาด):\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ผิดพลาด: {e}")

    def delete_product(self):
        if not hasattr(self, "current_product_id") or self.current_product_id is None:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกรายการสินค้าที่ต้องการลบ")
            return

        reply = QMessageBox.question(self, "ยืนยันการลบ", "คุณต้องการลบสินค้านี้จริงหรือไม่?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        db = ConnectSQLite()
        try:
            if db.open():
                cursor = db.get_cursor()
                sql = "DELETE FROM product WHERE id = ?"
                cursor.execute(sql, (self.current_product_id,))
                db.conn.commit()
                cursor.close()
                db.close()
                QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลสินค้าเรียบร้อยแล้ว")
                self.refresh_table()
                self.clear_and_disable_fields()
                self.current_product_id = None
            else:
                QMessageBox.critical(self, "ผิดพลาด", "เชื่อมต่อฐานข้อมูลไม่สำเร็จ")
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ผิดพลาด: {e}")

    def clear_fields(self):
        self.txtProductName.clear()
        self.textedit.clear()
        self.spinPrice.setValue(0)
        self.spinStock.setValue(0)
        self.combobox.setCurrentIndex(0)
        self.txtBarcode.clear()
        self.spinCost.setValue(0)

    def clear_and_disable_fields(self):
        self.txtProductName.clear()
        self.txtProductName.setEnabled(False)

        self.textedit.clear()
        self.textedit.setEnabled(False)

        self.spinPrice.setValue(0)
        self.spinPrice.setEnabled(False)

        self.spinStock.setValue(0)
        self.spinStock.setEnabled(False)

        self.combobox.setCurrentIndex(0)
        self.combobox.setEnabled(False)

        self.txtBarcode.clear()
        self.txtBarcode.setEnabled(False)

        self.spinCost.setValue(0)
        self.spinCost.setEnabled(False)
        self.btnAdd.setEnabled(True)
        self.btnSave.setEnabled(False)
        self.btnDelete.setEnabled(False)

    def add_data(self):
        self.btnAdd.setEnabled(False)
        self.btnSave.setEnabled(True)
        self.btnDelete.setEnabled(True)
        self.combobox.setEnabled(True)
        self.txtBarcode.setEnabled(True)
        self.txtProductName.setEnabled(True)
        self.textedit.setEnabled(True)
        self.spinPrice.setEnabled(True)
        self.spinStock.setEnabled(True)
        self.spinCost.setEnabled(True)

    def get_category_rows(self):
        rows = []
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                cursor.execute("SELECT id, name FROM category ORDER BY id ASC")
                rows = cursor.fetchall()
                cursor.close()
                db.close()
            else:
                print("เชื่อมต่อไม่สำเร็จ!")
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            rows = []
        return rows

    def get_product_rows(self):
        rows = []
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                cursor.execute("""SELECT 
                                            product.id, 
                                            product.barcode,
                                            product.name, 
                                            product.price,
                                            product.stock  
                                        FROM 
                                            product
                                            INNER JOIN category ON product.categoryId = category.id;""")
                rows = cursor.fetchall()
                cursor.close()
                db.close()
            else:
                print("เชื่อมต่อไม่สำเร็จ!")
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            rows = []
        return rows

    def create_table_row(self):
        hbox = QHBoxLayout()
        self.table = QTableWidget()
        rows = self.get_product_rows()
        self.table.setFixedSize(580, 150)
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["รหัสสินค้า", "บาร์โค้ด", "ชื่อสินค้า", "ราคาสินค้า", "จำนวน"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.doubleClicked)
        hbox.addWidget(self.table)
        hbox.addStretch()
        return hbox

    def refresh_table(self):
        rows = self.get_product_rows()
        self.table.setRowCount(len(rows))
        # ลบข้อมูลเก่า (ถ้ามี) และเติมใหม่
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def doubleClicked(self, index):
        row = index.row()
        product_id = int(self.table.item(row, 0).text())
        self.current_product_id = product_id

        db = ConnectSQLite()
        if db.open():
            cursor = db.get_cursor()
            cursor.execute("SELECT name, description, price, stock, categoryId, barcode, cost FROM product WHERE id = ?", (product_id,))
            data = cursor.fetchone()
            cursor.close()
            db.close()
            if data:
                self.txtProductName.setText(data[0])
                self.textedit.setPlainText(data[1] if data[1] else "")
                self.spinPrice.setValue(data[2])
                self.spinStock.setValue(data[3])
                # combobox: หา index จาก categoryId
                idx = self.combobox.findData(data[4])
                self.combobox.setCurrentIndex(idx if idx != -1 else 0)
                self.txtBarcode.setText(data[5])
                self.spinCost.setValue(data[6])
                
                # enable ทุกฟิลด์ให้แก้ไขได้
                self.txtProductName.setEnabled(True)
                self.textedit.setEnabled(True)
                self.spinPrice.setEnabled(True)
                self.spinStock.setEnabled(True)
                self.combobox.setEnabled(True)
                self.txtBarcode.setEnabled(True)
                self.spinCost.setEnabled(True)
                self.btnSave.setEnabled(True)
                self.btnDelete.setEnabled(True)
                self.btnAdd.setEnabled(False)
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบข้อมูลสินค้านี้")

    def search_data(self):
        for rb in self.radiobuttons:
            if rb.isChecked():
                print("เลือก:", rb.text())

class FormWidget(QWidget):
    def __init__(self):
        super().__init__()     
        main_layout = QHBoxLayout()

        # ฝั่งซ้าย
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addLayout(self.create_label_row())
        left_layout.addLayout(self.create_label_order1())
        left_layout.addLayout(self.create_label_order2())
        left_layout.addLayout(self.create_label_order3())
        left_layout.addLayout(self.create_table_row())
        left_layout.addLayout(self.create_button_row_bottom())
        left_layout.addStretch()
        main_layout.addWidget(left_widget)

        # ฝั่งขวา
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addLayout(self.create_button_row_top())
        right_layout.addStretch()
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)

    def open_search_form_product(self):
        self.product_form = ProductForm(self)
        self.product_form.exec()  
        # ถ้าเป็น QDialog ใช้ exec() จะ block จนปิด dialog
        # ถ้าเป็น QWidget ใช้ self.search_form.show()

    def open_search_form_customer(self):
        self.customer_form = CustomerForm(self)
        self.customer_form.exec()  

    def create_button_row_top(self):
        hbox = QHBoxLayout()

        self.btnProduct = QPushButton(QIcon("icons/Hopstarter-Soft-Scraps-Zoom.256.png"), "ข้อมูลสินค้า")
        self.btnProduct.setFixedSize(150, 55)
        self.btnProduct.setIconSize(QSize(32, 32))
        self.btnProduct.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnProduct.setStyleSheet(btnSearch_style)
        self.btnProduct.clicked.connect(self.open_search_form_product)
        hbox.addWidget(self.btnProduct)

        self.btnCustomer = QPushButton(QIcon("icons/Icons-Land-Vista-People-Groups-Meeting-Light.256.png"), "ข้อมูลลูกค้า")
        self.btnCustomer.setFixedSize(150, 55)
        self.btnCustomer.setIconSize(QSize(32, 32))
        self.btnCustomer.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnCustomer.setStyleSheet(btnCustomer_style)
        self.btnCustomer.clicked.connect(self.open_search_form_customer)
        hbox.addWidget(self.btnCustomer)

        hbox.addStretch()
        return hbox

    def create_button_row_bottom(self):
        hbox = QHBoxLayout()
        # ปุ่มยกเลิกการขาย
        self.btnDelete = QPushButton(QIcon("icons/Custom-Icon-Design-Flatastic-1-Delete.512.png"), "ลบรายการ")
        self.btnDelete.setFixedSize(180, 55)
        self.btnDelete.setIconSize(QSize(32, 32))
        self.btnDelete.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnDelete.setStyleSheet(btnDelete_style)
        self.btnDelete.clicked.connect(self.delete_selected_row)
        hbox.addWidget(self.btnDelete)

        # ปุ่มจบการทำงาน (ควรปิดเฉพาะ subwindow)
        self.btnDeleteAll = QPushButton(QIcon("icons/Franksouza183-Fs-Places-trash-full.512.png"), "ลบรายการทั้งหมด")
        self.btnDeleteAll.setFixedSize(180, 55)
        self.btnDeleteAll.setIconSize(QSize(32, 32))
        self.btnDeleteAll.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnDeleteAll.setStyleSheet(btnDeleteAll_style)
        self.btnDeleteAll.clicked.connect(self.delete_all_row)
        hbox.addWidget(self.btnDeleteAll)

        self.btnCancelOrder = QPushButton(QIcon("icons/Hopstarter-Soft-Scraps-File-Delete.256.png"), "ยกเลิกคำสั่งซื้อ")
        self.btnCancelOrder.setFixedSize(180, 55)
        self.btnCancelOrder.setIconSize(QSize(32, 32))
        self.btnCancelOrder.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnCancelOrder.setStyleSheet(btnUp_style)
        self.btnCancelOrder.clicked.connect(self.cancel_order)
        hbox.addWidget(self.btnCancelOrder)

        self.btnExit = QPushButton(QIcon("icons/Visualpharm-Must-Have-Log-Out.256.png"), "ปิดหน้าต่าง")
        self.btnExit.setFixedSize(180, 55)
        self.btnExit.setIconSize(QSize(32, 32))
        self.btnExit.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.btnExit.setStyleSheet(btnExit_style)
        self.btnExit.clicked.connect(self.close_form)
        hbox.addWidget(self.btnExit)

        hbox.addStretch()
        return hbox

    def create_label_order1(self):
        hbox = QHBoxLayout()
        LABEL_WIDTH = 120

        labelOrderId = QLabel("เลขที่เอกสาร : ", self)
        labelOrderId.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelOrderId.setFixedWidth(LABEL_WIDTH)
        self.txtOrderId = QLineEdit(self)
        self.txtOrderId.setFixedSize(200, 28)
        self.txtOrderId.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtOrderId.textChanged.connect(self.update_table_by_order_id)

        labelDate = QLabel("วันที่ : ", self)
        labelDate.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelDate.setFixedWidth(80)
        today = QDate.currentDate()
        date_str = today.toString("dd/MM/yyyy")
        
        labelShowDate = QLabel(date_str, self)
        labelShowDate.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelShowDate.setFixedWidth(100)

        labelTime = QLabel("เวลา : ", self)
        labelTime.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelTime.setFixedWidth(80)
        self.labelShowTime = QLabel("", self)
        self.labelShowTime.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.labelShowTime.setFixedWidth(100)
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

        hbox.addWidget(labelOrderId)
        hbox.addWidget(self.txtOrderId)
        hbox.addSpacing(10)
        hbox.addWidget(labelDate)
        hbox.addWidget(labelShowDate)
        hbox.addSpacing(10)
        hbox.addWidget(labelTime)
        hbox.addWidget(self.labelShowTime)
        hbox.addStretch()
        return hbox

    def update_table_by_order_id(self, order_id):
        self.refresh_table(order_id=order_id)

    def refresh_table(self, barcode=None, order_id=None):
        rows = self.get_product_rows(barcode=barcode, order_id=order_id)
        num_rows = len(rows)
        num_cols = self.table.columnCount()
        self.table.setRowCount(num_rows)
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def update_time(self):
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M:%S") + " น."
        self.labelShowTime.setText(time_str)

    def create_label_order2(self):
        hbox = QHBoxLayout()
        LABEL_WIDTH = 120

        labelCustomerId = QLabel("รหัสลูกค้า : ", self)
        labelCustomerId.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelCustomerId.setFixedWidth(LABEL_WIDTH)
        self.txtCustomerId = QLineEdit(self)
        self.txtCustomerId.setFixedSize(200, 28)
        self.txtCustomerId.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.txtCustomerId.textChanged.connect(self.update_customer_name_label)

        labelCustomer = QLabel("ชื่อ - นามสกุลลูกค้า : ", self)
        labelCustomer.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelCustomer.setFixedWidth(170)
        self.labelCustomerName = QLabel(self.get_customer_name(self.txtCustomerId.text()), self)
        self.labelCustomerName.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.labelCustomerName.setFixedWidth(160)

        hbox.addWidget(labelCustomerId)
        hbox.addWidget(self.txtCustomerId)
        hbox.addSpacing(10)
        hbox.addWidget(labelCustomer)
        hbox.addWidget(self.labelCustomerName)
        hbox.addStretch()
        return hbox

    def create_label_order3(self):
        hbox = QHBoxLayout()
        LABEL_WIDTH = 120

        labelTaxName = QLabel("ชนิดภาษี : ", self)
        labelTaxName.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelTaxName.setFixedWidth(LABEL_WIDTH)
        self.labelTax = QLabel("1 = สินค้ารวมภาษี", self)
        self.labelTax.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.labelTax.setFixedWidth(200)

        labelTypeOfSaleName = QLabel("ชนิดการขาย : ", self)
        labelTypeOfSaleName.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        labelTypeOfSaleName.setFixedWidth(170)
        self.labelTypeOfSale = QLabel("1 = เงินสด", self)
        self.labelTypeOfSale.setFont(QFont("TH Sarabun New", 20, QFont.Weight.Bold))
        self.labelTypeOfSale.setFixedWidth(170)

        hbox.addWidget(labelTaxName)
        hbox.addWidget(self.labelTax)
        hbox.addSpacing(10)
        hbox.addWidget(labelTypeOfSaleName)
        hbox.addWidget(self.labelTypeOfSale)
        hbox.addStretch()
        return hbox

    def update_customer_name_label(self, text):
        name = self.get_customer_name(text)
        if name:
            self.labelCustomerName.setText(name)
        else:
            self.labelCustomerName.setText("ไม่พบลูกค้า")

    def get_customer_name(self, customer_id):
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                cursor.execute("SELECT name FROM customer WHERE id = ?", (customer_id,))
                row = cursor.fetchone()
                cursor.close()
                db.close()
                if row:
                    return row[0] 
                else:
                    return None 
            else:
                print("เชื่อมต่อไม่สำเร็จ!")
                return None
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            return None

    def create_label_row(self):
        hbox = QHBoxLayout()
        self.label = QLabel("0.00", self)
        self.label.setFixedSize(740, 100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label.setStyleSheet(labelMoney_style)
        hbox.addWidget(self.label)
        hbox.addStretch()

        return hbox

    def get_product_rows(self, barcode=None, order_id=None):
        rows = []
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                sql = """
                    SELECT
                        [order].id,
                        orderitem.id,
                        product.id, 
                        product.barcode,
                        product.name, 
                        product.price,  
                        orderitem.quantity, 
                        [order].total
                    FROM 
                        product
                        INNER JOIN category ON product.categoryId = category.id
                        INNER JOIN orderitem ON product.id = orderitem.productId
                        INNER JOIN [order] ON [order].id = orderitem.orderId
                """
                filters = []
                params = []
                if barcode:
                    filters.append("product.barcode = ?")
                    params.append(barcode)
                if order_id:
                    filters.append("[order].id = ?")
                    params.append(order_id)
                if filters:
                    sql += " WHERE " + " AND ".join(filters)
                sql += " ORDER BY product.id ASC"
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                cursor.close()
                db.close()
            else:
                print("เชื่อมต่อไม่สำเร็จ!")
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            rows = []
        return rows

    def create_table_row(self, barcode=None, order_id=None):
        hbox = QHBoxLayout()
        self.table = QTableWidget()
        rows = self.get_product_rows(barcode=barcode, order_id=order_id)
        self.table.setFixedSize(740, 250)
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["เลขที่คำสั่งซื้อ", "ลำดับรายการสั่งซื้อ", "รหัสสินค้า", "บาร์โค้ด", "ชื่อสินค้า", "ราคาสินค้า", "จำนวน", "รวมทั้งหมด"]
        )

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        hbox.addWidget(self.table)
        hbox.addStretch()
        return hbox

    def delete_selected_row(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกแถวที่ต้องการลบ")
            return
        
        row_idx = selected[0].row()
        order_id = self.table.item(row_idx, 0).text()
        orderitem_id = self.table.item(row_idx, 1).text()

        reply = QMessageBox.question(self, "ยืนยัน", f"ต้องการลบสินค้า id {orderitem_id} ใช่หรือไม่?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.delete_orderitem_select_row(orderitem_id)
        self.refresh_table(barcode=None, order_id=order_id)

    def delete_all_row(self):
        order_id = self.txtOrderId.text().strip()
        if not order_id:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกรหัสคำสั่งซื้อ (Order ID)")
            return

        reply = QMessageBox.question(self, "ยืนยัน", f"ต้องการลบข้อมูลใน orderitem ของ Order ID {order_id} ทั้งหมดหรือไม่?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.delete_orderitem_all_row(order_id)
        self.refresh_table(barcode=None, order_id=order_id)

    def cancel_order(self):
        order_id = self.txtOrderId.text().strip()
        if not order_id:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกรหัสคำสั่งซื้อ (Order ID)")
            return

        reply = QMessageBox.question(self, "ยืนยัน", f"ต้องการยกเลิกข้อมูลในรายการคำสั่งซื้อเลขที่ {order_id} ทั้งหมดหรือไม่?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        # ลบออกจากฐานข้อมูล
        self.delete_order(order_id)
        # รีเฟรชตารางใหม่
        self.refresh_table(barcode=None, order_id=order_id)

    def delete_order(self, order_id):
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                cursor.execute("DELETE FROM orderitem WHERE orderId = ?", (order_id,))
                cursor.execute("DELETE FROM [order] WHERE id = ?", (order_id,))
                db.get_connection().commit()  # หรือใช้ db.get_connection().commit() ถ้าคลาสคุณออกแบบแบบนี้
                cursor.close()
                db.close()
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "เชื่อมต่อฐานข้อมูลไม่สำเร็จ")
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ลบข้อมูลไม่สำเร็จ:\n{e}")

    def delete_orderitem_all_row(self, order_id):
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                cursor.execute("DELETE FROM orderitem WHERE orderId = ?", (order_id,))
                db.commit()  # หรือ db.conn.commit() แล้วแต่คลาสคุณ
                cursor.close()
                db.close()
            else:
                QMessageBox.warning(self, "ข้อผิดพลาด", "เชื่อมต่อฐานข้อมูลไม่สำเร็จ")
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ลบข้อมูลไม่สำเร็จ:\n{e}")

    def delete_orderitem_select_row(self, orderitem_id):
        try:
            db = ConnectSQLite()
            if db.open():
                cursor = db.get_cursor()
                cursor.execute("DELETE FROM orderitem WHERE id = ?", (orderitem_id,))
                # cursor.execute("DELETE FROM [order] WHERE id = ?", (order_id,))
                db.get_connection().commit()  # หรือใช้ db.get_connection().commit() ถ้าคลาสคุณออกแบบแบบนี้
                cursor.close()
                db.close()
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "เชื่อมต่อฐานข้อมูลไม่สำเร็จ")
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาด: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ลบข้อมูลไม่สำเร็จ:\n{e}")

    def refresh_table(self, barcode=None, order_id=None):
        rows = self.get_product_rows(barcode=barcode, order_id=order_id)
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def close_form(self):
        # ปิด subwindow ที่บรรจุ widget นี้ (FormWidget)
        parent = self.parent()
        while parent:
            if isinstance(parent, QMdiSubWindow):
                parent.close()
                break
            parent = parent.parent()

    def exit_data(self):
        # ปิด subwindow ที่บรรจุ widget นี้ (FormWidget)
        parent = self.parent()
        while parent:
            if isinstance(parent, QMdiSubWindow):
                parent.close()
                break
            parent = parent.parent()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDI Form Example")
        self.set_centered_window(0.95, 0.9)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.init_status_bar()

        tb = self.addToolBar("My Toolbar")
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        newTb = QAction(QIcon('icons/Aha-Soft-Large-Business-Cash-register.512.png'), "ขายหน้าร้าน", self)
        newTb.triggered.connect(self.create_subwindow)
        tb.addAction(newTb)
        openTb = QAction(QIcon('icons/empty.png'), "Open", self)
        openTb.setShortcut("Ctrl+N")
        openTb.triggered.connect(self.create_subwindow)
        tb.addAction(openTb)
        saveTb = QAction(QIcon('icons/save.png'), "Save", self)
        tb.addAction(saveTb)
        exitTb = QAction(QIcon('icons/exit.png'),"Exit",self)
        exitTb.triggered.connect(self.exitFunc)
        tb.addAction(exitTb)
        tb.actionTriggered.connect(self.btnFunc)

    def init_status_bar(self):
        status = QStatusBar()
        status.setFont(QFont("TH Sarabun New", 14))
        self.setStatusBar(status)
        self.statusBar().showMessage("พร้อมใช้งาน...")

    def set_centered_window(self, width_ratio=0.8, height_ratio=0.8):
        screen = self.screen() or QApplication.primaryScreen()
        rect = screen.geometry()
        screen_width = rect.width()
        screen_height = rect.height()
        window_width = int(screen_width * width_ratio)
        window_height = int(screen_height * height_ratio)
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.setGeometry(x, y, window_width, window_height)

    def create_subwindow(self):
        try:
            sub = QMdiSubWindow()
            form = FormWidget()
            sub.setWidget(form)
            sub.setWindowTitle("New Form")
            self.mdi.addSubWindow(sub)
            sub.showMaximized()
            sub.show()
        except Exception as e:
            import traceback
            print("Error in create_subwindow:", e)
            traceback.print_exc()

    def exitFunc(self):
        self.close()

    def btnFunc(self):
        pass

def main():
    App = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(App.exec())

if __name__ == "__main__":
    main()
