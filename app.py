import os
import io
import base64
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
from PIL import Image
from decimal import Decimal
import tempfile
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

def get_color_mask(mask_name, fill_color, back_color):
    """Get the appropriate color mask based on name"""
    # Convert hex to RGB tuples
    fill_rgb = hex_to_rgb(fill_color)
    back_rgb = hex_to_rgb(back_color)
    
    mask_map = {
        "solid": SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb),
        "radial_gradient": RadialGradiantColorMask(back_color=back_rgb, center_color=fill_rgb),
        "square_gradient": SquareGradiantColorMask(back_color=back_rgb, center_color=fill_rgb),
        "horizontal_gradient": HorizontalGradiantColorMask(back_color=back_rgb, left_color=fill_rgb),
        "vertical_gradient": VerticalGradiantColorMask(back_color=back_rgb, top_color=fill_rgb)
    }
    return mask_map.get(mask_name, SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb))

def generate_qr_code(data, version=None, error_correction="M", box_size=10, border=4,
                    fill_color="#000000", back_color="#FFFFFF", 
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
    color_mask_obj = get_color_mask(color_mask, fill_color, back_color)
    
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
            fill_color, back_color, module_drawer, color_mask, embedded_image
        )
        
        # Save to temporary file
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Convert to base64 for display
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        # Generate a unique ID for this QR code
        qr_id = str(uuid.uuid4())
        
        # Save the image temporarily for download
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{qr_id}.png")
        img.save(temp_path)
        temp_files[qr_id] = temp_path
        
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
    if qr_id in temp_files and os.path.exists(temp_files[qr_id]):
        return send_file(temp_files[qr_id], as_attachment=True, 
                        download_name="qrcode.png", mimetype='image/png')
    return "File not found", 404

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files"""
    qr_id = request.form.get('qr_id')
    if qr_id in temp_files and os.path.exists(temp_files[qr_id]):
        os.remove(temp_files[qr_id])
        del temp_files[qr_id]
    return jsonify({'success': True})

# Cleanup function to remove temporary files when the server stops
def cleanup_temp_files():
    for file_path in temp_files.values():
        if os.path.exists(file_path):
            os.remove(file_path)

# Register cleanup function
import atexit
atexit.register(cleanup_temp_files)

if __name__ == '__main__':
    # Disable auto-reloader but keep debug mode to fix issues with paths containing spaces
    app.run(debug=True, use_reloader=False)