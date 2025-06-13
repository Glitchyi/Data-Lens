import pandas as pd
from .enrich import Summarizer
import json
import getpass
import os
import tempfile
import io
from groq import Groq

import dotenv   

dotenv.load_dotenv()

class GroqLLMWrapper:
    """Wrapper class to make Groq client compatible with the Summarizer interface"""
    def __init__(self, client):
        self.client = client
    
    def invoke(self, prompts):
        """Make the Groq client compatible with the expected interface"""
        # Take the first prompt
        prompt = prompts[0] if isinstance(prompts, list) else prompts
        
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0,
                max_tokens=None,
            )
            
            # Create a response object that mimics the expected structure
            class Response:
                def __init__(self, content):
                    self.content = content
            
            return Response(completion.choices[0].message.content)
        except Exception as e:
            # Return error response
            class Response:
                def __init__(self, content):
                    self.content = content
            
            return Response(f'{{"error": "Failed to generate summary: {str(e)}"}}')

def get_groq_llm():
    """Initialize and return Groq LLM instance"""
    if "GROQ_API_KEY" not in os.environ:
        os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return GroqLLMWrapper(client)

def process_parquet_file(minio_client, bucket_name, parquet_filename):
    """
    Download parquet file from MinIO, process it, and return metadata
    """
    try:
        # Download parquet file from MinIO
        response = minio_client.get_object(bucket_name, parquet_filename)
        parquet_data = response.read()
        
        # Create temporary file to read parquet data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as temp_file:
            temp_file.write(parquet_data)
            temp_filepath = temp_file.name
        
        try:
            # Load dataset
            df = pd.read_parquet(temp_filepath)
            
            # Get LLM instance
            llm = get_groq_llm()
            
            # Get summarization
            summarizer = Summarizer()
            summary = summarizer.summarize(df, summary_method='llm', text_gen=llm, file_name=parquet_filename)
            
            # Process summary
            if isinstance(summary, str):
                if summary.startswith('"') and summary.endswith('"'):
                    summary = summary[1:-1]
                summary = summary.encode('utf-8').decode('unicode_escape')
                try:
                    data_summary = json.loads(summary)
                except json.JSONDecodeError:
                    data_summary = {"error": "Failed to parse summary", "raw_summary": summary}
            else:
                data_summary = summary
            
            # Generate README content
            readme_content = generate_readme_content(data_summary, parquet_filename, df)
            
            # Save metadata to bucket
            metadata_filename = os.path.splitext(parquet_filename)[0] + "_metadata.md"
            save_metadata_to_bucket(minio_client, bucket_name, metadata_filename, readme_content)
            
            return {
                "status": "success",
                "summary": data_summary,
                "metadata_file": metadata_filename,
                "rows": len(df),
                "columns": len(df.columns)
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
                
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def generate_readme_content(data_summary, filename, df):
    """Generate README content from data summary"""
    
    readme_content = f"""# Dataset Metadata: {filename}

## Overview
- **Dataset Name**: {data_summary.get('name', filename)}
- **Description**: {data_summary.get('dataset_description', 'No description available')}
- **Rows**: {len(df)}
- **Columns**: {len(df.columns)}

## Data Fields

"""
    
    fields = data_summary.get('fields', [])
    for field in fields:
        column_name = field.get('column', 'Unknown')
        properties = field.get('properties', {})
        
        readme_content += f"### {column_name}\n"
        readme_content += f"- **Data Type**: {properties.get('dtype', 'Unknown')}\n"
        readme_content += f"- **Semantic Type**: {properties.get('semantic_type', 'Not specified')}\n"
        readme_content += f"- **Description**: {properties.get('description', 'No description available')}\n"
        readme_content += f"- **Unique Values**: {properties.get('num_unique_values', 'Unknown')}\n"
        
        if 'samples' in properties and properties['samples']:
            readme_content += f"- **Sample Values**: {properties['samples']}\n"
        
        if properties.get('dtype') == 'number':
            if 'min' in properties:
                readme_content += f"- **Min**: {properties['min']}\n"
            if 'max' in properties:
                readme_content += f"- **Max**: {properties['max']}\n"
            if 'std' in properties:
                readme_content += f"- **Standard Deviation**: {properties['std']}\n"
        
        readme_content += "\n"
    
    readme_content += f"""
## Generated Information
- **Processing Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source File**: {filename}
- **Generated by**: Dataset Summarizer Tool

"""
    
    return readme_content

def save_metadata_to_bucket(minio_client, bucket_name, filename, content):
    """Save metadata content to MinIO bucket"""
    try:
        content_bytes = content.encode('utf-8')
        content_stream = io.BytesIO(content_bytes)
        
        minio_client.put_object(
            bucket_name,
            filename,
            content_stream,
            length=len(content_bytes),
            content_type='text/markdown'
        )
        
        return True
    except Exception as e:
        print(f"Error saving metadata to bucket: {e}")
        return False