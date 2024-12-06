import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import threading

def on_submit():
    root.geometry("800x1000+300+100")  # Width x Height + X-offset + Y-offset
    # Hide the initial frame
    initial_frame.pack_forget()

    # Create a new frame for the "Creating key..." screen
    creating_frame = tk.Frame(root)
    creating_frame.pack(expand=True, fill="both")

    # Add a "Creating key..." label
    label = tk.Label(creating_frame, text="Creating Key...", font=("Arial", 24, "bold"))
    label.pack(pady=10)

    # Add a Text widget to display real-time output
    output_text = tk.Text(creating_frame, font=("Courier", 12), bg="black", fg="white", wrap="word")
    output_text.pack(expand=True, fill="both", padx=10, pady=10)

    # Run the C program in a separate thread to avoid freezing the GUI
    def run_c_program():
        try:
            # Run the C program with subprocess.Popen
            args = [
                "./main",  # Path to the compiled C program
                key_size.get(),
                key_part_size.get(),
                eavesdropping.get(),
                calibration_error.get(),
                eve_listen_percent.get(),
                eve_sections_listened.get(),
                allowed_wrong_bits.get(),
            ]
            process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Read output line by line and update the Text widget
            for line in process.stdout:
                output_text.insert(tk.END, line)
                output_text.see(tk.END)  # Auto-scroll to the bottom
                root.update_idletasks()

            # Wait for the process to complete
            process.wait()

            if process.returncode != 0:
                # Capture and display errors
                error = process.stderr.read()
                output_text.insert(tk.END, f"\nError:\n{error}\n")
                output_text.see(tk.END)

        except Exception as e:
            output_text.insert(tk.END, f"\nAn error occurred: {e}\n")
            output_text.see(tk.END)

    # Start the thread
    threading.Thread(target=run_c_program, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("QKD - Quantum Key Distribution")
root.geometry("800x1000+300+100")

# Create an initial frame to hold all the initial widgets
initial_frame = tk.Frame(root)
initial_frame.pack(expand=True, fill="both")

# Dropdown creation function
def create_dropdown(label_text, options, default, parent):
    frame = tk.Frame(parent)
    frame.pack(pady=5, anchor="w", padx=20)

    label = tk.Label(frame, text=label_text, font=("Arial", 14))
    label.pack(side=tk.LEFT, padx=5)

    dropdown = ttk.Combobox(frame, values=options, state="readonly", width=10)
    dropdown.set(default)
    dropdown.pack(side=tk.LEFT)
    return dropdown

# Widgets for the initial frame
title = tk.Label(initial_frame, text="QKD - Quantum Key Distribution", font=("Arial", 24, "bold"))
title.pack()

subtitle = tk.Label(initial_frame, text="A project by: Nicole Frumkin & Keren Koifman", font=("Arial", 18))
subtitle.pack()

image = Image.open("first_image.jpg")
photo = ImageTk.PhotoImage(image)

img_label = tk.Label(initial_frame, image=photo)
img_label.pack(pady=10)

description = tk.Label(initial_frame, text="You are Alice!\nYou're trying to pass a key to Bob in order to encrypt a message.\n"
                                           "Please choose the following parameters:", font=("Arial", 16))
description.pack(pady=10)

key_size = create_dropdown("Key Size (bits)", ["1024", "2048", "4096"], "1024", initial_frame)
key_part_size = create_dropdown("Key Part Size (bits)", ["16", "32", "64"], "32", initial_frame)
eavesdropping = create_dropdown("Eavesdropping", ["Enable", "Disable"], "Enable", initial_frame)
calibration_error = create_dropdown("Calibration Error Percentage", ["1%", "5%", "10%"], "1%", initial_frame)
eve_listen_percent = create_dropdown("Eve Listening Percentage in a Section", ["10%", "25%", "50%"], "25%", initial_frame)
eve_sections_listened = create_dropdown("Eve Sections Listened", ["10%", "25%", "50%"], "25%", initial_frame)
allowed_wrong_bits = create_dropdown("Allowed Wrong Bits in a Section", ["0", "1", "2", "5"], "1", initial_frame)

submit_button = tk.Button(initial_frame, text="Submit", command=on_submit, bg="green", font=("Arial", 12, "bold"))
submit_button.pack(pady=20)

root.mainloop()
