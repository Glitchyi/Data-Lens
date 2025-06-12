from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '.'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
ALLOWED_EXTENSIONS = {'csv', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_parquet(filepath, file_extension):
    """Convert CSV or JSON file to Parquet format"""
    if file_extension == 'csv':
        dataFrame = pd.read_csv(filepath)
    elif file_extension == 'json':
        dataFrame = pd.read_json(filepath, orient="records", lines=True)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
    
    # Generate Parquet filename
    parquet_file = os.path.splitext(filepath)[0] + ".parquet"
    
    # Convert to Parquet
    dataFrame.to_parquet(parquet_file, index=False)
    
    return parquet_file, len(dataFrame)

@app.route('/convert-to-parquet', methods=['POST'])
def convert_file_to_parquet():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV and JSON files are allowed.'}), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get file extension to determine conversion method
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Convert to Parquet
        parquet_file, rows_converted = convert_to_parquet(filepath, file_extension)
        
        # Clean up the original file (optional - remove this if you want to keep it)
        # os.remove(filepath)
        
        return jsonify({
            'message': f'{file_extension.upper()} file converted to Parquet successfully',
            'input_file': filename,
            'output_file': os.path.basename(parquet_file),
            'rows_converted': rows_converted,
            'file_size': os.path.getsize(parquet_file)
        })
        
    except Exception as e:
        # Clean up the uploaded file if conversion failed
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)