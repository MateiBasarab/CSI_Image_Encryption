import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from Crypto.Hash import SHA256
import random
import encrypt
import decrypt

LANG = {
    'EN': {
        'title': 'Image Cryptography Studio',
        'btn_enc_menu': 'Encrypt Image',
        'btn_dec_menu': 'Decrypt Image',
        'lang_lbl': 'Language:',
        'tab_stream': 'Visual Stream (XOR)',
        'tab_vuln': 'Visual Stream (Vigenere)',
        'tab_secure': 'Secure Mode (AES)',
        'file_box': 'File Selection',
        'no_file': 'No file selected',
        'browse': 'Browse',
        'key_box': 'Cryptographic Key',
        'btn_exec': 'Execute',
        'btn_back': 'Back to Menu',
        'orig_preview': 'Original Image',
        'live_preview': 'Live Preview',
        'aes_preview': '[ AES Binary Output - No Preview ]',
        'msg_sel_file': 'Please select a file first.',
        'msg_req_key': 'Please enter a cryptographic key/password.',
        'msg_success': 'Operation completed!\nSaved to: {}',
        'msg_fail': 'Operation failed. Incorrect password or corrupted file.',
        'msg_err': 'An unexpected error occurred:\n{}',
        'succ_title': 'Success',
        'err_title': 'Error'
    },
    'RO': {
        'title': 'Studio de Criptografie',
        'btn_enc_menu': 'Cripteaza Imaginea',
        'btn_dec_menu': 'Decripteaza Imaginea',
        'lang_lbl': 'Limba:',
        'tab_stream': 'Flux Vizual (XOR)',
        'tab_vuln': 'Flux Vizual (Vigenere)',
        'tab_secure': 'Mod Securizat (AES)',
        'file_box': 'Selectie fisier',
        'no_file': 'Niciun fisier selectat',
        'browse': 'Rasfoieste',
        'key_box': 'Cheie criptografica',
        'btn_exec': 'Executa',
        'btn_back': 'Inapoi la Meniu',
        'orig_preview': 'Imagine Originala',
        'live_preview': 'Previzualizare Live',
        'aes_preview': '[ Date Binare AES - Fara Previzualizare ]',
        'msg_sel_file': 'Te rog selecteaza un fisier mai intai.',
        'msg_req_key': 'Te rog introdu o cheie criptografica/parola.',
        'msg_success': 'Operatiune finalizata!\nSalvat in: {}',
        'msg_fail': 'Operatiune esuata. Parola incorecta sau fisier corupt.',
        'msg_err': 'A aparut o eroare neasteptata:\n{}',
        'succ_title': 'Succes',
        'err_title': 'Eroare'
    }
}

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.lang = 'EN'
        self.current_action = None
        
        self.source_full_img = None 
        self.source_display = None 
        
        self.resize_timer = None
        self.key_timer = None
        
        self.apply_dark_theme()
        self.build_main_menu()

    def apply_dark_theme(self):
        """Applies a universally readable Material Dark / VS Code style theme."""
        bg_color = "#1e1e1e"        # Main background
        surface_color = "#252526"   # Slightly lighter for panels
        text_color = "#cccccc"      # Off-white for readability
        accent_color = "#0e639c"    # Muted blue accent
        btn_bg = "#333333"          # Button resting state
        btn_hover = "#444444"       # Button hover state
        
        self.root.configure(bg=bg_color)
        
        style = ttk.Style()
        # 'clam' allows for better color overriding than the Windows/Mac default themes
        style.theme_use('clam') 
        
        # General Frame and Label styling
        style.configure('TFrame', background=bg_color)
        style.configure('Surface.TFrame', background=surface_color)
        style.configure('TLabel', background=bg_color, foreground=text_color, font=('Segoe UI', 10))
        
        # Label Frames (The borders around File Selection and Key)
        style.configure('TLabelframe', background=bg_color, foreground=text_color, bordercolor=btn_hover)
        style.configure('TLabelframe.Label', background=bg_color, foreground=text_color, font=('Segoe UI', 10, 'bold'))
        
        # Buttons
        style.configure('TButton', background=btn_bg, foreground=text_color, borderwidth=0, focuscolor=accent_color, font=('Segoe UI', 10, 'bold'))
        style.map('TButton', background=[('active', btn_hover), ('pressed', accent_color)])
        
        # Notebook (Tabs)
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=surface_color, foreground=text_color, padding=[10, 5], font=('Segoe UI', 10))
        style.map('TNotebook.Tab', background=[('selected', accent_color)], foreground=[('selected', '#ffffff')])
        
        # Entry (Text Input)
        style.configure('TEntry', fieldbackground=surface_color, foreground=text_color, bordercolor=btn_bg, insertcolor=text_color)
        
        # Dropdown Menu
        style.configure('TMenubutton', background=btn_bg, foreground=text_color)
        style.map('TMenubutton', background=[('active', btn_hover)])
        
        # Save colors for dynamic widgets (like the image placeholders)
        self.colors = {'bg': bg_color, 'surface': surface_color, 'text': text_color}

    def get_text(self, key):
        return LANG[self.lang][key]

    def set_lang(self, choice):
        self.lang = 'EN' if choice.startswith('EN') else 'RO'
        if self.current_action is None:
            self.build_main_menu()
        else:
            self.build_process_menu(self.current_action)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.source_full_img = None

    def build_main_menu(self):
        self.clear_window()
        self.current_action = None
        self.root.title(self.get_text('title'))
        self.root.geometry("600x400") 

        # Language Selector (Anchored to top-right of the whole window)
        lang_frame = ttk.Frame(self.root)
        lang_frame.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        ttk.Label(lang_frame, text=self.get_text('lang_lbl')).pack(side='left')
        lang_var = tk.StringVar(value=self.lang)
        ttk.OptionMenu(lang_frame, lang_var, self.lang, 'EN', 'RO', command=self.set_lang).pack(side='left', padx=5)

        # --- Top Half Frame ---
        # Takes up exactly 100% width and 50% height, starting from the top
        top_half = ttk.Frame(self.root)
        top_half.place(relx=0, rely=0, relwidth=1.0, relheight=0.5)

        # Inner container to perfectly center the group inside the top half
        center_group = ttk.Frame(top_half)
        center_group.place(relx=0.5, rely=0.5, anchor='center')

        # Title Label
        title_lbl = ttk.Label(center_group, text=self.get_text('title'), font=('Segoe UI', 16, 'bold'))
        title_lbl.pack(pady=(0, 20))

        # Action Buttons Container (Side-by-Side)
        btn_frame = ttk.Frame(center_group)
        btn_frame.pack(expand=True, fill='both')
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        ttk.Button(btn_frame, text=self.get_text('btn_enc_menu'), 
                   command=lambda: self.build_process_menu('encrypt')).grid(row=0, column=0, sticky='nsew', padx=10)
                   
        ttk.Button(btn_frame, text=self.get_text('btn_dec_menu'), 
                   command=lambda: self.build_process_menu('decrypt')).grid(row=0, column=1, sticky='nsew', padx=10)

        # --- Bottom Half Frame ---
        # Takes up exactly 100% width and 50% height, starting from the middle
        bottom_half = ttk.Frame(self.root)
        bottom_half.place(relx=0, rely=0.5, relwidth=1.0, relheight=0.5)
        
        # You can add a logo, credits, or future features to 'bottom_half' later
        # Example placeholder:
        # ttk.Label(bottom_half, text="Bottom Half Ready", foreground="#555555").place(relx=0.5, rely=0.5, anchor='center')

    def build_process_menu(self, action):
        self.clear_window()
        self.current_action = action
        self.root.geometry("1100x650")
        
        action_title = self.get_text('btn_enc_menu') if action == 'encrypt' else self.get_text('btn_dec_menu')
        self.root.title(f"{self.get_text('title')} - {action_title}")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(10, 5))

        tab_stream = ttk.Frame(self.notebook)
        self.notebook.add(tab_stream, text=self.get_text('tab_stream'))
        self.setup_action_tab(tab_stream, action, 'stream')

        tab_vuln = ttk.Frame(self.notebook)
        self.notebook.add(tab_vuln, text=self.get_text('tab_vuln'))
        self.setup_action_tab(tab_vuln, action, 'vulnerable')

        tab_secure = ttk.Frame(self.notebook)
        self.notebook.add(tab_secure, text=self.get_text('tab_secure'))
        self.setup_action_tab(tab_secure, action, 'secure')

        ttk.Button(self.root, text=self.get_text('btn_back'),
                   command=self.build_main_menu).pack(pady=10, ipady=3)

    def setup_action_tab(self, parent, action, mode):
        control_frame = ttk.Frame(parent, width=280)
        control_frame.pack(side='left', fill='y', padx=15, pady=15, expand=False)

        preview_frame = ttk.Frame(parent)
        preview_frame.pack(side='right', fill='both', expand=True, padx=15, pady=15)
        
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        file_frame = ttk.LabelFrame(control_frame, text=self.get_text('file_box'), padding=15)
        file_frame.pack(fill='x', pady=10)
        file_label = ttk.Label(file_frame, text=self.get_text('no_file'), wraplength=200, foreground="#aaaaaa")
        file_label.pack(side='top', fill='x', pady=(0, 10))
        
        btn_browse = ttk.Button(file_frame, text=self.get_text('browse'),
                                command=lambda: self.browse_file(file_label, mode, action, lbl_orig, lbl_prev, key_entry))
        btn_browse.pack(side='top', fill='x', ipady=3)

        key_frame = ttk.LabelFrame(control_frame, text=self.get_text('key_box'), padding=15)
        key_frame.pack(fill='x', pady=10)
        key_entry = ttk.Entry(key_frame, font=('Segoe UI', 12)) 
        key_entry.pack(fill='x')

        btn_exec = ttk.Button(control_frame, text=self.get_text('btn_exec'),
                              command=lambda: self.process_file(file_label, key_entry, action, mode))
        btn_exec.pack(pady=30, fill='x', ipady=5)

        ttk.Label(preview_frame, text=self.get_text('orig_preview'), font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, pady=(0, 5))
        lbl_orig = tk.Label(preview_frame, bg=self.colors['surface'], fg=self.colors['text']) # Using tk.Label for solid background color support
        lbl_orig.grid(row=1, column=0, sticky='nsew', padx=10)

        ttk.Label(preview_frame, text=self.get_text('live_preview'), font=('Segoe UI', 11, 'bold')).grid(row=0, column=1, pady=(0, 5))
        lbl_prev = tk.Label(preview_frame, bg=self.colors['surface'], fg=self.colors['text'])
        lbl_prev.grid(row=1, column=1, sticky='nsew', padx=10)

        preview_frame.bind('<Configure>', lambda e: self.on_frame_resize(e, lbl_orig, lbl_prev, key_entry, mode, action))
        key_entry.bind('<KeyRelease>', lambda e: self.on_key_release(key_entry.get(), mode, action, lbl_prev))

    def on_frame_resize(self, event, orig_label, prev_label, key_widget, mode, action):
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
        self.resize_timer = self.root.after(200, lambda: self.redraw_previews(event.width, event.height, orig_label, prev_label, key_widget, mode, action))

    def on_key_release(self, key_string, mode, action, prev_label):
        if self.key_timer:
            self.root.after_cancel(self.key_timer)
        self.key_timer = self.root.after(150, lambda: self.update_live_preview(key_string, mode, action, prev_label))

    def browse_file(self, label_widget, mode, action, orig_label, prev_label, key_widget):
        filetypes = (("All files", "*.*"),) if mode == 'secure' else (("Image files", "*.jpg *.png *.jpeg"), ("All files", "*.*"))
        filepath = filedialog.askopenfilename(title=self.get_text('file_box'), filetypes=filetypes)
        
        if filepath:
            label_widget.config(text=filepath, foreground=self.colors['text'])
            try:
                self.source_full_img = Image.open(filepath).convert('RGB')
                frame = orig_label.master
                frame.update_idletasks() 
                self.redraw_previews(frame.winfo_width(), frame.winfo_height(), orig_label, prev_label, key_widget, mode, action)
            except Exception as e:
                orig_label.config(image='', text="Preview Error")
                prev_label.config(image='', text="Preview Error")

    def redraw_previews(self, frame_w, frame_h, orig_label, prev_label, key_widget, mode, action):
        if not self.source_full_img: return

        avail_w = (frame_w // 2) - 20
        avail_h = frame_h - 40 
        
        if avail_w < 50 or avail_h < 50: return 

        img_orig = self.source_full_img.copy()
        img_orig.thumbnail((avail_w, avail_h), Image.Resampling.LANCZOS)
        
        self.tk_orig_img = ImageTk.PhotoImage(img_orig)
        orig_label.config(image=self.tk_orig_img)

        self.source_display = self.source_full_img.copy()
        self.source_display.thumbnail((avail_w, avail_h), Image.Resampling.LANCZOS)

        self.update_live_preview(key_widget.get(), mode, action, prev_label)

    def update_live_preview(self, key_string, mode, action, prev_label):
        if not self.source_full_img: return

        if mode == 'secure':
            prev_label.config(image='', text=self.get_text('aes_preview'))
            return

        if not key_string:
            self.tk_prev_img = ImageTk.PhotoImage(self.source_display)
            prev_label.config(image=self.tk_prev_img, text='')
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
            
            elif mode == 'vulnerable':
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

            self.tk_prev_img = ImageTk.PhotoImage(img_copy)
            prev_label.config(image=self.tk_prev_img, text='')
            
        except Exception as e:
            pass 

    def process_file(self, label_widget, key_widget, action, mode):
        input_path = label_widget.cget("text")
        key = key_widget.get()

        if input_path == self.get_text('no_file') or not input_path:
            messagebox.showerror(self.get_text('err_title'), self.get_text('msg_sel_file'))
            return
        if not key:
            messagebox.showerror(self.get_text('err_title'), self.get_text('msg_req_key'))
            return

        base, ext = input_path.rsplit('.', 1)
        if action == 'encrypt':
            output_path = f"{base}_encrypted.png" if mode in ['stream', 'vulnerable'] else f"{base}_encrypted.bin"
        else:
            output_path = f"{base}_decrypted.{ext}" if mode in ['stream', 'vulnerable'] else f"{base}_decrypted.jpg"

        try:
            success = False
            if action == 'encrypt':
                if mode == 'stream': success = encrypt.encrypt_visual_stream(input_path, output_path, key)
                elif mode == 'vulnerable': success = encrypt.encrypt_visual_vulnerable(input_path, output_path, key)
                elif mode == 'secure': success = encrypt.encrypt_secure_aes(input_path, output_path, key)
            else:
                if mode == 'stream': success = decrypt.decrypt_visual_stream(input_path, output_path, key)
                elif mode == 'vulnerable': success = decrypt.decrypt_visual_vulnerable(input_path, output_path, key)
                elif mode == 'secure': success = decrypt.decrypt_secure_aes(input_path, output_path, key)

            if success:
                msg = self.get_text('msg_success').format(output_path)
                messagebox.showinfo(self.get_text('succ_title'), msg)
            else:
                messagebox.showerror(self.get_text('err_title'), self.get_text('msg_fail'))

        except Exception as e:
            msg = self.get_text('msg_err').format(str(e))
            messagebox.showerror(self.get_text('err_title'), msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()