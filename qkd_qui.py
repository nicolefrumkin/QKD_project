import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def on_submit():
    # You can add the logic for handling the form submission here
    print("Parameters submitted!")

# Create the main application window
root = tk.Tk()
root.title("QKD - Quantum Key Distribution")
root.geometry("600x800")

# Add the project title
title = tk.Label(root, text="QKD - Quantum Key Distribution", font=("Arial", 18, "bold"))
title.pack()
# Add the image
image = Image.open("first_image.jpg")
photo = ImageTk.PhotoImage(image)

img_label = tk.Label(root, image=photo)
img_label.pack(pady=10)

# Add the contributors
subtitle = tk.Label(root, text="A project by: Nicole Frumkin & Keren Koifman", font=("Arial", 12))
subtitle.pack()

# Add description
description = tk.Label(root, text="You are Alice!\nYou're trying to pass a key to Bob in order to encrypt a message.\n"
                                  "Please choose the following parameters:", font=("Arial", 10))
description.pack(pady=10)

# Add input fields with labels
def create_dropdown(label_text, options, default, parent):
    frame = tk.Frame(parent)
    frame.pack(pady=5, anchor="w", padx=20)

    label = tk.Label(frame, text=label_text, font=("Arial", 10))
    label.pack(side=tk.LEFT, padx=5)

    dropdown = ttk.Combobox(frame, values=options, state="readonly", width=10)
    dropdown.set(default)
    dropdown.pack(side=tk.LEFT)
    return dropdown

key_size = create_dropdown("Key Size (bits)", ["1024", "2048", "4096"], "1024", root)
key_part_size = create_dropdown("Key Part Size (bits)", ["16", "32", "64"], "32", root)
eavesdropping = create_dropdown("Eavesdropping", ["Enable", "Disable"], "Enable", root)
calibration_error = create_dropdown("Calibration Error Percentage", ["1%", "5%", "10%"], "1%", root)
eve_listen_percent = create_dropdown("Eve Listening Percentage in a Section", ["10%", "25%", "50%"], "25%", root)
eve_sections_listened = create_dropdown("Eve Sections Listened", ["10%", "25%", "50%"], "25%", root)
allowed_wrong_bits = create_dropdown("Allowed Wrong Bits in a Section", ["0", "1", "2", "5"], "1", root)

# Add the submit button
submit_button = tk.Button(root, text="Submit", command=on_submit, bg="green", fg="white", font=("Arial", 12, "bold"))
submit_button.pack(pady=20)

# Run the application
root.mainloop()

