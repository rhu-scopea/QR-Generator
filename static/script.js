document.addEventListener('DOMContentLoaded', function() {
    // Populate version dropdown with options 1-40
    const versionSelect = document.getElementById('version');
    for (let i = 1; i <= 40; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        versionSelect.appendChild(option);
    }

    // Form elements
    const qrForm = document.getElementById('qr-form');
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');
    const qrPreview = document.getElementById('qr-preview');
    const colorMaskSelect = document.getElementById('color_mask');
    const gradientColorContainer = document.getElementById('gradient_color_container');
    const fillColorLabel = document.getElementById('fill_color_label');
    const fillColorHelp = document.getElementById('fill_color_help');
    const gradientColorLabel = document.getElementById('gradient_color_label');
    const gradientColorHelp = document.getElementById('gradient_color_help');
    
    // Current QR code ID for download
    let currentQrId = null;
    
    // Debounce timer
    let debounceTimer;
    
    // Function to update color input labels based on selected color style
    function updateColorInputs() {
        const colorStyle = colorMaskSelect.value;
        
        // Show/hide gradient color input based on selected style
        if (colorStyle === 'solid') {
            gradientColorContainer.style.display = 'none';
            fillColorLabel.textContent = 'Fill Color:';
            fillColorHelp.textContent = 'Color of the QR code modules';
        } else {
            gradientColorContainer.style.display = 'flex';
            
            // Update labels based on gradient type
            switch (colorStyle) {
                case 'radial_gradient':
                    fillColorLabel.textContent = 'Center Color:';
                    fillColorHelp.textContent = 'Color at the center of the QR code';
                    gradientColorLabel.textContent = 'Edge Color:';
                    gradientColorHelp.textContent = 'Color at the edges of the QR code';
                    break;
                case 'square_gradient':
                    fillColorLabel.textContent = 'Center Color:';
                    fillColorHelp.textContent = 'Color at the center of the QR code';
                    gradientColorLabel.textContent = 'Edge Color:';
                    gradientColorHelp.textContent = 'Color at the edges of the QR code';
                    break;
                case 'horizontal_gradient':
                    fillColorLabel.textContent = 'Left Color:';
                    fillColorHelp.textContent = 'Color on the left side of the QR code';
                    gradientColorLabel.textContent = 'Right Color:';
                    gradientColorHelp.textContent = 'Color on the right side of the QR code';
                    break;
                case 'vertical_gradient':
                    fillColorLabel.textContent = 'Top Color:';
                    fillColorHelp.textContent = 'Color at the top of the QR code';
                    gradientColorLabel.textContent = 'Bottom Color:';
                    gradientColorHelp.textContent = 'Color at the bottom of the QR code';
                    break;
            }
        }
    }
    
    // Initialize color inputs based on default selection
    updateColorInputs();
    
    // Add event listener for color style changes
    colorMaskSelect.addEventListener('change', function() {
        updateColorInputs();
        debouncedGenerateQRCode();
    });
    
    // Function to generate QR code
    function generateQRCode(showLoading = true) {
        // Clear any previous debounced calls
        clearTimeout(debounceTimer);
        
        // Show loading state if requested
        if (showLoading) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        }
        
        // Clear any previous error messages
        const errorMessage = document.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
        
        // Create FormData object
        const formData = new FormData(qrForm);
        
        // Send AJAX request
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-qrcode"></i> Generate QR Code';
            
            if (data.success) {
                // Display the QR code
                qrPreview.innerHTML = `<img id="qr-image" src="${data.image}" alt="Generated QR Code">`;
                
                // Enable download button
                downloadBtn.disabled = false;
                
                // Store QR ID for download
                currentQrId = data.qr_id;
                
                // Set up cleanup on page unload
                window.addEventListener('beforeunload', function() {
                    cleanupTempFile(currentQrId);
                });
            } else {
                // Show error message
                showError(data.error || 'Failed to generate QR code');
            }
        })
        .catch(error => {
            // Reset button state
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-qrcode"></i> Generate QR Code';
            
            // Show error message
            showError('An error occurred: ' + error.message);
        });
    }
    
    // Debounced function to generate QR code after input changes
    function debouncedGenerateQRCode() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            generateQRCode(false); // Don't show loading state for automatic updates
        }, 500); // 500ms debounce time
    }
    
    // Form submission (manual generation)
    qrForm.addEventListener('submit', function(e) {
        e.preventDefault();
        generateQRCode(true); // Show loading state for manual generation
    });
    
    // Add event listeners to all form inputs for automatic generation
    const formInputs = qrForm.querySelectorAll('input, select');
    formInputs.forEach(input => {
        if (input.type === 'radio') {
            input.addEventListener('change', debouncedGenerateQRCode);
        } else if (input.type === 'file') {
            input.addEventListener('change', debouncedGenerateQRCode);
        } else {
            // For text, number, color inputs and select dropdowns
            input.addEventListener('input', debouncedGenerateQRCode);
            input.addEventListener('change', debouncedGenerateQRCode);
        }
    });
    
    // Generate initial QR code on page load
    generateQRCode(true);
    
    // Download button click
    downloadBtn.addEventListener('click', function() {
        if (currentQrId) {
            window.location.href = `/download/${currentQrId}`;
        }
    });
    
    // Function to show error message
    function showError(message) {
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        // Insert at the top of the form
        qrForm.insertBefore(errorDiv, qrForm.firstChild);
        
        // Scroll to top of form
        qrForm.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Function to clean up temporary file
    function cleanupTempFile(qrId) {
        if (!qrId) return;
        
        const formData = new FormData();
        formData.append('qr_id', qrId);
        
        // Use sendBeacon for reliable delivery during page unload
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/cleanup', formData);
        } else {
            // Fallback to fetch
            fetch('/cleanup', {
                method: 'POST',
                body: formData,
                keepalive: true
            });
        }
    }
    
    // File input preview (optional enhancement)
    const embeddedImage = document.getElementById('embedded_image');
    if (embeddedImage) {
        embeddedImage.addEventListener('change', function() {
            // Show filename or preview if needed
            const fileName = this.files[0]?.name;
            if (fileName) {
                // You could add a small preview here if desired
                console.log('Selected file:', fileName);
            }
        });
    }
    
    // Form field tooltips and help (optional enhancement)
    const helpElements = document.querySelectorAll('small');
    helpElements.forEach(element => {
        // Add tooltip or enhanced help functionality if needed
        element.style.cursor = 'help';
    });
});