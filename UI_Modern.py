import sys
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QFrame, 
                             QHBoxLayout, QVBoxLayout, QTabWidget, QFileDialog, 
                             QMessageBox, QComboBox, QLineEdit, QGroupBox, QSizePolicy)
from PyQt6.QtCore import QPropertyAnimation, QRect, QEasingCurve, Qt, QParallelAnimationGroup, QTimer
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PIL import Image
from Crypto.Hash import SHA256

import encrypt
import decrypt

# ---------------------------------------------------------
# DICTIONARY
# ---------------------------------------------------------
LANG = {
    'EN': {
        'enc_card': 'Encryption', 'dec_card': 'Decryption', 'lang': 'Language:',
        'tab_vig': 'Visual Stream (Vigenere)', 'tab_xor': 'Visual Stream (XOR)', 'tab_aes': 'Secure Mode (AES)',
        'file_box': 'File Selection', 'no_file': 'No file selected...', 'browse': 'Browse',
        'key_box': 'Cryptographic Key', 'btn_exec': 'Execute Operation', 'back': '←',
        'orig_prev': 'ORIGINAL IMAGE', 'live_prev': 'LIVE PREVIEW', 'aes_prev': '[ AES File Encryption - Visual Preview Not Available ]',
        'msg_sel': 'Please select a file first.', 'msg_key': 'Please enter a cryptographic key/password.',
        'succ': 'Operation completed!\nSaved to:\n{}', 'fail': 'Operation failed. Incorrect password or corrupted file.',
        'err': 'An unexpected error occurred:\n{}', 'succ_title': 'Success', 'err_title': 'Error'
    },
    'RO': {
        'enc_card': 'Criptare', 'dec_card': 'Decriptare', 'lang': 'Limba:',
        'tab_vig': 'Flux Vizual (Vigenere)', 'tab_xor': 'Flux Vizual (XOR)', 'tab_aes': 'Mod Securizat (AES)',
        'file_box': 'Selectie fisier', 'no_file': 'Niciun fisier selectat...', 'browse': 'Rasfoieste',
        'key_box': 'Cheie criptografica', 'btn_exec': 'Executa Operatiunea', 'back': '←',
        'orig_prev': 'IMAGINE ORIGINALA', 'live_prev': 'PREVIZUALIZARE LIVE', 'aes_prev': '[ Criptare Fisier AES - Previzualizare Indisponibila ]',
        'msg_sel': 'Te rog selecteaza un fisier mai intai.', 'msg_key': 'Te rog introdu o cheie criptografica/parola.',
        'succ': 'Operatiune finalizata!\nSalvat in:\n{}', 'fail': 'Operatiune esuata. Parola incorecta sau fisier corupt.',
        'err': 'A aparut o eroare neasteptata:\n{}', 'succ_title': 'Succes', 'err_title': 'Eroare'
    }
}

class ClickableFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked_callback = None
        self.is_expanded = False 

    def mousePressEvent(self, event):
        if self.clicked_callback and not self.is_expanded:
            self.clicked_callback()
        super().mousePressEvent(event)


class CryptoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSI App - Image Encryption/Decryption")
        self.setFixedSize(1600, 1000) 
        
        self.lang = 'EN'
        self.is_animating = False
        self.anim_group = None
        self.source_full_img = None
        self.source_display = None

        self.key_timer = QTimer()
        self.key_timer.setSingleShot(True)
        
        # Translation Trackers
        self.translatable_widgets = []
        self.translatable_tabs = []
        
        # State Trackers (to allow global clearing)
        self.all_file_labels = []
        self.all_key_inputs = []
        self.all_orig_labels = []
        self.all_live_labels = []
        
        self.apply_theme()
        self.build_ui()

    def get_text(self, key):
        return LANG[self.lang][key]

    def register_text(self, widget, key):
        self.translatable_widgets.append((widget, key))
        self.update_widget_text(widget, key)

    def update_widget_text(self, widget, key):
        if isinstance(widget, QLabel) or isinstance(widget, QPushButton):
            widget.setText(self.get_text(key))
        elif isinstance(widget, QGroupBox):
            widget.setTitle(self.get_text(key))

    def set_language(self, index):
        self.lang = 'EN' if index == 0 else 'RO'
        
        for widget, key in self.translatable_widgets:
            self.update_widget_text(widget, key)
            
        for tabs, idx, key in self.translatable_tabs:
            tabs.setTabText(idx, self.get_text(key))
            
        for lbl in self.all_file_labels:
            if lbl.text() in [LANG['EN']['no_file'], LANG['RO']['no_file']]:
                lbl.setText(self.get_text('no_file'))

    def apply_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #cccccc; font-family: 'Segoe UI'; }
            QTabWidget::pane { border: 1px solid #333; border-radius: 8px; background: #252526; }
            QTabBar::tab { background: #1e1e1e; padding: 12px 25px; border: 1px solid #333; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-weight: bold; }
            QTabBar::tab:selected { background: #0e639c; color: white; border-bottom-color: #0e639c; }
            QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 8px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; }
        """)

    def clear_all_inputs(self):
        """Wipes all data, previews, and text boxes globally."""
        self.key_timer.stop() # Cancel any pending 2-second preview timers
        self.source_full_img = None
        self.source_display = None
        
        for lbl in self.all_file_labels:
            lbl.setText(self.get_text('no_file'))
            
        for txt in self.all_key_inputs:
            # Block signals so clearing the text doesn't trigger the preview logic
            txt.blockSignals(True)
            txt.clear()
            txt.blockSignals(False)
            
        for lbl in self.all_orig_labels:
            lbl.clear()
            
        for lbl in self.all_live_labels:
            lbl.clear()

    def build_ui(self):
        # Language Selector
        self.lang_combo = QComboBox(self)
        self.lang_combo.addItems(['EN', 'RO'])
        self.lang_combo.setCurrentIndex(0)
        self.lang_combo.setGeometry(QRect(1480, 20, 100, 35))
        self.lang_combo.setStyleSheet("background-color: #333333; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
        self.lang_combo.currentIndexChanged.connect(self.set_language)

        # --- ENCRYPTION CARD ---
        self.enc_card = ClickableFrame(self)
        self.enc_card.setStyleSheet("background-color: #252526; border-radius: 16px; border: 1px solid #333333;")
        self.enc_card.setGeometry(QRect(400, 410, 350, 180)) 
        self.enc_card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.enc_card.clicked_callback = lambda: self.trigger_morph('encrypt')

        self.enc_back_btn = QPushButton(self.get_text('back'), self.enc_card)
        self.enc_back_btn.setGeometry(QRect(20, 15, 50, 50))
        self.enc_back_btn.setStyleSheet("background: transparent; border: none; color: #888888; font-size: 30px; font-weight: bold;")
        self.enc_back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.enc_back_btn.clicked.connect(lambda: self.reverse_morph('encrypt'))
        self.enc_back_btn.hide()

        self.enc_title = QLabel(self.enc_card)
        self.register_text(self.enc_title, 'enc_card')
        self.enc_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.enc_title.setGeometry(QRect(0, 0, 350, 180))
        self.enc_title.setStyleSheet("font-size: 24px; font-weight: bold; border: none; background: transparent;")

        self.enc_workspace = self.create_workspace(self.enc_card, 'encrypt')

        # --- DECRYPTION CARD ---
        self.dec_card = ClickableFrame(self)
        self.dec_card.setStyleSheet("background-color: #252526; border-radius: 16px; border: 1px solid #333333;")
        self.dec_card.setGeometry(QRect(850, 410, 350, 180)) 
        self.dec_card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.dec_card.clicked_callback = lambda: self.trigger_morph('decrypt')

        self.dec_back_btn = QPushButton(self.get_text('back'), self.dec_card)
        self.dec_back_btn.setGeometry(QRect(20, 15, 50, 50))
        self.dec_back_btn.setStyleSheet("background: transparent; border: none; color: #888888; font-size: 30px; font-weight: bold;")
        self.dec_back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.dec_back_btn.clicked.connect(lambda: self.reverse_morph('decrypt'))
        self.dec_back_btn.hide()

        self.dec_title = QLabel(self.dec_card)
        self.register_text(self.dec_title, 'dec_card')
        self.dec_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dec_title.setGeometry(QRect(0, 0, 350, 180))
        self.dec_title.setStyleSheet("font-size: 24px; font-weight: bold; border: none; background: transparent;")

        self.dec_workspace = self.create_workspace(self.dec_card, 'decrypt')

    def create_workspace(self, parent_card, action):
        workspace = QWidget(parent_card)
        workspace.setGeometry(QRect(30, 80, 1500, 850)) 
        workspace.setStyleSheet("background: transparent; border: none;")
        
        layout = QVBoxLayout(workspace)
        tabs = QTabWidget()
        
        # Wipe all data and previews when the user switches tabs
        tabs.currentChanged.connect(lambda idx: self.clear_all_inputs())
        
        # New Tab Order: Vigenere, XOR (Stream), AES (Secure)
        tabs.addTab(self.create_tab_content(action, 'vigenere'), "")
        tabs.addTab(self.create_tab_content(action, 'stream'), "")
        tabs.addTab(self.create_tab_content(action, 'secure'), "")
        
        self.translatable_tabs.extend([
            (tabs, 0, 'tab_vig'),
            (tabs, 1, 'tab_xor'),
            (tabs, 2, 'tab_aes')
        ])
        
        tabs.setTabText(0, self.get_text('tab_vig'))
        tabs.setTabText(1, self.get_text('tab_xor'))
        tabs.setTabText(2, self.get_text('tab_aes'))
        
        layout.addWidget(tabs)
        workspace.hide()
        return workspace

    def create_tab_content(self, action, mode):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # --- LEFT PANEL (CONTROLS) ---
        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        file_group = QGroupBox()
        self.register_text(file_group, 'file_box')
        file_vbox = QVBoxLayout()
        
        lbl_file = QLabel(self.get_text('no_file'))
        self.all_file_labels.append(lbl_file)
        lbl_file.setWordWrap(True)
        lbl_file.setFixedWidth(280)
        
        btn_browse = QPushButton()
        self.register_text(btn_browse, 'browse')
        btn_browse.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_browse.setStyleSheet("""
            QPushButton { background-color: #333333; border: 1px solid #555555; padding: 10px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #444444; border: 1px solid #777777; }
            QPushButton:pressed { background-color: #222222; }
        """)
        
        file_vbox.addWidget(lbl_file)
        file_vbox.addWidget(btn_browse)
        file_group.setLayout(file_vbox)

        key_group = QGroupBox()
        self.register_text(key_group, 'key_box')
        key_vbox = QVBoxLayout()
        
        txt_key = QLineEdit()
        self.all_key_inputs.append(txt_key)
        txt_key.setEchoMode(QLineEdit.EchoMode.Password if mode == 'secure' else QLineEdit.EchoMode.Normal)
        txt_key.setStyleSheet("""
            QLineEdit { background-color: #111111; border: 2px solid #444444; padding: 12px; border-radius: 6px; color: #ffffff; font-size: 14px; }
            QLineEdit:focus { border: 2px solid #0e639c; }
        """)
        key_vbox.addWidget(txt_key)
        key_group.setLayout(key_vbox)

        btn_exec = QPushButton()
        self.register_text(btn_exec, 'btn_exec')
        btn_exec.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_exec.setStyleSheet("""
            QPushButton { background-color: #0e639c; color: white; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 8px; border: 2px solid #094771; }
            QPushButton:hover { background-color: #1177bb; border: 2px solid #0e639c; }
            QPushButton:pressed { background-color: #083c5e; padding-top: 17px; padding-bottom: 13px; }
        """)

        controls_layout.addWidget(file_group)
        controls_layout.addWidget(key_group)
        controls_layout.addSpacing(30)
        controls_layout.addWidget(btn_exec)

        control_panel = QWidget()
        control_panel.setLayout(controls_layout)
        control_panel.setFixedWidth(320)
        
        # --- VERTICAL DELIMITER ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("border-left: 2px solid #333333; margin-left: 15px; margin-right: 15px;")
        
        # --- RIGHT PANEL (PREVIEWS) ---
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(20)
        
        # Top Image (Original)
        v_orig = QVBoxLayout()
        v_orig.setSpacing(5)
        lbl_orig_title = QLabel()
        self.register_text(lbl_orig_title, 'orig_prev')
        lbl_orig_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl_orig_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum) 
        lbl_orig_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0e639c; letter-spacing: 1px;")
        
        lbl_orig = QLabel()
        self.all_orig_labels.append(lbl_orig)
        lbl_orig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_orig.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lbl_orig.setStyleSheet("background-color: #111111; border: 2px dashed #444; border-radius: 8px;")
        v_orig.addWidget(lbl_orig_title)
        v_orig.addWidget(lbl_orig)

        # Bottom Image (Live)
        v_live = QVBoxLayout()
        v_live.setSpacing(5)
        lbl_live_title = QLabel()
        self.register_text(lbl_live_title, 'live_prev')
        lbl_live_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl_live_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        lbl_live_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0e639c; letter-spacing: 1px;")
        
        lbl_live = QLabel()
        self.all_live_labels.append(lbl_live)
        lbl_live.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_live.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lbl_live.setStyleSheet("background-color: #111111; border: 2px dashed #444; border-radius: 8px;")
        v_live.addWidget(lbl_live_title)
        v_live.addWidget(lbl_live)

        preview_layout.addLayout(v_orig)
        preview_layout.addLayout(v_live)

        # Assemble main layout
        layout.addWidget(control_panel)
        layout.addWidget(separator)
        layout.addLayout(preview_layout)

        # Wires
        btn_browse.clicked.connect(lambda: self.browse_file(lbl_file, lbl_orig, lbl_live, txt_key.text(), action, mode))
        txt_key.textChanged.connect(lambda text: self.schedule_preview(text, lbl_live, action, mode))
        btn_exec.clicked.connect(lambda: self.execute_logic(lbl_file.text(), txt_key.text(), action, mode))

        return tab

    # ---------------------------------------------------------
    # ANIMATIONS (MORPHING)
    # ---------------------------------------------------------
    def trigger_morph(self, action):
        if self.is_animating: return
        self.is_animating = True

        # Wipe state when entering a new workspace
        self.clear_all_inputs()

        target_card = self.enc_card if action == 'encrypt' else self.dec_card
        other_card = self.dec_card if action == 'encrypt' else self.enc_card
        target_title = self.enc_title if action == 'encrypt' else self.dec_title
        
        target_card.is_expanded = True
        target_card.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        other_card.hide()
        self.lang_combo.hide()

        self.anim_group = QParallelAnimationGroup()

        anim_card = QPropertyAnimation(target_card, b"geometry")
        anim_card.setDuration(600)
        anim_card.setStartValue(target_card.geometry())
        anim_card.setEndValue(QRect(20, 20, 1560, 960))
        anim_card.setEasingCurve(QEasingCurve.Type.InOutQuart)

        anim_title = QPropertyAnimation(target_title, b"geometry")
        anim_title.setDuration(600)
        anim_title.setStartValue(target_title.geometry())
        anim_title.setEndValue(QRect(80, 15, 300, 50)) 
        anim_title.setEasingCurve(QEasingCurve.Type.InOutQuart)

        self.anim_group.addAnimation(anim_card)
        self.anim_group.addAnimation(anim_title)

        def on_finish():
            workspace = self.enc_workspace if action == 'encrypt' else self.dec_workspace
            back_btn = self.enc_back_btn if action == 'encrypt' else self.dec_back_btn
            
            target_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            workspace.show()
            back_btn.show()
            self.is_animating = False

        self.anim_group.finished.connect(on_finish)
        self.anim_group.start()

    def reverse_morph(self, action):
        if self.is_animating: return
        self.is_animating = True

        # Wipe state when leaving a workspace to ensure no residues
        self.clear_all_inputs()

        target_card = self.enc_card if action == 'encrypt' else self.dec_card
        other_card = self.dec_card if action == 'encrypt' else self.enc_card
        target_title = self.enc_title if action == 'encrypt' else self.dec_title
        workspace = self.enc_workspace if action == 'encrypt' else self.dec_workspace
        back_btn = self.enc_back_btn if action == 'encrypt' else self.dec_back_btn

        target_card.is_expanded = False
        target_card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        workspace.hide()
        back_btn.hide()
        target_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.anim_group = QParallelAnimationGroup()

        orig_card_rect = QRect(400, 410, 350, 180) if action == 'encrypt' else QRect(850, 410, 350, 180)
        orig_title_rect = QRect(0, 0, 350, 180)

        anim_card = QPropertyAnimation(target_card, b"geometry")
        anim_card.setDuration(500)
        anim_card.setStartValue(target_card.geometry())
        anim_card.setEndValue(orig_card_rect)
        anim_card.setEasingCurve(QEasingCurve.Type.InOutQuart)

        anim_title = QPropertyAnimation(target_title, b"geometry")
        anim_title.setDuration(500)
        anim_title.setStartValue(target_title.geometry())
        anim_title.setEndValue(orig_title_rect)
        anim_title.setEasingCurve(QEasingCurve.Type.InOutQuart)

        self.anim_group.addAnimation(anim_card)
        self.anim_group.addAnimation(anim_title)

        def on_finish():
            other_card.show()
            self.lang_combo.show()
            self.is_animating = False

        self.anim_group.finished.connect(on_finish)
        self.anim_group.start()

    # ---------------------------------------------------------
    # LOGIC (FILE & PREVIEWS)
    # ---------------------------------------------------------
    def pil_to_pixmap(self, pil_image):
        im = pil_image.convert("RGBA")
        data = im.tobytes("raw", "RGBA")
        qim = QImage(data, im.width, im.height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qim)

    def browse_file(self, lbl_file, lbl_orig, lbl_live, current_key, action, mode):
        filter_str = "All Files (*.*)" if mode == 'secure' else "Images (*.png *.jpg *.jpeg);;All Files (*.*)"
        filepath, _ = QFileDialog.getOpenFileName(self, self.get_text('file_box'), "", filter_str)
        
        if filepath:
            lbl_file.setText(filepath)
            try:
                self.source_full_img = Image.open(filepath).convert('RGB')
                
                avail_w = lbl_orig.width() - 4
                avail_h = lbl_orig.height() - 4
                if avail_w < 100: avail_w = 1100
                if avail_h < 100: avail_h = 350
                
                img_orig = self.source_full_img.copy()
                img_orig.thumbnail((avail_w, avail_h), Image.Resampling.LANCZOS)
                lbl_orig.setPixmap(self.pil_to_pixmap(img_orig))

                self.source_display = img_orig.copy()
                self.run_preview_math(current_key, lbl_live, action, mode)
                
            except Exception as e:
                lbl_orig.setText("Preview Error")
                lbl_live.setText("Preview Error")

    def schedule_preview(self, text, lbl_live, action, mode):
        try: self.key_timer.timeout.disconnect() 
        except: pass
        self.key_timer.timeout.connect(lambda: self.run_preview_math(text, lbl_live, action, mode))
        # Wait exactly 2000 milliseconds (2 seconds) after the user stops typing
        self.key_timer.start(2000) 

    def run_preview_math(self, key_string, lbl_live, action, mode):
        if not self.source_full_img: return

        if mode == 'secure':
            lbl_live.clear()
            lbl_live.setText(self.get_text('aes_prev'))
            return

        if not key_string:
            lbl_live.setPixmap(self.pil_to_pixmap(self.source_display))
            return

        try:
            img_copy = self.source_full_img.copy()
            pixels = img_copy.load()
            width, height = img_copy.size
            key_bytes = key_string.encode('utf-8')
            key_length = len(key_bytes)
            
            if mode == 'stream':
                seed_bytes = SHA256.new(key_bytes).digest()
                seed_int = int.from_bytes(seed_bytes, 'big')
                random.seed(seed_int)

                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        rand_r = random.randint(0, 255)
                        rand_g = random.randint(0, 255)
                        rand_b = random.randint(0, 255)
                        pixels[x, y] = (r ^ rand_r, g ^ rand_g, b ^ rand_b)
            
            elif mode == 'vigenere':
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        shift = key_bytes[(x + y) % key_length]
                        if action == 'encrypt':
                            pixels[x, y] = ((r + shift) % 256, (g + shift) % 256, (b + shift) % 256)
                        else:
                            pixels[x, y] = ((r - shift) % 256, (g - shift) % 256, (b - shift) % 256)

            display_w, display_h = self.source_display.size
            img_copy.thumbnail((display_w, display_h), Image.Resampling.LANCZOS)
            lbl_live.setPixmap(self.pil_to_pixmap(img_copy))
            
        except Exception:
            pass 

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------
    def execute_logic(self, input_path, key, action, mode):
        if input_path in [LANG['EN']['no_file'], LANG['RO']['no_file']] or not input_path:
            QMessageBox.critical(self, self.get_text('err_title'), self.get_text('msg_sel'))
            return
        if not key:
            QMessageBox.critical(self, self.get_text('err_title'), self.get_text('msg_key'))
            return

        base, ext = input_path.rsplit('.', 1)
        if action == 'encrypt':
            output_path = f"{base}_encrypted.png" if mode in ['stream', 'vigenere'] else f"{base}_encrypted.bin"
        else:
            output_path = f"{base}_decrypted.{ext}" if mode in ['stream', 'vigenere'] else f"{base}_decrypted.jpg"

        try:
            success = False
            if action == 'encrypt':
                if mode == 'stream': success = encrypt.encrypt_visual_stream(input_path, output_path, key)
                elif mode == 'vigenere': success = encrypt.encrypt_visual_vulnerable(input_path, output_path, key)
                elif mode == 'secure': success = encrypt.encrypt_secure_aes(input_path, output_path, key)
            else:
                if mode == 'stream': success = decrypt.decrypt_visual_stream(input_path, output_path, key)
                elif mode == 'vigenere': success = decrypt.decrypt_visual_vulnerable(input_path, output_path, key)
                elif mode == 'secure': success = decrypt.decrypt_secure_aes(input_path, output_path, key)

            if success:
                msg = self.get_text('succ').format(output_path)
                QMessageBox.information(self, self.get_text('succ_title'), msg)
            else:
                QMessageBox.critical(self, self.get_text('err_title'), self.get_text('fail'))

        except Exception as e:
            msg = self.get_text('err').format(str(e))
            QMessageBox.critical(self, self.get_text('err_title'), msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CryptoApp()
    window.show()
    sys.exit(app.exec())