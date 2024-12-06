import tkinter as tk

def display_output():
    # Clear existing screen
    for widget in root.winfo_children():
        widget.destroy()

    # Create a frame for the grid
    grid_frame = tk.Frame(root)
    grid_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Data to display
    labels = [
        "Raw keys", "Single photons", "Measurement bases", "Measurement results",
        "Sifted keys", "Key distillation", "Secret keys"
    ]
    data = [
        ["1", "0", "0", "1", "0", "1", "0", "0", "1"],
        ["↔", "↕", "↔", "↗", "↘", "↔", "↕", "↔", "↕"],
        ["+", "×", "+", "+", "×", "×", "+", "×", "+"],
        ["✓", "×", "✓", "✓", "✓", "×", "✓", "×", "×"],
        ["-", "0", "-", "1", "1", "0", "-", "-", "-"],
        ["-", "1", "-", "0", "-", "-", "-", "-", "-"],
        ["0", "-", "1", "-", "1", "-", "-", "1", "0"]
    ]
    colors = {
        "↔": "blue", "↕": "green", "↗": "orange", "↘": "pink",
        "+": "yellow", "×": "red", "✓": "lightgreen", "×": "red",
        "0": "white", "1": "black", "-": "gray"
    }

    # Add labels to the grid
    for row, (label_text, row_data) in enumerate(zip(labels, data)):
        # Row label
        label = tk.Label(grid_frame, text=label_text, font=("Arial", 14, "bold"), anchor="e", width=20)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="e")

        # Data cells
        for col, value in enumerate(row_data):
            bg_color = colors.get(value, "white")
            cell = tk.Label(grid_frame, text=value, bg=bg_color, font=("Arial", 12, "bold"), width=5, height=2)
            cell.grid(row=row, column=col + 1, padx=5, pady=5)

    # Add a "Back" button to return to the initial view
    back_button = tk.Button(root, text="Back", command=main_view, font=("Arial", 12))
    back_button.pack(pady=20)

def main_view():
    # Clear existing screen
    for widget in root.winfo_children():
        widget.destroy()

    # Add a button to display the output
    start_button = tk.Button(root, text="Show Output", command=display_output, font=("Arial", 14, "bold"))
    start_button.pack(pady=100)

# Create the main application window
root = tk.Tk()
root.title("QKD Visualization")
root.geometry("800x600")

main_view()

root.mainloop()
