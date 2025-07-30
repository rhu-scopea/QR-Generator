# QR Code Generator

A user-friendly web interface for generating customized QR codes using the Python `qrcode[pil]` package.

![QR Code Generator Screenshot](https://i.imgur.com/example.png)

## Features

- Generate QR codes from any text, URL, or data
- Customize QR code appearance:
  - Size and version
  - Error correction level
  - Colors (fill and background)
  - Module shapes (square, circle, rounded, etc.)
  - Color styles (solid, gradients)
- Embed images in the center of QR codes
- Preview QR codes before downloading
- Download QR codes as PNG images

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Download the Project

Download and extract the project to a folder on your computer.

### Step 2: Install Dependencies

Open a command prompt or terminal window and navigate to the project folder. Then run:

```
pip install -e .
```

This will install all the required dependencies, including:
- qrcode[pil] - For QR code generation
- Flask - For the web interface

## Usage

### Starting the Application

1. Open a command prompt or terminal window
2. Navigate to the project folder
3. Run the following command:

```
python app.py
```

4. Open your web browser and go to: http://127.0.0.1:5000

### Generating a QR Code

1. Enter the text, URL, or data you want to encode in the "Data to encode" field
2. Adjust the settings as desired:
   - **Version**: Controls the size of the QR code (1-40, or Auto)
   - **Error Correction**: Higher levels allow the QR code to be readable even if partially damaged
   - **Box Size**: Size of each module (box) in pixels
   - **Border**: Width of the border around the QR code

3. Customize the appearance:
   - **Fill Color**: Color of the QR code modules
   - **Background Color**: Background color of the QR code
   - **Module Shape**: Shape of the QR code modules (Square, Circle, Rounded, etc.)
   - **Color Style**: Style of coloring (Solid, Radial Gradient, etc.)
   - **Embedded Image**: Optionally embed an image in the center of the QR code

4. Click the "Generate QR Code" button
5. The generated QR code will appear in the preview area
6. Click "Download QR Code" to save the image to your computer

### Tips for Best Results

- **Error Correction**: Use higher error correction (H - High) when embedding images
- **Testing**: Always test your QR code with multiple scanning apps to ensure it works correctly
- **Contrast**: Ensure good contrast between fill and background colors for better scanning
- **Embedded Images**: Keep embedded images small and simple for better compatibility

## Troubleshooting

- **QR Code Not Scanning**: Try increasing the error correction level or adjusting the colors for better contrast
- **Application Not Starting**: Make sure all dependencies are installed correctly
- **Image Embedding Issues**: Ensure the image is not too large and use high error correction

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [qrcode](https://github.com/lincolnloop/python-qrcode) - Python QR Code generator
- [Pillow](https://python-pillow.org/) - Python Imaging Library
- [Flask](https://flask.palletsprojects.com/) - Web framework