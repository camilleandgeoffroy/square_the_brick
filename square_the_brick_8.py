import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import json
import os
import math

class MentalMathGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Square The Brick!")
        self.root.geometry("600x550")
        self.center_window(self.root, 600, 550)
        
        # Game settings
        self.settings = self.load_settings()
        
        # Game variables
        self.game_window = None
        self.canvas = None
        self.current_brick = None
        self.current_number = 0
        self.brick_y = 0
        self.brick_speed = 0
        self.base_speed = 0  # Store original speed for speed increase mode
        self.speed_increase_mode = False
        self.current_mode = None
        self.current_hardness = None
        self.lives = 0
        self.level = 0
        self.game_active = False
        self.game_paused = False
        self.start_time = 0
        self.total_time = 0
        self.correct_answers = 0
        self.answer_times = []
        self.failed_numbers = []
        
        self.create_start_screen()
        
    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
        
    def load_settings(self):
        default_settings = {"lives": 3, "speed_increase": False}
        try:
            if os.path.exists("game_settings.json"):
                with open("game_settings.json", "r") as f:
                    loaded = json.load(f)
                    # Ensure speed_increase exists in loaded settings
                    if "speed_increase" not in loaded:
                        loaded["speed_increase"] = False
                    return loaded
        except:
            pass
        return default_settings
    
    def load_leaderboard(self):
        default_leaderboard = {}
        # Create leaderboard for each combination of mode and hardness
        modes = ["Newbie", "Beginner", "Intermediate", "Expert"]
        hardness_levels = ["Easy", "Medium", "Hard", "Insane"]
        
        for mode in modes:
            for hardness in hardness_levels:
                key = f"{mode}_{hardness}"
                default_leaderboard[key] = []
        
        try:
            if os.path.exists("leaderboard.json"):
                with open("leaderboard.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return default_leaderboard
    
    def save_leaderboard(self, leaderboard):
        try:
            with open("leaderboard.json", "w") as f:
                json.dump(leaderboard, f)
        except:
            pass
        
    def save_settings(self):
        try:
            with open("game_settings.json", "w") as f:
                json.dump(self.settings, f)
        except:
            pass
            
    def create_start_screen(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Add background color
        self.root.configure(bg="#F5F5F5")
        
        title = tk.Label(self.root, text="Square The Brick!", font=("Arial", 24, "bold"), 
                         fg="#1a1a1a", bg="#F5F5F5")
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="Train your mental math skills!", 
                           font=("Arial", 12), fg="#333", bg="#F5F5F5")
        subtitle.pack(pady=(0, 20))
        
        # Selection frame
        selection_frame = tk.Frame(self.root, bg="#F5F5F5")
        selection_frame.pack(pady=10)
        
        # Mode selection
        mode_frame = tk.LabelFrame(selection_frame, text="Speed Mode", font=("Arial", 12, "bold"),
                                  bg="#F5F5F5", fg="#1a1a1a", padx=10, pady=10)
        mode_frame.pack(side="left", padx=20, pady=10)
        
        self.selected_mode = tk.StringVar(value="Beginner")
        modes = [
            ("Newbie (20s)", "Newbie", 20),
            ("Beginner (12s)", "Beginner", 12),
            ("Intermediate (8s)", "Intermediate", 8),
            ("Expert (4s)", "Expert", 4),
            ("Custom", "Custom", None)
        ]
        
        for display_name, mode_name, speed in modes:
            rb = tk.Radiobutton(mode_frame, text=display_name, variable=self.selected_mode,
                               value=mode_name, font=("Arial", 10), bg="#F5F5F5",
                               activebackground="#F5F5F5", selectcolor="#E0E0E0")
            rb.pack(anchor="w", pady=2)
            
        # Hardness selection
        hardness_frame = tk.LabelFrame(selection_frame, text="Hardness Level", font=("Arial", 12, "bold"),
                                      bg="#F5F5F5", fg="#1a1a1a", padx=10, pady=10)
        hardness_frame.pack(side="right", padx=20, pady=10)
        
        self.selected_hardness = tk.StringVar(value="Medium")
        hardness_levels = [
            ("Easy (1-100)", "Easy", 100),
            ("Medium (1-250)", "Medium", 250),
            ("Hard (1-500)", "Hard", 500),
            ("Insane (1-1000)", "Insane", 1000),
            ("Custom", "Custom", None)
        ]
        
        for display_name, hardness_name, max_num in hardness_levels:
            rb = tk.Radiobutton(hardness_frame, text=display_name, variable=self.selected_hardness,
                               value=hardness_name, font=("Arial", 10), bg="#F5F5F5",
                               activebackground="#F5F5F5", selectcolor="#E0E0E0")
            rb.pack(anchor="w", pady=2)
        
        # Start button - macOS compatible with Canvas-based styling
        start_canvas = tk.Canvas(self.root, width=220, height=60, bg="#F5F5F5", highlightthickness=0)
        start_canvas.pack(pady=20)
        
        # Create retro-style button with rounded corners and gradient
        start_rect = start_canvas.create_rectangle(10, 10, 210, 50, fill="#1e7e34", outline="#155724", width=3)
        start_canvas.create_rectangle(12, 12, 208, 25, fill="#28a745", outline="")  # Highlight
        start_text = start_canvas.create_text(110, 30, text="START GAME", font=("Arial", 14, "bold"), fill="white")
        
        def on_start_click(event):
            # Immediate button press effect
            start_canvas.delete("hover")  # Remove hover effect first
            start_canvas.create_rectangle(10, 10, 210, 50, fill="#155724", outline="#0d4f1a", width=3, tags="pressed")
            start_canvas.after(50, lambda: [start_canvas.delete("pressed"), self.start_game_with_selections()])
        
        def on_start_enter(event):
            start_canvas.create_rectangle(12, 12, 208, 48, fill="#34ce57", outline="", tags="hover")
        
        def on_start_leave(event):
            start_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        start_canvas.bind("<Button-1>", on_start_click)
        start_canvas.bind("<ButtonPress-1>", on_start_click)
        start_canvas.bind("<ButtonRelease-1>", on_start_click)
        start_canvas.bind("<Enter>", on_start_enter)
        start_canvas.bind("<Leave>", on_start_leave)
        start_canvas.config(cursor="hand2")
        start_canvas.focus_set()  # Make it focusable
        
        # Settings and Leaderboard buttons - macOS compatible
        buttons_frame = tk.Frame(self.root, bg="#F5F5F5")
        buttons_frame.pack(pady=15)
        
        # Manual button canvas (new)
        manual_canvas = tk.Canvas(buttons_frame, width=120, height=50, bg="#F5F5F5", highlightthickness=0)
        manual_canvas.pack(side="left", padx=8)
        
        manual_canvas.create_rectangle(5, 5, 115, 45, fill="#17a2b8", outline="#138496", width=2)
        manual_canvas.create_rectangle(7, 7, 113, 20, fill="#1fb6d3", outline="")  # Highlight
        manual_canvas.create_text(60, 25, text="Manual", font=("Arial", 10, "bold"), fill="white")
        
        def on_manual_click(event):
            manual_canvas.delete("hover")  # Remove hover effect first
            manual_canvas.create_rectangle(5, 5, 115, 45, fill="#138496", outline="#0f6674", width=2, tags="pressed")
            manual_canvas.after(50, lambda: [manual_canvas.delete("pressed"), self.show_manual()])
        
        def on_manual_enter(event):
            manual_canvas.create_rectangle(7, 7, 113, 43, fill="#20c4e0", outline="", tags="hover")
        
        def on_manual_leave(event):
            manual_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        manual_canvas.bind("<Button-1>", on_manual_click)
        manual_canvas.bind("<ButtonPress-1>", on_manual_click)
        manual_canvas.bind("<ButtonRelease-1>", on_manual_click)
        manual_canvas.bind("<Enter>", on_manual_enter)
        manual_canvas.bind("<Leave>", on_manual_leave)
        manual_canvas.config(cursor="hand2")
        manual_canvas.focus_set()
        
        # Settings button canvas
        settings_canvas = tk.Canvas(buttons_frame, width=120, height=50, bg="#F5F5F5", highlightthickness=0)
        settings_canvas.pack(side="left", padx=8)
        
        settings_canvas.create_rectangle(5, 5, 115, 45, fill="#495057", outline="#343a40", width=2)
        settings_canvas.create_rectangle(7, 7, 113, 20, fill="#6c757d", outline="")  # Highlight
        settings_canvas.create_text(60, 25, text="Settings", font=("Arial", 10, "bold"), fill="white")
        
        def on_settings_click(event):
            settings_canvas.delete("hover")  # Remove hover effect first
            settings_canvas.create_rectangle(5, 5, 115, 45, fill="#343a40", outline="#23272b", width=2, tags="pressed")
            settings_canvas.after(50, lambda: [settings_canvas.delete("pressed"), self.show_settings()])
        
        def on_settings_enter(event):
            settings_canvas.create_rectangle(7, 7, 113, 43, fill="#8a9096", outline="", tags="hover")
        
        def on_settings_leave(event):
            settings_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        settings_canvas.bind("<Button-1>", on_settings_click)
        settings_canvas.bind("<ButtonPress-1>", on_settings_click)
        settings_canvas.bind("<ButtonRelease-1>", on_settings_click)
        settings_canvas.bind("<Enter>", on_settings_enter)
        settings_canvas.bind("<Leave>", on_settings_leave)
        settings_canvas.config(cursor="hand2")
        settings_canvas.focus_set()
        
        # Leaderboard button canvas
        leaderboard_canvas = tk.Canvas(buttons_frame, width=120, height=50, bg="#F5F5F5", highlightthickness=0)
        leaderboard_canvas.pack(side="right", padx=8)
        
        leaderboard_canvas.create_rectangle(5, 5, 115, 45, fill="#721c24", outline="#501419", width=2)
        leaderboard_canvas.create_rectangle(7, 7, 113, 20, fill="#dc3545", outline="")  # Highlight
        leaderboard_canvas.create_text(60, 25, text="Leaderboard", font=("Arial", 10, "bold"), fill="white")
        
        def on_leaderboard_click(event):
            leaderboard_canvas.delete("hover")  # Remove hover effect first
            leaderboard_canvas.create_rectangle(5, 5, 115, 45, fill="#501419", outline="#331015", width=2, tags="pressed")
            leaderboard_canvas.after(50, lambda: [leaderboard_canvas.delete("pressed"), self.show_leaderboard()])
        
        def on_leaderboard_enter(event):
            leaderboard_canvas.create_rectangle(7, 7, 113, 43, fill="#e85d6d", outline="", tags="hover")
        
        def on_leaderboard_leave(event):
            leaderboard_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        leaderboard_canvas.bind("<Button-1>", on_leaderboard_click)
        leaderboard_canvas.bind("<ButtonPress-1>", on_leaderboard_click)
        leaderboard_canvas.bind("<ButtonRelease-1>", on_leaderboard_click)
        leaderboard_canvas.bind("<Enter>", on_leaderboard_enter)
        leaderboard_canvas.bind("<Leave>", on_leaderboard_leave)
        leaderboard_canvas.config(cursor="hand2")
        leaderboard_canvas.focus_set()
        
    def start_game_with_selections(self):
        mode = self.selected_mode.get()
        hardness = self.selected_hardness.get()
        
        # Handle custom inputs
        if mode == "Custom" or hardness == "Custom":
            self.show_custom_dialog(mode, hardness)
        else:
            # Get speed and max number from selections
            speed_map = {"Newbie": 20, "Beginner": 12, "Intermediate": 8, "Expert": 4}
            hardness_map = {"Easy": 100, "Medium": 250, "Hard": 500, "Insane": 1000}
            
            speed = speed_map[mode]
            max_number = hardness_map[hardness]
            
            self.start_game(speed, mode, max_number, hardness)
        
    def show_custom_dialog(self, mode, hardness):
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Settings")
        dialog.geometry("400x200")
        self.center_window(dialog, 400, 200)
        dialog.transient(self.root)
        dialog.grab_set()
        
        if mode == "Custom":
            tk.Label(dialog, text="Enter time in seconds (1-99):", font=("Arial", 12)).pack(pady=10)
            speed_entry = tk.Entry(dialog, font=("Arial", 14), width=10)
            speed_entry.pack(pady=5)
            speed_entry.focus()
        else:
            speed_map = {"Newbie": 20, "Beginner": 12, "Intermediate": 8, "Expert": 4}
            speed = speed_map[mode]
            speed_entry = None
            
        if hardness == "Custom":
            tk.Label(dialog, text="Enter max number (1-9999):", font=("Arial", 12)).pack(pady=10)
            hardness_entry = tk.Entry(dialog, font=("Arial", 14), width=10)
            hardness_entry.pack(pady=5)
            if mode != "Custom":
                hardness_entry.focus()
        else:
            hardness_map = {"Easy": 100, "Medium": 250, "Hard": 500, "Insane": 1000}
            max_number = hardness_map[hardness]
            hardness_entry = None
        
        def submit():
            try:
                final_speed = speed if mode != "Custom" else int(speed_entry.get())
                final_max_number = max_number if hardness != "Custom" else int(hardness_entry.get())
                
                if mode == "Custom" and not (1 <= final_speed <= 99):
                    messagebox.showerror("Error", "Speed must be between 1 and 99 seconds")
                    return
                if hardness == "Custom" and not (1 <= final_max_number <= 9999):
                    messagebox.showerror("Error", "Max number must be between 1 and 9999")
                    return
                    
                dialog.destroy()
                self.start_game(final_speed, mode, final_max_number, hardness)
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
                
        def on_enter(event):
            submit()
            
        if speed_entry:
            speed_entry.bind("<Return>", on_enter)
        if hardness_entry:
            hardness_entry.bind("<Return>", on_enter)
        
        # Fixed submit button - macOS compatible
        submit_canvas = tk.Canvas(dialog, width=120, height=40, bg=dialog.cget('bg'), highlightthickness=0)
        submit_canvas.pack(pady=20)
        
        submit_canvas.create_rectangle(5, 5, 115, 35, fill="#007bff", outline="#0056b3", width=2)
        submit_canvas.create_rectangle(7, 7, 113, 18, fill="#28a745", outline="")  # Highlight
        submit_canvas.create_text(60, 20, text="Start Game", font=("Arial", 10, "bold"), fill="white")
        
        def on_submit_click(event):
            submit_canvas.delete("hover")  # Remove hover effect first
            submit_canvas.create_rectangle(5, 5, 115, 35, fill="#0056b3", outline="#004085", width=2, tags="pressed")
            submit_canvas.after(50, lambda: [submit_canvas.delete("pressed"), submit()])
        
        def on_submit_enter(event):
            submit_canvas.create_rectangle(7, 7, 113, 33, fill="#45a049", outline="", tags="hover")
        
        def on_submit_leave(event):
            submit_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        submit_canvas.bind("<Button-1>", on_submit_click)
        submit_canvas.bind("<ButtonPress-1>", on_submit_click)
        submit_canvas.bind("<ButtonRelease-1>", on_submit_click)
        submit_canvas.bind("<Enter>", on_submit_enter)
        submit_canvas.bind("<Leave>", on_submit_leave)
        submit_canvas.config(cursor="hand2")
        submit_canvas.focus_set()
        
    def show_manual(self):
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Square The Brick! - Game Manual")
        manual_window.geometry("700x600")
        self.center_window(manual_window, 700, 600)
        manual_window.transient(self.root)
        manual_window.grab_set()
        manual_window.configure(bg="#F5F5DC")  # Beige book-like background
        
        # Create notebook-style manual with pages
        self.manual_notebook = ttk.Notebook(manual_window)
        self.manual_notebook.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Style the notebook to look book-like
        style = ttk.Style()
        style.configure('Manual.TNotebook', background="#8B4513")
        style.configure('Manual.TNotebook.Tab', 
                       padding=[20, 10], 
                       font=("Georgia", 10, "bold"))
        style.map('Manual.TNotebook.Tab',
                 background=[('selected', '#4A90E2'), ('!selected', '#2C3E50')],
                 foreground=[('selected', 'white'), ('!selected', 'white')])
        
        self.manual_notebook.configure(style='Manual.TNotebook')
        
        # Page 1: How to Play
        page1 = tk.Frame(self.manual_notebook, bg="#F5F5DC")
        self.manual_notebook.add(page1, text="📖 How to Play")
        
        self.create_manual_page(page1, "How to Play", [
            "Welcome to Square The Brick!",
            "",
            "🎯 OBJECTIVE:",
            "Calculate the square of numbers before the brick hits the ground!",
            "",
            "🎮 GAMEPLAY:",
            "• Numbers appear on falling bricks",
            "• Type the square of the number (e.g., 5² = 25)",
            "• Press ENTER to submit your answer",
            "• Get it right: brick explodes and you advance!",
            "• Get it wrong or too slow: lose a life ❤️",
            "",
            "⚡ SPEED MODES:",
            "• Newbie: 20 seconds per brick",
            "• Beginner: 12 seconds per brick", 
            "• Intermediate: 8 seconds per brick",
            "• Expert: 4 seconds per brick",
            "• Custom: Set your own time!"
        ])
        
        # Page 2: Controls & Features
        page2 = tk.Frame(self.manual_notebook, bg="#F5F5DC")
        self.manual_notebook.add(page2, text="🎮 Controls")
        
        self.create_manual_page(page2, "Controls & Features", [
            "🕹️ GAME CONTROLS:",
            "",
            "SPACEBAR - Pause/Resume game",
            "ENTER - Submit answer",
            "ESC - Close game window",
            "",
            "📊 DIFFICULTY LEVELS:",
            "• Easy: Numbers 1-100",
            "• Medium: Numbers 1-250", 
            "• Hard: Numbers 1-500",
            "• Insane: Numbers 1-1000",
            "• Custom: Set your own range!",
            "",
            "🚀 SPEED INCREASE MODE:",
            "Enable in Settings for extra challenge!",
            "Speed increases by 10% every 10 levels",
            "",
            "📈 TRACKING:",
            "• Failed numbers are shown on the left",
            "• Your level progress is displayed",
            "• Average response time is calculated"
        ])
        
        # Page 3: Scoring & Tips
        page3 = tk.Frame(self.manual_notebook, bg="#F5F5DC")
        self.manual_notebook.add(page3, text="🏆 Scoring")
        
        self.create_manual_page(page3, "Scoring & Strategy", [
            "🏆 SCORING SYSTEM:",
            "",
            "• Each correct answer = +1 Level",
            "• Reach higher levels to climb the leaderboard",
            "• Only default settings (3 lives) count for leaderboard",
            "",
            "💡 PRO TIPS:",
            "",
            "• Practice perfect squares: 1, 4, 9, 16, 25, 36...",
            "• For larger numbers, use patterns:",
            "  - 25² = 625 (ends in 25)",
            "  - Numbers ending in 5: n5² always ends in 25",
            "• Stay calm under pressure",
            "• Use the pause feature (SPACEBAR) if needed",
            "",
            "🧠 MENTAL MATH TRICKS:",
            "• 11² = 121, 12² = 144, 13² = 169...",
            "• (a+b)² = a² + 2ab + b²",
            "• Practice makes perfect!"
        ])
        
        # Page 4: Settings & Customization
        page4 = tk.Frame(self.manual_notebook, bg="#F5F5DC")
        self.manual_notebook.add(page4, text="⚙️ Settings")
        
        self.create_manual_page(page4, "Settings & Customization", [
            "⚙️ GAME SETTINGS:",
            "",
            "🔧 BASIC SETTINGS:",
            "• Lives: Set 1-10 lives (default: 3)",
            "• Speed Increase: Enable progressive difficulty",
            "",
            "🎨 CUSTOM MODES:",
            "• Custom Speed: 1-99 seconds per brick",
            "• Custom Range: Numbers 1-9999",
            "",
            "💾 DATA STORAGE:",
            "• Settings saved automatically",
            "• Leaderboard tracks top 5 scores per mode",
            "• Failed numbers help you practice",
            "",
            "🏅 LEADERBOARD:",
            "• Separate rankings for each difficulty combo",
            "• Only non-custom modes with 3 lives qualify",
            "• Compete with yourself or friends!",
            "",
            "Good luck and have fun squaring those bricks! 🧱²"
        ])
        
        # Close button at bottom
        close_canvas = tk.Canvas(manual_window, width=120, height=45, bg="#F5F5DC", highlightthickness=0)
        close_canvas.pack(pady=10)
        
        # Improved button with better contrast and visibility
        close_canvas.create_rectangle(5, 5, 115, 40, fill="#2C3E50", outline="#1B252F", width=2)
        close_canvas.create_rectangle(7, 7, 113, 20, fill="#34495E", outline="")  # Highlight
        close_canvas.create_rectangle(7, 25, 113, 38, fill="#1A252F", outline="")  # Shadow
        close_canvas.create_text(60, 22, text="Close Manual", font=("Georgia", 10, "bold"), fill="white")
        
        def on_manual_close_click(event):
            # Immediate response and better visual feedback
            close_canvas.delete("all")
            close_canvas.create_rectangle(5, 5, 115, 40, fill="#1B252F", outline="#0D1117", width=2)
            close_canvas.create_text(60, 22, text="Close Manual", font=("Georgia", 10, "bold"), fill="#CCCCCC")
            close_canvas.after(50, manual_window.destroy)  # Shorter delay for immediate response
        
        def on_manual_close_enter(event):
            close_canvas.create_rectangle(7, 7, 113, 38, fill="#4A90E2", outline="", tags="hover")
        
        def on_manual_close_leave(event):
            close_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        close_canvas.bind("<Button-1>", on_manual_close_click)
        close_canvas.bind("<ButtonPress-1>", on_manual_close_click)
        close_canvas.bind("<ButtonRelease-1>", on_manual_close_click)
        close_canvas.bind("<Enter>", on_manual_close_enter)
        close_canvas.bind("<Leave>", on_manual_close_leave)
        close_canvas.config(cursor="hand2")
        # Make canvas focusable to improve responsiveness
        close_canvas.focus_set()
    
    def create_manual_page(self, parent, title, content_lines):
        # Create scrollable text area
        canvas = tk.Canvas(parent, bg="#F5F5DC", highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F5F5DC")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title with book-like styling
        title_label = tk.Label(scrollable_frame, text=title, 
                              font=("Georgia", 18, "bold"), 
                              fg="#8B4513", bg="#F5F5DC")
        title_label.pack(pady=(20, 10))
        
        # Add decorative line
        line_canvas = tk.Canvas(scrollable_frame, width=400, height=3, bg="#F5F5DC", highlightthickness=0)
        line_canvas.pack()
        line_canvas.create_line(0, 1, 400, 1, fill="#8B4513", width=2)
        
        # Content with book-like formatting
        for line in content_lines:
            if line.startswith("🎯") or line.startswith("🎮") or line.startswith("⚡") or line.startswith("🕹️") or \
               line.startswith("📊") or line.startswith("🚀") or line.startswith("📈") or line.startswith("🏆") or \
               line.startswith("💡") or line.startswith("🧠") or line.startswith("⚙️") or line.startswith("🔧") or \
               line.startswith("🎨") or line.startswith("💾") or line.startswith("🏅"):
                # Section headers
                label = tk.Label(scrollable_frame, text=line, 
                               font=("Georgia", 12, "bold"), 
                               fg="#8B4513", bg="#F5F5DC", anchor="w")
            elif line.startswith("•"):
                # Bullet points
                label = tk.Label(scrollable_frame, text=line, 
                               font=("Georgia", 10), 
                               fg="#654321", bg="#F5F5DC", anchor="w")
            elif line == "":
                # Empty lines for spacing
                label = tk.Label(scrollable_frame, text=" ", bg="#F5F5DC")
            else:
                # Regular text
                label = tk.Label(scrollable_frame, text=line, 
                               font=("Georgia", 11), 
                               fg="#2F1B14", bg="#F5F5DC", anchor="w")
            
            label.pack(fill="x", padx=30, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Game Settings")
        settings_window.geometry("400x300")
        self.center_window(settings_window, 400, 300)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Number of lives
        tk.Label(settings_window, text="Number of lives (1-10):", font=("Arial", 12)).pack(pady=15)
        lives_entry = tk.Entry(settings_window, font=("Arial", 12), width=10)
        lives_entry.pack(pady=5)
        lives_entry.insert(0, str(self.settings["lives"]))
        
        # Speed increase mode
        tk.Label(settings_window, text="Speed Increase Mode:", font=("Arial", 12)).pack(pady=(20, 5))
        tk.Label(settings_window, text="(Speed increases 10% every 10 levels)", 
                font=("Arial", 9), fg="gray").pack()
        
        speed_increase_var = tk.BooleanVar(value=self.settings.get("speed_increase", False))
        speed_check = tk.Checkbutton(settings_window, text="Enable Speed Increase", 
                                   variable=speed_increase_var, font=("Arial", 11))
        speed_check.pack(pady=10)
        
        def save_and_close():
            try:
                lives = int(lives_entry.get())
                
                if not (1 <= lives <= 10):
                    messagebox.showerror("Error", "Lives must be between 1 and 10")
                    return
                    
                self.settings["lives"] = lives
                self.settings["speed_increase"] = speed_increase_var.get()
                self.save_settings()
                settings_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        def reset_defaults():
            lives_entry.delete(0, tk.END)
            lives_entry.insert(0, "3")
            speed_increase_var.set(False)
        
        buttons_frame = tk.Frame(settings_window)
        buttons_frame.pack(pady=30)
        
        # Fixed buttons - macOS compatible
        save_canvas = tk.Canvas(buttons_frame, width=110, height=35, bg=settings_window.cget('bg'), highlightthickness=0)
        save_canvas.pack(side="left", padx=10)
        
        save_canvas.create_rectangle(3, 3, 107, 32, fill="#28a745", outline="#1e7e34", width=2)
        save_canvas.create_rectangle(5, 5, 105, 16, fill="#34ce57", outline="")  # Highlight
        save_canvas.create_text(55, 17, text="Save & Close", font=("Arial", 9, "bold"), fill="white")
        
        def on_save_click(event):
            save_canvas.delete("hover")  # Remove hover effect first
            save_canvas.create_rectangle(3, 3, 107, 32, fill="#1e7e34", outline="#155724", width=2, tags="pressed")
            save_canvas.after(50, lambda: [save_canvas.delete("pressed"), save_and_close()])
        
        def on_save_enter(event):
            save_canvas.create_rectangle(5, 5, 105, 30, fill="#45a049", outline="", tags="hover")
        
        def on_save_leave(event):
            save_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        save_canvas.bind("<Button-1>", on_save_click)
        save_canvas.bind("<ButtonPress-1>", on_save_click)
        save_canvas.bind("<ButtonRelease-1>", on_save_click)
        save_canvas.bind("<Enter>", on_save_enter)
        save_canvas.bind("<Leave>", on_save_leave)
        save_canvas.config(cursor="hand2")
        save_canvas.focus_set()
        
        reset_canvas = tk.Canvas(buttons_frame, width=110, height=35, bg=settings_window.cget('bg'), highlightthickness=0)
        reset_canvas.pack(side="right", padx=10)
        
        reset_canvas.create_rectangle(3, 3, 107, 32, fill="#6c757d", outline="#495057", width=2)
        reset_canvas.create_rectangle(5, 5, 105, 16, fill="#868e96", outline="")  # Highlight
        reset_canvas.create_text(55, 17, text="Reset Defaults", font=("Arial", 9, "bold"), fill="white")
        
        def on_reset_click(event):
            reset_canvas.delete("hover")  # Remove hover effect first
            reset_canvas.create_rectangle(3, 3, 107, 32, fill="#495057", outline="#343a40", width=2, tags="pressed")
            reset_canvas.after(50, lambda: [reset_canvas.delete("pressed"), reset_defaults()])
        
        def on_reset_enter(event):
            reset_canvas.create_rectangle(5, 5, 105, 30, fill="#95a5a6", outline="", tags="hover")
        
        def on_reset_leave(event):
            reset_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        reset_canvas.bind("<Button-1>", on_reset_click)
        reset_canvas.bind("<ButtonPress-1>", on_reset_click)
        reset_canvas.bind("<ButtonRelease-1>", on_reset_click)
        reset_canvas.bind("<Enter>", on_reset_enter)
        reset_canvas.bind("<Leave>", on_reset_leave)
        reset_canvas.config(cursor="hand2")
        reset_canvas.focus_set()
        
    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Leaderboard")
        leaderboard_window.geometry("600x500")
        self.center_window(leaderboard_window, 600, 500)
        leaderboard_window.transient(self.root)
        leaderboard_window.grab_set()
        
        leaderboard = self.load_leaderboard()
        
        tk.Label(leaderboard_window, text="LEADERBOARD", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(leaderboard_window, text="(Default lives setting only: 3 lives)", 
                font=("Arial", 10), fg="gray").pack()
        
        # Create notebook for tabs with custom style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', padding=[15, 8])
        style.map('TNotebook.Tab', 
                 background=[('selected', '#2E86AB'), ('!selected', '#E5E5E5')],
                 foreground=[('selected', 'white'), ('!selected', 'black')])
        
        notebook = ttk.Notebook(leaderboard_window)
        notebook.pack(expand=True, fill="both", padx=20, pady=20)
        
        modes = ["Newbie", "Beginner", "Intermediate", "Expert"]
        hardness_levels = ["Easy", "Medium", "Hard", "Insane"]
        
        for mode in modes:
            mode_frame = ttk.Frame(notebook)
            notebook.add(mode_frame, text=mode)
            
            # Create sub-tabs for hardness levels
            sub_notebook = ttk.Notebook(mode_frame)
            sub_notebook.pack(expand=True, fill="both", padx=10, pady=10)
            
            for hardness in hardness_levels:
                hardness_frame = ttk.Frame(sub_notebook)
                sub_notebook.add(hardness_frame, text=hardness)
                
                key = f"{mode}_{hardness}"
                scores = leaderboard.get(key, [])
                scores.sort(reverse=True)  # Sort by score (level) descending
                
                if scores:
                    for i, score in enumerate(scores[:5]):  # Top 5
                        rank_text = f"{i+1}. Level {score}"
                        tk.Label(hardness_frame, text=rank_text, font=("Arial", 14)).pack(pady=5)
                else:
                    tk.Label(hardness_frame, text="No scores yet!", font=("Arial", 14), fg="gray").pack(pady=20)
        
        # Fixed close button - macOS compatible
        close_canvas = tk.Canvas(leaderboard_window, width=80, height=35, bg=leaderboard_window.cget('bg'), highlightthickness=0)
        close_canvas.pack(pady=10)
        
        close_canvas.create_rectangle(3, 3, 77, 32, fill="#dc3545", outline="#c82333", width=2)
        close_canvas.create_rectangle(5, 5, 75, 16, fill="#e85d6d", outline="")  # Highlight
        close_canvas.create_text(40, 17, text="Close", font=("Arial", 10, "bold"), fill="white")
        
        def on_close_click(event):
            close_canvas.delete("hover")  # Remove hover effect first
            close_canvas.create_rectangle(3, 3, 77, 32, fill="#c82333", outline="#bd2130", width=2, tags="pressed")
            close_canvas.after(50, lambda: [close_canvas.delete("pressed"), leaderboard_window.destroy()])
        
        def on_close_enter(event):
            close_canvas.create_rectangle(5, 5, 75, 30, fill="#f5626a", outline="", tags="hover")
        
        def on_close_leave(event):
            close_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        close_canvas.bind("<Button-1>", on_close_click)
        close_canvas.bind("<ButtonPress-1>", on_close_click)
        close_canvas.bind("<ButtonRelease-1>", on_close_click)
        close_canvas.bind("<Enter>", on_close_enter)
        close_canvas.bind("<Leave>", on_close_leave)
        close_canvas.config(cursor="hand2")
        close_canvas.focus_set()
        
    def start_game(self, speed, mode, max_number, hardness):
        self.brick_speed = speed
        self.base_speed = speed  # Store original speed
        self.speed_increase_mode = self.settings.get("speed_increase", False)
        self.current_mode = mode
        self.current_hardness = hardness
        self.max_number = max_number
        self.lives = self.settings["lives"]
        self.level = 0
        self.correct_answers = 0
        self.total_time = 0
        self.answer_times = []
        self.failed_numbers = []
        self.game_active = True
        self.game_paused = False
        
        # Create game window
        if self.game_window:
            self.game_window.destroy()
            
        self.game_window = tk.Toplevel(self.root)
        self.game_window.title("Square The Brick!")
        self.game_window.geometry("750x800")
        self.center_window(self.game_window, 750, 800)
        self.game_window.protocol("WM_DELETE_WINDOW", self.close_game)
        self.game_window.configure(bg="#F0F8FF")
        
        # Create UI elements
        self.create_game_ui()
        self.spawn_new_brick()
        
        # Auto-select the answer entry field for immediate typing
        self.game_window.after(100, self.auto_focus_entry)
        
        self.update_game()
        
    def create_game_ui(self):
        # Main container
        main_frame = tk.Frame(self.game_window, bg="#F0F8FF")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Top frame for level and lives - Enhanced retro style
        top_frame = tk.Frame(main_frame, bg="#F0F8FF")
        top_frame.pack(fill="x", pady=5)
        
        # Level display with retro styling
        level_frame = tk.Frame(top_frame, bg="#F0F8FF")
        level_frame.pack(side="left")
        
        # "LEVEL" label
        level_text_label = tk.Label(level_frame, text="LEVEL", font=("Arial", 12, "bold"), 
                                   fg="#FFD700", bg="#000080", relief="raised", bd=2,
                                   padx=5, pady=2)
        level_text_label.pack()
        
        # Level number with retro arcade styling
        self.level_label = tk.Label(level_frame, text="0", font=("Courier", 24, "bold"), 
                                   relief="solid", borderwidth=4, width=4, height=1,
                                   bg="#000000", fg="#00FF00")  # Classic green on black
        self.level_label.pack(pady=(2, 0))
        
        # Lives display
        lives_frame = tk.Frame(top_frame, bg="#F0F8FF")
        lives_frame.pack(side="right")
        
        self.heart_labels = []
        for i in range(self.settings["lives"]):
            heart = tk.Label(lives_frame, text="❤️", font=("Arial", 20), bg="#F0F8FF")
            heart.pack(side="left")
            self.heart_labels.append(heart)
            
        # Content frame with game area and failed numbers
        content_frame = tk.Frame(main_frame, bg="#F0F8FF")
        content_frame.pack(fill="both", expand=True)
        
        # Failed numbers list (left side)
        failed_frame = tk.Frame(content_frame, bg="#F0F8FF")
        failed_frame.pack(side="left", fill="y", padx=(0, 10))
        
        tk.Label(failed_frame, text="Failed Numbers:", font=("Arial", 12, "bold"), 
                bg="#F0F8FF", fg="#C73E1D").pack(anchor="w")
        
        # Scrollable frame for failed numbers
        self.failed_canvas = tk.Canvas(failed_frame, width=120, height=300, bg="white", 
                                      relief="sunken", bd=2)
        self.failed_scrollbar = tk.Scrollbar(failed_frame, orient="vertical", 
                                           command=self.failed_canvas.yview)
        self.failed_scrollable_frame = tk.Frame(self.failed_canvas, bg="white")
        
        self.failed_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.failed_canvas.configure(scrollregion=self.failed_canvas.bbox("all"))
        )
        
        self.failed_canvas.create_window((0, 0), window=self.failed_scrollable_frame, anchor="nw")
        self.failed_canvas.configure(yscrollcommand=self.failed_scrollbar.set)
        
        self.failed_canvas.pack(side="left", fill="both", expand=True)
        self.failed_scrollbar.pack(side="right", fill="y")
        
        # Game area (right side)
        game_area = tk.Frame(content_frame, bg="#F0F8FF")
        game_area.pack(side="right", fill="both", expand=True)
        
        # Message area
        self.message_label = tk.Label(game_area, text="", font=("Arial", 14), 
                                     fg="red", height=2, bg="#F0F8FF")
        self.message_label.pack()
        
        # Game canvas
        self.canvas = tk.Canvas(game_area, width=450, height=480, bg="#87CEEB", relief="raised", bd=3)
        self.canvas.pack()
        
        # Draw background
        self.draw_background()
        
        # Answer input
        input_frame = tk.Frame(game_area, bg="#F0F8FF")
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Answer:", font=("Arial", 14, "bold"), bg="#F0F8FF").pack(side="left")
        self.answer_entry = tk.Entry(input_frame, font=("Arial", 16), width=15, relief="solid", bd=2,
                                   highlightthickness=2, highlightcolor="#4A90E2", insertwidth=3)
        self.answer_entry.pack(side="left", padx=10)
        self.answer_entry.focus_set()
        self.answer_entry.bind("<Return>", self.check_answer)
        self.answer_entry.bind("<Button-1>", self.focus_answer_entry)
        self.answer_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.answer_entry.bind("<FocusOut>", self.on_entry_focus_out)
        
        # Bind space for pause
        self.game_window.bind("<KeyPress-space>", self.toggle_pause)
        self.game_window.focus_set()
        
    def auto_focus_entry(self):
        """Automatically focus and select the answer entry field"""
        if hasattr(self, 'answer_entry') and self.answer_entry.winfo_exists():
            self.answer_entry.focus_set()
            self.answer_entry.select_range(0, tk.END)  # Select all text if any
            self.answer_entry.icursor(tk.END)  # Move cursor to end
            # Ensure the game window also has focus
            self.game_window.focus_force()
            self.answer_entry.focus_force()
        
    def draw_background(self):
        # Retro-style sky with pixel-art gradient
        colors = ["#87CEEB", "#7EC0EE", "#6BB6FF", "#5CACEE", "#4F94CD", "#4682B4"]
        for i, color in enumerate(colors):
            y_start = i * 65
            y_end = (i + 1) * 65
            self.canvas.create_rectangle(0, y_start, 450, y_end, fill=color, outline="")
        
        # Add retro clouds with pixel-style
        cloud_positions = [(80, 80), (200, 60), (320, 100), (150, 120)]
        for x, y in cloud_positions:
            # Pixelated cloud style
            self.canvas.create_rectangle(x, y, x+40, y+20, fill="white", outline="#CCCCCC")
            self.canvas.create_rectangle(x+10, y-10, x+30, y+10, fill="white", outline="#CCCCCC")
            self.canvas.create_rectangle(x+20, y-15, x+35, y+5, fill="white", outline="#CCCCCC")
        
        # Retro-style grass with pixel texture
        self.canvas.create_rectangle(0, 400, 450, 480, fill="#228B22", outline="")
        # Add pixel-style grass texture
        for i in range(0, 450, 15):
            self.canvas.create_rectangle(i, 400, i + 8, 480, fill="#32CD32", outline="")
            self.canvas.create_rectangle(i+8, 405, i + 15, 480, fill="#006400", outline="")
        
        # Enhanced retro buildings with more detail and pixel-art style
        buildings = [
            (30, 280, 80, 400),
            (100, 240, 140, 400),
            (160, 300, 200, 400),
            (280, 260, 330, 400),
            (350, 290, 390, 400)
        ]
        
        colors = ["#696969", "#778899", "#2F4F4F", "#483D8B", "#8B4513"]
        
        for i, (x1, y1, x2, y2) in enumerate(buildings):
            # Building body with pixel-art style
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[i], outline="black", width=2)
            
            # Add vertical lines for texture
            for line_x in range(x1 + 10, x2, 8):
                self.canvas.create_line(line_x, y1, line_x, y2, fill="black", width=1)
            
            # Retro-style roof
            roof_color = "#8B0000" if i % 2 == 0 else "#4B0082"
            self.canvas.create_polygon(x1-5, y1, (x1+x2)//2, y1-20, x2+5, y1, 
                                     fill=roof_color, outline="black", width=2)
            
            # Pixel-style windows with retro glow
            for wx in range(x1 + 8, x2 - 8, 15):
                for wy in range(y1 + 15, y2 - 15, 20):
                    if random.random() > 0.3:
                        # Lit window with retro glow effect
                        self.canvas.create_rectangle(wx, wy, wx + 8, wy + 8, 
                                                   fill="#FFFF00", outline="black")
                        # Add glow effect
                        self.canvas.create_rectangle(wx+1, wy+1, wx + 7, wy + 7, 
                                                   fill="#FFFF88", outline="")
                    else:
                        # Dark window
                        self.canvas.create_rectangle(wx, wy, wx + 8, wy + 8, 
                                                   fill="#000080", outline="black")
                        
        # Add retro stars in the sky
        star_positions = [(60, 50), (150, 40), (250, 70), (350, 45), (400, 65)]
        for sx, sy in star_positions:
            # Create pixelated star
            self.canvas.create_rectangle(sx, sy, sx+3, sy+3, fill="white", outline="")
            self.canvas.create_rectangle(sx+1, sy-2, sx+2, sy+5, fill="white", outline="")
            self.canvas.create_rectangle(sx-2, sy+1, sx+5, sy+2, fill="white", outline="")
                    
    def spawn_new_brick(self):
        if not self.game_active or self.game_paused:
            return
            
        self.current_number = random.randint(1, self.max_number)
        self.brick_y = 0
        self.start_time = time.time()
        
        # Clear any existing brick elements
        if hasattr(self, 'current_brick') and self.current_brick:
            self.canvas.delete(self.current_brick)
        if hasattr(self, 'brick_highlight'):
            self.canvas.delete(self.brick_highlight)
        if hasattr(self, 'brick_shadow'):
            self.canvas.delete(self.brick_shadow)
        if hasattr(self, 'brick_text'):
            self.canvas.delete(self.brick_text)
        if hasattr(self, 'brick_text_shadow'):
            self.canvas.delete(self.brick_text_shadow)
        
        # Create new brick at center
        brick_x = 175  # Center of 450px wide canvas minus half brick width (100/2)
        
        # Create 3D-looking brick with gradient effect
        self.current_brick = self.canvas.create_rectangle(
            brick_x, self.brick_y, brick_x + 100, self.brick_y + 40,
            fill="#FF6347", outline="#8B0000", width=3
        )
        
        # Add brick highlight for 3D effect
        self.brick_highlight = self.canvas.create_rectangle(
            brick_x + 3, self.brick_y + 3, brick_x + 97, self.brick_y + 15,
            fill="#FFA07A", outline=""
        )
        
        # Add brick shadow for 3D effect
        self.brick_shadow = self.canvas.create_rectangle(
            brick_x + 3, self.brick_y + 25, brick_x + 97, self.brick_y + 37,
            fill="#CD5C5C", outline=""
        )
        
        # Add number text with shadow
        self.brick_text_shadow = self.canvas.create_text(
            brick_x + 52, self.brick_y + 22, text=str(self.current_number),
            font=("Arial", 16, "bold"), fill="#8B0000"
        )
        
        self.brick_text = self.canvas.create_text(
            brick_x + 50, self.brick_y + 20, text=str(self.current_number),
            font=("Arial", 16, "bold"), fill="white"
        )
        
    def focus_answer_entry(self, event=None):
        """Ensure the answer entry gets focus when clicked"""
        if hasattr(self, 'answer_entry'):
            self.answer_entry.focus_set()
            self.answer_entry.icursor(tk.END)  # Move cursor to end
    
    def on_entry_focus_in(self, event=None):
        """Handle when entry field gains focus"""
        if hasattr(self, 'answer_entry'):
            self.answer_entry.config(highlightbackground="#4A90E2", bg="#FFFFFF")
    
    def on_entry_focus_out(self, event=None):
        """Handle when entry field loses focus"""
        if hasattr(self, 'answer_entry'):
            self.answer_entry.config(highlightbackground="#CCCCCC", bg="#F8F8F8")
    
    def toggle_pause(self, event=None):
        if not self.game_active:
            return
            
        if self.game_paused:
            # Unpause
            self.game_paused = False
            self.message_label.config(text="")
            self.start_time = time.time()  # Reset start time
            self.auto_focus_entry()  # Refocus on answer entry with selection
            self.update_game()
        else:
            # Pause
            self.game_paused = True
            self.message_label.config(text="PAUSED - Press SPACE to continue")
            
    def update_game(self):
        if not self.game_active or self.game_paused:
            return
            
        # Move brick down
        if self.current_brick:
            self.brick_y += 480 / (self.brick_speed * 60)  # 60 FPS assumption
            
            # Update all brick elements
            brick_x = 175
            self.canvas.coords(self.current_brick, 
                             brick_x, self.brick_y, brick_x + 100, self.brick_y + 40)
            self.canvas.coords(self.brick_highlight,
                             brick_x + 3, self.brick_y + 3, brick_x + 97, self.brick_y + 15)
            self.canvas.coords(self.brick_shadow,
                             brick_x + 3, self.brick_y + 25, brick_x + 97, self.brick_y + 37)
            self.canvas.coords(self.brick_text, brick_x + 50, self.brick_y + 20)
            self.canvas.coords(self.brick_text_shadow, brick_x + 52, self.brick_y + 22)
            
            # Check if brick hit the ground
            if self.brick_y >= 360:  # Ground level minus brick height
                self.lose_life()
                
        # Schedule next update
        if self.game_active and not self.game_paused:
            self.game_window.after(16, self.update_game)  # ~60 FPS
            
    def check_answer(self, event=None):
        if not self.game_active or self.game_paused:
            return
            
        try:
            answer = int(self.answer_entry.get())
            correct_answer = self.current_number ** 2
            
            if answer == correct_answer:
                # Correct answer
                self.correct_answers += 1
                self.level += 1
                self.level_label.config(text=str(self.level))
                
                # Apply speed increase if enabled (every 10 levels)
                if self.speed_increase_mode and self.level % 10 == 0:
                    self.brick_speed = self.base_speed * (0.9 ** (self.level // 10))
                
                # Record time
                answer_time = time.time() - self.start_time
                self.answer_times.append(answer_time)
                self.total_time += answer_time
                
                # Clear message
                self.message_label.config(text="")
                
                # Explode brick
                self.explode_brick()
                
                # Clear answer field
                self.answer_entry.delete(0, tk.END)
                
                # Spawn new brick after a short delay and refocus entry
                self.game_window.after(500, lambda: [self.spawn_new_brick(), self.auto_focus_entry()])
                
        except ValueError:
            pass  # Invalid input, ignore
            
    def explode_brick(self):
        if not self.current_brick:
            return
            
        # Get brick position
        coords = self.canvas.coords(self.current_brick)
        center_x = (coords[0] + coords[2]) / 2
        center_y = (coords[1] + coords[3]) / 2
        
        # Remove original brick elements
        self.canvas.delete(self.current_brick)
        self.canvas.delete(self.brick_highlight)
        self.canvas.delete(self.brick_shadow)
        self.canvas.delete(self.brick_text)
        self.canvas.delete(self.brick_text_shadow)
        self.current_brick = None
        
        # Create explosion pieces
        pieces = []
        for i in range(8):
            angle = i * 45
            dx = math.cos(math.radians(angle)) * 3
            dy = math.sin(math.radians(angle)) * 3
            
            piece = self.canvas.create_rectangle(
                center_x - 5, center_y - 5, center_x + 5, center_y + 5,
                fill="#FF6347", outline="black"
            )
            pieces.append((piece, dx, dy, center_x, center_y))
            
        # Animate explosion
        self.animate_explosion(pieces, 0)
        
    def animate_explosion(self, pieces, frame):
        if frame > 30:  # Animation duration
            for piece, _, _, _, _ in pieces:
                self.canvas.delete(piece)
            return
            
        alpha = 1 - frame / 30  # Fade out
        
        for i, (piece, dx, dy, start_x, start_y) in enumerate(pieces):
            new_x = start_x + dx * frame
            new_y = start_y + dy * frame
            
            self.canvas.coords(piece, new_x - 5, new_y - 5, new_x + 5, new_y + 5)
            
        self.game_window.after(50, lambda: self.animate_explosion(pieces, frame + 1))
        
    def lose_life(self):
        self.lives -= 1
        
        # Add failed number to the list
        self.failed_numbers.append(self.current_number)
        self.update_failed_numbers_display()
        
        # Clear all brick elements completely
        if hasattr(self, 'current_brick') and self.current_brick:
            self.canvas.delete(self.current_brick)
        if hasattr(self, 'brick_highlight'):
            self.canvas.delete(self.brick_highlight)
        if hasattr(self, 'brick_shadow'):
            self.canvas.delete(self.brick_shadow)
        if hasattr(self, 'brick_text'):
            self.canvas.delete(self.brick_text)
        if hasattr(self, 'brick_text_shadow'):
            self.canvas.delete(self.brick_text_shadow)
        self.current_brick = None
        
        # Show correct answer briefly
        correct_answer = self.current_number ** 2
        self.message_label.config(text=f"Fail! The correct answer was: {correct_answer}")
        
        # Clear the message after 2 seconds
        self.game_window.after(2000, lambda: self.message_label.config(text=""))
        
        # Remove a heart
        if self.heart_labels:
            heart = self.heart_labels.pop()
            heart.destroy()
            
        # Clear answer field
        self.answer_entry.delete(0, tk.END)
        
        if self.lives <= 0:
            self.game_over()
        else:
            # Spawn new brick and refocus entry
            self.spawn_new_brick()
            self.game_window.after(100, self.auto_focus_entry)
    
    def update_failed_numbers_display(self):
        # Clear existing failed numbers
        for widget in self.failed_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Add all failed numbers
        for number in self.failed_numbers:
            label = tk.Label(self.failed_scrollable_frame, text=str(number), 
                           font=("Arial", 11), bg="white", fg="#C73E1D", 
                           relief="flat", pady=2)
            label.pack(fill="x", padx=5, pady=1)
        
        # Update scroll region
        self.failed_scrollable_frame.update_idletasks()
        self.failed_canvas.configure(scrollregion=self.failed_canvas.bbox("all"))
        
    def game_over(self):
        self.game_active = False
        self.game_paused = False
        
        # Clear all brick elements
        if hasattr(self, 'current_brick') and self.current_brick:
            self.canvas.delete(self.current_brick)
        if hasattr(self, 'brick_highlight'):
            self.canvas.delete(self.brick_highlight)
        if hasattr(self, 'brick_shadow'):
            self.canvas.delete(self.brick_shadow)
        if hasattr(self, 'brick_text'):
            self.canvas.delete(self.brick_text)
        if hasattr(self, 'brick_text_shadow'):
            self.canvas.delete(self.brick_text_shadow)
        
        # Show FAIL message on the game canvas with better readability
        # Create background rectangle for better contrast
        fail_bg = self.canvas.create_rectangle(50, 150, 400, 320, fill="#000000", outline="#FF0000", width=4)
        self.canvas.create_rectangle(55, 155, 395, 315, fill="#330000", outline="")  # Inner shadow
        
        self.canvas.create_text(225, 200, text="GAME OVER", font=("Courier", 32, "bold"), fill="#FF0000", tags="gameover")
        
        # Create readable background for instructions
        instruction_bg = self.canvas.create_rectangle(80, 250, 370, 290, fill="#FFFF00", outline="#000000", width=2)
        self.canvas.create_text(225, 270, text="Press SPACE to see stats", 
                               font=("Arial", 14, "bold"), fill="#000000", tags="gameover")
        
        # Bind space key for stats
        self.game_window.bind("<KeyPress-space>", self.show_stats)
        self.game_window.focus_set()
        
    def show_stats(self, event=None):
        # Save to leaderboard if using default settings and not custom mode
        if (self.current_mode != "Custom" and self.current_hardness != "Custom" and
            self.settings["lives"] == 3 and self.level > 0):
            
            leaderboard = self.load_leaderboard()
            key = f"{self.current_mode}_{self.current_hardness}"
            
            if key not in leaderboard:
                leaderboard[key] = []
            
            leaderboard[key].append(self.level)
            leaderboard[key].sort(reverse=True)
            leaderboard[key] = leaderboard[key][:5]  # Keep top 5
            
            self.save_leaderboard(leaderboard)
        
        # Clear the game window
        for widget in self.game_window.winfo_children():
            widget.destroy()
            
        # Stats display
        stats_frame = tk.Frame(self.game_window)
        stats_frame.pack(expand=True, fill="both")
        
        tk.Label(stats_frame, text="GAME STATS", font=("Arial", 24, "bold")).pack(pady=20)
        
        tk.Label(stats_frame, text=f"Level Reached: {self.level}", 
                font=("Arial", 18)).pack(pady=10)
        
        if self.answer_times:
            avg_time = sum(self.answer_times) / len(self.answer_times)
            tk.Label(stats_frame, text=f"Average Time per Correct Answer: {avg_time:.2f}s",
                    font=("Arial", 18)).pack(pady=10)
        else:
            tk.Label(stats_frame, text="Average Time per Correct Answer: N/A",
                    font=("Arial", 18)).pack(pady=10)
        
        # Show leaderboard message if score was saved
        if (self.current_mode != "Custom" and self.current_hardness != "Custom" and
            self.settings["lives"] == 3 and self.level > 0):
            tk.Label(stats_frame, text="Score saved to leaderboard!", 
                    font=("Arial", 14), fg="green").pack(pady=5)
            
        # Fixed play again button - macOS compatible with retro styling
        play_again_canvas = tk.Canvas(stats_frame, width=200, height=60, bg=stats_frame.cget('bg'), highlightthickness=0)
        play_again_canvas.pack(pady=30)
        
        # Retro-style button with multiple layers
        play_again_canvas.create_rectangle(10, 10, 190, 50, fill="#4169E1", outline="#191970", width=3)
        play_again_canvas.create_rectangle(12, 12, 188, 25, fill="#6495ED", outline="")  # Highlight
        play_again_canvas.create_rectangle(12, 35, 188, 48, fill="#0000CD", outline="")  # Shadow
        play_again_canvas.create_text(100, 30, text="PLAY AGAIN", font=("Courier", 14, "bold"), fill="white")
        
        def on_play_again_click(event):
            play_again_canvas.delete("hover")  # Remove hover effect first
            play_again_canvas.create_rectangle(10, 10, 190, 50, fill="#191970", outline="#000080", width=3, tags="pressed")
            play_again_canvas.after(50, lambda: [play_again_canvas.delete("pressed"), self.close_game()])
        
        def on_play_again_enter(event):
            play_again_canvas.create_rectangle(12, 12, 188, 48, fill="#87CEEB", outline="", tags="hover")
        
        def on_play_again_leave(event):
            play_again_canvas.delete("hover")
        
        # Multiple event bindings for better responsiveness
        play_again_canvas.bind("<Button-1>", on_play_again_click)
        play_again_canvas.bind("<ButtonPress-1>", on_play_again_click)
        play_again_canvas.bind("<ButtonRelease-1>", on_play_again_click)
        play_again_canvas.bind("<Enter>", on_play_again_enter)
        play_again_canvas.bind("<Leave>", on_play_again_leave)
        play_again_canvas.config(cursor="hand2")
        play_again_canvas.focus_set()
        
    def close_game(self):
        if self.game_window:
            self.game_window.destroy()
            self.game_window = None
        self.game_active = False
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = MentalMathGame()
    game.run()