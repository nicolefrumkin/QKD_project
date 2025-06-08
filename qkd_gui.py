import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import threading
import time

# Color scheme - ADD THIS RIGHT HERE
PRIMARY_COLOR = "#2E86AB"      # Professional blue
SECONDARY_COLOR = "#A23B72"    # Accent purple
ACCENT_COLOR = "#F18F01"       # Orange accent
BACKGROUND_COLOR = "#F7F9FA"   # Light background
TEXT_COLOR = "#2F3E46"         # Dark gray
CARD_COLOR = "#FFFFFF"         # White cards

def on_submit():
    # SAVE ALL VALUES BEFORE DESTROYING WIDGETS
    saved_values = {
        'key_size': key_size.get(),
        'key_part_size': key_part_size.get(),
        'eavesdropping': eavesdropping.get(),
        'calib_error_percentage': calib_error_percentage.get(),
        'eve_percent_reproduce': eve_percent_reproduce.get(),
        'eve_percent_section': eve_percent_section.get(),
        'allowed_wrong_bits': allowed_wrong_bits.get()
    }
    
    # COMPLETELY CLEAR THE PREVIOUS SCREEN
    for widget in root.winfo_children():
        widget.destroy()
    
    # Reset root configuration
    root.attributes('-fullscreen', True)  
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.configure(bg=BACKGROUND_COLOR)

    # Create a container frame for scrolling
    container = tk.Frame(root, bg=BACKGROUND_COLOR)
    container.pack(expand=True, fill="both", padx=10, pady=10)

    # Create a canvas for the scrolling content
    canvas = tk.Canvas(container, bg=BACKGROUND_COLOR)
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
    scrollable_frame = tk.Frame(canvas, bg=BACKGROUND_COLOR)

    # Add the scrollable frame to the canvas
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Update the scrollregion dynamically based on the frame's size
    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(canvas_window, width=scrollable_frame.winfo_reqwidth())

    scrollable_frame.bind("<Configure>", update_scroll_region)

    # Enable mouse wheel scrolling (vertical and horizontal)
    def on_mouse_wheel(event):
        if event.state & 1:  # Shift key pressed for horizontal scrolling
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # CREATE CENTERED LOADING SCREEN
    # Create a main container that fills the entire screen
    loading_container = tk.Frame(root, bg="#F5F5F5")
    loading_container.place(x=0, y=0, relwidth=1, relheight=1)  # Fill entire screen
    
    # Create centered loading frame
    loading_frame = tk.Frame(loading_container, bg="#FFFFFF", relief="ridge", bd=2)
    loading_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center in screen
    
    # Add padding inside the loading frame
    loading_content = tk.Frame(loading_frame, bg="#FFFFFF")
    loading_content.pack(padx=60, pady=40)

    # Loading title
    loading_title = tk.Label(loading_content, text="Generating Quantum Key Distribution...", 
                           font=("Segoe UI", 24, "bold"), fg="#2E86AB", bg="#FFFFFF")
    loading_title.pack(pady=(0, 20))

    # Loading spinner/progress
    loading_label = tk.Label(loading_content, text="⟳ Processing", 
                           font=("Segoe UI", 18), fg="#666666", bg="#FFFFFF")
    loading_label.pack(pady=10)

    # Progress text
    progress_text = tk.Label(loading_content, text="Starting C program...", 
                           font=("Segoe UI", 14), fg="#888888", bg="#FFFFFF")
    progress_text.pack(pady=10)

    # Progress bar with custom styling
    style = ttk.Style()
    style.configure("Custom.Horizontal.TProgressbar", 
                troughcolor="#E0E0E0", 
                background="#2E86AB", 
                borderwidth=0,
                thickness=10)  # This controls the height
    
    progress_bar = ttk.Progressbar(loading_content, mode='indeterminate', 
                                 length=400,
                                 style="Custom.Horizontal.TProgressbar")
    progress_bar.pack(pady=20)
    progress_bar.start(15)  # Start the animation

    # Force GUI update
    root.update()
    
    def run_c_program():
        try:
            # Start timing the entire process
            start_time = time.time()
            # Update progress
            progress_text.config(text="Preparing arguments...")
            root.update()
            
            # Run the C program and capture its output - USE SAVED VALUES
            args = [
                r"C:\Users\nicol\Documents\QKD_project\main.exe",
                "-k" + saved_values['key_size'],
                "-ps" + saved_values['key_part_size'],
                "-ee" + saved_values['calib_error_percentage'].strip('%'),
                "-ep" + saved_values['eve_percent_reproduce'].strip('%'),
                "-es" + saved_values['eve_percent_section'].strip('%'),
                "-a" + saved_values['allowed_wrong_bits'],
                "-e" + ("1" if saved_values['eavesdropping'] == "Enable" else "0")
            ]
            
            # Update progress
            progress_text.config(text="Running QKD simulation...")
            loading_label.config(text="⟳ Generating quantum keys...")
            root.update()
            
            process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            output, error = process.communicate()
            # Calculate total time taken
            end_time = time.time()
            total_time = end_time - start_time
            if process.returncode != 0:
                # Stop progress bar and hide loading screen
                progress_bar.stop()
                loading_container.destroy()
                
                error_label = tk.Label(scrollable_frame, text=f"Error: {error}", fg="red", font=("Segoe UI", 20))
                error_label.pack(pady=10)
                return

            # Update progress - processing output
            progress_text.config(text="Processing results...")
            loading_label.config(text="⟳ Parsing output...")
            root.update()
            
            # Print lines to console
            for line in output.splitlines():
                print(line)
            
            # Update progress - building display
            progress_text.config(text="Building display...")
            loading_label.config(text="⟳ Creating visualization...")
            root.update()
            
            # Parse the output
            parsed_data = parse_c_output(output)
            
            # Replace the time in the output with our measured time

            if "Summary of Key Generation Statistics" in parsed_data:
                summary_lines = parsed_data["Summary of Key Generation Statistics"]
                for i, line in enumerate(summary_lines):
                    if "Time Taken to Generate the Key" in line:
                        summary_lines[i] = f"Time Taken to Generate the Key  : {total_time:.3f} seconds"
                        break
            # *** DELAY DISPLAY UNTIL EVERYTHING IS READY ***
            # Create all the content in a hidden frame first
            temp_frame = tk.Frame(scrollable_frame, bg=BACKGROUND_COLOR)
            display_sections(parsed_data, temp_frame, saved_values)  # Pass saved values
            
            # Force layout calculation
            temp_frame.update_idletasks()
            
            # Update progress one final time
            progress_text.config(text="Finalizing...")
            root.update()
            
            # Small delay to show "Finalizing" message
            root.after(500, lambda: finalize_display(loading_container, progress_bar, temp_frame))

        except Exception as e:
            # Stop progress bar and hide loading screen
            progress_bar.stop()
            loading_container.destroy()
            error_label = tk.Label(scrollable_frame, text=f"Error: {e}", fg="red", font=("Segoe UI", 20))
            error_label.pack(pady=10)

    def finalize_display(loading_container, progress_bar, temp_frame):
        """Show the final content and hide loading screen"""
        # Stop progress bar and hide loading screen
        progress_bar.stop()
        loading_container.destroy()
        
        # Now show the actual content
        temp_frame.pack(fill="both", expand=True)
        
        # Update scroll region
        scrollable_frame.update_idletasks()

    # Start the thread
    threading.Thread(target=run_c_program, daemon=True).start()

def parse_c_output(output):
    sections = {}
    current_section = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("=" * 20) or line.startswith("-" * 20):
            continue
        elif not line:
            continue
        elif line.startswith("Section #") or line.startswith("Regenerating Section") or line.startswith("Final Key")  or line.startswith("Key Bit Errors Report") or line.startswith("Summary"):
            current_section = line
            sections[current_section] = []
        else:
            if current_section is None:
                current_section = "General"
                sections[current_section] = []
            sections[current_section].append(line)
    return sections

def display_sections(parsed_data, parent_frame, saved_values=None):
    count = 0 
    
    # Define modern colors for special symbols
    colors = {
        "↔": "#3B82F6",  # Modern blue
        "↕": "#10B981",  # Modern green
        "↗": "#F59E0B",  # Modern orange
        "↘": "#EF4444",  # Modern red
        "+": "#06B6D4",  # Modern cyan
        "x": "#EC4899",  # Modern pink
        "✗": "#EF4444",  # Modern red
        "✓": "#10B981",  # Modern green
        "0": "#F3F4F6",  # Light gray
        "1": "#E5E7EB",  # Slightly darker gray
        "2": "#D1D5DB",
        "3": "#9CA3AF",
        "4": "#6B7280",
        "5": "#4B5563",
        "6": "#374151",
        "7": "#1F2937",
        "8": "#111827",
        "9": "#030712",
        "-": "#F9FAFB",  # Very light gray
        "*": "#8B5CF6",  # Purple
        "@": "#A855F7",  # Different purple
        "⬤": "#6366F1"   # Indigo
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
        "*": "⬤",
        "@": "⬤"
    }

    # Create main container with modern styling
    main_container = tk.Frame(parent_frame, bg="#FFFFFF", relief="flat", bd=0)
    main_container.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
    
    # Configuration Details Section
    config_card = tk.Frame(main_container, bg="#FFFFFF", relief="solid", bd=1, highlightbackground="#E5E7EB")
    config_card.pack(fill="x", pady=(0, 20))
    
    # Card header
    config_header = tk.Frame(config_card, bg="#F8FAFC", height=50)
    config_header.pack(fill="x")
    config_header.pack_propagate(False)
    
    title_label = tk.Label(config_header, text="⚙️ Configuration Details", 
                          font=("Segoe UI", 14, "bold"), 
                          fg="#1F2937", bg="#F8FAFC")
    title_label.pack(side="left", padx=15, pady=15)

    # Card content
    config_content = tk.Frame(config_card, bg="#FFFFFF")
    config_content.pack(fill="x", padx=20, pady=15)

    # Extract values from the saved values
    if saved_values:
        data = {
            "Key Size": f"{saved_values['key_size']} bits",
            "Key Part Size": f"{saved_values['key_part_size']} bits", 
            "Number of Key Parts": f"{int(saved_values['key_size']) // int(saved_values['key_part_size'])}",
            "Eavesdropping": f"{saved_values['eavesdropping']}",
            "Calibration Error Percentage": f"{saved_values['calib_error_percentage']}",
            "Eve Error Percentage": f"{saved_values['eve_percent_reproduce']}",
            "Eve Section Eavesdropping": f"{saved_values['eve_percent_section']}",
            "Allowed Wrong Bits": f"{saved_values['allowed_wrong_bits']} bits",
        }
    else:
        # Fallback data if no saved values
        data = {
            "Key Size": "N/A",
            "Key Part Size": "N/A", 
            "Number of Key Parts": "N/A",
            "Eavesdropping": "N/A",
            "Calibration Error Percentage": "N/A",
            "Eve Error Percentage": "N/A",
            "Eve Section Eavesdropping": "N/A",
            "Allowed Wrong Bits": "N/A",
        }
    # Create grid for configuration data
    for i, (key, value) in enumerate(data.items()):
        row_frame = tk.Frame(config_content, bg=CARD_COLOR)
        row_frame.pack(fill="x", pady=3)
        
        key_label = tk.Label(row_frame, text=key + ":", 
                           font=("Segoe UI", 10, "bold"), 
                           fg="#4B5563", bg="#ffffff",
                           width=25, anchor="w")  # Fixed width to align values
        key_label.pack(side="left")
        
        value_label = tk.Label(row_frame, text=value, 
                             font=("Segoe UI", 10), 
                             fg="#1F2937", bg="#FFFFFF")
        value_label.pack(side="left")

    # Legend Section
    legend_card = tk.Frame(main_container, bg="#FFFFFF", relief="solid", bd=1, highlightbackground="#E5E7EB")
    legend_card.pack(fill="x", pady=(0, 20))
    
    # Legend header
    legend_header = tk.Frame(legend_card, bg="#F8FAFC", height=50)
    legend_header.pack(fill="x")
    legend_header.pack_propagate(False)
    
    legend_title = tk.Label(legend_header, text="🔍 Symbol Legend", 
                           font=("Segoe UI", 14, "bold"), 
                           fg="#1F2937", bg="#F8FAFC")
    legend_title.pack(side="left", padx=15, pady=15)

    # Legend content with sections
    legend_content = tk.Frame(legend_card, bg="#FFFFFF")
    legend_content.pack(fill="x", padx=20, pady=15)

    # Basis Symbols
    basis_frame = tk.Frame(legend_content, bg="#FFFFFF")
    basis_frame.pack(fill="x", pady=(0, 15))
    
    basis_title = tk.Label(basis_frame, text="Basis Symbols", 
                          font=("Segoe UI", 11, "bold"), 
                          fg="#374151", bg="#FFFFFF")
    basis_title.pack(anchor="w")
    
    basis_symbols = tk.Frame(basis_frame, bg="#FFFFFF")
    basis_symbols.pack(fill="x", pady=(5, 0))
    
    basis_content = {"+": "Rectilinear Basis", "x": "Diagonal Basis"}
    
    for symbol, description in basis_content.items():
        symbol_frame = tk.Frame(basis_symbols, bg="#FFFFFF")
        symbol_frame.pack(side="left", padx=(0, 20))
        
        visual = symbol_mapping.get(symbol, symbol)
        bg_color = colors.get(visual, "#ffffff")
        
        symbol_label = tk.Label(symbol_frame, text=visual, 
                               bg=bg_color, fg="white" if bg_color in ["#EC4899", "#3B82F6", "#10B981"] else "#1F2937",
                               font=("Segoe UI", 12, "bold"), 
                               width=3, height=1, relief="flat")
        symbol_label.pack(side="left", padx=(0, 8))
        
        desc_label = tk.Label(symbol_frame, text=description, 
                            font=("Segoe UI", 10), 
                            fg="#6B7280", bg="#FFFFFF")
        desc_label.pack(side="left")

    # Filter Symbols
    filter_frame = tk.Frame(legend_content, bg="#FFFFFF")
    filter_frame.pack(fill="x", pady=(0, 15))
    
    filter_title = tk.Label(filter_frame, text="Filter Symbols", 
                           font=("Segoe UI", 11, "bold"), 
                           fg="#374151", bg="#FFFFFF")
    filter_title.pack(anchor="w")
    
    # Bit 0 symbols
    bit0_frame = tk.Frame(filter_frame, bg="#FFFFFF")
    bit0_frame.pack(fill="x", pady=(5, 5))
    
    bit0_label = tk.Label(bit0_frame, text="(bit = 0):", 
                         font=("Segoe UI", 10, "italic"), 
                         fg="#6B7280", bg="#FFFFFF")
    bit0_label.pack(side="left", padx=(0, 10))
    
    filter_content = {
        "d": "Diagonal (45°)", "v": "Vertical",
        "h": "Horizontal      ", "b": "Diagonal (-45°)"
    }
    
    for i, (symbol, description) in enumerate(filter_content.items()):
        if i == 2:  # After first 2 symbols, create bit=1 section
            bit1_frame = tk.Frame(filter_frame, bg="#FFFFFF") 
            bit1_frame.pack(fill="x", pady=(5, 0))
            
            bit1_label = tk.Label(bit1_frame, text="(bit = 1):", 
                                 font=("Segoe UI", 10, "italic"), 
                                 fg="#6B7280", bg="#FFFFFF")
            bit1_label.pack(side="left", padx=(0, 10))
            current_frame = bit1_frame
        else:
            current_frame = bit0_frame if i < 2 else bit1_frame
            
        symbol_container = tk.Frame(current_frame, bg="#FFFFFF")
        symbol_container.pack(side="left", padx=(0, 15))
        
        visual = symbol_mapping.get(symbol, symbol)
        bg_color = colors.get(visual, "#ffffff")
        
        symbol_label = tk.Label(symbol_container, text=visual, 
                               bg=bg_color, fg="white" if bg_color in ["#F59E0B", "#EF4444", "#10B981", "#3B82F6"] else "#1F2937",
                               font=("Segoe UI", 12, "bold"), 
                               width=3, height=1, relief="flat")
        symbol_label.pack(side="left", padx=(0, 8))
        
        desc_label = tk.Label(symbol_container, text=description, 
                            font=("Segoe UI", 10), 
                            fg="#6B7280", bg="#FFFFFF")
        desc_label.pack(side="left")

    # Measurement Symbols
    measurement_frame = tk.Frame(legend_content, bg="#FFFFFF")
    measurement_frame.pack(fill="x")
    
    measurement_title = tk.Label(measurement_frame, text="Measurement Symbols", 
                                font=("Segoe UI", 11, "bold"), 
                                fg="#374151", bg="#FFFFFF")
    measurement_title.pack(anchor="w")
    
    measurement_symbols = tk.Frame(measurement_frame, bg="#FFFFFF")
    measurement_symbols.pack(fill="x", pady=(5, 0))
    
    measurement_content = {"V": "Correct Measurement", "X": "Wrong Measurement"}
    
    for symbol, description in measurement_content.items():
        symbol_frame = tk.Frame(measurement_symbols, bg="#FFFFFF")
        symbol_frame.pack(side="left", padx=(0, 20))
        
        visual = symbol_mapping.get(symbol, symbol)
        bg_color = colors.get(visual, "#ffffff")
        
        symbol_label = tk.Label(symbol_frame, text=visual, 
                               bg=bg_color, fg="white",
                               font=("Segoe UI", 12, "bold"), 
                               width=3, height=1, relief="flat")
        symbol_label.pack(side="left", padx=(0, 8))
        
        desc_label = tk.Label(symbol_frame, text=description, 
                            font=("Segoe UI", 10), 
                            fg="#6B7280", bg="#FFFFFF")
        desc_label.pack(side="left")

    # Data Sections
    sections_container = tk.Frame(main_container, bg="#FFFFFF")
    sections_container.pack(fill="both", expand=True, pady=(0, 20))

    current_row = 0
    
    for section, content in parsed_data.items():
        if count < 20:
            # Section card
            section_card = tk.Frame(sections_container, bg="#FFFFFF", relief="solid", bd=1, highlightbackground="#E5E7EB")
            section_card.pack(fill="x", pady=(0, 15))
            
            # Section header
            section_header = tk.Frame(section_card, bg="#F1F5F9", height=45)
            section_header.pack(fill="x")
            section_header.pack_propagate(False)
            
            section_label = tk.Label(section_header, text=section, 
                                   font=("Segoe UI", 12, "bold"), 
                                   fg="#1E293B", bg="#F1F5F9")
            section_label.pack(side="left", padx=15, pady=12)

            # Section content
            section_content = tk.Frame(section_card, bg="#FFFFFF")
            section_content.pack(fill="x", padx=15, pady=15)

            # Display the content with appropriate colors
            for line in content:
                if ":" in line:  # Handle rows with keys and values
                    key, value = map(str.strip, line.split(":", 1))
                    
                    line_frame = tk.Frame(section_content, bg="#FFFFFF")
                    line_frame.pack(fill="x", pady=2)
                    
                    key_label = tk.Label(line_frame, text=key + ":", 
                                       font=("Segoe UI", 10, "bold"), 
                                       fg="#4B5563", bg="#FFFFFF",
                                       width=25, anchor="e")
                    key_label.pack(side="left", padx=(0, 10))

                    # Character display frame
                    chars_frame = tk.Frame(line_frame, bg="#FFFFFF")
                    chars_frame.pack(side="left")

                    # Display the value with colored characters
                    for col, char in enumerate(value):
                        display_char = symbol_mapping.get(char, char)
                        bg_color = colors.get(display_char, "#ffffff")
                        text_color = "white" if bg_color in ["#EC4899", "#3B82F6", "#10B981", "#EF4444", "#F59E0B", "#8B5CF6"] else "#1F2937"
                        
                        char_label = tk.Label(chars_frame, text=display_char, 
                                            bg=bg_color, fg=text_color,
                                            font=("Segoe UI", 9, "bold"), 
                                            width=2, height=1, relief="flat",
                                            padx=1, pady=1)
                        char_label.pack(side="left", padx=1)

                else:  # Handle rows with raw data
                    line_frame = tk.Frame(section_content, bg="#FFFFFF")
                    line_frame.pack(fill="x", pady=2)
                    
                    for col, char in enumerate(line):
                        display_char = symbol_mapping.get(char, char)
                        bg_color = colors.get(display_char, "#ffffff")
                        text_color = "white" if bg_color in ["#EC4899", "#3B82F6", "#10B981", "#EF4444", "#F59E0B", "#8B5CF6"] else "#1F2937"
                        
                        char_label = tk.Label(line_frame, text=display_char, 
                                            bg=bg_color, fg=text_color,
                                            font=("Segoe UI", 9, "bold"), 
                                            width=2, height=1, relief="flat",
                                            padx=1, pady=1)
                        char_label.pack(side="left", padx=1)
        
        # Handle Final Key section specially
        elif "Final Key (" in section:
            final_card = tk.Frame(sections_container, bg="#FFFFFF", relief="solid", bd=1, highlightbackground="#10B981")
            final_card.pack(fill="x", pady=(0, 15))
            
            final_header = tk.Frame(final_card, bg="#ECFDF5", height=45)
            final_header.pack(fill="x")
            final_header.pack_propagate(False)
            
            final_label = tk.Label(final_header, text=f"🔑 {section}", 
                                 font=("Segoe UI", 12, "bold"), 
                                 fg="#065F46", bg="#ECFDF5")
            final_label.pack(side="left", padx=15, pady=12)
            
            final_content = tk.Frame(final_card, bg="#FFFFFF")
            final_content.pack(fill="x", padx=15, pady=15)
            
            for line in content:
                line_frame = tk.Frame(final_content, bg="#FFFFFF")
                line_frame.pack(fill="x", pady=2)
                
                for col, char in enumerate(line):
                    display_char = symbol_mapping.get(char, char)
                    bg_color = colors.get(display_char, "#ffffff")
                    text_color = "#1F2937"
                    
                    char_label = tk.Label(line_frame, text=display_char, 
                                        bg=bg_color, fg=text_color,
                                        font=("Consolas", 10, "bold"), 
                                        width=2, height=1, relief="flat",
                                        padx=1, pady=1)
                    char_label.pack(side="left", padx=1)

        # Handle Summary section as regular text
        elif "Summary of Key Generation" in section:
            summary_card = tk.Frame(sections_container, bg="#FFFFFF", relief="solid", bd=1, highlightbackground="#3B82F6")
            summary_card.pack(fill="x", pady=(0, 15))
            
            summary_header = tk.Frame(summary_card, bg="#EFF6FF", height=45)
            summary_header.pack(fill="x")
            summary_header.pack_propagate(False)
            
            summary_label = tk.Label(summary_header, text=f"📊 {section}", 
                                   font=("Segoe UI", 12, "bold"), 
                                   fg="#1E40AF", bg="#EFF6FF")
            summary_label.pack(side="left", padx=15, pady=12)
            
            summary_content = tk.Frame(summary_card, bg="#FFFFFF")
            summary_content.pack(fill="x", padx=15, pady=15)
            
            for line in content:
                line_label = tk.Label(summary_content, text=line, 
                                    font=("Consolas", 11), 
                                    fg="#1F2937", bg="#FFFFFF",
                                    anchor="w")
                line_label.pack(fill="x", pady=2)
        
        count += 1
        

# GUI Setup
root = tk.Tk()
root.title("QKD - Quantum Key Distribution")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
root.configure(bg=BACKGROUND_COLOR)

# Create a main container with background
main_container = tk.Frame(root, bg=BACKGROUND_COLOR)
main_container.pack(expand=True, fill="both")

# Create an initial frame to hold all the initial widgets
initial_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
initial_frame.pack(expand=True, fill="both")

# Create main horizontal layout container
horizontal_container = tk.Frame(initial_frame, bg=BACKGROUND_COLOR)
horizontal_container.pack(expand=True, fill="both", padx=40, pady=50)

# LEFT SIDE - Title, Image, Description
left_side = tk.Frame(horizontal_container, bg=BACKGROUND_COLOR, width=700)
left_side.pack(side="left", fill="y", padx=(0, 30))
left_side.pack_propagate(False)

# Title section - more compact
title_frame = tk.Frame(left_side, bg=BACKGROUND_COLOR)
title_frame.pack(pady=(0, 10))

# Main title
title = tk.Label(title_frame, text="QKD", 
                font=("Segoe UI", 40, "bold"), 
                fg=PRIMARY_COLOR, bg=BACKGROUND_COLOR)
title.pack()

subtitle_main = tk.Label(title_frame, text="Quantum Key Distribution", 
                        font=("Segoe UI", 24, "normal"), 
                        fg=TEXT_COLOR, bg=BACKGROUND_COLOR)
subtitle_main.pack()

# Authors - smaller
subtitle = tk.Label(title_frame, text="A project by Nicole Frumkin & Keren Koifman", 
                   font=("Segoe UI", 14, "italic"), 
                   fg=SECONDARY_COLOR, bg=BACKGROUND_COLOR)
subtitle.pack(pady=(5, 0))

# Image section - smaller and to the side
image_frame = tk.Frame(left_side, bg=BACKGROUND_COLOR)
image_frame.pack(pady=15)

try:
    image = Image.open("images/first_image.jpg")
    image = image.resize((500,341), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    
    # Create border frame for image
    img_border = tk.Frame(image_frame, bg=PRIMARY_COLOR, relief="solid", bd=2)
    img_border.pack()
    
    img_label = tk.Label(img_border, image=photo, bg=CARD_COLOR)
    img_label.pack(padx=2, pady=2)
except:
    # Fallback if image not found
    img_placeholder = tk.Label(image_frame, text="🔐 Quantum Security", 
                              font=("Segoe UI", 18), 
                              fg=PRIMARY_COLOR, bg=BACKGROUND_COLOR)
    img_placeholder.pack(pady=15)

# Description - more compact
description_frame = tk.Frame(left_side, bg=BACKGROUND_COLOR)
description_frame.pack(pady=15)

description = tk.Label(description_frame, 
                      text="Welcome to the Quantum Key Distribution Simulator!\n\n" +
                           "You are Alice, trying to securely share an encryption key with Bob\n" +
                           "using quantum mechanics principles.",
                      font=("Segoe UI", 14), 
                      fg=TEXT_COLOR, bg=BACKGROUND_COLOR,
                      justify="center")
description.pack()

# RIGHT SIDE - Parameters in a compact card
right_side = tk.Frame(horizontal_container, bg=BACKGROUND_COLOR)
right_side.pack(side="left", fill="both", expand=True)

# Create a compact card for parameters
params_card = tk.Frame(right_side, bg=CARD_COLOR, relief="raised", bd=2)
params_card.pack(fill="both", expand=True, pady=20)

# Add shadow effect
params_shadow = tk.Frame(right_side, bg="#E0E0E0", relief="flat", bd=0)
params_shadow.place(in_=params_card, x=4, y=4, relwidth=1, relheight=1)
params_card.lift()

# Content inside the parameters card
params_content = tk.Frame(params_card, bg=CARD_COLOR)
params_content.pack(expand=True, fill="both", padx=30, pady=10)

# Parameters title
params_title = tk.Label(params_content, text="⚙️ Simulation Parameters", 
                       font=("Segoe UI", 20, "bold"), 
                       fg=PRIMARY_COLOR, bg=CARD_COLOR)
params_title.pack(pady=(100, 20))

# Create a more compact grid for parameters - 2 columns instead of 3
params_grid = tk.Frame(params_content, bg=CARD_COLOR)
params_grid.pack(expand=True)

# Dropdown creation function with more compact styling
def create_compact_dropdown(label_text, options, default, parent, row, column):
    # Create container frame
    container = tk.Frame(parent, bg=CARD_COLOR)
    container.grid(row=row, column=column, padx=20, pady=10, sticky="ew")
    
    # Label
    label = tk.Label(container, text=label_text, 
                    font=("Segoe UI", 14, "bold"), 
                    fg=TEXT_COLOR, bg=CARD_COLOR)
    label.pack(anchor="w")
    
    # Style the combobox
    style = ttk.Style()
    style.configure("Compact.TCombobox",
                   fieldbackground=BACKGROUND_COLOR,
                   background=CARD_COLOR,
                   foreground=TEXT_COLOR,
                   borderwidth=2,
                   relief="solid")
    
    dropdown = ttk.Combobox(container, values=options, state="readonly", 
                           width=18, font=("Segoe UI", 12),
                           style="Compact.TCombobox")
    dropdown.set(default)
    dropdown.pack(anchor="w", pady=(3, 0))
    
    return dropdown

# Configure grid weights for 2 columns
for i in range(2):
    params_grid.grid_columnconfigure(i, weight=1)

# Create dropdowns in a 2-column layout
key_size = create_compact_dropdown("Key Size (bits)", ["1024", "2048", "4096"], "1024", params_grid, 0, 0)
key_part_size = create_compact_dropdown("Key Part Size (bits)", ["32", "64", "128"], "32", params_grid, 0, 1)

eavesdropping = create_compact_dropdown("Eavesdropping", ["Enable", "Disable"], "Enable", params_grid, 1, 0)
calib_error_percentage = create_compact_dropdown("Calibration Error %", ["1%", "5%", "10%"], "1%", params_grid, 1, 1)

eve_percent_reproduce = create_compact_dropdown("Eve Listening %", ["10%", "25%", "50%"], "10%", params_grid, 2, 0)
eve_percent_section = create_compact_dropdown("Eve Sections %", ["10%", "25%", "50%"], "25%", params_grid, 2, 1)

allowed_wrong_bits = create_compact_dropdown("Allowed Wrong Bits", ["0", "1", "2", "5"], "1", params_grid, 3, 0)

# Add some spacing
spacer = tk.Frame(params_grid, bg=CARD_COLOR, height=15)
spacer.grid(row=4, column=0, columnspan=2)

# Submit button - centered below parameters
button_frame = tk.Frame(params_content, bg=CARD_COLOR)
button_frame.pack(pady=20)

# Create a gradient-like effect with multiple frames
button_shadow = tk.Frame(button_frame, bg="#1a5f7a", relief="flat")
button_shadow.pack()

submit_button = tk.Button(button_shadow, text="🚀 Start Quantum Simulation", 
                         command=on_submit,
                         font=("Segoe UI", 12, "bold"),
                         fg="white",
                         bg=PRIMARY_COLOR,
                         activebackground=SECONDARY_COLOR,
                         activeforeground="white",
                         relief="flat",
                         bd=0,
                         padx=25,
                         pady=10,
                         cursor="hand2")
submit_button.pack()

# Add hover effects
def on_enter(e):
    submit_button.config(bg=SECONDARY_COLOR)

def on_leave(e):
    submit_button.config(bg=PRIMARY_COLOR)

submit_button.bind("<Enter>", on_enter)
submit_button.bind("<Leave>", on_leave)

# Footer at the bottom
footer_frame = tk.Frame(initial_frame, bg=BACKGROUND_COLOR)
footer_frame.pack(side="bottom", fill="x", pady=10)

footer_text = tk.Label(footer_frame, 
                      text="Press ESC to exit fullscreen • Built with Python & Tkinter",
                      font=("Segoe UI", 9), 
                      fg="#888888", bg=BACKGROUND_COLOR)
footer_text.pack()

root.mainloop()