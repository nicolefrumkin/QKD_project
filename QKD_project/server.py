from flask import Flask, request, render_template, url_for
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve the form data
    key_size = request.form.get('key_size')
    key_part_size = request.form.get('key_part_size')
    eavesdropping = request.form.get('eavesdropping')
    calib_error_percentage = request.form.get('calib_error_percentage')
    eve_error_percentage = request.form.get('eve_error_percentage')
    eve_percent_section = request.form.get('eve_percent_section')
    allowed_wrong_bits = request.form.get('allowed_wrong_bits')

    # Define the data as a dictionary to save in an Excel row
    form_data = {
        "Key Size": key_size,
        "Key Part Size": key_part_size,
        "Eavesdropping": eavesdropping,
        "Calibration Error Percentage": calib_error_percentage,
        "Eve Error Percentage": eve_error_percentage,
        "Eve Percent Section": eve_percent_section,
        "Allowed Wrong Bits": allowed_wrong_bits
    }

    # Specify the file name
    file_name = 'form_data.xlsx'

    # Check if the file exists, if so, append to it; otherwise, create a new file
    if os.path.exists(file_name):
        # Append data to the existing Excel file
        df = pd.read_excel(file_name)
        df = df.append(form_data, ignore_index=True)
        df.to_excel(file_name, index=False)
    else:
        # Create a new Excel file and write the data
        df = pd.DataFrame([form_data])
        df.to_excel(file_name, index=False)

    # Render the result.html template with the form data
    return render_template(
        'result.html',
        key_size=key_size,
        key_part_size=key_part_size,
        eavesdropping=eavesdropping,
        calib_error_percentage=calib_error_percentage,
        eve_error_percentage=eve_error_percentage,
        eve_percent_section=eve_percent_section,
        allowed_wrong_bits=allowed_wrong_bits
    )

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
