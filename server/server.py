from flask import Flask, jsonify, render_template, request
import os
import pandas as pd
from werkzeug.utils import secure_filename
from minio import Minio
from minio.error import S3Error
import io
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '.'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
ALLOWED_EXTENSIONS = {'csv', 'json'}

# MinIO Configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '9.38.73.29:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'ROOTUSER')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'CHANGEME123')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'parquet-files')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'False').lower() == 'true'

# Initialize MinIO client
try:
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )
    
    # Create bucket if it doesn't exist
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        minio_client.make_bucket(MINIO_BUCKET_NAME)
        print(f"Created bucket: {MINIO_BUCKET_NAME}")
    else:
        print(f"Bucket {MINIO_BUCKET_NAME} already exists")
        
except Exception as e:
    print(f"Failed to initialize MinIO client: {e}")
    minio_client = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_parquet(file_content, filename, file_extension):
    """Convert CSV or JSON file content to Parquet format and upload to MinIO"""
    # Create a temporary file to process the data
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=f'.{file_extension}') as temp_file:
        temp_file.write(file_content)
        temp_filepath = temp_file.name
    
    try:
        # Read the file based on extension
        if file_extension == 'csv':
            dataFrame = pd.read_csv(temp_filepath)
        elif file_extension == 'json':
            dataFrame = pd.read_json(temp_filepath, orient="records", lines=True)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        # Convert to Parquet in memory
        parquet_buffer = io.BytesIO()
        dataFrame.to_parquet(parquet_buffer, index=False)
        parquet_data = parquet_buffer.getvalue()
        
        # Generate Parquet filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = os.path.splitext(filename)[0]
        parquet_filename = f"{original_name}_{timestamp}.parquet"
        
        # Upload to MinIO
        if minio_client:
            parquet_buffer_for_upload = io.BytesIO(parquet_data)
            minio_client.put_object(
                MINIO_BUCKET_NAME,
                parquet_filename,
                parquet_buffer_for_upload,
                length=len(parquet_data),
                content_type='application/octet-stream'
            )
            
            return parquet_filename, len(dataFrame), len(parquet_data)
        else:
            raise Exception("MinIO client not initialized")
            
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

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
        
        if not minio_client:
            return jsonify({'error': 'MinIO storage not available'}), 500
        
        # Get filename and extension
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Read file content
        file_content = file.read()
        
        # Convert to Parquet and upload to MinIO
        parquet_filename, rows_converted, file_size = convert_to_parquet(file_content, filename, file_extension)
        
        # Generate MinIO URL for the uploaded file (optional)
        protocol = "https" if MINIO_SECURE else "http"
        minio_url = f"{protocol}://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{parquet_filename}"
        
        return jsonify({
            'message': f'{file_extension.upper()} file converted to Parquet and uploaded to MinIO successfully',
            'input_file': filename,
            'output_file': parquet_filename,
            'rows_converted': rows_converted,
            'file_size': file_size,
            'minio_bucket': MINIO_BUCKET_NAME,
            'minio_url': minio_url
        })
        
    except S3Error as e:
        return jsonify({'error': f'MinIO error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

@app.route('/list-files', methods=['GET'])
def list_minio_files():
    """List all files in the MinIO bucket"""
    try:
        if not minio_client:
            return jsonify({'error': 'MinIO storage not available'}), 500
        
        objects = minio_client.list_objects(MINIO_BUCKET_NAME)
        files = []
        
        for obj in objects:
            files.append({
                'filename': obj.object_name,
                'size': obj.size,
                'last_modified': obj.last_modified.isoformat() if obj.last_modified else None,
                'download_url': f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{obj.object_name}"
            })
        
        return jsonify({
            'bucket': MINIO_BUCKET_NAME,
            'files': files,
            'total_files': len(files)
        })
        
    except S3Error as e:
        return jsonify({'error': f'MinIO error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a file from MinIO bucket"""
    try:
        if not minio_client:
            return jsonify({'error': 'MinIO storage not available'}), 500
        
        # Get the file from MinIO
        response = minio_client.get_object(MINIO_BUCKET_NAME, filename)
        
        # Return the file content
        from flask import Response
        return Response(
            response.data,
            mimetype='application/octet-stream',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except S3Error as e:
        return jsonify({'error': f'File not found or MinIO error: {str(e)}'}), 404
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)