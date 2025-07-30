document.addEventListener('DOMContentLoaded', function() {
    // Populate version dropdown with options 1-40
    const versionSelect = document.getElementById('version');
    for (let i = 1; i <= 40; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        versionSelect.appendChild(option);
    }

    // Form submission
    const qrForm = document.getElementById('qr-form');
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');
    const qrPreview = document.getElementById('qr-preview');
    
    // Current QR code ID for download
    let currentQrId = null;

    qrForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        
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
    });
    
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