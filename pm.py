import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor

class ElevatorPMApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("مدیریت آسانسور هتل")
        self.setGeometry(200, 200, 800, 600)
        self.setWindowIcon(QIcon("icons/elevator.png"))

        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)

        self.current_user = None

        self.load_elevators_data()
        self.show_login_screen()

    def load_elevators_data(self):
        """ بارگذاری داده‌های آسانسورها از فایل JSON """
        try:
            with open("elevators_data.json", "r") as file:
                self.elevators_data = json.load(file)
        except FileNotFoundError:
            self.elevators_data = []

    def save_elevators_data(self):
        """ ذخیره داده‌های آسانسورها به فایل JSON """
        with open("elevators_data.json", "w") as file:
            json.dump(self.elevators_data, file, ensure_ascii=False, indent=4)

    def show_login_screen(self):
        login_screen = QWidget(self)
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("نام کاربری")
        self.username_input.setStyleSheet("font-size: 18px; padding: 10px; margin: 10px; border-radius: 5px;")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font-size: 18px; padding: 10px; margin: 10px; border-radius: 5px;")
        layout.addWidget(self.password_input)

        login_button = QPushButton("ورود", self)
        login_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        login_button.clicked.connect(self.authenticate)
        layout.addWidget(login_button)

        login_screen.setLayout(layout)
        self.central_widget.addWidget(login_screen)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # اعتبارسنجی ورود (بدون رمز برای تست)
        if username == "admin" and password == "admin123":
            self.current_user = username
            self.show_dashboard()
        else:
            self.show_error("نام کاربری یا رمز عبور اشتباه است.")

    def show_dashboard(self):
        dashboard = QWidget(self)
        layout = QVBoxLayout()

        title_label = QLabel(f"خوش آمدید، {self.current_user}", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; margin: 20px; color: #333;")
        layout.addWidget(title_label)

        # دکمه‌ها
        elevators_button = QPushButton("مدیریت آسانسورها", self)
        elevators_button.setStyleSheet("background-color: #2196F3; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        elevators_button.clicked.connect(self.show_elevators_screen)
        layout.addWidget(elevators_button)

        pm_plans_button = QPushButton("برنامه‌های نگهداری دوره‌ای", self)
        pm_plans_button.setStyleSheet("background-color: #FF9800; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        pm_plans_button.clicked.connect(self.show_pm_plans_screen)
        layout.addWidget(pm_plans_button)

        failures_button = QPushButton("گزارش خرابی‌ها", self)
        failures_button.setStyleSheet("background-color: #F44336; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        failures_button.clicked.connect(self.show_failures_screen)
        layout.addWidget(failures_button)

        self.central_widget.addWidget(dashboard)

    def show_error(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("خطا")
        error_label = QLabel(message, self)
        layout = QVBoxLayout()
        layout.addWidget(error_label)
        error_dialog.setLayout(layout)
        error_dialog.exec_()

    def show_elevators_screen(self):
        elevators_screen = QWidget(self)
        layout = QVBoxLayout()

        back_button = QPushButton("بازگشت", self)
        back_button.setStyleSheet("background-color: #9E9E9E; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        back_button.clicked.connect(self.show_dashboard)
        layout.addWidget(back_button)

        title_label = QLabel("لیست آسانسورها", self)
        title_label.setStyleSheet("font-size: 20px; margin: 20px; color: #333;")
        layout.addWidget(title_label)

        elevators_table = QTableWidget(self)
        elevators_table.setRowCount(len(self.elevators_data))  
        elevators_table.setColumnCount(4)  # نام، وضعیت، تغییر وضعیت، حذف
        elevators_table.setHorizontalHeaderLabels(["آسانسور", "وضعیت", "اقدام", "حذف"])

        for row, elevator in enumerate(self.elevators_data):
            elevators_table.setItem(row, 0, QTableWidgetItem(elevator["name"]))
            elevators_table.setItem(row, 1, QTableWidgetItem(elevator["status"]))
            edit_button = QPushButton("تغییر وضعیت")
            edit_button.clicked.connect(lambda checked, r=row: self.change_elevator_status(r))
            elevators_table.setCellWidget(row, 2, edit_button)
            delete_button = QPushButton("حذف")
            delete_button.clicked.connect(lambda checked, r=row: self.delete_elevator(r))
            elevators_table.setCellWidget(row, 3, delete_button)

        layout.addWidget(elevators_table)

        add_button = QPushButton("اضافه کردن آسانسور", self)
        add_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        add_button.clicked.connect(self.add_elevator)
        layout.addWidget(add_button)

        elevators_screen.setLayout(layout)
        self.central_widget.addWidget(elevators_screen)

    def change_elevator_status(self, row):
        """ تغییر وضعیت آسانسور """
        current_status = self.elevators_data[row]["status"]
        new_status = "فعال" if current_status == "خراب" else "خراب"
        self.elevators_data[row]["status"] = new_status
        self.save_elevators_data()
        self.show_elevators_screen()

    def delete_elevator(self, row):
        """ حذف آسانسور """
        del self.elevators_data[row]
        self.save_elevators_data()
        self.show_elevators_screen()

    def add_elevator(self):
        """ افزودن آسانسور جدید """
        add_elevator_dialog = QDialog(self)
        add_elevator_dialog.setWindowTitle("افزودن آسانسور")
        layout = QFormLayout()

        name_input = QLineEdit(self)
        layout.addRow("نام آسانسور:", name_input)

        status_input = QLineEdit(self)
        layout.addRow("وضعیت (فعال/خراب):", status_input)

        add_button = QPushButton("اضافه کردن", self)
        layout.addWidget(add_button)

        add_elevator_dialog.setLayout(layout)
        add_elevator_dialog.exec_()

        # پس از تایید، داده‌ها ذخیره می‌شود
        name = name_input.text()
        status = status_input.text()
        self.elevators_data.append({"name": name, "status": status})
        self.save_elevators_data()
        self.show_elevators_screen()

    def show_pm_plans_screen(self):
        pm_plans_screen = QWidget(self)
        layout = QVBoxLayout()

        back_button = QPushButton("بازگشت", self)
        back_button.setStyleSheet("background-color: #9E9E9E; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        back_button.clicked.connect(self.show_dashboard)
        layout.addWidget(back_button)

        title_label = QLabel("برنامه‌های نگهداری دوره‌ای", self)
        title_label.setStyleSheet("font-size: 20px; margin: 20px; color: #333;")
        layout.addWidget(title_label)

        pm_plans_table = QTableWidget(self)
        pm_plans_table.setRowCount(3)
        pm_plans_table.setColumnCount(3)
        pm_plans_table.setHorizontalHeaderLabels(["برنامه", "تاریخ", "وضعیت"])
        pm_plans_table.setItem(0, 0, QTableWidgetItem("PM 1"))
        pm_plans_table.setItem(0, 1, QTableWidgetItem("1404/01/01"))
        pm_plans_table.setItem(0, 2, QTableWidgetItem("انجام شده"))
        layout.addWidget(pm_plans_table)

        pm_plans_screen.setLayout(layout)
        self.central_widget.addWidget(pm_plans_screen)

    def show_failures_screen(self):
        failures_screen = QWidget(self)
        layout = QVBoxLayout()

        back_button = QPushButton("بازگشت", self)
        back_button.setStyleSheet("background-color: #9E9E9E; color: white; font-size: 18px; padding: 15px; border-radius: 10px;")
        back_button.clicked.connect(self.show_dashboard)
        layout.addWidget(back_button)

        title_label = QLabel("گزارش خرابی‌ها", self)
        title_label.setStyleSheet("font-size: 20px; margin: 20px; color: #333;")
        layout.addWidget(title_label)

        failures_table = QTableWidget(self)
        failures_table.setRowCount(3)
        failures_table.setColumnCount(3)
        failures_table.setHorizontalHeaderLabels(["آسانسور", "توضیحات", "وضعیت"])
        failures_table.setItem(0, 0, QTableWidgetItem("آسانسور 1"))
        failures_table.setItem(0, 1, QTableWidgetItem("مشکل موتور"))
        failures_table.setItem(0, 2, QTableWidgetItem("در حال تعمیر"))
        layout.addWidget(failures_table)

        failures_screen.setLayout(layout)
        self.central_widget.addWidget(failures_screen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ElevatorPMApp()
    window.show()
    sys.exit(app.exec_())
