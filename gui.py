import customtkinter as ctk
import threading
from aria_core import AriaCore
import sys

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Colors
COLOR_BG = "#343541"
COLOR_USER_MSG = "#343541" 
COLOR_ARIA_MSG = "#444654" 
COLOR_INPUT_BG = "#40414f"
COLOR_TEXT = "#ececf1"

class ChatMessageRow(ctk.CTkFrame):
    def __init__(self, master, text, sender="Aria", **kwargs):
        bg_color = COLOR_ARIA_MSG if sender == "Aria" else COLOR_USER_MSG
        super().__init__(master, fg_color=bg_color, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=8) 
        self.grid_columnconfigure(2, weight=1)

        # Avatar / Icon 
        avatar_text = "🤖" if sender == "Aria" else "👤"
        self.avatar = ctk.CTkLabel(self, text=avatar_text, font=("Arial", 20))
        self.avatar.grid(row=0, column=0, sticky="n", padx=(10, 5), pady=15)

        # Message Text
        self.msg_label = ctk.CTkLabel(
            self, 
            text=text, 
            text_color=COLOR_TEXT,
            font=("Roboto", 13),
            justify="left",
            wraplength=250, # Reduced for compact width
            anchor="w"
        )
        self.msg_label.grid(row=0, column=1, sticky="w", padx=5, pady=15)

class AriaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aria")
        self.geometry("350x650") # Compact Size
        self.configure(fg_color=COLOR_BG)

        # Initialize Core
        self.aria = AriaCore(on_speak=self.display_aria_message)

        # Layout: Single Column
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Main Chat Area ---
        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Scrollable Chat Container
        self.chat_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color=COLOR_BG, corner_radius=0)
        self.chat_scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        # Input Area (Bottom)
        self.input_container = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG, height=80, corner_radius=0)
        self.input_container.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.input_container.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkEntry(
            self.input_container, 
            placeholder_text="Message...", 
            fg_color=COLOR_INPUT_BG,
            border_width=0,
            text_color="white",
            height=40,
            corner_radius=20
        )
        self.input_box.grid(row=0, column=0, padx=(10, 5), pady=15, sticky="ew")
        self.input_box.bind("<Return>", self.on_enter_pressed)

        self.send_btn = ctk.CTkButton(
            self.input_container, 
            text="➢", # New Icon
            width=35, 
            height=35,
            fg_color=COLOR_INPUT_BG, 
            hover_color="#2b2c36",
            corner_radius=20,
            command=self.send_command
        )
        self.send_btn.grid(row=0, column=1, padx=(5, 5), pady=15)

        self.mic_btn = ctk.CTkButton(
            self.input_container, 
            text="🎙", 
            width=35, 
            height=35,
            fg_color=COLOR_INPUT_BG,
            hover_color="#2b2c36",
            corner_radius=20,
            command=self.start_listening_thread
        )
        self.mic_btn.grid(row=0, column=2, padx=(5, 10), pady=15)

        # Voice Mode Switch
        self.voice_mode_var = ctk.BooleanVar(value=False)
        self.voice_switch = ctk.CTkSwitch(
            self.main_frame, 
            text="Voice Mode", 
            variable=self.voice_mode_var, 
            command=self.toggle_voice_mode,
            progress_color="#1f6aa5",
            text_color="gray"
        )
        self.voice_switch.grid(row=2, column=0, pady=(0, 10))

        # Initial Message
        self.display_system_message("Hi! I'm Aria.")

    def add_message_row(self, text, sender):
        row = ChatMessageRow(self.chat_scroll, text=text, sender=sender)
        row.pack(fill="x", pady=0)
        
        # Auto-scroll
        self.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def display_aria_message(self, text):
        self.after(0, lambda: self.add_message_row(text, "Aria"))

    def display_user_message(self, text):
        self.add_message_row(text, "You")

    def display_system_message(self, text):
        self.after(0, lambda: self.add_message_row(text, "Aria"))

    def on_enter_pressed(self, event):
        self.send_command()

    def send_command(self):
        text = self.input_box.get()
        if not text:
            return
        self.input_box.delete(0, "end")
        self.display_user_message(text)
        
        t = threading.Thread(target=self.process_command_thread, args=(text,))
        t.daemon = True
        t.start()

    def start_listening_thread(self):
        self.mic_btn.configure(fg_color="#e74c3c") # Red color
        self.input_box.configure(placeholder_text="Listening...")
        t = threading.Thread(target=self.listen_thread)
        t.daemon = True
        t.start()

    def listen_thread(self):
        text = self.aria.listen()
        
        # Reset UI
        self.mic_btn.configure(fg_color=COLOR_INPUT_BG)
        self.input_box.configure(placeholder_text="Message...")
        
        if text:
            self.after(0, lambda: self.display_user_message(text))
            self.process_command_thread(text)
        else:
            pass 

    def toggle_voice_mode(self):
        if self.voice_mode_var.get():
            self.display_system_message("Voice Mode ON. Say 'Aria'...")
            self.mic_btn.configure(state="disabled", fg_color="gray") # Disable manual mic
            t = threading.Thread(target=self.always_listen_loop)
            t.daemon = True
            t.start()
        else:
            self.display_system_message("Voice Mode OFF.")
            self.mic_btn.configure(state="normal", fg_color=COLOR_INPUT_BG) # Enable manual mic

    def always_listen_loop(self):
        while self.voice_mode_var.get():
            # Listen without blocking UI (handled by thread)
            # We don't update UI to "Listening..." here to avoid flickering
            text = self.aria.listen()
            
            if not text:
                time.sleep(1) # Prevent tight loop on error
                continue
                
            # Check for Wake Word
            if self.aria.wake_word in text:
                self.after(0, lambda: self.display_user_message(text))
                self.process_command_thread(text)
            else:
                print(f"Ignored (No wake word): {text}")

    def process_command_thread(self, text):
        self.aria.process_command(text)

    def on_closing(self):
        self.voice_mode_var.set(False) # Stop loop
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = AriaApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
