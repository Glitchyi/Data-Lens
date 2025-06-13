# Advaithum-Pillerum_thinknite

## Team Members:
- Nikhil Joshi (nikhiljoshi@ibm.com)
- Ivine Joju (Ivine@ibm.com)
- Advaith Narayanan (advaithnarayanan@ibm.com)
- Adrin Jose CT (adrinjosect@ibm.com)
- Aanand Deva Suresh (aanand.deva@ibm.com)

## Project Overview

This project is a comprehensive data processing solution that combines file conversion, AI-powered analysis, and cloud storage capabilities. The system converts CSV/JSON files to efficient Parquet format and generates intelligent metadata using Groq LLM.

## Architecture

### 📁 Project Structure
```
├── data/                          # Sample data files
│   ├── AirlineSatisfactionSurvey1.csv
│   └── dummy_marksheet.csv
├── server/                        # Main application server
│   ├── server.py                  # Flask web application
│   ├── requirements.txt           # Python dependencies
│   ├── setup.sh                   # Automated setup script
│   ├── start.sh                   # Server start script
│   ├── test_integration.py        # Integration tests
│   ├── .env.example              # Environment configuration template
│   ├── templates/
│   │   └── index.html            # Web interface
│   └── utils/                     # Data processing modules
│       ├── __init__.py           # Package initialization
│       ├── enrich.py             # Data analysis engine
│       └── summarizer.py         # AI summarization module
└── README.md                      # This file
```

### 🔧 Core Components

#### Data Processing Engine (`utils/`)
- **enrich.py**: Advanced data analysis and column profiling
  - Automatic data type detection
  - Statistical analysis for numerical columns
  - Semantic type inference
  - Sample data extraction

- **summarizer.py**: AI-powered metadata generation
  - Groq LLM integration for intelligent descriptions
  - Parquet file processing from MinIO storage
  - README generation in markdown format
  - Metadata file management

#### Web Application (`server.py`)
- **File Upload & Conversion**: Drag & drop interface for CSV/JSON to Parquet conversion
- **MinIO Integration**: Secure cloud storage for processed files
- **AI Analysis**: On-demand metadata generation for parquet files
- **File Management**: Browse, download, and analyze stored files

## Features

### 🚀 Data Conversion
- Convert CSV and JSON files to efficient Parquet format
- Automatic file upload and processing
- Real-time progress feedback
- Secure cloud storage with MinIO

### 🤖 AI-Powered Analysis
- Generate comprehensive dataset descriptions using Groq LLM
- Automatic field analysis and semantic type detection
- Create detailed README files with statistics and samples
- Export metadata in markdown format

### 📊 Data Management
- Browse all stored files with rich metadata
- Download original and processed files
- View generated analysis reports
- Integrated file management interface

## Quick Start

### 1. Setup
```bash
cd server/
./setup.sh
```

### 2. Configuration
Edit `.env` file with your settings:
```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
```

### 3. Run
```bash
./start.sh
```

### 4. Access
Open http://localhost:5000 in your browser

## Usage Workflow

1. **Upload Data**: Drag & drop CSV/JSON files for automatic Parquet conversion
2. **Analyze Files**: Select Parquet files for AI-powered metadata generation
3. **View Results**: Browse comprehensive analysis reports and download files

## Technical Stack

- **Backend**: Flask, Python 3.8+
- **Data Processing**: pandas, pyarrow
- **AI/ML**: Groq LLM API
- **Storage**: MinIO object storage
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **File Formats**: CSV, JSON input → Parquet output

## API Endpoints

- `POST /convert-to-parquet` - File conversion
- `POST /process-parquet/<filename>` - AI analysis
- `GET /list-files` - File management
- `GET /get-metadata/<filename>` - Metadata retrieval
- `GET /download/<filename>` - File download

## Development

### Testing
```bash
python test_integration.py
```

### Debug Mode
```bash
export FLASK_DEBUG=1
python server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

---

**Advaithum Pillerum** - Advanced Data Processing Solutions
