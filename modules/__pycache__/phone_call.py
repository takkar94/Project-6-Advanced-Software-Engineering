# This script handles the Phone Call distraction (audible notification interrupting the user)

import tkinter as tk
from tkinter import ttk
import threading
import pygame
import time
import csv
import os

# Initialize pygame mixer
pygame.mixer.init()

# Global variables to track task and phone call state
phone_playing = False
start_time = None
task_completed = False
phone_channel = None  # To control the phone call playback

# Function to play phone call sound in a separate thread
def play_phone_call():
    global phone_playing, phone_channel
    phone_playing = True
    phone_channel = pygame.mixer.Sound('phone_call.mp3')  # Load the phone call audio file
    phone_channel.play(-1)  # -1 means loop indefinitely
    while phone_playing:
        time.sleep(0.1)  # Keep thread alive while phone sound is playing
    phone_channel.stop()  # Stop when phone_playing becomes False

# Function to start phone call sound
def start_phone():
    global phone_playing
    if not phone_playing:
        phone_thread = threading.Thread(target=play_phone_call)
        phone_thread.start()
        log_event("Phone Call Started")
        status_label.config(text="Phone Call Playing...")

# Function to stop phone call sound
def stop_phone():
    global phone_playing
    if phone_playing:
        phone_playing = False
        if phone_channel:
            phone_channel.stop()
        log_event("Phone Call Stopped")
        status_label.config(text="Phone Call Stopped")

# Function to log events to CSV
def log_event(event_description):
    global start_time
    if start_time is None and event_description == "Task Started":
        start_time = time.time()
    
    current_time = time.time()
    elapsed_time = current_time - start_time if start_time else 0
    
    with open('phone_task_log.csv', mode='a', newline='') as file:
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
    if not os.path.exists('phone_task_log.csv'):
        with open('phone_task_log.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Event", "Timestamp", "Elapsed Time (seconds)"])

# Create the main GUI window
root = tk.Tk()
root.title("Programming Environment with Phone Call Distraction")
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

# Distraction control (Phone Call ..

phone_start_button = ttk.Button(root, text="Start Phone Call", command=start_phone)
phone_start_button.pack(pady=5)

phone_stop_button = ttk.Button(root, text="Stop Phone Call", command=stop_phone)
phone_stop_button.pack(pady=5)

# Status label
status_label = tk.Label(root, text="Ready", font=("Arial", 12))
status_label.pack(pady=10)

# Initialize CSV file
initialize_csv()

# Start the GUI loop
root.mainloop()

# Cleanup pygame mixer on exit
pygame.mixer.quit()
