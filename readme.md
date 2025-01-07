
# Quantum Key Distribution (QKD) Simulator

This project is a **Quantum Key Distribution (QKD)** simulator built using **Python** for the GUI and **C** for the backend simulation. The system enables users to simulate a QKD process with configurable parameters, visualize the results, and analyze the key distribution.

## Overview

Quantum Key Distribution (QKD) is a secure communication method that uses quantum mechanics to encrypt and exchange encryption keys. This simulator allows you to experiment with different configurations and observe the effects of eavesdropping, calibration errors, and more.

---

## Features

- **Interactive GUI**: Built using Tkinter for parameter selection and result display.
- **Configurable Settings**:
  - Key Size
  - Key Part Size
  - Calibration Error Percentage
  - Eavesdropping Options
- **Visualization**: Displays the QKD process, including key generation, polarization, and measurement results.
- **Error Simulation**: Includes calibration errors and eavesdropping attacks.

---

## Screenshots

### GUI Interface
![GUI Interface](./images/Screenshot-2025-01-07-160617.png)

### Configuration Details and Legend
![Configuration Details and Legend](./images/Screenshot-2025-01-07-160550.png)

### Section Results
![Section Results](./images/Screenshot-2025-01-07-160539.png)

---

## How It Works

1. **Parameter Selection**: Use the GUI to set up the simulation parameters like key size, calibration error percentage, and eavesdropping.
2. **Backend Simulation**: The Python program passes the parameters to a C program (`main.c`) for the QKD simulation.
3. **Visualization**: The results are displayed in the GUI, with details like keys, measurement bases, and errors.

---

## Getting Started

### Prerequisites

- **Python 3.x**: Install Python and necessary libraries like `tkinter` and `Pillow`.
- **C Compiler**: Ensure you have a C compiler (e.g., GCC) to build the `main.c` program.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nicolefrumkin/QKD_project.git
   cd QKD_project
   ```

2. Install Python dependencies:
   ```bash
   pip install Pillow
   ```

3. Compile the C program:
   ```bash
   gcc main.c -o main.exe
   ```

---

## Usage

1. Run the Python GUI:
   ```bash
   python qkd_gui.py
   ```

2. Configure the simulation parameters using the GUI.

3. Click **Submit** to start the simulation. The results will be displayed in the GUI.
---
## Credits
- **Developers**: Nicole Frumkin & Keren Koifman
- **Languages Used**: Python, C
- **Frameworks/Libraries**: Tkinter, PIL (Pillow)
