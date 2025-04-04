import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class ElevatorPMApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("مدیریت آسانسور هتل")
        self.setGeometry(200, 200, 800, 600)
        self.setWindowIcon(QIcon("icons/elevator.png"))
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.current_user = None

        self.show_login_screen()

    def show_login_screen(self):
        self.login_screen = QWidget(self)
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("نام کاربری")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("ورود", self)
        login_button.clicked.connect(self.authenticate)
        layout.addWidget(login_button)

        self.login_screen.setLayout(layout)
        self.setCentralWidget(self.login_screen)

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
        self.dashboard = QWidget(self)
        layout = QVBoxLayout()

        title_label = QLabel(f"خوش آمدید، {self.current_user}", self)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # دکمه‌ها
        elevators_button = QPushButton("مدیریت آسانسورها", self)
        elevators_button.clicked.connect(self.show_elevators_screen)
        layout.addWidget(elevators_button)

        pm_plans_button = QPushButton("برنامه‌های نگهداری دوره‌ای", self)
        pm_plans_button.clicked.connect(self.show_pm_plans_screen)
        layout.addWidget(pm_plans_button)

        failures_button = QPushButton("گزارش خرابی‌ها", self)
        failures_button.clicked.connect(self.show_failures_screen)
        layout.addWidget(failures_button)

        self.dashboard.setLayout(layout)
        self.setCentralWidget(self.dashboard)

    def show_error(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("خطا")
        error_label = QLabel(message, self)
        layout = QVBoxLayout()
        layout.addWidget(error_label)
        error_dialog.setLayout(layout)
        error_dialog.exec_()

    def show_elevators_screen(self):
        self.elevators_screen = QWidget(self)
        layout = QVBoxLayout()

        title_label = QLabel("لیست آسانسورها", self)
        layout.addWidget(title_label)

        self.elevators_table = QTableWidget(self)
        self.elevators_table.setRowCount(3)  # نمونه داده
        self.elevators_table.setColumnCount(3)
        self.elevators_table.setHorizontalHeaderLabels(["آسانسور", "وضعیت", "اقدام"])
        self.elevators_table.setItem(0, 0, QTableWidgetItem("آسانسور 1"))
        self.elevators_table.setItem(0, 1, QTableWidgetItem("فعال"))
        self.elevators_table.setItem(0, 2, QTableWidgetItem("نگهداری"))
        self.elevators_table.setItem(1, 0, QTableWidgetItem("آسانسور 2"))
        self.elevators_table.setItem(1, 1, QTableWidgetItem("خراب"))
        self.elevators_table.setItem(1, 2, QTableWidgetItem("تعمیر"))

        layout.addWidget(self.elevators_table)

        self.elevators_screen.setLayout(layout)
        self.setCentralWidget(self.elevators_screen)

    def show_pm_plans_screen(self):
        self.pm_plans_screen = QWidget(self)
        layout = QVBoxLayout()

        title_label = QLabel("برنامه‌های نگهداری دوره‌ای", self)
        layout.addWidget(title_label)

        pm_plans_table = QTableWidget(self)
        pm_plans_table.setRowCount(3)
        pm_plans_table.setColumnCount(3)
        pm_plans_table.setHorizontalHeaderLabels(["برنامه", "تاریخ", "وضعیت"])
        pm_plans_table.setItem(0, 0, QTableWidgetItem("PM 1"))
        pm_plans_table.setItem(0, 1, QTableWidgetItem("1404/01/01"))
        pm_plans_table.setItem(0, 2, QTableWidgetItem("انجام شده"))
        layout.addWidget(pm_plans_table)

        self.pm_plans_screen.setLayout(layout)
        self.setCentralWidget(self.pm_plans_screen)

    def show_failures_screen(self):
        self.failures_screen = QWidget(self)
        layout = QVBoxLayout()

        title_label = QLabel("گزارش خرابی‌ها", self)
        layout.addWidget(title_label)

        failures_table = QTableWidget(self)
        failures_table.setRowCount(3)
        failures_table.setColumnCount(3)
        failures_table.setHorizontalHeaderLabels(["آسانسور", "توضیحات", "وضعیت"])
        failures_table.setItem(0, 0, QTableWidgetItem("آسانسور 1"))
        failures_table.setItem(0, 1, QTableWidgetItem("مشکل موتور"))
        failures_table.setItem(0, 2, QTableWidgetItem("در حال تعمیر"))
        layout.addWidget(failures_table)

        self.failures_screen.setLayout(layout)
        self.setCentralWidget(self.failures_screen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ElevatorPMApp()
    window.show()
    sys.exit(app.exec_())
