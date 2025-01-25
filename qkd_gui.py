import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import threading

def on_submit():
    root.geometry("1536x864+300+100")  # Resize for a larger view
    initial_frame.pack_forget()  # Hide the initial frame

    # Create a container frame for scrolling
    container = tk.Frame(root)
    container.pack(expand=True, fill="both", padx=10, pady=10)

    # Create a canvas for the scrolling content
    canvas = tk.Canvas(container)
    canvas.pack(side=tk.LEFT, expand=True, fill="both")

    # Add vertical scrollbar
    v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill="y")

    # Add horizontal scrollbar
    h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill="x")

    # Configure canvas scrolling
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Create a frame inside the canvas for the actual content
    scrollable_frame = tk.Frame(canvas)

    # Add the scrollable frame to the canvas
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Update the scrollregion dynamically based on the frame's size
    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Ensure the canvas size is large enough to allow horizontal scrolling
        canvas.itemconfig(canvas_window, width=scrollable_frame.winfo_reqwidth())

    scrollable_frame.bind("<Configure>", update_scroll_region)

    # Enable mouse wheel scrolling (vertical and horizontal)
    def on_mouse_wheel(event):
        if event.state & 1:  # Shift key pressed for horizontal scrolling
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    def run_c_program():
        try:
            # Run the C program and capture its output
            args = [
                "./main.exe",
                key_size.get(),             # Key Size
                key_part_size.get(),        # Key Part Size
                calibration_error.get().strip('%'),  # Calibration Error Percentage (strip '%' if present)
                eve_listen_percent.get().strip('%'),  # Eve Error Percentage
                eve_sections_listened.get().strip('%'),  # Eve Reproduction Percentage
                allowed_wrong_bits.get(),   # Allowed Wrong Bits
                "1" if eavesdropping.get() == "Enable" else "0"  # Eavesdropping (1 if enabled, 0 if disabled)
            ]
            process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            output, error = process.communicate()

            if process.returncode != 0:
                error_label = tk.Label(scrollable_frame, text=f"Error: {error}", fg="red", font=("Arial", 14))
                error_label.pack(pady=10)
                return

            # Parse and display the output
            parsed_data = parse_c_output(output)
            display_sections(parsed_data, scrollable_frame)

        except Exception as e:
            error_label = tk.Label(scrollable_frame, text=f"Error: {e}", fg="red", font=("Arial", 14))
            error_label.pack(pady=10)

    # Start the thread
    threading.Thread(target=run_c_program, daemon=True).start()

def parse_c_output(output):
    sections = {}
    current_section = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("=" * 40) or line.startswith("-" * 40):
            continue
        elif not line:
            continue
        elif line.startswith("Section #") or line.startswith("Final Key"):
            current_section = line
            sections[current_section] = []
        else:
            if current_section is None:
                current_section = "General"
                sections[current_section] = []
            sections[current_section].append(line)
    return sections


def display_sections(parsed_data, parent_frame):
    count = 0 
    # Define colors for special symbols
    colors = {
        "↔": "#226fb1",  # blue
        "↕": "#1ba84d",  # green
        "↗": "#fcbd14",  # orange
        "↘": "#e12927",  # red
        "+": "#0f969e",  # light-blue
        "x": "#ed3e94",  # pink
        "✗": "white",  
        "✓": "white",  # green
        "1": "white",
        "0": "white",
        "-": "white",
        "*": "white"
    }

    # Map symbols to their display representations
    symbol_mapping = {
        "h": "↔",
        "v": "↕",
        "d": "↗",
        "b": "↘",
        "x": "x",
        "X": "✗",
        "V": "✓",
        "-": "-",
        "0": "0",
        "1": "1",
        "*": "*"
    }

    data_frame = tk.Frame(parent_frame)
    data_frame.grid(row=0, column=0, sticky="w", padx=1, pady=10)

    # Extract values from the variables
    data = {
        "Key Size": f"{key_size.get()} bits",
        "Key Part Size": f"{key_part_size.get()} bits",
        "Number of Key Parts": f"{int(key_size.get()) // int(key_part_size.get())}",
        "Eavesdropping": f"{eavesdropping.get()}",
        "Calibration Error Percentage": f"{calibration_error.get()}",
        "Eve Error Percentage": f"{eve_listen_percent.get()}",
        "Eve Section Eavesdropping": f"{eve_sections_listened.get()}",
        "Allowed Wrong Bits": f"{allowed_wrong_bits.get()} bits",
    }
    title_label = tk.Label(data_frame, text="Configuration Details", font=("Arial", 12, "bold"), anchor="w")
    title_label.grid(row=0, column=0, columnspan=2, padx=1, pady=10, sticky="w")

    # Start the row index after the title
    row = 1  # Start at 1 to leave space for the title
    # Display the first set of data
    for key, value in data.items():
        # Display the key (label)
        key_label = tk.Label(data_frame, text=key, font=("Arial", 9, "bold"), anchor="w")
        key_label.grid(row=row, column=0, padx=1, pady=5, sticky="w")

        # Display the value as plain text
        value_label = tk.Label(data_frame, text=value, font=("Arial", 9), anchor="w")
        value_label.grid(row=row, column=1, padx=1, pady=5, sticky="w")

        row += 1

    symbols_frame = tk.Frame(parent_frame)
    symbols_frame.grid(row=row, column=0, sticky="w", padx=1, pady=10)

    # Add Basis Symbols Section
    row+=1
    basis_title = tk.Label(symbols_frame, text="Basis Symbols", font=("Arial", 12, "bold"), anchor="w")
    basis_title.grid(row=row, column=0, columnspan=2, padx=1, pady=10, sticky="w")
    row+=1
    basis_content = {
        "+":"Rectilinear Basis",
        "x":"Diagonal Basis"
    }

    for symbol, description in basis_content.items():
        # Extract the visual representation and color
        visual = symbol_mapping.get(symbol, symbol)
        bg_color = colors.get(visual, "SystemButtonFace")

        # Create a label for the symbol with its color
        symbol_label = tk.Label(symbols_frame, text=visual, bg=bg_color, font=("Arial", 10, "bold"), width=2, height=1)
        symbol_label.grid(row=row, column=0, padx=1, pady=2, sticky="w")

        # Create a label for the description
        description_label = tk.Label(symbols_frame, text=description, font=("Arial", 10), anchor="w")
        description_label.grid(row=row, column=1, padx=1, pady=2, sticky="w")

        row += 1
    # Add Filter Symbols Section
    filter_title = tk.Label(symbols_frame, text="Filter Symbols", font=("Arial", 12, "bold"), anchor="w")
    filter_title.grid(row=row, column=0, columnspan=2, padx=1, pady=2, sticky="w")
    row += 1

    filter_content = {
        "d": "Diagonal Basis (45°)",
        "v": "Vertical Basis",
        "h": "Horizontal Basis",
        "b": "Diagonal Basis (-45°)",
    }

    count2 = row
    filter_title = tk.Label(symbols_frame, text="(bit = 0):", font=("Arial", 10), anchor="w")
    filter_title.grid(row=row, column=0, columnspan=2, padx=1, pady=3, sticky="w")
    row+=1
    for symbol, description in filter_content.items():
        if row == count2 + 3:
            filter_title = tk.Label(symbols_frame, text="(bit = 1):", font=("Arial", 10), anchor="w")
            filter_title.grid(row=row, column=0, columnspan=2, padx=1, pady=10, sticky="w")
            row += 1
        
        # Extract the visual representation and color
        visual = symbol_mapping.get(symbol, symbol)
        bg_color = colors.get(visual, "SystemButtonFace")

        # Create a label for the symbol with its color
        symbol_label = tk.Label(symbols_frame, text=visual, bg=bg_color, font=("Arial", 10, "bold"), width=2, height=1)
        symbol_label.grid(row=row, column=0, padx=1, pady=2, sticky="w")

        # Create a label for the description
        description_label = tk.Label(symbols_frame, text=description, font=("Arial", 10), anchor="w")
        description_label.grid(row=row, column=1, padx=1, pady=2, sticky="w")

        row += 1
    
    # Add Measurement Symbols Section
    measurement_title = tk.Label(symbols_frame, text="Measurement Symbols", font=("Arial", 12, "bold"), anchor="w")
    measurement_title.grid(row=row, column=0, columnspan=2, padx=1, pady=10, sticky="w")
    row += 1

    measurement_content = {
        "✓":"Correct Measurement",
        "✗":"Wrong Measurement"
    }
    for symbol, description in measurement_content.items():
        # Extract the visual representation and color
        visual = symbol_mapping.get(symbol, symbol)
        bg_color = colors.get(visual, "SystemButtonFace")

        # Create a label for the symbol with its color
        symbol_label = tk.Label(symbols_frame, text=visual, bg=bg_color, font=("Arial", 10, "bold"), width=2, height=1)
        symbol_label.grid(row=row, column=0, padx=1, pady=2, sticky="w")

        # Create a label for the description
        description_label = tk.Label(symbols_frame, text=description, font=("Arial", 10), anchor="w")
        description_label.grid(row=row, column=1, padx=1, pady=2, sticky="w")

        row += 1

    parent_frame2 = tk.Frame(parent_frame)
    parent_frame2.grid(row=row, column=0, sticky="w", padx=1, pady=10)

    for section, content in parsed_data.items():
        # Display section title
        section_label = tk.Label(parent_frame2, text=section, font=("Arial", 12, "bold"))
        section_label.grid(row=row, column=0, columnspan=10, padx=10, pady=10, sticky="w")
        row += 1

        # Display the content with appropriate colors
        for line in content:
            if ":" in line:  # Handle rows with keys and values
                key, value = map(str.strip, line.split(":", 1))
                key_label = tk.Label(parent_frame2, text=key, font=("Arial", 9, "bold"), anchor="e")
                key_label.grid(row=row, column=0, padx=2, pady=5, sticky="e")

                # Display the value with colored characters
                for col, char in enumerate(value):
                    char = symbol_mapping.get(char, char)  # Convert if necessary
                    bg_color = colors.get(char, None)  # Get color if defined
                    value_char = tk.Label(parent_frame2, text=char, bg=bg_color or "SystemButtonFace", font=("Arial", 9, "bold"), width=2, height=1)
                    value_char.grid(row=row, column=1 + col, padx=0.5, pady=0.5)

                row += 1
            else:  # Handle rows with raw data
                for col, char in enumerate(line):  # Iterate through each character in the line
                    #char = symbol_mapping.get(char, char)  # Convert if necessary
                    #bg_color = colors.get(char, None)  # Get color if defined
                    cell = tk.Label(parent_frame2, text=char, bg=bg_color or "SystemButtonFace", font=("Arial", 9, "bold"), width=2, height=1)
                    cell.grid(row=row, column=col, padx=0.5, pady=0.5)
                row += 1

        #if count == 3:
        #    break
        #count += 1

# GUI Setup
root = tk.Tk()
root.title("QKD - Quantum Key Distribution")
root.geometry("1536x864")

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
