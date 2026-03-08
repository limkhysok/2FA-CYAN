import sys
import time
import pyotp
import pyperclip
import os
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QFrame,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFontDatabase


class TFAApp(QWidget):
    def __init__(self):
        super().__init__()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "assets", "logo.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(500, 200)

        # Load Custom Font
        font_path = os.path.join(base_dir, "assets", "font", "CascadiaMono-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                self.custom_font = font_families[0]
            else:
                self.custom_font = "Cascadia Mono"
        else:
            self.custom_font = "Consolas, monospace"

        # Apply modern premium styling with customized colors
        style = """
            QWidget { 
                background-color: #0b0c10; 
                color: #c5c6c7; 
                font-family: '<FONT_FAMILY>';
            }
            QLineEdit#enter_secret_key { 
                background-color: #1f2833; 
                border: 1px solid none; 
                border-radius: 5px; 
                padding: 12px 10px; 
                color: #66fcf1; 
                font-size: 13px; 
                letter-spacing: 1px;
            }
            QLineEdit#enter_secret_key:focus {
                border: 1px solid none;
                background-color: #1f2833;
            }

            QPushButton#clear_btn {
                padding: 14px 10px;
                border-radius: 5px; 
                background-color: #1f2833;
                color: #c5c6c7;
                border: 1px solid none;
            }
            QPushButton#clear_btn:hover {
                background-color: #2b3846;
                color: #ffffff;
            }
            QPushButton#clear_btn:pressed {
                background-color: #3e8e8a;
                border: 1px solid #45a29e;
            }
            QPushButton#copy_btn {
                padding: 14px 20px;
                border-radius: 5px; 
                background-color: #1f2833;
                color: #c5c6c7;
                border: 1px solid #1f2833;

            }
            QPushButton#copy_btn:hover {
                background-color: #2b3846;
                color: #ffffff;
            }
            QPushButton#copy_btn:pressed {
                background-color: #3e8e8a;
                border: 1px solid #45a29e;
            }
            QPushButton#icon_btn {
                background-color: transparent;
                color: #45a29e;
                font-size: 14px;
                padding: 5px;
                border: none;
            }
            QPushButton#icon_btn:hover {
                background-color: transparent;
                color: #66fcf1;
            }
            QPushButton#icon_btn:pressed {
                background-color: transparent;
                color: #3e8e8a;
            }
            QFrame#otp_frame { 
                background-color: #161921;
                border: 1px solid #1f2833; 
                border-radius: 5px; 
                padding: 5px; 
            }
            QLabel { 
                font-size: 14px; 
            }
            QLabel#title { 
                font-size: 28px; 
                font-weight: bold; 
                color: #66fcf1;
                letter-spacing: 7px;
            }
            QLabel#subtitle {
                font-size: 12px;
                color: #45a29e;
                letter-spacing: 1px;
            }
            QLabel#otp_display {
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 3px;
                color: #66fcf1;
                margin: 0px;
                background-color: #161921;
            }

            QProgressBar {
                border: none;
                background-color: #1f2833;
                border-radius: 3px;
                height: 8px;
                margin-top: 3px;
            }
            QProgressBar::chunk {
                background-color: #66fcf1;
                border-radius: 3px;
            }
        """

        self.setStyleSheet(style.replace("<FONT_FAMILY>", self.custom_font))

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)

        # --- TOP SECTION (Titles & Icons) ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # Left Side (Titles)
        titles_layout = QVBoxLayout()
        titles_layout.setSpacing(2)
        titles_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title_label = QLabel(
            "2FA-CYAN", objectName="title", alignment=Qt.AlignmentFlag.AlignLeft
        )
        titles_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(
            "AUTHENTICATOR GENERATOR",
            objectName="subtitle",
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        titles_layout.addWidget(self.subtitle_label)

        top_layout.addLayout(titles_layout)

        # Right Side (Icons)
        icons_layout = QHBoxLayout()
        icons_layout.setContentsMargins(0, 0, 30, 0)
        icons_layout.setSpacing(5)
        icons_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        self.github_btn = QPushButton("GITHUB", objectName="icon_btn")
        self.github_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.telegram_btn = QPushButton("TELEGRAM", objectName="icon_btn")
        self.telegram_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        import webbrowser

        self.github_btn.clicked.connect(
            lambda: webbrowser.open("https://github.com/limkhysok/")
        )
        self.telegram_btn.clicked.connect(
            lambda: webbrowser.open("https://t.me/soklimkhy")
        )

        icons_layout.addWidget(self.github_btn)
        icons_layout.addWidget(self.telegram_btn)

        top_layout.addLayout(icons_layout)
        top_layout.setStretchFactor(titles_layout, 1)
        top_layout.setStretchFactor(icons_layout, 0)

        layout.addLayout(top_layout)

        # --- CENTER SECTION (Input & Clear) ---
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.secret_input = QLineEdit(placeholderText="ENTER SECRET KEY")
        self.secret_input.setObjectName("enter_secret_key")
        self.secret_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.secret_input.textChanged.connect(self.on_secret_changed)
        input_layout.addWidget(self.secret_input)

        self.clear_button = QPushButton(
            "CLEAR", objectName="clear_btn", clicked=self.clear_secret
        )
        self.clear_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        input_layout.addWidget(self.clear_button)

        layout.addLayout(input_layout)

        # Add vertical spacing between input sec and otp sec
        layout.addSpacing(3)

        # OTP & Status Box Frame
        otp_frame = QFrame(objectName="otp_frame")
        otp_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        otp_frame.setContentsMargins(0, 0, 0, 0)

        otp_main_layout = QHBoxLayout()
        otp_main_layout.setSpacing(5)
        otp_main_layout.setContentsMargins(0, 0, 0, 0)

        # Left Part: OTP Display & Progress Bar
        otp_left_layout = QVBoxLayout()
        otp_left_layout.setSpacing(3)
        otp_left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.otp_display = QLabel(
            "------", objectName="otp_display", alignment=Qt.AlignmentFlag.AlignCenter
        )
        otp_left_layout.addWidget(self.otp_display)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 30)
        otp_left_layout.addWidget(self.progress_bar)

        otp_main_layout.addLayout(otp_left_layout)

        # Right Part: Copy Button
        self.copy_button = QPushButton(
            "_COPY__", objectName="copy_btn", clicked=self.copy_otp
        )
        self.copy_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        otp_main_layout.addWidget(self.copy_button)

        otp_main_layout.setStretchFactor(otp_left_layout, 1)
        otp_main_layout.setStretchFactor(self.copy_button, 0)

        otp_frame.setLayout(otp_main_layout)
        layout.addWidget(otp_frame)

        self.setLayout(layout)
        self.setWindowTitle("2FA-CYAN")

        # Timer for OTP updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_otp)
        self.timer.start(1000)

        self.current_secret = ""

    def on_secret_changed(self, text):
        self.current_secret = text.replace(" ", "").strip()
        self.update_otp()

    def update_otp(self):
        if hasattr(self, "copy_button") and self.copy_button.text() == "COPIED!":
            self.copy_button.setText("_COPY__")

        if not self.current_secret:
            self._reset_ui()
            return

        if len(self.current_secret) < 16:
            self._reset_ui()
            return

        try:
            # Check valid base32 characters
            totp = pyotp.TOTP(self.current_secret)
            otp = totp.now()

            # Format as 123 456
            formatted_otp = f"{otp[:3]} {otp[3:]}"
            self.otp_display.setText(formatted_otp)

            # Update progress bar
            time_remaining = 30 - (int(time.time()) % 30)
            self.progress_bar.setValue(time_remaining)

            # Color coding urgency
            if time_remaining <= 5:
                # Urgent state
                self.progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #ff4c4c; border-radius: 3px; }"
                )
                self.otp_display.setStyleSheet("color: #ff4c4c;")
            elif time_remaining <= 10:
                # Warning state
                self.progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #ffbd45; border-radius: 3px; }"
                )
                self.otp_display.setStyleSheet("color: #ffbd45;")
            else:
                # Normal state
                self.progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #66fcf1; border-radius: 3px; }"
                )
                self.otp_display.setStyleSheet("color: #66fcf1;")

        except Exception:
            self._reset_ui()

    def _reset_ui(self):
        self.otp_display.setText("------")
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            "QProgressBar::chunk { background-color: #1f2833; }"
        )
        self.otp_display.setStyleSheet("color: #66fcf1;")

    def copy_otp(self):
        otp_text = self.otp_display.text().replace(" ", "")
        if otp_text.isdigit():
            pyperclip.copy(otp_text)
            self.copy_button.setText("COPIED!")

    def clear_secret(self):
        self.secret_input.clear()
        self.current_secret = ""
        self.update_otp()


def main():
    app = QApplication(sys.argv)
    window = TFAApp()
    window.show()
    sys.exit(app.exec())
