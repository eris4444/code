import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor
from math import sqrt, sin, cos, tan, log, log10, pi, e, factorial

class AdvancedCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ماشین حساب پیشرفته")
        self.setMinimumSize(400, 600)
        
        # متغیرهای حالت
        self.current_input = ""
        self.result = ""
        self.history = []
        self.dark_mode = False
        self.parentheses_count = 0
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # تغییر تم اولیه
        self.toggle_theme()
    
    def init_ui(self):
        # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # لایه اصلی
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # نمایشگر تاریخچه
        self.history_label = QLabel()
        self.history_label.setAlignment(Qt.AlignRight)
        self.history_label.setStyleSheet("color: #888; font-size: 14px;")
        self.history_label.setMaximumHeight(30)
        main_layout.addWidget(self.history_label)
        
        # نمایشگر اصلی
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("""
            font-size: 32px; 
            border: none;
            background: transparent;
        """)
        self.display.setMinimumHeight(80)
        main_layout.addWidget(self.display)
        
        # لایه دکمه‌ها
        buttons_layout = QVBoxLayout()
        
        # ردیف اول - منو و توابع پیشرفته
        row1 = QHBoxLayout()
        self.theme_btn = self.create_button("☀️", self.toggle_theme, "#f0f0f0", "#333")
        self.clear_btn = self.create_button("C", self.clear, "#ff6b6b", "white")
        self.del_btn = self.create_button("⌫", self.backspace, "#f0f0f0", "#333")
        self.div_btn = self.create_button("÷", lambda: self.append_operator("/"), "#f0f0f0", "#333")
        row1.addWidget(self.theme_btn)
        row1.addWidget(self.clear_btn)
        row1.addWidget(self.del_btn)
        row1.addWidget(self.div_btn)
        buttons_layout.addLayout(row1)
        
        # ردیف دوم
        row2 = QHBoxLayout()
        self.sin_btn = self.create_button("sin", lambda: self.append_function("sin("), "#e0e0e0", "#333")
        self.seven_btn = self.create_button("7", lambda: self.append_number("7"), "#f8f9fa", "#333")
        self.eight_btn = self.create_button("8", lambda: self.append_number("8"), "#f8f9fa", "#333")
        self.nine_btn = self.create_button("9", lambda: self.append_number("9"), "#f8f9fa", "#333")
        self.mul_btn = self.create_button("×", lambda: self.append_operator("*"), "#f0f0f0", "#333")
        row2.addWidget(self.sin_btn)
        row2.addWidget(self.seven_btn)
        row2.addWidget(self.eight_btn)
        row2.addWidget(self.nine_btn)
        row2.addWidget(self.mul_btn)
        buttons_layout.addLayout(row2)
        
        # ردیف سوم
        row3 = QHBoxLayout()
        self.cos_btn = self.create_button("cos", lambda: self.append_function("cos("), "#e0e0e0", "#333")
        self.four_btn = self.create_button("4", lambda: self.append_number("4"), "#f8f9fa", "#333")
        self.five_btn = self.create_button("5", lambda: self.append_number("5"), "#f8f9fa", "#333")
        self.six_btn = self.create_button("6", lambda: self.append_number("6"), "#f8f9fa", "#333")
        self.sub_btn = self.create_button("-", lambda: self.append_operator("-"), "#f0f0f0", "#333")
        row3.addWidget(self.cos_btn)
        row3.addWidget(self.four_btn)
        row3.addWidget(self.five_btn)
        row3.addWidget(self.six_btn)
        row3.addWidget(self.sub_btn)
        buttons_layout.addLayout(row3)
        
        # ردیف چهارم
        row4 = QHBoxLayout()
        self.tan_btn = self.create_button("tan", lambda: self.append_function("tan("), "#e0e0e0", "#333")
        self.one_btn = self.create_button("1", lambda: self.append_number("1"), "#f8f9fa", "#333")
        self.two_btn = self.create_button("2", lambda: self.append_number("2"), "#f8f9fa", "#333")
        self.three_btn = self.create_button("3", lambda: self.append_number("3"), "#f8f9fa", "#333")
        self.add_btn = self.create_button("+", lambda: self.append_operator("+"), "#f0f0f0", "#333")
        row4.addWidget(self.tan_btn)
        row4.addWidget(self.one_btn)
        row4.addWidget(self.two_btn)
        row4.addWidget(self.three_btn)
        row4.addWidget(self.add_btn)
        buttons_layout.addLayout(row4)
        
        # ردیف پنجم
        row5 = QHBoxLayout()
        self.sqrt_btn = self.create_button("√", lambda: self.append_function("sqrt("), "#e0e0e0", "#333")
        self.zero_btn = self.create_button("0", lambda: self.append_number("0"), "#f8f9fa", "#333")
        self.dot_btn = self.create_button(".", lambda: self.append_number("."), "#f8f9fa", "#333")
        self.pi_btn = self.create_button("π", lambda: self.append_number(str(pi)), "#e0e0e0", "#333")
        self.equal_btn = self.create_button("=", self.calculate, "#4dabf7", "white")
        row5.addWidget(self.sqrt_btn)
        row5.addWidget(self.zero_btn)
        row5.addWidget(self.dot_btn)
        row5.addWidget(self.pi_btn)
        row5.addWidget(self.equal_btn)
        buttons_layout.addLayout(row5)
        
        # ردیف ششم - دکمه‌های پیشرفته
        row6 = QHBoxLayout()
        self.log_btn = self.create_button("log", lambda: self.append_function("log10("), "#e0e0e0", "#333")
        self.ln_btn = self.create_button("ln", lambda: self.append_function("log("), "#e0e0e0", "#333")
        self.pow_btn = self.create_button("x^y", lambda: self.append_operator("^"), "#e0e0e0", "#333")
        self.fact_btn = self.create_button("n!", self.append_factorial, "#e0e0e0", "#333")
        self.par_btn = self.create_button("( )", self.toggle_parentheses, "#e0e0e0", "#333")
        row6.addWidget(self.log_btn)
        row6.addWidget(self.ln_btn)
        row6.addWidget(self.pow_btn)
        row6.addWidget(self.fact_btn)
        row6.addWidget(self.par_btn)
        buttons_layout.addLayout(row6)
        
        main_layout.addLayout(buttons_layout)
    
    def create_button(self, text, callback, bg_color, text_color):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 10px;
                font-size: 20px;
                padding: 15px;
                margin: 3px;
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(bg_color)};
            }}
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return btn
    
    def darken_color(self, color):
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # تم تیره
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(40, 40, 40))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.white)
            self.setPalette(palette)
            self.theme_btn.setText("🌙")
            self.display.setStyleSheet("""
                font-size: 32px; 
                border: none;
                color: white;
                background: transparent;
            """)
            self.history_label.setStyleSheet("color: #aaa; font-size: 14px;")
        else:
            # تم روشن
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.ButtonText, Qt.black)
            self.setPalette(palette)
            self.theme_btn.setText("☀️")
            self.display.setStyleSheet("""
                font-size: 32px; 
                border: none;
                color: black;
                background: transparent;
            """)
            self.history_label.setStyleSheet("color: #888; font-size: 14px;")
    
    def append_number(self, number):
        self.current_input += number
        self.update_display()
    
    def append_operator(self, operator):
        if self.current_input and self.current_input[-1] not in "+-*/^":
            self.current_input += operator
            self.update_display()
        elif operator == "-" and (not self.current_input or self.current_input[-1] in "+-*/^"):
            # اجازه دادن به اعداد منفی
            self.current_input += operator
            self.update_display()
    
    def append_function(self, func):
        self.current_input += func
        self.parentheses_count += 1
        self.update_display()
    
    def append_factorial(self):
        if self.current_input and (self.current_input[-1].isdigit() or self.current_input[-1] == ')'):
            self.current_input += "!"
            self.update_display()
    
    def toggle_parentheses(self):
        if "(" not in self.current_input or self.parentheses_count <= 0:
            self.current_input += "("
            self.parentheses_count += 1
        else:
            self.current_input += ")"
            self.parentheses_count -= 1
        self.update_display()
    
    def clear(self):
        self.current_input = ""
        self.result = ""
        self.parentheses_count = 0
        self.update_display()
        self.history_label.setText("")
    
    def backspace(self):
        if not self.current_input:
            return
        
        # مدیریت پرانتزها
        if self.current_input[-1] == "(":
            self.parentheses_count -= 1
        elif self.current_input[-1] == ")":
            self.parentheses_count += 1
        
        self.current_input = self.current_input[:-1]
        self.update_display()
    
    def update_display(self):
        self.display.setText(self.current_input)
        self.display.setFocus()
    
    def calculate(self):
        if not self.current_input:
            return
        
        try:
            # بستن پرانتزهای باز
            while self.parentheses_count > 0:
                self.current_input += ")"
                self.parentheses_count -= 1
            
            # جایگزینی نمادهای ریاضی برای ارزیابی
            expr = self.current_input
            expr = expr.replace("^", "**").replace("÷", "/").replace("×", "*")
            
            # جایگزینی فاکتوریل
            i = 0
            while i < len(expr):
                if expr[i] == "!":
                    j = i - 1
                    while j >= 0 and (expr[j].isdigit() or expr[j] == ')'):
                        if expr[j] == ')':
                            # پیدا کردن پرانتز باز مربوطه
                            balance = 1
                            k = j - 1
                            while k >= 0 and balance > 0:
                                if expr[k] == ')':
                                    balance += 1
                                elif expr[k] == '(':
                                    balance -= 1
                                k -= 1
                            j = k
                            break
                        j -= 1
                    
                    num_expr = expr[j+1:i]
                    expr = expr[:j+1] + f"factorial({num_expr})" + expr[i+1:]
                    i = j + len(f"factorial({num_expr})")
                i += 1
            
            # ارزیابی عبارت
            result = eval(expr, {
                'sqrt': sqrt,
                'sin': sin,
                'cos': cos,
                'tan': tan,
                'log': log,
                'log10': log10,
                'pi': pi,
                'e': e,
                'factorial': factorial
            })
            
            # نمایش نتیجه
            self.result = str(result)
            if '.' in self.result:
                self.result = self.result.rstrip('0').rstrip('.') if '.' in self.result else self.result
            
            self.history.append(f"{self.current_input} = {self.result}")
            self.history_label.setText(self.history[-1] if len(self.history) <= 1 else "... " + self.history[-1])
            self.current_input = self.result
            self.update_display()
        
        except ZeroDivisionError:
            self.display.setText("خطا: تقسیم بر صفر")
            self.current_input = ""
        except ValueError as ve:
            self.display.setText(f"خطا: {str(ve)}")
            self.current_input = ""
        except Exception as e:
            self.display.setText("خطا در محاسبه")
            self.current_input = ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    calculator = AdvancedCalculator()
    calculator.show()
    sys.exit(app.exec_())
