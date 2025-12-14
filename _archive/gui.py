import customtkinter as ctk
import threading
import time
from aria_core import AriaCore
import sys
from PIL import Image
import math

# --- Premium UI Setup ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Enhanced Color Palette - Modern & Vibrant
# Light mode colors
COLOR_BG_LIGHT = "#f8f9fa"
COLOR_CARD_LIGHT = "#ffffff"
COLOR_INPUT_BG_LIGHT = "#ffffff"
COLOR_TEXT_PRIMARY_LIGHT = "#1a1a2e"
COLOR_TEXT_SECONDARY_LIGHT = "#64748b"
COLOR_ACCENT_LIGHT = "#6366f1"  # Vibrant indigo
COLOR_ACCENT_HOVER_LIGHT = "#4f46e5"
COLOR_ACCENT_SECONDARY_LIGHT = "#8b5cf6"  # Purple accent
COLOR_BORDER_LIGHT = "#e2e8f0"
COLOR_SHADOW_LIGHT = "#0f172a"
COLOR_USER_BUBBLE_LIGHT = "#6366f1"
COLOR_AI_CARD_LIGHT = "#ffffff"

# Dark mode colors
COLOR_BG_DARK = "#0f172a"
COLOR_CARD_DARK = "#1e293b"
COLOR_INPUT_BG_DARK = "#1e293b"
COLOR_TEXT_PRIMARY_DARK = "#f1f5f9"
COLOR_TEXT_SECONDARY_DARK = "#94a3b8"
COLOR_ACCENT_DARK = "#818cf8"
COLOR_ACCENT_HOVER_DARK = "#6366f1"
COLOR_ACCENT_SECONDARY_DARK = "#a78bfa"
COLOR_BORDER_DARK = "#334155"
COLOR_SHADOW_DARK = "#000000"
COLOR_USER_BUBBLE_DARK = "#6366f1"
COLOR_AI_CARD_DARK = "#1e293b"

# Dynamic color tuples (light, dark)
COLOR_BG = (COLOR_BG_LIGHT, COLOR_BG_DARK)
COLOR_CARD = (COLOR_CARD_LIGHT, COLOR_CARD_DARK)
COLOR_INPUT_BG = (COLOR_INPUT_BG_LIGHT, COLOR_INPUT_BG_DARK)
COLOR_TEXT_PRIMARY = (COLOR_TEXT_PRIMARY_LIGHT, COLOR_TEXT_PRIMARY_DARK)
COLOR_TEXT_SECONDARY = (COLOR_TEXT_SECONDARY_LIGHT, COLOR_TEXT_SECONDARY_DARK)
COLOR_ACCENT = (COLOR_ACCENT_LIGHT, COLOR_ACCENT_DARK)
COLOR_ACCENT_HOVER = (COLOR_ACCENT_HOVER_LIGHT, COLOR_ACCENT_HOVER_DARK)
COLOR_ACCENT_SECONDARY = (COLOR_ACCENT_SECONDARY_LIGHT, COLOR_ACCENT_SECONDARY_DARK)
COLOR_BORDER = (COLOR_BORDER_LIGHT, COLOR_BORDER_DARK)
COLOR_USER_BUBBLE = (COLOR_USER_BUBBLE_LIGHT, COLOR_USER_BUBBLE_DARK)
COLOR_AI_CARD = (COLOR_AI_CARD_LIGHT, COLOR_AI_CARD_DARK)

class AnimatedButton(ctk.CTkButton):
    """Enhanced button with smooth hover animations"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_width = kwargs.get('width', 100)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
    
    def on_hover(self, event):
        """Subtle scale effect on hover"""
        self.configure(cursor="hand2")
    
    def on_leave(self, event):
        """Return to normal state"""
        self.configure(cursor="")

class ChatMessageCard(ctk.CTkFrame):
    """Premium chat message card with smooth animations and glassmorphism"""
    def __init__(self, master, text, sender="Aria", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        is_user = sender == "You"
        
        # Main container for the message row
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=12, pady=6)
        
        if is_user:
            # User messages: modern bubble on the right
            container.grid_columnconfigure(0, weight=1)
            container.grid_columnconfigure(1, weight=0)
            
            bubble = ctk.CTkFrame(
                container,
                fg_color=COLOR_USER_BUBBLE,
                corner_radius=18,
                border_width=0
            )
            bubble.grid(row=0, column=1, sticky="e")
            
            msg_label = ctk.CTkLabel(
                bubble,
                text=text,
                font=("Inter", 14),
                text_color="white",
                justify="left",
                anchor="w",
                wraplength=200
            )
            msg_label.pack(padx=16, pady=10)
            
            # Animate appearance
            self.animate_slide_in(bubble, from_right=True)
            
        else:
            # AI messages: elegant card on the left with avatar
            container.grid_columnconfigure(0, weight=0)
            container.grid_columnconfigure(1, weight=1)
            
            # Avatar with glow effect
            avatar_frame = ctk.CTkFrame(
                container,
                fg_color=COLOR_ACCENT,
                corner_radius=20,
                width=40,
                height=40
            )
            avatar_frame.grid(row=0, column=0, sticky="n", padx=(0, 10))
            avatar_frame.grid_propagate(False)
            
            avatar = ctk.CTkLabel(
                avatar_frame,
                text="✨",
                font=("Segoe UI", 18),
                text_color="white"
            )
            avatar.place(relx=0.5, rely=0.5, anchor="center")
            
            # Message card with glassmorphism
            card = ctk.CTkFrame(
                container,
                fg_color=COLOR_AI_CARD,
                corner_radius=18,
                border_width=1,
                border_color=COLOR_BORDER
            )
            card.grid(row=0, column=1, sticky="w")
            
            msg_label = ctk.CTkLabel(
                card,
                text=text,
                font=("Inter", 14),
                text_color=COLOR_TEXT_PRIMARY,
                justify="left",
                anchor="w",
                wraplength=200
            )
            msg_label.pack(padx=16, pady=10)
            
            # Animate appearance
            self.animate_slide_in(card, from_right=False)
    
    def animate_slide_in(self, widget, from_right=False):
        """Smooth slide-in animation for messages"""
        # Note: CustomTkinter has limitations, but we can simulate with opacity
        widget.lift()

class AriaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Aria - AI Assistant")
        
        # Position window on the left side
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_width = 360
        window_height = screen_height - 80
        x_pos = 20
        y_pos = 40
        
        self.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.minsize(340, 600)
        self.configure(fg_color=COLOR_BG)
        
        # Core logic
        self.aria = AriaCore(on_speak=self.display_aria_message)
        self.voice_mode_var = ctk.BooleanVar(value=False)
        self.pulse_animation_running = False
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        
        self.create_ui()
        self.after(500, lambda: self.display_welcome())
    
    def create_ui(self):
        """Create the premium UI with modern design elements"""
        
        # Header with glassmorphism effect
        self.header = ctk.CTkFrame(
            self, 
            fg_color=COLOR_CARD, 
            height=70, 
            corner_radius=0,
            border_width=1,
            border_color=COLOR_BORDER
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)
        self.header.grid_propagate(False)
        
        # Logo with gradient effect (simulated)
        logo_frame = ctk.CTkFrame(
            self.header,
            fg_color=COLOR_ACCENT,
            corner_radius=12,
            width=44,
            height=44
        )
        logo_frame.grid(row=0, column=0, padx=(16, 0), pady=13)
        logo_frame.grid_propagate(False)
        
        logo = ctk.CTkLabel(
            logo_frame,
            text="✨",
            font=("Segoe UI", 22)
        )
        logo.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title with better typography
        title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", padx=12)
        
        title = ctk.CTkLabel(
            title_frame,
            text="Aria",
            font=("Inter", 20, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="AI Assistant",
            font=("Inter", 11),
            text_color=COLOR_TEXT_SECONDARY
        )
        subtitle.pack(anchor="w")
        
        # Header controls
        controls = ctk.CTkFrame(self.header, fg_color="transparent")
        controls.grid(row=0, column=2, padx=12)
        
        # Settings button with modern style
        self.settings_btn = AnimatedButton(
            controls,
            text="⚙️",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            font=("Segoe UI", 16),
            command=self.show_settings_menu
        )
        self.settings_btn.pack(side="left", padx=4)
        
        # Theme toggle button
        self.theme_btn = AnimatedButton(
            controls,
            text="🌙",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            font=("Segoe UI", 16),
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=4)
        
        self.settings_menu = None
        
        # Chat area with smooth scrolling
        self.chat_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_BG,
            corner_radius=0,
            scrollbar_button_color=COLOR_BORDER,
            scrollbar_button_hover_color=COLOR_TEXT_SECONDARY
        )
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", pady=8)
        self.chat_scroll.grid_columnconfigure(0, weight=1)
        
        # Enhanced input section
        self.input_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            height=90,
            corner_radius=0,
            border_width=1,
            border_color=COLOR_BORDER
        )
        self.input_frame.grid(row=2, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)
        
        self.input_container = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.input_container.pack(fill="x", padx=16, pady=16)
        self.input_container.grid_columnconfigure(0, weight=1)
        
        # Input row with elevation
        self.input_row = ctk.CTkFrame(
            self.input_container,
            fg_color=COLOR_INPUT_BG,
            corner_radius=26,
            border_width=2,
            border_color=COLOR_BORDER,
            height=52
        )
        self.input_row.grid(row=0, column=0, sticky="ew")
        self.input_row.grid_columnconfigure(1, weight=1)
        self.input_row.grid_propagate(False)
        
        # Voice button with animation
        self.voice_btn = AnimatedButton(
            self.input_row,
            text="🎙️",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="transparent",
            hover_color=COLOR_BG,
            border_width=0,
            font=("Segoe UI", 18),
            command=self.toggle_voice_mode
        )
        self.voice_btn.grid(row=0, column=0, padx=(8, 4), pady=6)
        
        # Input field
        self.input_box = ctk.CTkEntry(
            self.input_row,
            placeholder_text="Type a message...",
            fg_color="transparent",
            border_width=0,
            text_color=COLOR_TEXT_PRIMARY,
            placeholder_text_color=COLOR_TEXT_SECONDARY,
            font=("Inter", 14)
        )
        self.input_box.grid(row=0, column=1, sticky="ew", padx=8)
        self.input_box.bind("<Return>", self.on_enter_pressed)
        self.input_box.bind("<FocusIn>", self.on_input_focus)
        self.input_box.bind("<FocusOut>", self.on_input_unfocus)
        
        # Send button with gradient effect
        self.send_btn = AnimatedButton(
            self.input_row,
            text="↑",
            width=40,
            height=40,
            corner_radius=20,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="white",
            font=("Inter", 20, "bold"),
            command=self.send_command,
            border_width=0
        )
        self.send_btn.grid(row=0, column=2, padx=(4, 8), pady=6)
    
    def on_input_focus(self, event):
        """Visual feedback when input is focused"""
        self.input_row.configure(border_color=COLOR_ACCENT)
    
    def on_input_unfocus(self, event):
        """Return to normal border when unfocused"""
        self.input_row.configure(border_color=COLOR_BORDER)
    
    def display_welcome(self):
        """Display welcome message with smooth animation"""
        welcome_text = "Hello! I'm Aria, your AI assistant. How can I help you today?"
        
        def speak_welcome():
            self.aria.speak(welcome_text)
        
        threading.Thread(target=speak_welcome, daemon=True).start()
    
    def add_message(self, text, sender):
        """Add message with smooth animation"""
        card = ChatMessageCard(self.chat_scroll, text=text, sender=sender)
        card.pack(fill="x", pady=4)
        self.update_idletasks()
        self.after(50, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))
    
    def display_aria_message(self, text):
        """Display Aria's response"""
        self.after(0, lambda: self.add_message(text, "Aria"))
    
    def display_user_message(self, text):
        """Display user message"""
        self.add_message(text, "You")
    
    def display_system_message(self, text):
        """Display system message"""
        self.after(0, lambda: self.add_message(text, "Aria"))
    
    def on_enter_pressed(self, event):
        """Handle Enter key press"""
        self.send_command()
    
    def send_command(self):
        """Send user command with visual feedback"""
        text = self.input_box.get().strip()
        if not text:
            return
        
        self.input_box.delete(0, "end")
        self.display_user_message(text)
        
        # Animate send button
        self.animate_send_button()
        
        t = threading.Thread(target=self.process_command_thread, args=(text,))
        t.daemon = True
        t.start()
    
    def animate_send_button(self):
        """Quick pulse animation for send button"""
        original_color = self.send_btn.cget("fg_color")
        self.send_btn.configure(fg_color=COLOR_ACCENT_SECONDARY)
        self.after(150, lambda: self.send_btn.configure(fg_color=original_color))
    
    def toggle_voice_mode(self):
        """Toggle voice mode with enhanced visual feedback"""
        new_val = not self.voice_mode_var.get()
        self.voice_mode_var.set(new_val)
        
        if new_val:
            # Activate voice mode
            self.voice_btn.configure(
                fg_color=COLOR_ACCENT,
                text_color="white"
            )
            self.display_system_message("🎙️ Voice mode active - Say 'Aria' to start")
            self.pulse_animation_running = True
            self.pulse_voice_button()
            
            t = threading.Thread(target=self.always_listen_loop)
            t.daemon = True
            t.start()
        else:
            # Deactivate voice mode
            self.voice_btn.configure(
                fg_color="transparent",
                text_color=COLOR_TEXT_PRIMARY
            )
            self.pulse_animation_running = False
            self.display_system_message("Voice mode deactivated")
    
    def pulse_voice_button(self):
        """Smooth breathing animation for voice button"""
        if not self.pulse_animation_running or not self.voice_mode_var.get():
            return
        
        current_color = self.voice_btn.cget("fg_color")
        
        # Alternate between accent colors
        if isinstance(current_color, tuple):
            current_color = current_color[0] if ctk.get_appearance_mode() == "Light" else current_color[1]
        
        if current_color in [COLOR_ACCENT_LIGHT, COLOR_ACCENT_DARK, COLOR_ACCENT]:
            self.voice_btn.configure(fg_color=COLOR_ACCENT_HOVER)
        else:
            self.voice_btn.configure(fg_color=COLOR_ACCENT)
        
        self.after(600, self.pulse_voice_button)
    
    def toggle_theme(self):
        """Smooth theme transition"""
        current = ctk.get_appearance_mode()
        if current == "Light":
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="☀️")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="🌙")
    
    def show_settings_menu(self):
        """Show modern settings popup"""
        if self.settings_menu is not None:
            self.settings_menu.destroy()
            self.settings_menu = None
            return
        
        # Create elegant popup
        self.settings_menu = ctk.CTkToplevel(self)
        self.settings_menu.title("Settings")
        self.settings_menu.geometry("280x260+60+80")
        self.settings_menu.configure(fg_color=COLOR_CARD)
        self.settings_menu.attributes("-topmost", True)
        self.settings_menu.resizable(False, False)
        
        # Add rounded corners effect
        self.settings_menu.overrideredirect(False)
        
        # Menu header
        header = ctk.CTkFrame(
            self.settings_menu,
            fg_color=COLOR_ACCENT,
            corner_radius=0,
            height=60
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="⚙️ Settings",
            font=("Inter", 18, "bold"),
            text_color="white"
        ).pack(pady=18)
        
        # Menu content
        content = ctk.CTkFrame(self.settings_menu, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Clear chat button
        ctk.CTkButton(
            content,
            text="🗑️  Clear Chat",
            width=240,
            height=40,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Inter", 13),
            anchor="w",
            command=self.clear_chat
        ).pack(pady=6)
        
        # Toggle theme button
        ctk.CTkButton(
            content,
            text="🌓  Toggle Theme",
            width=240,
            height=40,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Inter", 13),
            anchor="w",
            command=lambda: [self.toggle_theme(), self.settings_menu.destroy(), setattr(self, 'settings_menu', None)]
        ).pack(pady=6)
        
        # About button
        ctk.CTkButton(
            content,
            text="ℹ️  About Aria",
            width=240,
            height=40,
            fg_color="transparent",
            hover_color=COLOR_BORDER,
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Inter", 13),
            anchor="w",
            command=self.show_about
        ).pack(pady=6)
        
        # Close button
        ctk.CTkButton(
            content,
            text="Close",
            width=240,
            height=38,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="white",
            font=("Inter", 13, "bold"),
            command=lambda: [self.settings_menu.destroy(), setattr(self, 'settings_menu', None)]
        ).pack(pady=(10, 0))
    
    def clear_chat(self):
        """Clear chat history with confirmation"""
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self.display_system_message("✨ Chat cleared")
        if self.settings_menu:
            self.settings_menu.destroy()
            self.settings_menu = None
    
    def show_about(self):
        """Show about information"""
        self.display_system_message("✨ Aria v2.0\\nYour Premium AI Assistant\\n\\nDeveloped with  by Shreyas")
        if self.settings_menu:
            self.settings_menu.destroy()
            self.settings_menu = None
    
    def always_listen_loop(self):
        """Continuous listening loop for voice mode"""
        while self.voice_mode_var.get():
            text = self.aria.listen()
            if not text:
                time.sleep(1)
                continue
            
            if self.aria.wake_word in text.lower():
                self.after(0, lambda t=text: self.display_user_message(t))
                self.process_command_thread(text)
    
    def process_command_thread(self, text):
        """Process command in separate thread"""
        self.aria.process_command(text)
    
    def on_closing(self):
        """Clean exit"""
        self.voice_mode_var.set(False)
        self.pulse_animation_running = False
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = AriaApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
