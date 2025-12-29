from flask import Flask, send_file, jsonify, request
import os

app = Flask(__name__)

# Get the base directory (one level up from api/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define folder paths
FOLDERS = {
    'html': 'JMP MAPS',
    'excel': 'JMP EXCEL',
    'pdf': 'JMP PDF'
}

# Create folders if they don't exist
for folder in FOLDERS.values():
    folder_path = os.path.join(BASE_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

def get_all_original_files():
    """Get all files with their original names and availability"""
    original_files = {}
    
    for file_type, folder in FOLDERS.items():
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.exists(folder_path):
            try:
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
            except Exception as e:
                print(f"Error reading {folder_path}: {e}")
    
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
    """Serve the main HTML page"""
    html_path = os.path.join(BASE_DIR, 'templates', 'index.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({
            'error': 'index.html not found',
            'path': html_path,
            'base_dir': BASE_DIR
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint for debugging"""
    try:
        files = get_all_original_files()
        return jsonify({
            'status': 'ok',
            'base_dir': BASE_DIR,
            'folders': {k: os.path.exists(os.path.join(BASE_DIR, v)) for k, v in FOLDERS.items()},
            'templates_path': os.path.join(BASE_DIR, 'templates'),
            'templates_exists': os.path.exists(os.path.join(BASE_DIR, 'templates')),
            'index_html_exists': os.path.exists(os.path.join(BASE_DIR, 'templates', 'index.html')),
            'file_count': len(files)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'base_dir': BASE_DIR
        }), 500

@app.route('/api/files')
def api_files():
    """Get list of files with optional search"""
    try:
        query = request.args.get('q', '').strip()
        files = search_files(query)
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_type>/<filename>')
def download_file(file_type, filename):
    """Download a specific file"""
    try:
        if file_type not in FOLDERS:
            return jsonify({'error': 'Invalid file type'}), 404
        
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
        
        return jsonify({'error': 'File not found', 'filename': filename}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# This is required for Vercel
handler = app
