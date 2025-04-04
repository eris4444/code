import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QTextEdit, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon

class HotelElevatorSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم مدیریت آسانسورهای هتل")
        self.setWindowIcon(QIcon("elevator_icon.png"))  # نیاز به فایل آیکون
        self.setMinimumSize(1000, 700)
        
        # اتصال به پایگاه داده
        self.db_connection = sqlite3.connect('hotel_elevators.db')
        self.create_tables()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری داده‌های اولیه
        self.load_elevators()
        self.load_maintenance_logs()
    
    def create_tables(self):
        """ایجاد جداول پایگاه داده اگر وجود نداشته باشند"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS elevators (
                elevator_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                current_floor INTEGER,
                status TEXT CHECK(status IN ('فعال', 'غیرفعال', 'در حال تعمیر', 'نیاز به سرویس')),
                last_service DATE,
                next_service DATE,
                service_interval INTEGER,
                capacity INTEGER,
                manufacturer TEXT,
                installation_date DATE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                elevator_id INTEGER,
                technician TEXT,
                service_date DATE,
                service_type TEXT,
                description TEXT,
                parts_replaced TEXT,
                next_service_date DATE,
                FOREIGN KEY (elevator_id) REFERENCES elevators (elevator_id)
            )
        ''')
        
        self.db_connection.commit()
    
    def init_ui(self):
        """ایجاد رابط کاربری گرافیکی"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # لایه اصلی
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # تب‌های مختلف
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # تب مدیریت آسانسورها
        self.init_elevator_tab()
        
        # تب سرویس و نگهداری
        self.init_maintenance_tab()
        
        # تب گزارشات
        self.init_reports_tab()
        
        # تب کنترل آسانسور
        self.init_control_tab()
    
    def init_elevator_tab(self):
        """تب مدیریت آسانسورها"""
        tab = QWidget()
        self.tabs.addTab(tab, "مدیریت آسانسورها")
        
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # فرم اضافه کردن آسانسور جدید
        form_layout = QVBoxLayout()
        
        # ردیف اول
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("نام آسانسور:"))
        self.elevator_name_input = QLineEdit()
        row1.addWidget(self.elevator_name_input)
        
        row1.addWidget(QLabel("ظرفیت:"))
        self.capacity_input = QLineEdit()
        self.capacity_input.setValidator(QIntValidator(1, 20))
        row1.addWidget(self.capacity_input)
        form_layout.addLayout(row1)
        
        # ردیف دوم
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("سازنده:"))
        self.manufacturer_input = QLineEdit()
        row2.addWidget(self.manufacturer_input)
        
        row2.addWidget(QLabel("تاریخ نصب:"))
        self.installation_date_input = QDateEdit()
        self.installation_date_input.setCalendarPopup(True)
        self.installation_date_input.setDate(QDate.currentDate())
        row2.addWidget(self.installation_date_input)
        form_layout.addLayout(row2)
        
        # ردیف سوم
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("بازه سرویس (روز):"))
        self.service_interval_input = QLineEdit("90")
        self.service_interval_input.setValidator(QIntValidator(1, 365))
        row3.addWidget(self.service_interval_input)
        
        add_button = QPushButton("اضافه کردن آسانسور")
        add_button.clicked.connect(self.add_elevator)
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        row3.addWidget(add_button)
        form_layout.addLayout(row3)
        
        layout.addLayout(form_layout)
        
        # جدول آسانسورها
        self.elevators_table = QTableWidget()
        self.elevators_table.setColumnCount(8)
        self.elevators_table.setHorizontalHeaderLabels([
            "کد", "نام", "طبقه فعلی", "وضعیت", "آخرین سرویس", 
            "سرویس بعدی", "ظرفیت", "سازنده"
        ])
        self.elevators_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.elevators_table.doubleClicked.connect(self.show_elevator_details)
        layout.addWidget(self.elevators_table)
    
    def init_maintenance_tab(self):
        """تب سرویس و نگهداری"""
        tab = QWidget()
        self.tabs.addTab(tab, "سرویس و نگهداری")
        
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # فرم ثبت سرویس
        form_layout = QVBoxLayout()
        
        # ردیف اول
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("آسانسور:"))
        self.maintenance_elevator_combo = QComboBox()
        row1.addWidget(self.maintenance_elevator_combo)
        
        row1.addWidget(QLabel("تکنسین:"))
        self.technician_input = QLineEdit()
        row1.addWidget(self.technician_input)
        form_layout.addLayout(row1)
        
        # ردیف دوم
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("نوع سرویس:"))
        self.service_type_combo = QComboBox()
        self.service_type_combo.addItems([
            "سرویس دوره‌ای", "تعمیر مکانیکی", "تعمیر الکتریکی", 
            "تعویض قطعه", "بازرسی ایمنی"
        ])
        row2.addWidget(self.service_type_combo)
        
        row2.addWidget(QLabel("تاریخ سرویس:"))
        self.service_date_input = QDateEdit()
        self.service_date_input.setCalendarPopup(True)
        self.service_date_input.setDate(QDate.currentDate())
        row2.addWidget(self.service_date_input)
        form_layout.addLayout(row2)
        
        # ردیف سوم
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("قطعات تعویض شده:"))
        self.parts_replaced_input = QLineEdit()
        row3.addWidget(self.parts_replaced_input)
        form_layout.addLayout(row3)
        
        # توضیحات
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("توضیحات سرویس...")
        form_layout.addWidget(self.description_input)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        log_button = QPushButton("ثبت سرویس")
        log_button.clicked.connect(self.log_maintenance)
        log_button.setStyleSheet("background-color: #2196F3; color: white;")
        buttons_layout.addWidget(log_button)
        
        report_problem_button = QPushButton("گزارش مشکل")
        report_problem_button.clicked.connect(self.report_problem_dialog)
        report_problem_button.setStyleSheet("background-color: #FF9800; color: white;")
        buttons_layout.addWidget(report_problem_button)
        
        form_layout.addLayout(buttons_layout)
        layout.addLayout(form_layout)
        
        # جدول تاریخچه سرویس‌ها
        self.maintenance_table = QTableWidget()
        self.maintenance_table.setColumnCount(7)
        self.maintenance_table.setHorizontalHeaderLabels([
            "تاریخ", "آسانسور", "تکنسین", "نوع سرویس", 
            "توضیحات", "قطعات", "سرویس بعدی"
        ])
        layout.addWidget(self.maintenance_table)
    
    def init_reports_tab(self):
        """تب گزارشات"""
        tab = QWidget()
        self.tabs.addTab(tab, "گزارشات")
        
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # فیلترهای گزارش
        filters_layout = QHBoxLayout()
        
        filters_layout.addWidget(QLabel("وضعیت:"))
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["همه", "فعال", "غیرفعال", "در حال تعمیر", "نیاز به سرویس"])
        filters_layout.addWidget(self.status_filter_combo)
        
        filters_layout.addWidget(QLabel("از تاریخ:"))
        self.from_date_input = QDateEdit()
        self.from_date_input.setCalendarPopup(True)
        self.from_date_input.setDate(QDate.currentDate().addMonths(-1))
        filters_layout.addWidget(self.from_date_input)
        
        filters_layout.addWidget(QLabel("تا تاریخ:"))
        self.to_date_input = QDateEdit()
        self.to_date_input.setCalendarPopup(True)
        self.to_date_input.setDate(QDate.currentDate())
        filters_layout.addWidget(self.to_date_input)
        
        filter_button = QPushButton("اعمال فیلتر")
        filter_button.clicked.connect(self.apply_filters)
        filter_button.setStyleSheet("background-color: #607D8B; color: white;")
        filters_layout.addWidget(filter_button)
        
        layout.addLayout(filters_layout)
        
        # گزارش آسانسورهای نیازمند سرویس
        due_label = QLabel("آسانسورهای نیازمند سرویس:")
        due_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(due_label)
        
        self.due_table = QTableWidget()
        self.due_table.setColumnCount(4)
        self.due_table.setHorizontalHeaderLabels(["کد", "نام", "وضعیت", "تاریخ سرویس بعدی"])
        layout.addWidget(self.due_table)
        
        # گزارش آماری
        stats_label = QLabel("آمار سرویس‌ها:")
        stats_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(stats_label)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
    
    def init_control_tab(self):
        """تب کنترل آسانسور"""
        tab = QWidget()
        self.tabs.addTab(tab, "کنترل آسانسور")
        
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # انتخاب آسانسور
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("آسانسور:"))
        self.control_elevator_combo = QComboBox()
        control_layout.addWidget(self.control_elevator_combo)
        
        layout.addLayout(control_layout)
        
        # نمایش وضعیت
        self.status_display = QLabel("وضعیت: -")
        self.status_display.setAlignment(Qt.AlignCenter)
        self.status_display.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.status_display)
        
        self.floor_display = QLabel("طبقه فعلی: -")
        self.floor_display.setAlignment(Qt.AlignCenter)
        self.floor_display.setStyleSheet("font-size: 24px; color: #E91E63;")
        layout.addWidget(self.floor_display)
        
        # کنترل حرکت
        move_layout = QHBoxLayout()
        move_layout.addWidget(QLabel("طبقه مقصد:"))
        self.target_floor_input = QLineEdit()
        self.target_floor_input.setValidator(QIntValidator(1, 20))
        move_layout.addWidget(self.target_floor_input)
        
        move_button = QPushButton("حرکت به طبقه")
        move_button.clicked.connect(self.move_elevator)
        move_button.setStyleSheet("background-color: #8BC34A; color: white;")
        move_layout.addWidget(move_button)
        
        layout.addLayout(move_layout)
        
        # لاگ حرکات
        self.movement_log = QTextEdit()
        self.movement_log.setReadOnly(True)
        layout.addWidget(self.movement_log)
    
    # --- متدهای عملیاتی ---
    
    def load_elevators(self):
        """بارگذاری لیست آسانسورها"""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM elevators")
        elevators = cursor.fetchall()
        
        self.elevators_table.setRowCount(len(elevators))
        for row, elevator in enumerate(elevators):
            for col, value in enumerate(elevator[:8]):  # فقط 8 ستون اول
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.elevators_table.setItem(row, col, item)
        
        # پر کردن کامبو باکس‌ها
        self.maintenance_elevator_combo.clear()
        self.control_elevator_combo.clear()
        for elevator in elevators:
            self.maintenance_elevator_combo.addItem(f"{elevator[0]} - {elevator[1]}", elevator[0])
            self.control_elevator_combo.addItem(f"{elevator[0]} - {elevator[1]}", elevator[0])
    
    def load_maintenance_logs(self):
        """بارگذاری تاریخچه سرویس‌ها"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT m.service_date, e.name, m.technician, m.service_type, 
                   m.description, m.parts_replaced, m.next_service_date
            FROM maintenance_logs m
            JOIN elevators e ON m.elevator_id = e.elevator_id
            ORDER BY m.service_date DESC
        ''')
        logs = cursor.fetchall()
        
        self.maintenance_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            for col, value in enumerate(log):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.maintenance_table.setItem(row, col, item)
        
        # بارگذاری گزارشات
        self.load_reports()
    
    def load_reports(self):
        """بارگذاری گزارشات"""
        # آسانسورهای نیازمند سرویس
        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT elevator_id, name, status, next_service 
            FROM elevators 
            WHERE next_service <= ? AND status != 'در حال تعمیر'
            ORDER BY next_service ASC
        ''', (datetime.now().date().strftime('%Y-%m-%d'),))
        
        due_elevators = cursor.fetchall()
        self.due_table.setRowCount(len(due_elevators))
        for row, elevator in enumerate(due_elevators):
            for col, value in enumerate(elevator):
                item = QTableWidgetItem(str(value))
                if col == 3 and value <= datetime.now().date().strftime('%Y-%m-%d'):
                    item.setBackground(Qt.red)
                    item.setForeground(Qt.white)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.due_table.setItem(row, col, item)
        
        # آمار سرویس‌ها
        cursor.execute('''
            SELECT 
                COUNT(*) as total_services,
                COUNT(DISTINCT elevator_id) as elevators_serviced,
                SUM(CASE WHEN service_type = 'سرویس دوره‌ای' THEN 1 ELSE 0 END) as periodic,
                SUM(CASE WHEN service_type = 'تعمیر مکانیکی' THEN 1 ELSE 0 END) as mechanical,
                SUM(CASE WHEN service_type = 'تعمیر الکتریکی' THEN 1 ELSE 0 END) as electrical
            FROM maintenance_logs
            WHERE service_date BETWEEN ? AND ?
        ''', (
            self.from_date_input.date().toString('yyyy-MM-dd'),
            self.to_date_input.date().toString('yyyy-MM-dd')
        ))
        
        stats = cursor.fetchone()
        stats_text = f"""
        آمار سرویس‌ها از {self.from_date_input.date().toString('yyyy/MM/dd')} تا {self.to_date_input.date().toString('yyyy/MM/dd')}:
        
        - تعداد کل سرویس‌ها: {stats[0]}
        - تعداد آسانسورهای سرویس شده: {stats[1]}
        - سرویس‌های دوره‌ای: {stats[2]}
        - تعمیرات مکانیکی: {stats[3]}
        - تعمیرات الکتریکی: {stats[4]}
        """
        self.stats_text.setPlainText(stats_text)
    
    def add_elevator(self):
        """اضافه کردن آسانسور جدید"""
        name = self.elevator_name_input.text().strip()
        capacity = self.capacity_input.text().strip()
        manufacturer = self.manufacturer_input.text().strip()
        service_interval = self.service_interval_input.text().strip()
        installation_date = self.installation_date_input.date().toString('yyyy-MM-dd')
        
        if not name or not capacity or not manufacturer:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدهای ضروری را پر کنید")
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO elevators (
                    name, current_floor, status, last_service, next_service,
                    service_interval, capacity, manufacturer, installation_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                1,
                'فعال',
                datetime.now().date().strftime('%Y-%m-%d'),
                (datetime.now() + timedelta(days=int(service_interval))).strftime('%Y-%m-%d'),
                int(service_interval),
                int(capacity),
                manufacturer,
                installation_date
            ))
            self.db_connection.commit()
            
            QMessageBox.information(self, "موفق", "آسانسور جدید با موفقیت اضافه شد")
            
            # پاک کردن فیلدها
            self.elevator_name_input.clear()
            self.capacity_input.clear()
            self.manufacturer_input.clear()
            
            # بارگذاری مجدد لیست
            self.load_elevators()
        
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در اضافه کردن آسانسور: {str(e)}")
    
    def log_maintenance(self):
        """ثبت سرویس انجام شده"""
        elevator_id = self.maintenance_elevator_combo.currentData()
        technician = self.technician_input.text().strip()
        service_type = self.service_type_combo.currentText()
        description = self.description_input.toPlainText().strip()
        parts_replaced = self.parts_replaced_input.text().strip()
        service_date = self.service_date_input.date().toString('yyyy-MM-dd')
        
        if not technician or not description:
            QMessageBox.warning(self, "خطا", "لطفاً فیلدهای تکنسین و توضیحات را پر کنید")
            return
        
        try:
            # دریافت بازه سرویس برای این آسانسور
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT service_interval FROM elevators WHERE elevator_id = ?', (elevator_id,))
            interval = cursor.fetchone()[0]
            
            next_service = (datetime.strptime(service_date, '%Y-%m-%d') + timedelta(days=interval)).strftime('%Y-%m-%d')
            
            # ثبت سرویس
            cursor.execute('''
                INSERT INTO maintenance_logs (
                    elevator_id, technician, service_date, service_type,
                    description, parts_replaced, next_service_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                elevator_id,
                technician,
                service_date,
                service_type,
                description,
                parts_replaced,
                next_service
            ))
            
            # به‌روزرسانی وضعیت آسانسور
            cursor.execute('''
                UPDATE elevators 
                SET status = 'فعال', last_service = ?, next_service = ?
                WHERE elevator_id = ?
            ''', (service_date, next_service, elevator_id))
            
            self.db_connection.commit()
            
            QMessageBox.information(self, "موفق", "سرویس با موفقیت ثبت شد")
            
            # پاک کردن فیلدها
            self.technician_input.clear()
            self.description_input.clear()
            self.parts_replaced_input.clear()
            
            # بارگذاری مجدد داده‌ها
            self.load_elevators()
            self.load_maintenance_logs()
        
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت سرویس: {str(e)}")
    
    def report_problem_dialog(self):
        """گزارش مشکل در آسانسور"""
        elevator_id = self.maintenance_elevator_combo.currentData()
        if not elevator_id:
            return
        
        # نمایش دیالوگ برای دریافت توضیحات مشکل
        text, ok = QInputDialog.getText(
            self, 
            "گزارش مشکل", 
            "لطفاً مشکل آسانسور را شرح دهید:",
            QLineEdit.Normal,
            ""
        )
        
        if ok and text:
            try:
                cursor = self.db_connection.cursor()
                
                # به‌روزرسانی وضعیت آسانسور
                cursor.execute('''
                    UPDATE elevators 
                    SET status = 'نیاز به سرویس'
                    WHERE elevator_id = ?
                ''', (elevator_id,))
                
                # ثبت در لاگ
                cursor.execute('''
                    INSERT INTO maintenance_logs (
                        elevator_id, service_date, description
                    )
                    VALUES (?, ?, ?)
                ''', (
                    elevator_id,
                    datetime.now().date().strftime('%Y-%m-%d'),
                    f"مشکل گزارش شده: {text}"
                ))
                
                self.db_connection.commit()
                
                QMessageBox.information(self, "موفق", "مشکل با موفقیت گزارش شد")
                
                # بارگذاری مجدد داده‌ها
                self.load_elevators()
                self.load_maintenance_logs()
            
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در گزارش مشکل: {str(e)}")
    
    def move_elevator(self):
        """کنترل حرکت آسانسور"""
        elevator_id = self.control_elevator_combo.currentData()
        target_floor = self.target_floor_input.text().strip()
        
        if not elevator_id or not target_floor:
            QMessageBox.warning(self, "خطا", "لطفاً آسانسور و طبقه مقصد را انتخاب کنید")
            return
        
        try:
            target_floor = int(target_floor)
            
            # دریافت وضعیت فعلی آسانسور
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT status, current_floor FROM elevators WHERE elevator_id = ?', (elevator_id,))
            status, current_floor = cursor.fetchone()
            
            if status != 'فعال':
                QMessageBox.warning(self, "خطا", f"آسانسور در وضعیت {status} نمی‌تواند حرکت کند")
                return
            
            # شبیه‌سازی حرکت
            time_taken = abs(target_floor - current_floor) * 2  # 2 ثانیه برای هر طبقه
            
            # به‌روزرسانی طبقه فعلی
            cursor.execute('''
                UPDATE elevators 
                SET current_floor = ?
                WHERE elevator_id = ?
            ''', (target_floor, elevator_id))
            self.db_connection.commit()
            
            # نمایش پیام
            self.movement_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] آسانسور {elevator_id} از طبقه {current_floor} به {target_floor} حرکت کرد. زمان: {time_taken} ثانیه")
            
            # به‌روزرسانی نمایش وضعیت
            self.update_elevator_status_display(elevator_id)
        
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در حرکت آسانسور: {str(e)}")
    
    def update_elevator_status_display(self, elevator_id):
        """به‌روزرسانی نمایش وضعیت آسانسور"""
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT name, status, current_floor FROM elevators WHERE elevator_id = ?', (elevator_id,))
        name, status, floor = cursor.fetchone()
        
        self.status_display.setText(f"وضعیت: {status}")
        self.floor_display.setText(f"طبقه فعلی: {floor}")
        
        # تغییر رنگ بر اساس وضعیت
        if status == 'فعال':
            self.status_display.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold;")
        elif status == 'نیاز به سرویس':
            self.status_display.setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold;")
        elif status == 'در حال تعمیر':
            self.status_display.setStyleSheet("color: #F44336; font-size: 18px; font-weight: bold;")
        else:
            self.status_display.setStyleSheet("color: #9E9E9E; font-size: 18px; font-weight: bold;")
    
    def apply_filters(self):
        """اعمال فیلترها روی گزارشات"""
        self.load_reports()
    
    def show_elevator_details(self, index):
        """نمایش جزئیات آسانسور"""
        row = index.row()
        elevator_id = self.elevators_table.item(row, 0).text()
        
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM elevators WHERE elevator_id = ?', (elevator_id,))
        elevator = cursor.fetchone()
        
        cursor.execute('''
            SELECT service_date, service_type, technician, description 
            FROM maintenance_logs 
            WHERE elevator_id = ? 
            ORDER BY service_date DESC
            LIMIT 5
        ''', (elevator_id,))
        logs = cursor.fetchall()
        
        details = f"""
        جزئیات آسانسور:
        
        کد: {elevator[0]}
        نام: {elevator[1]}
        وضعیت: {elevator[3]}
        طبقه فعلی: {elevator[2]}
        ظرفیت: {elevator[7]} نفر
        سازنده: {elevator[8]}
        تاریخ نصب: {elevator[9]}
        آخرین سرویس: {elevator[4]}
        سرویس بعدی: {elevator[5]}
        
        آخرین سرویس‌ها:
        """
        
        for log in logs:
            details += f"\n- {log[0]}: {log[1]} توسط {log[2]}\n   {log[3]}\n"
        
        QMessageBox.information(self, "جزئیات آسانسور", details)
    
    def closeEvent(self, event):
        """رویداد بستن پنجره"""
        self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تنظیم فونت برای پشتیبانی از فارسی
    font = QFont()
    font.setFamily("Arial")
    app.setFont(font)
    
    window = HotelElevatorSystem()
    window.show()
    sys.exit(app.exec_())
