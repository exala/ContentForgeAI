
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename
from modules import prompt_orchestrator, generate_content, post_processor, article_storage_manager
from modules.wordpress_publisher import create_wordpress_post, upload_image_to_wordpress

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_article():
    topic = request.json.get('topic', '')
    publish_to_wp = request.json.get('publish_to_wp', False)
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    try:
        prompt = prompt_orchestrator(topic)
        raw_content = generate_content(prompt)
        title, html_content = post_processor(raw_content)
        
        # Store in database
        article_storage_manager(title, html_content, topic)
        
        result = {
            'title': title,
            'content': html_content[:500] + '...' if len(html_content) > 500 else html_content,
            'word_count': len(html_content.split()),
            'published': False,
            'stored_in_db': True
        }
        
        # Publish to WordPress if requested
        if publish_to_wp and title and html_content:
            try:
                # Upload featured image (if exists)
                featured_media_id = upload_image_to_wordpress("/home/runner/workspace/font.PNG", title)
                
                # Create WordPress post
                success = create_wordpress_post(title, html_content, "publish", featured_media_id)
                result['published'] = success
                result['wp_message'] = "Successfully published to WordPress!" if success else "Failed to publish to WordPress"
            except Exception as wp_error:
                result['wp_message'] = f"WordPress error: {str(wp_error)}"
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Please upload an Excel file (.xlsx or .xls)'}), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read Excel file
        df = pd.read_excel(filepath)
        columns = df.columns.tolist()
        
        # Get first few rows as preview
        preview_data = df.head(5).to_dict('records')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'columns': columns,
            'preview': preview_data,
            'total_rows': len(df)
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing Excel file: {str(e)}'}), 500

@app.route('/process_excel', methods=['POST'])
def process_excel():
    data = request.json
    filename = data.get('filename')
    column_name = data.get('column_name')
    publish_to_wp = data.get('publish_to_wp', False)
    
    if not filename or not column_name:
        return jsonify({'error': 'Filename and column name are required'}), 400
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = pd.read_excel(filepath)
        
        if column_name not in df.columns:
            return jsonify({'error': f'Column "{column_name}" not found'}), 400
        
        topics = df[column_name].dropna().tolist()
        results = []
        
        for i, topic in enumerate(topics[:10]):  # Limit to 10 for demo
            try:
                prompt = prompt_orchestrator(topic)
                raw_content = generate_content(prompt)
                title, html_content = post_processor(raw_content)
                
                # Store in database
                article_storage_manager(title, html_content, topic)
                
                result = {
                    'topic': topic,
                    'title': title,
                    'word_count': len(html_content.split()) if html_content else 0,
                    'status': 'success',
                    'published': False,
                    'stored_in_db': True
                }
                
                # Publish to WordPress if requested
                if publish_to_wp and title and html_content:
                    try:
                        featured_media_id = upload_image_to_wordpress("/home/runner/workspace/font.PNG", title)
                        success = create_wordpress_post(title, html_content, "publish", featured_media_id)
                        result['published'] = success
                    except Exception as wp_error:
                        result['wp_error'] = str(wp_error)
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    'topic': topic,
                    'status': 'error',
                    'error': str(e),
                    'published': False
                })
        
        return jsonify({
            'success': True,
            'processed': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing topics: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
