import customtkinter as ctk
import threading
import time
from aria_core import AriaCore
import sys
from PIL import Image  # For custom PNG icons

# --- Modern Clean UI Configuration ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Adaptive Colors (Light, Dark)
COLOR_BG = ("#f5f5f7", "#1e1e1e")           # Background
COLOR_CARD = ("#ffffff", "#2b2b2b")         # Cards/containers  
COLOR_INPUT_BG = ("#ffffff", "#1a1a1a")     # Input box background
COLOR_TEXT_PRIMARY = ("#1d1d1f", "#e4e4e7") # Primary text
COLOR_TEXT_SECONDARY = ("#6e6e73", "#a1a1aa") # Secondary text
COLOR_ACCENT = ("#007aff", "#3b82f6")       # Blue accent
COLOR_ACCENT_HOVER = ("#0051d5", "#2563eb") # Darker blue
COLOR_BORDER = ("#e5e5e7", "#404040")       # Borders

class ChatMessageCard(ctk.CTkFrame):
    """Message bubble - user RIGHT, AI LEFT."""
    def __init__(self, master, text, sender="Aria", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        is_user = sender == "You"
        
        # Container with reduced padding for narrow width
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=10, pady=3)
        
        if is_user:
            # USER MESSAGE - RIGHT SIDE, BLUE BUBBLE
            container.grid_columnconfigure(0, weight=1)
            container.grid_columnconfigure(1, weight=0)
            
            bubble = ctk.CTkFrame(
                container,
                fg_color=COLOR_ACCENT,
                corner_radius=16,
                border_width=0
            )
            bubble.grid(row=0, column=1, sticky="e")
            
            msg_label = ctk.CTkLabel(
                bubble,
                text=text,
                font=("Segoe UI", 13),
                text_color="white",
                justify="left",
                anchor="w",
                wraplength=180
            )
            msg_label.pack(padx=12, pady=8)
            
        else:
            # AI MESSAGE - LEFT SIDE, WHITE CARD WITH AVATAR
            container.grid_columnconfigure(0, weight=0)
            container.grid_columnconfigure(1, weight=1)
            
            avatar = ctk.CTkLabel(
                container,
                text="🤖",
                font=("Segoe UI", 16),
                width=28,
                height=28
            )
            avatar.grid(row=0, column=0, sticky="n", padx=(0, 6))
            
            card = ctk.CTkFrame(
                container,
                fg_color=COLOR_CARD,
                corner_radius=16,
                border_width=1,
                border_color=COLOR_BORDER
            )
            card.grid(row=0, column=1, sticky="w")
            
            msg_label = ctk.CTkLabel(
                card,
                text=text,
                font=("Segoe UI", 13),
                text_color=COLOR_TEXT_PRIMARY,
                justify="left",
                anchor="w",
                wraplength=180
            )
            msg_label.pack(padx=12, pady=8)

class AriaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Aria")
        
        # Position on LEFT side
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_width = 300
        window_height = screen_height - 80
        x_pos = 0
        y_pos = 0
        
        self.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.minsize(300, 600)
        self.configure(fg_color=COLOR_BG)
        
        # Initialize Core
        self.aria = AriaCore(on_speak=self.display_aria_message)
        self.voice_mode_var = ctk.BooleanVar(value=False)
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        
        self.create_ui()
        self.after(500, lambda: self.display_welcome())
    
    def create_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=58, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)
        
        logo = ctk.CTkLabel(self.header, text="✨", font=("Segoe UI", 20))
        logo.grid(row=0, column=0, padx=(12, 6), pady=12)
        
        title = ctk.CTkLabel(self.header, text="Chat", font=("Segoe UI Semibold", 17), text_color=COLOR_TEXT_PRIMARY)
        title.grid(row=0, column=1, sticky="w")
        
        # Right controls frame
        controls = ctk.CTkFrame(self.header, fg_color="transparent")
        controls.grid(row=0, column=2, padx=10)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            controls, text="⚙️", width=34, height=34, corner_radius=17,
            fg_color="transparent", hover_color=COLOR_BORDER, border_width=1,
            border_color=COLOR_BORDER, font=("Segoe UI", 14), command=self.show_settings_menu
        )
        self.settings_btn.pack(side="left", padx=3)
        
        # Theme button
        self.theme_btn = ctk.CTkButton(
            controls, text="🌙", width=34, height=34, corner_radius=17,
            fg_color="transparent", hover_color=COLOR_BORDER, border_width=1,
            border_color=COLOR_BORDER, font=("Segoe UI", 15), command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=3)
        
        # Settings menu (hidden by default)
        self.settings_menu = None
        
        # Chat area
        self.chat_scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLOR_BG, corner_radius=0,
            scrollbar_button_color=COLOR_BORDER,
            scrollbar_button_hover_color=COLOR_TEXT_SECONDARY
        )
        self.chat_scroll.grid(row=1, column=0, sticky="nsew")
        self.chat_scroll.grid_columnconfigure(0, weight=1)
        
        # Input area
        self.input_frame = ctk.CTkFrame(
            self, fg_color=COLOR_CARD, height=80, corner_radius=0,
            border_width=1, border_color=COLOR_BORDER
        )
        self.input_frame.grid(row=2, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_container = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.input_container.pack(fill="x", padx=12, pady=12)
        self.input_container.grid_columnconfigure(0, weight=1)
        
        self.input_row = ctk.CTkFrame(
            self.input_container, fg_color=COLOR_INPUT_BG, corner_radius=24,
            border_width=2, border_color=COLOR_BORDER, height=50
        )
        self.input_row.grid(row=0, column=0, sticky="ew")
        self.input_row.grid_columnconfigure(1, weight=1)
        self.input_row.grid_propagate(False)
        
        # Voice button in input area
        self.voice_btn = ctk.CTkButton(
            self.input_row, text="🎙️", width=36, height=36, corner_radius=18,
            fg_color="transparent", hover_color=COLOR_BG, border_width=1,
            border_color=COLOR_BORDER, font=("Segoe UI", 16),
            command=self.toggle_voice_mode
        )
        self.voice_btn.grid(row=0, column=0, padx=(6, 2), pady=(2, 0))
        
        self.input_box = ctk.CTkEntry(
            self.input_row, placeholder_text="Message...", fg_color="transparent",
            border_width=0, text_color=COLOR_TEXT_PRIMARY,
            placeholder_text_color=COLOR_TEXT_SECONDARY, font=("Segoe UI", 13)
        )
        self.input_box.grid(row=0, column=1, sticky="ew", padx=6)
        self.input_box.bind("<Return>", self.on_enter_pressed)
        
        # Send button - you can use PNG icons by uncommenting the image parameter
        # Example: image=ctk.CTkImage(Image.open("send_icon.png"), size=(20, 20))
        self.send_btn = ctk.CTkButton(
            self.input_row, 
            text="↑",  # Use "" if using image
            # image=None,  # Add your custom PNG here
            width=38, 
            height=38, 
            corner_radius=19,
            fg_color=COLOR_ACCENT, 
            hover_color=COLOR_ACCENT_HOVER,
            text_color="white", 
            font=("Segoe UI", 18, "bold"),
            command=self.send_command,
            anchor="center"  # Center the icon
        )
        self.send_btn.grid(row=0, column=2, padx=(2, 7),  pady=(5, 0),sticky="")
    
    def display_welcome(self):
        self.display_system_message("Hello! I'm Aria, your AI assistant. How can I help you today?")
    
    def add_message(self, text, sender):
        card = ChatMessageCard(self.chat_scroll, text=text, sender=sender)
        card.pack(fill="x", pady=3)
        self.update_idletasks()
        self.after(50, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))
    
    def display_aria_message(self, text):
        self.after(0, lambda: self.add_message(text, "Aria"))
    
    def display_user_message(self, text):
        self.add_message(text, "You")
    
    def display_system_message(self, text):
        self.after(0, lambda: self.add_message(text, "Aria"))
    
    def on_enter_pressed(self, event):
        self.send_command()
    
    def send_command(self):
        text = self.input_box.get().strip()
        if not text:
            return
        
        self.input_box.delete(0, "end")
        self.display_user_message(text)
        
        t = threading.Thread(target=self.process_command_thread, args=(text,))
        t.daemon = True
        t.start()
    
    def toggle_voice_mode(self):
        """Toggle voice mode with pulsing animation."""
        new_val = not self.voice_mode_var.get()
        self.voice_mode_var.set(new_val)
        
        if new_val:
            self.voice_btn.configure(fg_color=COLOR_ACCENT, border_color=COLOR_ACCENT, text_color="white")
            self.display_system_message("🎙️ Listening... Say 'Aria' to start")
            self.pulse_voice_button()
            
            t = threading.Thread(target=self.always_listen_loop)
            t.daemon = True
            t.start()
        else:
            self.voice_btn.configure(fg_color="transparent", border_color=COLOR_BORDER, text_color=COLOR_TEXT_PRIMARY)
            self.display_system_message("Voice Mode deactivated.")
    
    def pulse_voice_button(self):
        """Animate button with pulsing effect."""
        if not self.voice_mode_var.get():
            return
        
        current_color = self.voice_btn.cget("fg_color")
        
        if current_color == COLOR_ACCENT:
            self.voice_btn.configure(fg_color=COLOR_ACCENT_HOVER)
        else:
            self.voice_btn.configure(fg_color=COLOR_ACCENT)
        
        self.after(500, self.pulse_voice_button)
    
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Light":
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="☀️")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="🌙")
    
    def show_settings_menu(self):
        """Show settings menu."""
        if self.settings_menu is not None:
            self.settings_menu.destroy()
            self.settings_menu = None
            return
        
        # Create popup menu
        self.settings_menu = ctk.CTkToplevel(self)
        self.settings_menu.title("Settings")
        self.settings_menu.geometry("250x220+50+60")
        self.settings_menu.configure(fg_color=COLOR_CARD)
        self.settings_menu.attributes("-topmost", True)
        self.settings_menu.resizable(False, False)
        
        # Settings options
        ctk.CTkLabel(
            self.settings_menu,
            text="Settings",
            font=("Segoe UI Semibold", 16),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(pady=(15, 10))
        
        # Clear chat button
        ctk.CTkButton(
            self.settings_menu,
            text="🗑️ Clear Chat",
            width=200,
            height=36,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 13),
            command=self.clear_chat
        ).pack(pady=5)
        
        # Toggle Dark Mode
        ctk.CTkButton(
            self.settings_menu,
            text="🌓 Toggle Theme",
            width=200,
            height=36,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 13),
            command=lambda: [self.toggle_theme(), self.settings_menu.destroy(), setattr(self, 'settings_menu', None)]
        ).pack(pady=5)
        
        # About
        ctk.CTkButton(
            self.settings_menu,
            text="ℹ️ About Aria",
            width=200,
            height=36,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 13),
            command=self.show_about
        ).pack(pady=5)
        
        # Close button
        ctk.CTkButton(
            self.settings_menu,
            text="Close",
            width=200,
            height=32,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="white",
            font=("Segoe UI", 12),
            command=lambda: [self.settings_menu.destroy(), setattr(self, 'settings_menu', None)]
        ).pack(pady=(10, 15))
    
    def clear_chat(self):
        """Clear all chat messages."""
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self.display_system_message("Chat cleared.")
        if self.settings_menu:
            self.settings_menu.destroy()
            self.settings_menu = None
    
    def show_about(self):
        """Show about dialog."""
        self.display_system_message("Aria v1.0 - Your AI Assistant\nDeveloped with ❤️")
        if self.settings_menu:
            self.settings_menu.destroy()
            self.settings_menu = None
    
    def always_listen_loop(self):
        while self.voice_mode_var.get():
            text = self.aria.listen()
            if not text:
                time.sleep(1)
                continue
            
            if self.aria.wake_word in text.lower():
                self.after(0, lambda t=text: self.display_user_message(t))
                self.process_command_thread(text)
    
    def process_command_thread(self, text):
        self.aria.process_command(text)
    
    def on_closing(self):
        self.voice_mode_var.set(False)
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = AriaApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
