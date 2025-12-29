from flask import Flask, send_file, jsonify, request
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define folder paths
FOLDERS = {
    'html': 'JMP MAPS',
    'excel': 'JMP EXCEL',
    'pdf': 'JMP PDF'
}

# Create folders if they don't exist (for Vercel)
for folder in FOLDERS.values():
    folder_path = os.path.join(BASE_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

def get_all_original_files():
    """Get all files with their original names and availability"""
    original_files = {}
    
    for file_type, folder in FOLDERS.items():
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.startswith('.'):
                    continue
                    
                name_without_ext = os.path.splitext(filename)[0]
                
                if name_without_ext not in original_files:
                    original_files[name_without_ext] = {
                        'html': False, 
                        'excel': False, 
                        'pdf': False
                    }
                
                original_files[name_without_ext][file_type] = True
    
    return original_files

def search_files(query):
    """Search files by partial or full name match"""
    original_files = get_all_original_files()
    
    # If no query, return all files
    if not query:
        result = {}
        for original_name, file_data in original_files.items():
            result[original_name] = {
                'html': file_data['html'],
                'excel': file_data['excel'],
                'pdf': file_data['pdf'],
                'original_name': original_name
            }
        return result
    
    # Search by query
    query_lower = query.lower()
    filtered = {}
    
    for original_name, file_data in original_files.items():
        if query_lower in original_name.lower():
            filtered[original_name] = {
                'html': file_data['html'],
                'excel': file_data['excel'],
                'pdf': file_data['pdf'],
                'original_name': original_name
            }
    
    return filtered

@app.route('/')
def index():
    # Read the HTML file and serve it
    html_path = os.path.join(BASE_DIR, 'templates', 'index.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: index.html not found at {html_path}", 404

@app.route('/health')
def health():
    """Health check endpoint for debugging"""
    return jsonify({
        'status': 'ok',
        'base_dir': BASE_DIR,
        'folders': {k: os.path.exists(os.path.join(BASE_DIR, v)) for k, v in FOLDERS.items()},
        'templates_path': os.path.join(BASE_DIR, 'templates'),
        'templates_exists': os.path.exists(os.path.join(BASE_DIR, 'templates'))
    })

@app.route('/api/files')
def api_files():
    query = request.args.get('q', '').strip()
    files = search_files(query)
    return jsonify(files)

@app.route('/download/<file_type>/<filename>')
def download_file(file_type, filename):
    if file_type not in FOLDERS:
        return "Invalid file type", 404
    
    folder = FOLDERS[file_type]
    folder_path = os.path.join(BASE_DIR, folder)
    
    # Find the file with correct extension
    extensions = {
        'html': ['.html', '.htm'],
        'excel': ['.xlsx', '.xls'],
        'pdf': ['.pdf']
    }
    
    for ext in extensions[file_type]:
        filepath = os.path.join(folder_path, filename + ext)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
    
    return "File not found", 404
