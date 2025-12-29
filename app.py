from flask import Flask, render_template, send_file, jsonify, request
import os
from pathlib import Path

app = Flask(__name__)

# Define folder paths
FOLDERS = {
    'html': 'JMP MAPS',
    'excel': 'JMP EXCEL',
    'pdf': 'JMP PDF'
}

def get_all_files():
    """Get all unique file names (without extensions) from all folders"""
    files = {}
    
    for file_type, folder in FOLDERS.items():
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.startswith('.'):
                    continue
                    
                name_without_ext = os.path.splitext(filename)[0]
                
                if name_without_ext not in files:
                    files[name_without_ext] = {'html': False, 'excel': False, 'pdf': False}
                
                files[name_without_ext][file_type] = True
    
    return files

def search_files(query):
    """Search files by partial or full name match"""
    all_files = get_all_files()
    if not query:
        return all_files
    
    query_lower = query.lower()
    filtered = {name: data for name, data in all_files.items() 
                if query_lower in name.lower()}
    return filtered

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files')
def api_files():
    query = request.args.get('q', '')
    files = search_files(query)
    return jsonify(files)

@app.route('/download/<file_type>/<filename>')
def download_file(file_type, filename):
    if file_type not in FOLDERS:
        return "Invalid file type", 404
    
    folder = FOLDERS[file_type]
    
    # Find the file with correct extension
    extensions = {
        'html': ['.html', '.htm'],
        'excel': ['.xlsx', '.xls'],
        'pdf': ['.pdf']
    }
    
    for ext in extensions[file_type]:
        filepath = os.path.join(folder, filename + ext)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
    
    return "File not found", 404
