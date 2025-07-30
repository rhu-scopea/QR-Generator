import os
import io
import base64
import datetime
import webbrowser
import threading
import time
import atexit

from flask import Flask, render_template, request, send_file, jsonify
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer,
    RoundedModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask, RadialGradiantColorMask, 
    SquareGradiantColorMask, HorizontalGradiantColorMask,
    VerticalGradiantColorMask
)
from decimal import Decimal
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Add datetime filter for templates
@app.template_filter('datetime')
def format_datetime(timestamp):
    """Format a timestamp to a readable date and time"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Create uploads and downloads folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# Store temporary files
temp_files = {}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_module_drawer(drawer_name, size_ratio=0.8):
    """Get the appropriate module drawer based on name"""
    drawer_map = {
        "square": SquareModuleDrawer(),
        "gapped_square": GappedSquareModuleDrawer(size_ratio=Decimal(size_ratio)),
        "circle": CircleModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "vertical_bars": VerticalBarsDrawer(),
        "horizontal_bars": HorizontalBarsDrawer()
    }
    return drawer_map.get(drawer_name, SquareModuleDrawer())

def get_color_mask(mask_name, fill_color, back_color, gradient_color=None):
    """Get the appropriate color mask based on name"""
    # Convert hex to RGB tuples
    fill_rgb = hex_to_rgb(fill_color)
    back_rgb = hex_to_rgb(back_color)
    
    # Make sure gradient_color is not None or empty
    if not gradient_color:
        gradient_color = "#0000FF"  # Default blue color
    
    # Convert gradient color to RGB
    gradient_rgb = hex_to_rgb(gradient_color)
    
    # Print debug information
    print(f"Color mask: {mask_name}")
    print(f"Fill color: {fill_color} -> {fill_rgb}")
    print(f"Back color: {back_color} -> {back_rgb}")
    print(f"Gradient color: {gradient_color} -> {gradient_rgb}")
    
    mask_map = {
        "solid": SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb),
        "radial_gradient": RadialGradiantColorMask(back_color=back_rgb, center_color=fill_rgb, edge_color=gradient_rgb),
        "square_gradient": SquareGradiantColorMask(back_color=back_rgb, center_color=fill_rgb, edge_color=gradient_rgb),
        "horizontal_gradient": HorizontalGradiantColorMask(back_color=back_rgb, left_color=fill_rgb, right_color=gradient_rgb),
        "vertical_gradient": VerticalGradiantColorMask(back_color=back_rgb, top_color=fill_rgb, bottom_color=gradient_rgb)
    }
    return mask_map.get(mask_name, SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb))

def generate_qr_code(data, version=None, error_correction="M", box_size=10, border=4,
                    fill_color="#000000", back_color="#FFFFFF", gradient_color=None,
                    module_drawer="square", color_mask="solid", embedded_image=None):
    """Generate a QR code with the given parameters"""
    # Map error correction levels
    error_correction_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H
    }
    
    # Create QR code
    qr = qrcode.QRCode(
        version=None if version == "auto" else int(version),
        error_correction=error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
        box_size=box_size,
        border=border
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Get module drawer and color mask
    module_drawer_obj = get_module_drawer(module_drawer)
    color_mask_obj = get_color_mask(color_mask, fill_color, back_color, gradient_color)
    
    # Generate image
    if embedded_image:
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer_obj,
            color_mask=color_mask_obj,
            embedded_image_path=embedded_image
        )
    else:
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer_obj,
            color_mask=color_mask_obj
        )
    
    return img

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    """Display all generated QR codes"""
    # Get all QR code files from the downloads folder
    qr_files = []
    for filename in os.listdir(app.config['DOWNLOAD_FOLDER']):
        if filename.endswith('.png'):
            qr_id = os.path.splitext(filename)[0]
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            creation_time = os.path.getctime(file_path)
            qr_files.append({
                'id': qr_id,
                'filename': filename,
                'path': file_path,
                'created': creation_time
            })
    
    # Sort by creation time (newest first)
    qr_files.sort(key=lambda x: x['created'], reverse=True)
    
    return render_template('gallery.html', qr_files=qr_files)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate QR code from form data"""
    try:
        # Get form data
        data = request.form.get('data', 'https://example.com')
        version = request.form.get('version', 'auto')
        error_correction = request.form.get('error_correction', 'M')
        box_size = int(request.form.get('box_size', 10))
        border = int(request.form.get('border', 4))
        fill_color = request.form.get('fill_color', '#000000')
        back_color = request.form.get('back_color', '#FFFFFF')
        gradient_color = request.form.get('gradient_color', '#0000FF')
        module_drawer = request.form.get('module_drawer', 'square')
        color_mask = request.form.get('color_mask', 'solid')
        
        # Handle embedded image if provided
        embedded_image = None
        if 'embedded_image' in request.files and request.files['embedded_image'].filename:
            file = request.files['embedded_image']
            # Create a unique filename
            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            embedded_image = filepath
            # Store for cleanup
            temp_files[filename] = filepath
        
        # Generate QR code
        img = generate_qr_code(
            data, version, error_correction, box_size, border,
            fill_color, back_color, gradient_color, module_drawer, color_mask, embedded_image
        )
        
        # Save to BytesIO for display and temporary storage
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Convert to base64 for display
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        # Generate a unique ID for this QR code
        qr_id = str(uuid.uuid4())
        
        # Store the image in memory for later download
        # Reset the pointer to the beginning of the BytesIO object
        img_io.seek(0)
        temp_files[qr_id] = {'image': img, 'bytes': img_io}
        
        return jsonify({
            'success': True,
            'image': f"data:image/png;base64,{img_base64}",
            'qr_id': qr_id
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<qr_id>')
def download(qr_id):
    """Download the generated QR code"""
    try:
        # First check if the QR code is in temp_files
        if qr_id in temp_files:
            # Check if the QR code has already been saved to the downloads folder
            if isinstance(temp_files[qr_id], dict):
                if 'image' in temp_files[qr_id]:
                    # Save the image to the downloads folder
                    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{qr_id}.png")
                    
                    # Use the PIL Image object to save the file
                    img = temp_files[qr_id]['image']
                    img.save(download_path)
                    
                    # Update temp_files to store the file path instead of the image object
                    temp_files[qr_id] = download_path
                    
                    return send_file(download_path, as_attachment=True, 
                                    download_name="qrcode.png", mimetype='image/png')
                elif 'bytes' in temp_files[qr_id]:
                    # If we have BytesIO but not the image, use that to save the file
                    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{qr_id}.png")
                    
                    # Get the BytesIO object and save it to a file
                    img_io = temp_files[qr_id]['bytes']
                    img_io.seek(0)  # Make sure we're at the beginning of the stream
                    
                    with open(download_path, 'wb') as f:
                        f.write(img_io.getvalue())
                    
                    # Update temp_files to store the file path
                    temp_files[qr_id] = download_path
                    
                    return send_file(download_path, as_attachment=True, 
                                    download_name="qrcode.png", mimetype='image/png')
            elif isinstance(temp_files[qr_id], str):
                # If it's already a path (already downloaded before), check if it exists
                if os.path.exists(temp_files[qr_id]):
                    return send_file(temp_files[qr_id], as_attachment=True, 
                                    download_name="qrcode.png", mimetype='image/png')
        
        # If not in temp_files or the file doesn't exist, check if it exists in the downloads folder
        # This handles cases where the server was restarted and temp_files was cleared
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{qr_id}.png")
        if os.path.exists(download_path):
            # Add to temp_files for future reference
            temp_files[qr_id] = download_path
            return send_file(download_path, as_attachment=True, 
                            download_name="qrcode.png", mimetype='image/png')
        
        # If we get here, the file wasn't found
        print(f"File not found for QR ID: {qr_id}")
        return "File not found", 404
    except Exception as e:
        # Log the error for debugging
        print(f"Error in download route: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files"""
    qr_id = request.form.get('qr_id')
    if qr_id in temp_files:
        # Check if it's a file path or an in-memory image
        if isinstance(temp_files[qr_id], str) and os.path.exists(temp_files[qr_id]):
            # It's a file path, remove the file
            os.remove(temp_files[qr_id])
        # Remove from temp_files dictionary regardless of type
        del temp_files[qr_id]
    return jsonify({'success': True})

# Cleanup function to remove temporary files when the server stops
def cleanup_temp_files():
    for key, value in list(temp_files.items()):
        if isinstance(value, str) and os.path.exists(value):
            # It's a file path, remove the file
            os.remove(value)
        # No need to clean up in-memory images as they'll be garbage collected
        # Remove from temp_files dictionary
        del temp_files[key]

# Register cleanup function
atexit.register(cleanup_temp_files)



def open_browser():
    """Open the browser after a short delay to ensure the server is up"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Disable auto-reloader but keep debug mode to fix issues with paths containing spaces
    app.run(debug=True, use_reloader=False)

    # Start a thread to open the browser
    threading.Thread(target=open_browser).start()

