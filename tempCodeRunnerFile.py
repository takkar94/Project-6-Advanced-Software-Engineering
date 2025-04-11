import tkinter as tk
import time
import datetime
from tkinter import font

class ToastNotification:
    def __init__(self, master, title, message, callback=None, timeout=None):
        self.master = master
        self.callback = callback
        self.timeout = timeout
        self.acknowledged = False
        
        # Create notification window
        self.window = tk.Toplevel(master)
        self.window.title("")
        self.window.overrideredirect(True)  # Remove window decorations
        
        # Position in bottom right corner   
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = 300
        window_height = 100
        x_position = screen_width - window_width - 20
        y_position = screen_height - window_height - 60
        
        self.window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.window.attributes('-topmost', True)  # Keep on top
        
        # Create a frame with border
        self.frame = tk.Frame(self.window, bg="#f0f0f0", relief="solid", borderwidth=1)
        self.frame.pack(fill="both", expand=True)
        
        # Title bar
        self.title_frame = tk.Frame(self.frame, bg="#e0e0e0")
        self.title_frame.pack(fill="x")
        
        # Title and close button in title bar
        bold_font = font.Font(weight="bold")
        title_label = tk.Label(self.title_frame, text=title, bg="#e0e0e0", anchor="w", font=bold_font)
        title_label.pack(side="left", padx=5, pady=2)
        
        close_button = tk.Label(self.title_frame, text="✕", bg="#e0e0e0", cursor="hand2")
        close_button.pack(side="right", padx=5, pady=2)
        close_button.bind("<Button-1>", self.on_close)
        
        # Message
        message_label = tk.Label(self.frame, text=message, bg="#f0f0f0", wraplength=280, justify="left")
        message_label.pack(padx=10, pady=5, anchor="w")
        
        # Action button
        action_button = tk.Button(self.frame, text="Acknowledge", command=self.acknowledge)
        action_button.pack(pady=5, padx=10, anchor="e")
        
        # Bind click on the notification
        self.window.bind("<Button-1>", self.acknowledge)
        
        # Auto-close timer if timeout is specified
        if self.timeout:
            self.window.after(self.timeout * 1000, self.auto_close)
        
        # Fade-in effect
        self.window.attributes('-alpha', 0.0)
        self.fade_in()
    
    def fade_in(self, alpha=0.0):
        if alpha < 1.0:
            alpha += 0.1
            self.window.attributes('-alpha', alpha)
            self.window.after(20, lambda: self.fade_in(alpha))
    
    def fade_out(self, alpha=1.0):
        if alpha > 0.0:
            alpha -= 0.1
            self.window.attributes('-alpha', alpha)
            self.window.after(20, lambda: self.fade_out(alpha))
        else:
            self.window.destroy()
    
    def acknowledge(self, event=None):
        if not self.acknowledged:
            self.acknowledged = True
            if self.callback:
                self.callback()
            self.fade_out()
    
    def on_close(self, event=None):
        if not self.acknowledged:
            self.acknowledged = True
            if self.callback:
                self.callback(was_closed=True)
            self.fade_out()
    
    def auto_close(self):
        if not self.acknowledged:
            self.acknowledged = True
            if self.callback:
                self.callback(timed_out=True)
            self.fade_out()

class NotificationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Notification Timer")
        self.root.geometry("400x300")
        
        self.start_time = None
        self.reaction_times = []
        self.active_notification = None
        
        # Create UI elements
        self.title_label = tk.Label(self.root, text="Toast Notification Timer", font=("Arial", 16))
        self.title_label.pack(pady=10)
        
        self.instruction_label = tk.Label(self.root, text="Click 'Send Notification' to start a timer.\nA toast notification will appear in the bottom right.")
        self.instruction_label.pack(pady=10)
        
        self.send_button = tk.Button(self.root, text="Send Notification", command=self.send_notification)
        self.send_button.pack(pady=10)
        
        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack(pady=10)
        
        self.history_label = tk.Label(self.root, text="Previous reaction times:")
        self.history_label.pack(pady=5)
        
        self.history_text = tk.Text(self.root, height=5, width=40)
        self.history_text.pack(pady=5)
        
        self.quit_button = tk.Button(self.root, text="Quit", command=self.root.quit)
        self.quit_button.pack(pady=10)
    
    def send_notification(self):
        # Disable the send button while notification is active
        self.send_button.config(state="disabled")
        
        # Create timestamp and start timer
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.result_label.config(text=f"Notification sent at: {current_time}\nWaiting for response...")
        self.start_time = time.time()
        
        # Show toast notification
        self.active_notification = ToastNotification(
            self.root,
            "Notification Alert",
            "This is a toast notification.\nClick anywhere or the 'Acknowledge' button.",
            callback=self.notification_callback,
            timeout=15  # Auto-close after 15 seconds
        )
    
    def notification_callback(self, was_closed=False, timed_out=False):
        # Calculate reaction time
        end_time = time.time()
        reaction_time = end_time - self.start_time
        
        # Determine action type
        action_type = "acknowledged"
        if was_closed:
            action_type = "closed"
        elif timed_out:
            action_type = "timed out"
        
        # Update result display
        self.result_label.config(text=f"Notification {action_type}\nReaction time: {reaction_time:.2f} seconds")
        
        # Add to history
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.reaction_times.append(reaction_time)
        history_entry = f"{timestamp}: {reaction_time:.2f}s ({action_type})\n"
        self.history_text.insert(tk.END, history_entry)
        
        # Re-enable send button
        self.send_button.config(state="normal")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NotificationApp()
    app.run()