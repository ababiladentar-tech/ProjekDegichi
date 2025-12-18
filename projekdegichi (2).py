import sys
import os
import sqlite3
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup,QScrollArea, QMessageBox, QGraphicsOpacityEffect, QGridLayout, QCheckBox, QComboBox)
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint)
from PyQt5.QtGui import (QFont, QColor, QPalette)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
import datetime

THEMES = {
    "Matematika": {"bg": "#0f172a", "accent": "#38bdf8", "text": "#e2e8f0", "progress": "#38bdf8"},
    "Fisika": {"bg": "#1e293b", "accent": "#818cf8", "text": "#f1f5f9", "progress": "#818cf8"},
    "Kimia": {"bg": "#451a03", "accent": "#fbbf24", "text": "#fef9c3", "progress": "#fbbf24"},
    "Biologi": {"bg": "#042f2e", "accent": "#10b981", "text": "#d1fae5", "progress": "#10b981"},
    "Bahasa Indonesia": {"bg": "#4c0519", "accent": "#ec4899", "text": "#fce7f3", "progress": "#ec4899"},
    "Bahasa Inggris": {"bg": "#a4520e", "accent": "#ea9839", "text": "#f1f5f9", "progress": "#FF7B00"},
    "PKN": {"bg": "#1e3a1e", "accent": "#22c55e", "text": "#d1fae5", "progress": "#22c55e"},
    "Sosiologi": {"bg": "#365314", "accent": "#a3e635", "text": "#ecfccb", "progress": "#a3e635"},
    "Ekonomi": {"bg": "#431407", "accent": "#f59e0b", "text": "#fef3c7", "progress": "#f59e0b"},
    "Geografi": {"bg": "#19232d", "accent": "#94a3b8", "text": "#e2e8f0", "progress": "#94a3b8"},
    "Sejarah": {"bg": "#3c2f2f", "accent": "#d97706", "text": "#fde68a", "progress": "#d97706"},
    "Matematika Lanjut": {"bg": "#1e1b4b", "accent": "#818cf8", "text": "#e0e7ff", "progress": "#818cf8"},
    "Olahraga": {"bg": "#1a2e05", "accent": "#84cc16", "text": "#d9f99d", "progress": "#84cc16"},
    "Agama": {"bg": "#1e3a1e", "accent": "#a3e635", "text": "#ecfccb", "progress": "#a3e635"},
}

def calculate_level(xp):
    level = 1
    while xp >= 100 * level:
        xp -= 100 * level
        level += 1
    return level

def init_db():
    conn = sqlite3.connect("quizquest.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            xp INTEGER DEFAULT 0,
            grade_class TEXT DEFAULT '10.1',  
            religion TEXT DEFAULT 'Islam',    
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    try:
        c.execute("INSERT INTO users (username, password, xp, grade_class, religion) VALUES (?, ?, ?, ?, ?)",
                  ("victus", "password123", 250, "11.5", "Islam"))
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN grade_class TEXT DEFAULT '10.1'")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN religion TEXT DEFAULT 'Islam'")
    except:
        pass
    conn.commit()
    conn.close()

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: #3b82f6; color: white; border: none;
                border-radius: 12px; padding: 12px 24px;
                font-size: 15px; font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:pressed {
                background: #1d4ed8;
            }
        """)

class SubjectCard(QPushButton):
    def __init__(self, subject, theme, parent=None):
        super().__init__(parent)
        self.subject = subject
        self.theme = theme
        self.setFixedSize(260, 160)
        style = f"""
            QPushButton {{
                background: {theme['accent']}; 
                color: #0f172a; 
                border-radius: 20px;
                font-size: 22px; font-weight: bold;
                qproperty-alignment: AlignCenter;
            }}
            QPushButton:hover {{
                background: {QColor(theme['accent']).lighter(120).name()};
            }}
        """
        self.setStyleSheet(style)
        self.setText(subject)

class PowerUpButton(QPushButton):
    def __init__(self, name, cost_minutes, icon_text, parent=None):
        super().__init__(parent)
        self.name = name
        self.cost_minutes = cost_minutes
        self.setFixedSize(90, 90)
        style = f"""
            QPushButton {{
                background: #1e293b; color: #94a3b8;
                border-radius: 45px; border: none;
                font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{
                background: #334155;
            }}
            QPushButton:disabled {{
                color: #475569;
            }}
        """
        self.setStyleSheet(style)
        self.setText(f"{icon_text}\n-{cost_minutes} menit")
        self.setToolTip(f"{name} (Kurangi {cost_minutes} menit dari waktu ujian)")

class ConfettiParticle(QLabel):
    def __init__(self, parent, x, y, color, size, fall_x_offset):
        super().__init__(parent)
        self.setText("✦")
        self.setFont(QFont("Arial", size))
        self.setStyleSheet(f"color: {color}; background: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.move(x, y)
        self.show()
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(2500 + random.randint(0, 1500))
        self.anim.setStartValue(QPoint(x, y))
        self.anim.setEndValue(QPoint(x + fall_x_offset, parent.height() + 100))
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(2000)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.anim.start()
        self.fade_anim.start()
        QTimer.singleShot(4000, self.deleteLater)

def play_confetti(parent_widget):
    colors_list = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6", "#8b5cf6", "#ec4899"]
    width = parent_widget.width()
    for _ in range(40):
        x = random.randint(0, width)
        y = random.randint(-100, -20)
        color = random.choice(colors_list)
        size = random.randint(18, 32)
        fall_x = random.randint(-120, 120)
        ConfettiParticle(parent_widget, x, y, color, size, fall_x)

def apply_background(widget, image_path):
    widget.setObjectName("background_container")
    widget.setStyleSheet(f"""
        #background_container {{
            background-image: url('{image_path}');
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }}
    """)

def load_questions_from_txt(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File tidak ditemukan: {filepath}")
        return []
    questions = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        blocks = content.split("[SOAL]")
        for block in blocks:
            if not block.strip():
                continue
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            q = {}
            options = []
            for line in lines:
                if line.startswith("text:"):
                    q["text"] = line[5:].strip()
                elif line.startswith("option_A:"):
                    options.append(line[9:].strip())
                elif line.startswith("option_B:"):
                    options.append(line[9:].strip())
                elif line.startswith("option_C:"):
                    options.append(line[9:].strip())
                elif line.startswith("option_D:"):
                    options.append(line[9:].strip())
                elif line.startswith("answer:"):
                    ans = line[7:].strip().upper()
                    q["answer"] = {"A":0, "B":1, "C":2, "D":3}.get(ans, 0)
                elif line.startswith("clue:"):
                    q["clue"] = line[6:].strip()
            if "text" in q and len(options) == 4:
                q["options"] = options
                questions.append(q)
    except Exception as e:
        print(f"❌ Error membaca {filepath}: {e}")
        return []
    return questions

class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DEGICHI - Quiz")
        self.setWindowState(Qt.WindowFullScreen)
        font = QFont()
        font.setPointSize(11)
        font.setFamily("Segoe UI, Tahoma, Geneva, Verdana, sans-serif")
        self.setFont(font)
        self.current_user = None
        self.current_subject = None
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.xp_earned = 0
        self.used_powerups = []
        self.selected_answer = -1
        self.time_left = 90 * 60 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.answers = [-1] * 20
        init_db()
        self.show_login_screen()

    def keyPressEvent(self, event):

        if not hasattr(self, 'questions') or not self.questions:
            return super().keyPressEvent(event)

        key = event.key()

        answer_map = {
            Qt.Key_A: 0, Qt.Key_1: 0,
            Qt.Key_B: 1, Qt.Key_2: 1,
            Qt.Key_C: 2, Qt.Key_3: 2,
            Qt.Key_D: 3, Qt.Key_4: 3,
        }

        if key in answer_map:
            idx = answer_map[key]
            if 0 <= idx < len(self.option_buttons):
                self.option_buttons[idx].setChecked(True)
                self.on_option_selected()  # Simpan jawaban

        elif key == Qt.Key_Right or key == Qt.Key_N:
            if self.selected_answer != -1:
                self.next_question()
            else:
                QMessageBox.warning(self, "Perhatian", "Pilih jawaban dulu sebelum lanjut.")

        elif key == Qt.Key_Left or key == Qt.Key_P:
            if self.current_question_index > 0:
                self.go_to_question(self.current_question_index - 1)

        elif key == Qt.Key_Escape:
            self.confirm_exit_quiz()

        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            if self.next_button.isEnabled():
                self.next_button.click()

        else:
            super().keyPressEvent(event)

    def toggle_password_visibility(self, line_edit, checkbox):
        if checkbox.isChecked():
            line_edit.setEchoMode(QLineEdit.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.Password)

    def show_login_screen(self):
        self.clear_screen()
        self.stacked_widget = QWidget()
        layout = QVBoxLayout(self.stacked_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        title = QLabel("DEGICHI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)
        subtitle = QLabel("Where Knowledge Meets Adventure!!")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18px; color: #94a3b8;")
        layout.addWidget(subtitle)
        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(15)
        form.setMaximumWidth(400)
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_username.setStyleSheet("""
            QLineEdit { padding: 12px; border-radius: 8px; 
            background: #1e293b; border: 1px solid #334155; color: white; }""")
        form_layout.addWidget(self.login_username)
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet("""
            QLineEdit { padding: 12px; border-radius: 8px; 
            background: #1e293b; border: 1px solid #334155; color: white; }""")
        form_layout.addWidget(self.login_password)
        toggle_layout = QHBoxLayout()
        self.login_toggle = QCheckBox("Lihat Password")
        self.login_toggle.setStyleSheet("color: #94a3b8;")
        self.login_toggle.toggled.connect(lambda: self.toggle_password_visibility(self.login_password, self.login_toggle))
        toggle_layout.addWidget(self.login_toggle)
        toggle_layout.addStretch()
        form_layout.addLayout(toggle_layout)
        btn_login = AnimatedButton("Masuk")
        btn_login.clicked.connect(self.handle_login)
        form_layout.addWidget(btn_login)
        btn_register = AnimatedButton("Daftar")
        btn_register.setStyleSheet("background: #64748b;")
        btn_register.clicked.connect(self.show_register_screen)
        form_layout.addWidget(btn_register)
        layout.addWidget(form)
        apply_background(self.stacked_widget, "asset/1.png")
        self.setCentralWidget(self.stacked_widget)

    def show_register_screen(self):
        self.clear_screen()
        self.stacked_widget = QWidget()
        layout = QVBoxLayout(self.stacked_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        btn_back = QPushButton("← Kembali")
        btn_back.setStyleSheet("color: #94a3b8; border: none; font-size: 14px;")
        btn_back.clicked.connect(self.show_login_screen)
        layout.addWidget(btn_back, alignment=Qt.AlignLeft)
        title = QLabel("Daftar Akun Baru")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)
        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(15)
        form.setMaximumWidth(400)
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Username (min 4 karakter)")
        self.reg_username.setStyleSheet("""
            QLineEdit { padding: 12px; border-radius: 8px; 
            background: #1e293b; border: 1px solid #334155; color: white; }
        """)
        form_layout.addWidget(self.reg_username)
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Password (min 6 karakter)")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setStyleSheet("""
            QLineEdit { padding: 12px; border-radius: 8px; 
            background: #1e293b; border: 1px solid #334155; color: white; }
        """)
        form_layout.addWidget(self.reg_password)
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Konfirmasi Password")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_confirm.setStyleSheet("""
            QLineEdit { padding: 12px; border-radius: 8px; 
            background: #1e293b; border: 1px solid #334155; color: white; }
        """)
        form_layout.addWidget(self.reg_confirm)
        toggle_layout = QHBoxLayout()
        self.reg_toggle = QCheckBox("Lihat Password")
        self.reg_toggle.setStyleSheet("color: #94a3b8;")
        self.reg_toggle.toggled.connect(lambda: self.toggle_password_visibility(self.reg_password, self.reg_toggle))
        self.reg_toggle.toggled.connect(lambda: self.toggle_password_visibility(self.reg_confirm, self.reg_toggle))
        toggle_layout.addWidget(self.reg_toggle)
        toggle_layout.addStretch()
        form_layout.addLayout(toggle_layout)
        grade_label = QLabel("Kelas:")
        grade_label.setStyleSheet("color: #94a3b8; font-size: 14px;")
        form_layout.addWidget(grade_label)
        self.grade_combo = QComboBox()
        kelas_list = []
        for grade in [10, 11, 12]:
            for rombel in range(1, 10):
                kelas_list.append(f"{grade}.{rombel}")
        self.grade_combo.addItems(kelas_list)
        self.grade_combo.setCurrentText("11.1")
        self.grade_combo.setStyleSheet("""
            QComboBox {
                padding: 8px; border-radius: 8px;
                background: #1e293b; color: white;
                border: 1px solid #334155;""")
        form_layout.addWidget(self.grade_combo)
        religion_label = QLabel("Agama:")
        religion_label.setStyleSheet("color: #94a3b8; font-size: 14px;")
        form_layout.addWidget(religion_label)
        religion_layout = QHBoxLayout()
        self.radio_islam = QRadioButton("Islam")
        self.radio_kristen = QRadioButton("Kristen")
        self.radio_islam.setChecked(True)
        religion_layout.addWidget(self.radio_islam)
        religion_layout.addWidget(self.radio_kristen)
        religion_layout.addStretch()
        form_layout.addLayout(religion_layout)
        btn_register = AnimatedButton("Daftar Sekarang")
        btn_register.clicked.connect(self.handle_register)
        form_layout.addWidget(btn_register)
        layout.addWidget(form)
        apply_background(self.stacked_widget, "asset/1.png")
        self.setCentralWidget(self.stacked_widget)

    def handle_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        grade_class = self.grade_combo.currentText()
        religion = "Islam" if self.radio_islam.isChecked() else "Kristen"
        if len(username) < 4:
            QMessageBox.warning(self, "Gagal Daftar", "Username minimal 4 karakter.")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Gagal Daftar", "Password minimal 6 karakter.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Gagal Daftar", "Password tidak cocok.")
            return
        try:
            conn = sqlite3.connect("quizquest.db")
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (username, password, xp, grade_class, religion) 
                VALUES (?, ?, 0, ?, ?)
            """, (username, password, grade_class, religion))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sukses", f"Akun {grade_class} ({religion}) berhasil dibuat!")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Gagal Daftar", "Username sudah digunakan.")

    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        conn = sqlite3.connect("quizquest.db")
        c = conn.cursor()
        c.execute("SELECT id, username, xp, grade_class, religion FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            self.current_user = {
                "id": user[0], 
                "username": user[1], 
                "xp": user[2],
                "grade_class": user[3],
                "religion": user[4]}
            self.show_dashboard()
        else:
            QMessageBox.warning(self, "Gagal Masuk", "Username atau password salah.")

    def show_dashboard(self):
        self.clear_screen()
        self.stacked_widget = QWidget()
        layout = QVBoxLayout(self.stacked_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        header = QHBoxLayout()
        if self.current_user:
            level = calculate_level(self.current_user['xp'])
            user_label = QLabel(f"Halo, {self.current_user['username']}! | XP: {self.current_user['xp']} | Lv.{level}")
            user_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            header.addWidget(user_label)
        header.addStretch()
        layout.addLayout(header)
        title = QLabel("Pilih Mata Pelajaran")
        title.setStyleSheet("font-size: 36px; font-weight: bold; margin: 20px 0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        grid = QGridLayout()
        grid.setSpacing(50)
        subjects = [
            "Matematika", "Fisika", "Kimia", "Biologi",
            "Bahasa Indonesia", "Bahasa Inggris",
            "PKN", "Sosiologi", "Ekonomi", "Geografi",
            "Sejarah", "Matematika Lanjut", "Olahraga", "Agama"
        ]
        for i, subject in enumerate(subjects):
            theme = THEMES.get(subject, THEMES["Fisika"])
            card = SubjectCard(subject, theme)
            card.clicked.connect(lambda _, s=subject: self.start_quiz(s))
            row, col = divmod(i, 4)
            grid.addWidget(card, row, col, Qt.AlignCenter)
        layout.addLayout(grid)
        layout.addStretch()
        footer = QHBoxLayout()
        btn_help = QPushButton("❓Help")
        btn_help.setStyleSheet("""
            QPushButton {
                background: #334155; color: #94a3b8;
                border-radius: 10px; padding: 8px 16px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover {
                background: #475569;
                color: white;
            }
        """)
        btn_help.clicked.connect(self.show_help_dialog)
        footer.addWidget(btn_help)
        footer.addStretch()
        btn_logout = QPushButton("Keluar")
        btn_logout.setStyleSheet("""
            QPushButton {
                background: #ef4444; color: white; 
                border-radius: 12px; padding: 10px 28px;
                font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        btn_logout.clicked.connect(self.show_login_screen)
        footer.addWidget(btn_logout)
        layout.addLayout(footer)
        apply_background(self.stacked_widget, "asset/2.png")
        self.setCentralWidget(self.stacked_widget)

    def show_help_dialog(self):
        help_text = (
            "<h3 style='color:#38bdf8;'>Petunjuk Penggunaan Kuis</h3>"
            "<p style='font-size:14px;'>"
            "<b>1. Timer ⏱️</b><br>"
            "&nbsp;&nbsp;• Waktu total: 90 menit untuk 20 soal.<br>"
            "&nbsp;&nbsp;• Jika waktu habis, kuis otomatis berakhir.<br><br>"
            "<b>2. Jawaban & Navigasi</b><br>"
            "&nbsp;&nbsp;• Klik salah satu pilihan (A–D) untuk memilih.<br>"
            "&nbsp;&nbsp;• Jawaban yang dipilih akan berubah warna & tebal.<br>"
            "&nbsp;&nbsp;• Gunakan scroll daftar nomor soal untuk loncat cepat.<br><br>"
            "<b>3. Power-up (Hanya di Mode Ujian)</b><br>"
            "&nbsp;&nbsp;• 💡 <b>Clue</b>: Dapatkan petunjuk (−5 menit)<br>"
            "&nbsp;&nbsp;• 🎯 <b>50:50</b>: Hilangkan 2 opsi salah (−10 menit)<br>"
            "&nbsp;&nbsp;• 🔍 <b>Reveal</b>: Tunjukkan jawaban benar (−20 menit)<br>"
            "&nbsp;&nbsp;• Power-up hanya aktif jika waktu tersisa cukup.<br><br>"
            "<b>4. Selesai & Hasil</b><br>"
            "&nbsp;&nbsp;• Di soal terakhir, tombol berubah jadi <b>'Selesai'</b>.<br>"
            "&nbsp;&nbsp;• Akan muncul konfirmasi sebelum submit.<br>"
            "&nbsp;&nbsp;• Hasil + XP langsung ditampilkan setelah selesai.<br><br>"
            "<b>5. Navigasi Keyboard</b><br>"
            "&nbsp;&nbsp;• <code>A</code> atau <code>1</code> → Pilih jawaban A<br>"
            "&nbsp;&nbsp;• <code>B</code> atau <code>2</code> → Pilih jawaban B<br>"
            "&nbsp;&nbsp;• <code>C</code> atau <code>3</code> → Pilih jawaban C<br>"
            "&nbsp;&nbsp;• <code>D</code> atau <code>4</code> → Pilih jawaban D<br>"
            "&nbsp;&nbsp;• <code>→</code> atau <code>N</code> → Soal berikutnya<br>"
            "&nbsp;&nbsp;• <code>←</code> atau <code>P</code> → Soal sebelumnya<br>"
            "&nbsp;&nbsp;• <code>Esc</code> → Keluar (dengan konfirmasi)<br><br>"
            "<b>Catatan:</b><br>"
            "&nbsp;&nbsp;• Jawaban otomatis tersimpan saat dipilih.<br>"
            "&nbsp;&nbsp;• Anda bisa mengganti jawaban kapan saja.<br>"
            "&nbsp;&nbsp;• Pastikan koneksi file soal berada di folder <code>questions/[kelas]/</code>."
            "</p>"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("❓ Bantuan Penggunaan")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0f172a;
                color: #e2e8f0;
            }
            QLabel {
                min-width: 500px;
                padding: 15px;
            }
            QPushButton {
                background: #3b82f6; 
                color: white; 
                border-radius: 8px; 
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        msg.exec_()

    def start_quiz(self, subject):
        grade_part = self.current_user["grade_class"].split(".")[0]
        subject_map = {
            "Matematika": "matematika",
            "Fisika": "fisika",
            "Kimia": "kimia",
            "Biologi": "biologi",
            "Bahasa Indonesia": "bahasa_indonesia",
            "Bahasa Inggris": "bahasa_inggris",
            "PKN": "pkn",
            "Sosiologi": "sosiologi",
            "Ekonomi": "ekonomi",
            "Geografi": "geografi",
            "Sejarah": "sejarah",
            "Matematika Lanjut": "matematika_lanjut",
            "Olahraga": "olahraga",
            "Agama": f"agama_{self.current_user['religion'].lower()}"
        }
        filename = subject_map.get(subject)
        if not filename:
            QMessageBox.critical(self, "Error", f"Mapel {subject} tidak didukung.")
            return
        filepath = f"questions/{grade_part}/{filename}.txt"
        if not os.path.exists(filepath):
            QMessageBox.critical(self, "File Tidak Ditemukan", 
                f"Soal tidak ditemukan:\n{filepath}\n"
                f"Pastikan folder & file sudah dibuat.")
            return
        all_questions = load_questions_from_txt(filepath)
        if len(all_questions) < 20:
            QMessageBox.warning(self, "Soal Kurang", 
                f"Hanya ada {len(all_questions)} soal untuk {subject} (kelas {grade_part}).\n"
                "Dibutuhkan minimal 20.")
            return
        self.questions = random.sample(all_questions, 20)
        self.current_subject = subject
        self.current_question_index = 0
        self.score = 0
        self.xp_earned = 0
        self.used_powerups = []
        self.selected_answer = -1
        self.time_left = 90 * 60
        self.timer.start(1000)
        self.answers = [-1] * 20
        self.show_quiz_screen()

    def show_quiz_screen(self):
        self.clear_screen()
        theme = THEMES[self.current_subject]
        self.stacked_widget = QWidget()
        main_layout = QVBoxLayout(self.stacked_widget)
        main_layout.setContentsMargins(30, 20, 30, 20)
        top_bar = QHBoxLayout()
        self.timer_label = QLabel(self.format_time(self.time_left))
        self.timer_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme['accent']};")
        top_bar.addWidget(self.timer_label)
        level = calculate_level(self.current_user['xp'] + self.xp_earned)
        self.xp_label = QLabel(f"XP: {self.current_user['xp'] + self.xp_earned} | Lv.{level}")
        self.xp_label.setStyleSheet("font-size: 16px;")
        top_bar.addWidget(self.xp_label)
        top_bar.addStretch()
        btn_menu = QPushButton("☰ Menu")
        btn_menu.setStyleSheet("color: #94a3b8; border: none;")
        btn_menu.clicked.connect(self.confirm_exit_quiz)
        top_bar.addWidget(btn_menu)
        main_layout.addLayout(top_bar)
        self.progress_bar = QLabel()
        self.progress_bar.setFixedHeight(8)
        self.update_progress_bar()
        main_layout.addWidget(self.progress_bar)
        q_num = QLabel(f"Soal {self.current_question_index + 1} dari 20")
        q_num.setStyleSheet("font-size: 18px; font-weight: bold; margin: 15px 0;")
        main_layout.addWidget(q_num)
        self.question_label = QLabel(self.questions[self.current_question_index]["text"])
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("font-size: 20px; margin: 20px 0;")
        main_layout.addWidget(self.question_label)
        self.option_group = QButtonGroup(self)
        self.option_buttons = []
        options_layout = QVBoxLayout()
        options_layout.setSpacing(12)
        for i, opt in enumerate(self.questions[self.current_question_index]["options"]):
            btn = QRadioButton(f"{chr(65+i)}. {opt}")
            style = f"""
                QRadioButton {{
                    background: #334155; color: {theme['text']}; 
                    border-radius: 10px; padding: 14px;
                    font-size: 16px;
                }}
                QRadioButton::indicator {{
                    width: 0; height: 0;
                }}
                QRadioButton:hover {{
                    background: #475569;
                }}
            """
            btn.setStyleSheet(style)
            self.option_group.addButton(btn, i)
            btn.clicked.connect(self.on_option_selected)
            options_layout.addWidget(btn)
            self.option_buttons.append(btn)
        main_layout.addLayout(options_layout)
        saved_answer = self.answers[self.current_question_index]
        if saved_answer != -1:
            self.option_buttons[saved_answer].setChecked(True)
            self.selected_answer = saved_answer
            self.on_option_selected()
        powerup_layout = QHBoxLayout()
        powerup_layout.setSpacing(20)
        powerup_layout.setAlignment(Qt.AlignCenter)
        self.powerup_buttons = []
        powerups = [
            ("Clue", 5, "💡"),
            ("50:50", 10, "🎯"),
            ("Reveal", 20, "🔍")
        ]
        for name, cost_min, icon in powerups:
            btn = PowerUpButton(name, cost_min, icon)
            btn.clicked.connect(lambda _, n=name: self.use_powerup(n))
            self.powerup_buttons.append(btn)
            powerup_layout.addWidget(btn)
        main_layout.addLayout(powerup_layout)
        nav_label = QLabel("Navigasi Soal:")
        nav_label.setStyleSheet("font-size: 14px; margin-top: 20px;")
        main_layout.addWidget(nav_label)
        nav_scroll = QScrollArea()
        nav_scroll.setFixedHeight(50)
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setStyleSheet("border: none;")
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setSpacing(6)
        self.nav_buttons = []
        for i in range(20):
            btn = QPushButton(str(i+1))
            btn.setFixedSize(36, 36)
            if i == self.current_question_index:
                btn.setStyleSheet("""
                    QPushButton { 
                        background: #60a5fa; color: white; 
                        border-radius: 18px; font-size: 12px; 
                        font-weight: bold;
                    }
                """)
            elif self.answers[i] != -1:
                btn.setStyleSheet("""
                    QPushButton { 
                        background: #3b82f6; color: white; 
                        border-radius: 18px; font-size: 12px; }""")
            else:
                btn.setStyleSheet("""
                    QPushButton { 
                        background: #475569; color: #94a3b8; 
                        border-radius: 18px; font-size: 12px; 
                    }
                    QPushButton:hover { background: #64748b; }
                """)
            btn.clicked.connect(lambda _, idx=i: self.go_to_question(idx))
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)
        nav_scroll.setWidget(nav_widget)
        main_layout.addWidget(nav_scroll)
        self.next_button = AnimatedButton("Soal Berikutnya")
        self.next_button.setEnabled(self.selected_answer != -1)
        self.next_button.clicked.connect(self.next_question)
        if self.current_question_index == 19:
            self.next_button.setText("Selesai")
        main_layout.addWidget(self.next_button, alignment=Qt.AlignCenter)
        bg_map = {
            "Matematika": "asset/3.png",
            "Biologi": "asset/5.png",
            "Fisika": "asset/6.png",
            "Bahasa Indonesia": "asset/7.png",
            "Kimia": "asset/8.png",
            "Bahasa Inggris": "asset/9.png",
        }
        bg_path = bg_map.get(self.current_subject, "asset/2.png")
        apply_background(self.stacked_widget, bg_path)
        self.setCentralWidget(self.stacked_widget)

    def show_result_screen(self):
        if not hasattr(self, 'score'):
            self.score = 0
        if not hasattr(self, 'xp_earned'):
            self.xp_earned = 0
        self.timer.stop()
        self.clear_screen()
        theme = THEMES[self.current_subject]
        self.stacked_widget = QWidget()
        layout = QVBoxLayout(self.stacked_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        title = QLabel("Hasil Ujian")
        title.setStyleSheet("font-size: 42px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        subtitle = QLabel(self.current_subject)
        subtitle.setStyleSheet(f"font-size: 24px; color: {theme['accent']};")
        layout.addWidget(subtitle)
        total_xp = self.current_user['xp'] + self.xp_earned
        conn = sqlite3.connect("quizquest.db")
        c = conn.cursor()
        c.execute("UPDATE users SET xp = ? WHERE username = ?", (total_xp, self.current_user['username']))
        conn.commit()
        conn.close()
        level = calculate_level(total_xp)
        stats = [
            ("Skor", f"{self.score} / 20"),
            ("Waktu Tersisa", self.format_time(self.time_left)),
            ("XP Diperoleh", f"+{self.xp_earned}"),
            ("Level Saat Ini", f"Lv. {level}"),
            ("Power-up Digunakan", str(len(self.used_powerups)) if self.used_powerups else "Tidak ada")
        ]
        for label, value in stats:
            row = QHBoxLayout()
            l = QLabel(label + ":")
            l.setStyleSheet("font-size: 18px; font-weight: bold;")
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 18px; color: {theme['accent']};")
            row.addWidget(l)
            row.addWidget(v)
            row.addStretch()
            layout.addLayout(row)
        score_percent = (self.score / 20) * 100
        if score_percent >= 90:
            message = "Luar Biasa! Kamu Hebat!"
            color = "gold"
        elif score_percent >= 80:
            message = "Bagus Sekali! Kamu Cerdas!"
            color = "#3b82f6"
        elif score_percent >= 70:
            message = "Lumayan! Tingkatkan Lagi!"
            color = "#10b981"
        elif score_percent >= 60:
            message = "Hampir Lulus! Belajar Lagi Ya!"
            color = "#f59e0b"
        else:
            message = "Belum Lulus. Jangan Menyerah!"
            color = "#ef4444"
        message_label = QLabel(message)
        message_label.setStyleSheet(f"font-size: 22px; color: {color}; margin: 30px 0; font-weight: bold;")
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)
        QTimer.singleShot(300, lambda: play_confetti(self.stacked_widget))
        btn_pdf = AnimatedButton("Cetak Hasil (PDF)")
        btn_pdf.clicked.connect(self.export_result_to_pdf)
        layout.addWidget(btn_pdf)
        btn_back = AnimatedButton("Kembali ke Dashboard")
        btn_back.clicked.connect(self.show_dashboard)
        layout.addWidget(btn_back)
        
        if self.current_subject == "Matematika":
            apply_background(self.stacked_widget, "asset/4.png")
        else:
            bg_map = {
                "Biologi": "asset/5.png",
                "Fisika": "asset/6.png",
                "Bahasa Indonesia": "asset/7.png",
                "Kimia": "asset/8.png",
                "Bahasa Inggris": "asset/9.png",
            }
            bg_path = bg_map.get(self.current_subject, "asset/2.png")
            apply_background(self.stacked_widget, bg_path)
        self.setCentralWidget(self.stacked_widget)

    def export_result_to_pdf(self):
        if not self.current_user or not self.current_subject:
            QMessageBox.warning(self, "Gagal", "Data ujian tidak ditemukan.")
            return
        folder = "reports"
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_subject = self.current_subject.replace(" ", "_").lower()
        filename = f"hasil_{self.current_user['username']}_{safe_subject}_{timestamp}.pdf"
        filepath = os.path.join(folder, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        margin = 20 * mm
        y = height - margin
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, y, "LAPORAN HASIL UJIAN")
        y -= 16
        c.setFont("Helvetica", 11)
        c.drawCentredString(width / 2, y, "Aplikasi CBT DEGICHI")
        y -= 10
        c.line(margin, y, width - margin, y)
        y -= 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, "DATA PESERTA")
        y -= 5
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.grey)
        c.rect(margin, y - 40, (width / 2) - margin * 1.2, 40, stroke=1, fill=0)
        c.setFont("Helvetica", 10)
        line_y = y - 10
        c.drawString(margin + 5, line_y, f"Nama        : {self.current_user['username']}")
        line_y -= 12
        c.drawString(margin + 5, line_y, f"Kelas       : {self.current_user.get('grade_class', '-')}")
        line_y -= 12
        c.drawString(margin + 5, line_y, f"Agama       : {self.current_user.get('religion', '-')}")
        box_x = (width / 2) + 5
        box_width = (width / 2) - margin - 5
        c.setFont("Helvetica-Bold", 11)
        c.drawString(box_x, y, "DATA UJIAN")
        y2 = y - 5
        c.rect(box_x, y2 - 40, box_width, 40, stroke=1, fill=0)
        c.setFont("Helvetica", 10)
        line_y2 = y2 - 10
        c.drawString(box_x + 5, line_y2, f"Mata Pelajaran : {self.current_subject}")
        line_y2 -= 12
        score_percent = (self.score / 20) * 100 if hasattr(self, "score") else 0
        c.drawString(box_x + 5, line_y2, f"Skor           : {self.score} / 20 ({score_percent:.1f}%)")
        line_y2 -= 12
        total_seconds = 90 * 60
        used_seconds = total_seconds - self.time_left if hasattr(self, "time_left") else 0
        used_minutes = used_seconds // 60
        c.drawString(box_x + 5, line_y2, f"Waktu Terpakai : {used_minutes} menit")
        y = y2 - 60
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, "REKAP NILAI")
        y -= 5
        c.rect(margin, y - 45, width - 2 * margin, 45, stroke=1, fill=0)
        KKM = 75
        nilai_angka = score_percent
        status = "LULUS" if nilai_angka >= KKM else "TIDAK LULUS"
        c.setFont("Helvetica", 10)
        line_y = y - 12
        c.drawString(margin + 5, line_y, f"Nilai Akhir : {nilai_angka:.1f}")
        line_y -= 12
        c.drawString(margin + 5, line_y, f"KKM         : {KKM}")
        line_y -= 12
        c.drawString(margin + 5, line_y, f"Status      : {status}")
        y = line_y - 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, "CATATAN")
        y -= 5
        c.rect(margin, y - 45, width - 2 * margin, 45, stroke=1, fill=0)
        c.setFont("Helvetica", 10)
        text = c.beginText()
        text.setTextOrigin(margin + 5, y - 15)
        text.setLeading(12)
        if score_percent >= 90:
            catatan = "Luar biasa. Pertahankan prestasi belajar Anda."
        elif score_percent >= 80:
            catatan = "Sangat baik. Tetap konsisten dalam belajar."
        elif score_percent >= 70:
            catatan = "Cukup baik. Masih bisa ditingkatkan."
        elif score_percent >= 60:
            catatan = "Hampir mencapai standar. Perbanyak latihan soal."
        else:
            catatan = "Belum memenuhi standar ketuntasan. Disarankan untuk belajar kembali materi terkait."
        text.textLine(catatan)
        c.drawText(text)
        y = y - 80
        today_str = datetime.datetime.now().strftime("%d %B %Y")
        c.setFont("Helvetica", 10)
        c.drawRightString(width - margin, y, f"Dicetak pada: {today_str}")
        y -= 50
        c.drawRightString(width - margin, y, "Guru Pengampu,")
        y -= 40
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(width - margin, y, "( ................................... )")
        c.showPage()
        c.save()
        QMessageBox.information(
            self,
            "PDF Berhasil Dibuat",
            f"Laporan hasil ujian berhasil disimpan.\nLokasi:\n{os.path.abspath(filepath)}"
        )

    def clear_screen(self):
        if self.centralWidget():
            self.centralWidget().deleteLater()

    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"⏱️ {mins:02d}:{secs:02d}"

    def update_timer(self):
        if self.time_left <= 0:
            self.time_left = 0
            self.timer.stop()
            QMessageBox.warning(self, "Waktu Habis!", "Waktu pengerjaan telah habis.")
            self.show_result_screen()
        else:
            self.time_left -= 1
            self.timer_label.setText(self.format_time(self.time_left))

    def update_progress_bar(self):
        theme = THEMES[self.current_subject]
        percent = (self.current_question_index + 1) / 20
        width = int(self.width() * 0.9)
        bar_width = int(width * percent)
        html = f"""
        <div style="background: #334155; height: 8px; border-radius: 4px;">
            <div style="background: {theme['progress']}; height: 8px; width: {bar_width}px; border-radius: 4px;"></div>
        </div>
        """
        self.progress_bar.setText(html)
        self.progress_bar.setTextFormat(Qt.RichText)

    def on_option_selected(self):
        self.selected_answer = self.option_group.checkedId()
        self.next_button.setEnabled(True)
        if self.answers is not None:
            self.answers[self.current_question_index] = self.selected_answer
        for i, btn in enumerate(self.option_buttons):
            if i == self.selected_answer:
                btn.setStyleSheet(f"""
                    QRadioButton {{
                        background: #3b82f6; color: white;
                        border-radius: 10px; padding: 14px;
                        font-size: 16px; font-weight: bold;
                    }}
                    QRadioButton::indicator {{ width: 0; height: 0; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QRadioButton {{
                        background: #334155; color: {THEMES[self.current_subject]['text']};
                        border-radius: 10px; padding: 14px;
                        font-size: 16px;
                    }}
                    QRadioButton::indicator {{ width: 0; height: 0; }}
                """)

    def next_question(self):
        if self.selected_answer == -1:
            QMessageBox.warning(self, "Perhatian", "Pilih jawaban terlebih dahulu!")
            return
        correct = self.selected_answer == self.questions[self.current_question_index]["answer"]
        if correct:
            self.score += 1
            self.xp_earned += 100
        self.current_question_index += 1
        if self.current_question_index >= 20:
            self.show_result_screen()
        else:
            self.show_quiz_screen()

    def go_to_question(self, index):
        if self.selected_answer != -1:
            self.answers[self.current_question_index] = self.selected_answer
        self.current_question_index = index
        self.show_quiz_screen()

    def use_powerup(self, name):
        if self.time_left <= 0:
            return
        cost_minutes = {"Clue": 5, "50:50": 10, "Reveal": 20}.get(name)
        if cost_minutes is None:
            return
        cost_seconds = cost_minutes * 60
        if self.time_left < cost_seconds:
            QMessageBox.warning(self, "Waktu Tidak Cukup",
                                f"Butuh minimal {cost_minutes} menit untuk {name}.\n"
                                f"Sisa waktu: {self.time_left//60} menit.")
            return
        self.time_left -= cost_seconds
        self.timer_label.setText(self.format_time(self.time_left))
        if not hasattr(self, 'option_buttons') or len(self.option_buttons) != 4:
            return
        q = self.questions[self.current_question_index]
        if name == "Clue":
            clue = q.get("clue", "Tidak ada petunjuk tersedia.")
            QMessageBox.information(self, "💡 Petunjuk", clue)
        elif name == "50:50":
            correct_idx = q["answer"]
            wrong_indices = [i for i in range(4) if i != correct_idx]
            to_remove = random.sample(wrong_indices, 2)
            for i in to_remove:
                if i < len(self.option_buttons):
                    btn = self.option_buttons[i]
                    btn.setText("(Dihilangkan)")
                    btn.setEnabled(False)
                    btn.setStyleSheet("color: #94a3b8;")
        elif name == "Reveal":
            correct_idx = q["answer"]
            for i, btn in enumerate(self.option_buttons):
                if i == correct_idx:
                    btn.setText(btn.text().rstrip(" ✅") + " ✅")
                    btn.setStyleSheet("""
                        QRadioButton {
                            background: #10b981; color: white;
                            border-radius: 10px; padding: 14px;
                            font-size: 16px; font-weight: bold;
                        }
                        QRadioButton::indicator { width: 0; height: 0; }
                    """)
                else:
                    btn.setEnabled(False)

    def confirm_exit_quiz(self):
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Apakah Anda yakin ingin keluar? Waktu tetap berjalan.",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.show_dashboard()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(15, 23, 42))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(30, 41, 59))
    dark_palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(50, 50, 50))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid white; }")
    window = QuizApp()
    window.show()
    sys.exit(app.exec_())