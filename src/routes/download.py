import requests
from flask import Blueprint, request, Response, jsonify, stream_with_context
from urllib.parse import urlparse
import re

download_bp = Blueprint('download', __name__)

@download_bp.route('/proxy', methods=['GET'])
def proxy_download():
    """
    Proxy endpoint that handles resumable downloads with Range requests.
    Supports downloading from any URL with proper Range header handling.
    """
    # Get the target URL from query parameters
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    # Validate URL
    try:
        parsed_url = urlparse(target_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({'error': 'Invalid URL'}), 400
    except Exception:
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Get Range header from client request
    range_header = request.headers.get('Range')
    
    # Prepare headers for the upstream request
    upstream_headers = {}
    if range_header:
        upstream_headers['Range'] = range_header
    
    # Add other relevant headers
    if request.headers.get('User-Agent'):
        upstream_headers['User-Agent'] = request.headers.get('User-Agent')
    
    try:
        # Make request to the target URL
        response = requests.get(
            target_url, 
            headers=upstream_headers, 
            stream=True,
            timeout=30
        )
        
        # Prepare response headers
        response_headers = {}
        
        # Copy important headers from upstream response
        headers_to_copy = [
            'Content-Type', 'Content-Length', 'Content-Range', 
            'Accept-Ranges', 'Last-Modified', 'ETag'
        ]
        
        for header in headers_to_copy:
            if header in response.headers:
                response_headers[header] = response.headers[header]
        
        # Add CORS headers
        response_headers['Access-Control-Allow-Origin'] = '*'
        response_headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response_headers['Access-Control-Allow-Headers'] = 'Range, Content-Type'
        response_headers['Access-Control-Expose-Headers'] = 'Content-Range, Content-Length, Accept-Ranges'
        
        # Stream the response
        def generate():
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            except Exception as e:
                print(f"Error streaming content: {e}")
                return
        
        return Response(
            stream_with_context(generate()),
            status=response.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@download_bp.route('/info', methods=['GET'])
def get_file_info():
    """
    Get file information (size, range support) without downloading the file.
    """
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    try:
        # Make HEAD request to get file info
        response = requests.head(target_url, timeout=10)
        
        file_info = {
            'url': target_url,
            'size': None,
            'supports_ranges': False,
            'content_type': None,
            'last_modified': None,
            'etag': None
        }
        
        # Extract file information
        if 'Content-Length' in response.headers:
            file_info['size'] = int(response.headers['Content-Length'])
        
        if 'Accept-Ranges' in response.headers:
            file_info['supports_ranges'] = response.headers['Accept-Ranges'].lower() == 'bytes'
        
        if 'Content-Type' in response.headers:
            file_info['content_type'] = response.headers['Content-Type']
        
        if 'Last-Modified' in response.headers:
            file_info['last_modified'] = response.headers['Last-Modified']
        
        if 'ETag' in response.headers:
            file_info['etag'] = response.headers['ETag']
        
        return jsonify(file_info)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to get file info: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@download_bp.route('/proxy', methods=['OPTIONS'])
def handle_preflight():
    """Handle CORS preflight requests"""
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Range, Content-Type'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

