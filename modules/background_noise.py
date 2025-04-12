import tkinter as tk
from tkinter import ttk
import threading
import pygame
import time
import csv
import os

# Initialize pygame mixer
pygame.mixer.init()

# Global variables to track task and noise state
noise_playing = False
start_time = None
task_completed = False
noise_channel = None  # To control the noise playback

# Function to play background noise in a separate thread
def play_background_noise():
    global noise_playing, noise_channel
    noise_playing = True
    noise_channel = pygame.mixer.Sound('office_chatter.mp3')  # Load the audio file
    noise_channel.play(-1)  # -1 means loop indefinitely
    while noise_playing:
        time.sleep(0.1)  # Keep thread alive while noise is playing
    noise_channel.stop()  # Stop when noise_playing becomes False

# Function to start background noise
def start_noise():
    global noise_playing
    if not noise_playing:
        noise_thread = threading.Thread(target=play_background_noise)
        noise_thread.start()
        log_event("Background Noise Started")
        status_label.config(text="Background Noise Playing...")

# Function to stop background noise
def stop_noise():
    global noise_playing
    if noise_playing:
        noise_playing = False
        if noise_channel:
            noise_channel.stop()
        log_event("Background Noise Stopped")
        status_label.config(text="Noise Stopped")

# Function to log events to CSV
def log_event(event_description):
    global start_time
    if start_time is None and event_description == "Task Started":
        start_time = time.time()
    
    current_time = time.time()
    elapsed_time = current_time - start_time if start_time else 0
    
    with open('task_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([event_description, time.strftime('%Y-%m-%d %H:%M:%S'), elapsed_time])

# Function to start the task
def start_task():
    log_event("Task Started")
    status_label.config(text="Task in Progress...")

# Function to complete the task
def complete_task():
    global task_completed
    task_completed = True
    log_event("Task Completed")
    status_label.config(text="Task Completed!")

# Function to initialize the CSV log file
def initialize_csv():
    if not os.path.exists('task_log.csv'):
        with open('task_log.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Event", "Timestamp", "Elapsed Time (seconds)"])

# Create the main GUI window
root = tk.Tk()
root.title("Programming Environment with Distractions")
root.geometry("600x400")

# Coding workspace (simplified as a text area)
code_label = tk.Label(root, text="Coding Workspace", font=("Arial", 14))
code_label.pack(pady=10)

code_text = tk.Text(root, height=10, width=50)
code_text.pack(pady=10)
code_text.insert(tk.END, "# Write your code here\nprint('Hello, World!')")

# Buttons for task control
start_button = ttk.Button(root, text="Start Task", command=start_task)
start_button.pack(pady=5)

complete_button = ttk.Button(root, text="Complete Task", command=complete_task)
complete_button.pack(pady=5)

# Distraction control (Background Noise)
noise_start_button = ttk.Button(root, text="Start Background Noise", command=start_noise)
noise_start_button.pack(pady=5)

noise_stop_button = ttk.Button(root, text="Stop Background Noise", command=stop_noise)
noise_stop_button.pack(pady=5)

# Status label
status_label = tk.Label(root, text="Ready", font=("Arial", 12))
status_label.pack(pady=10)

# Initialize CSV file
initialize_csv()

# Start the GUI loop
root.mainloop()

# Cleanup pygame mixer on exit
pygame.mixer.quit()
