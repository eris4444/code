import sqlite3
from datetime import datetime
import random

class HotelElevatorSystem:
    def __init__(self, db_name='hotel_elevators.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """ایجاد جداول پایگاه داده"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS elevators (
                elevator_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                current_floor INTEGER,
                status TEXT CHECK(status IN ('فعال', 'غیرفعال', 'در حال تعمیر', 'نیاز به سرویس')),
                last_service DATE,
                next_service DATE,
                service_interval INTEGER,  -- تعداد روز بین سرویس‌ها
                capacity INTEGER,
                manufacturer TEXT,
                installation_date DATE
            )
        ''')
        
        self.cursor.execute('''
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
        
        self.conn.commit()
    
    def add_elevator(self, name, capacity, manufacturer, installation_date, service_interval=90):
        """اضافه کردن آسانسور جدید"""
        self.cursor.execute('''
            INSERT INTO elevators (name, current_floor, status, last_service, next_service, 
                                 service_interval, capacity, manufacturer, installation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, 1, 'فعال', datetime.now().date(), 
              (datetime.now() + timedelta(days=service_interval)).date(),
              service_interval, capacity, manufacturer, installation_date))
        self.conn.commit()
    
    def log_maintenance(self, elevator_id, technician, service_type, description, parts_replaced=''):
        """ثبت سرویس انجام شده"""
        # دریافت اطلاعات آسانسور
        self.cursor.execute('SELECT service_interval FROM elevators WHERE elevator_id = ?', (elevator_id,))
        interval = self.cursor.fetchone()[0]
        
        service_date = datetime.now().date()
        next_service = (datetime.now() + timedelta(days=interval)).date()
        
        self.cursor.execute('''
            INSERT INTO maintenance_logs (elevator_id, technician, service_date, service_type, 
                                        description, parts_replaced, next_service_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (elevator_id, technician, service_date, service_type, description, parts_replaced, next_service))
        
        # به‌روزرسانی وضعیت آسانسور
        self.cursor.execute('''
            UPDATE elevators 
            SET status = 'فعال', last_service = ?, next_service = ?
            WHERE elevator_id = ?
        ''', (service_date, next_service, elevator_id))
        
        self.conn.commit()
    
    def report_problem(self, elevator_id, problem_description):
        """گزارش مشکل در آسانسور"""
        self.cursor.execute('''
            UPDATE elevators 
            SET status = 'نیاز به سرویس'
            WHERE elevator_id = ?
        ''', (elevator_id,))
        
        # ثبت در لاگ
        self.cursor.execute('''
            INSERT INTO maintenance_logs (elevator_id, service_date, description)
            VALUES (?, ?, ?)
        ''', (elevator_id, datetime.now().date(), f"مشکل گزارش شده: {problem_description}"))
        
        self.conn.commit()
    
    def get_elevators_due_for_service(self):
        """دریافت لیست آسانسورهای نیازمند سرویس"""
        self.cursor.execute('''
            SELECT elevator_id, name, next_service 
            FROM elevators 
            WHERE next_service <= ? AND status != 'در حال تعمیر'
            ORDER BY next_service ASC
        ''', (datetime.now().date(),))
        return self.cursor.fetchall()
    
    def simulate_elevator_movement(self, elevator_id, target_floor):
        """شبیه‌سازی حرکت آسانسور"""
        self.cursor.execute('SELECT status FROM elevators WHERE elevator_id = ?', (elevator_id,))
        status = self.cursor.fetchone()[0]
        
        if status != 'فعال':
            return False, f"آسانسور در وضعیت {status} نمی‌تواند حرکت کند"
        
        # شبیه‌سازی حرکت
        time_taken = abs(target_floor - self.get_current_floor(elevator_id)) * 2  # 2 ثانیه برای هر طبقه
        self._update_current_floor(elevator_id, target_floor)
        
        # 5% احتمال ایجاد مشکل
        if random.random() < 0.05:
            self.report_problem(elevator_id, "مشکل مکانیکی در حین حرکت")
            return False, "آسانسور در حین حرکت دچار مشکل شد"
        
        return True, f"آسانسور به طبقه {target_floor} رسید. زمان حرکت: {time_taken} ثانیه"
    
    def _update_current_floor(self, elevator_id, floor):
        """به‌روزرسانی طبقه فعلی آسانسور"""
        self.cursor.execute('''
            UPDATE elevators 
            SET current_floor = ?
            WHERE elevator_id = ?
        ''', (floor, elevator_id))
        self.conn.commit()
    
    def get_current_floor(self, elevator_id):
        """دریافت طبقه فعلی آسانسور"""
        self.cursor.execute('SELECT current_floor FROM elevators WHERE elevator_id = ?', (elevator_id,))
        return self.cursor.fetchone()[0]
    
    def get_maintenance_history(self, elevator_id, limit=10):
        """دریافت تاریخچه سرویس‌های آسانسور"""
        self.cursor.execute('''
            SELECT service_date, service_type, technician, description 
            FROM maintenance_logs 
            WHERE elevator_id = ?
            ORDER BY service_date DESC
            LIMIT ?
        ''', (elevator_id, limit))
        return self.cursor.fetchall()
    
    def close(self):
        """بستن اتصال به پایگاه داده"""
        self.conn.close()

# نمونه استفاده از سیستم
if __name__ == "__main__":
    from datetime import timedelta
    
    system = HotelElevatorSystem()
    
    # اضافه کردن آسانسورهای نمونه
    system.add_elevator("آسانسور شمالی", 10, "OTIS", "2020-01-15")
    system.add_elevator("آسانسور جنوبی", 8, "Schindler", "2019-05-20")
    
    # شبیه‌سازی حرکت
    success, message = system.simulate_elevator_movement(1, 5)
    print(message)
    
    if not success:
        # ثبت سرویس
        system.log_maintenance(1, "تکنیسین احمدی", "تعمیر مکانیکی", "تعویض کابل کششی", "کابل کششی")
    
    # نمایش آسانسورهای نیازمند سرویس
    print("\nآسانسورهای نیازمند سرویس:")
    for elevator in system.get_elevators_due_for_service():
        print(f"{elevator[1]} (کد: {elevator[0]}) - تاریخ سرویس بعدی: {elevator[2]}")
    
    system.close()
