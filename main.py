import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
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
from PIL import Image, ImageTk
import os
from decimal import Decimal

class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set up the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for inputs
        left_panel = ttk.Frame(main_frame, padding="10", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create right panel for QR code display
        right_panel = ttk.Frame(main_frame, padding="10", width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Variables
        self.data_var = tk.StringVar(value="https://example.com")
        self.version_var = tk.StringVar(value="Auto")
        self.error_correction_var = tk.StringVar(value="M")
        self.box_size_var = tk.IntVar(value=10)
        self.border_var = tk.IntVar(value=4)
        self.fill_color_var = tk.StringVar(value="#000000")
        self.back_color_var = tk.StringVar(value="#FFFFFF")
        self.module_drawer_var = tk.StringVar(value="Square")
        self.color_mask_var = tk.StringVar(value="Solid")
        self.embedded_image_path = None
        self.qr_image = None
        self.pil_image = None
        
        # Create input fields
        self.create_input_fields(left_panel)
        
        # Create QR code display
        self.create_qr_display(right_panel)
        
        # Generate initial QR code
        self.generate_qr_code()
    
    def create_input_fields(self, parent):
        # Data input
        data_frame = ttk.LabelFrame(parent, text="QR Code Data", padding="5")
        data_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(data_frame, text="Data:").pack(anchor=tk.W)
        data_entry = ttk.Entry(data_frame, textvariable=self.data_var, width=40)
        data_entry.pack(fill=tk.X, pady=5)
        
        # Basic settings
        basic_frame = ttk.LabelFrame(parent, text="Basic Settings", padding="5")
        basic_frame.pack(fill=tk.X, pady=5)
        
        # Version
        ttk.Label(basic_frame, text="Version:").pack(anchor=tk.W)
        versions = ["Auto"] + [str(i) for i in range(1, 41)]
        version_combo = ttk.Combobox(basic_frame, textvariable=self.version_var, values=versions)
        version_combo.pack(fill=tk.X, pady=2)
        
        # Error correction
        ttk.Label(basic_frame, text="Error Correction:").pack(anchor=tk.W)
        error_levels = [
            ("L - Low (7%)", "L"),
            ("M - Medium (15%)", "M"),
            ("Q - Quartile (25%)", "Q"),
            ("H - High (30%)", "H")
        ]
        error_frame = ttk.Frame(basic_frame)
        error_frame.pack(fill=tk.X, pady=2)
        
        for text, value in error_levels:
            ttk.Radiobutton(error_frame, text=text, value=value, 
                           variable=self.error_correction_var).pack(anchor=tk.W)
        
        # Box size and border
        size_frame = ttk.Frame(basic_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="Box Size:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(size_frame, from_=1, to=100, textvariable=self.box_size_var, 
                   width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(size_frame, text="Border:").grid(row=1, column=0, sticky=tk.W)
        ttk.Spinbox(size_frame, from_=0, to=100, textvariable=self.border_var, 
                   width=5).grid(row=1, column=1, padx=5)
        
        # Style settings
        style_frame = ttk.LabelFrame(parent, text="Style Settings", padding="5")
        style_frame.pack(fill=tk.X, pady=5)
        
        # Colors
        color_frame = ttk.Frame(style_frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(color_frame, text="Fill Color:").grid(row=0, column=0, sticky=tk.W)
        fill_color_btn = ttk.Button(color_frame, text="Choose", 
                                  command=lambda: self.choose_color("fill"))
        fill_color_btn.grid(row=0, column=1, padx=5)
        
        ttk.Label(color_frame, text="Background:").grid(row=1, column=0, sticky=tk.W)
        back_color_btn = ttk.Button(color_frame, text="Choose", 
                                   command=lambda: self.choose_color("back"))
        back_color_btn.grid(row=1, column=1, padx=5)
        
        # Module drawer
        ttk.Label(style_frame, text="Module Shape:").pack(anchor=tk.W)
        module_drawers = [
            "Square", "Gapped Square", "Circle", "Rounded", 
            "Vertical Bars", "Horizontal Bars"
        ]
        module_combo = ttk.Combobox(style_frame, textvariable=self.module_drawer_var, 
                                  values=module_drawers)
        module_combo.pack(fill=tk.X, pady=2)
        
        # Color mask
        ttk.Label(style_frame, text="Color Style:").pack(anchor=tk.W)
        color_masks = [
            "Solid", "Radial Gradient", "Square Gradient", 
            "Horizontal Gradient", "Vertical Gradient"
        ]
        mask_combo = ttk.Combobox(style_frame, textvariable=self.color_mask_var, 
                                values=color_masks)
        mask_combo.pack(fill=tk.X, pady=2)
        
        # Embedded image
        embed_frame = ttk.Frame(style_frame)
        embed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(embed_frame, text="Embedded Image:").grid(row=0, column=0, sticky=tk.W)
        self.embed_label = ttk.Label(embed_frame, text="No image selected")
        self.embed_label.grid(row=0, column=1, padx=5)
        
        embed_btn = ttk.Button(embed_frame, text="Select Image", 
                             command=self.select_embedded_image)
        embed_btn.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        clear_btn = ttk.Button(embed_frame, text="Clear Image", 
                             command=self.clear_embedded_image)
        clear_btn.grid(row=1, column=1, padx=5, pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=10)
        
        generate_btn = ttk.Button(action_frame, text="Generate QR Code", 
                                command=self.generate_qr_code)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(action_frame, text="Save QR Code", 
                            command=self.save_qr_code)
        save_btn.pack(side=tk.LEFT, padx=5)
    
    def create_qr_display(self, parent):
        # QR code display
        display_frame = ttk.LabelFrame(parent, text="QR Code Preview", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.qr_label = ttk.Label(display_frame)
        self.qr_label.pack(fill=tk.BOTH, expand=True)
    
    def choose_color(self, color_type):
        current_color = self.fill_color_var.get() if color_type == "fill" else self.back_color_var.get()
        color = colorchooser.askcolor(color=current_color, title=f"Choose {color_type} color")
        
        if color[1]:  # If a color was chosen
            if color_type == "fill":
                self.fill_color_var.set(color[1])
            else:
                self.back_color_var.set(color[1])
    
    def select_embedded_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        
        if file_path:
            self.embedded_image_path = file_path
            self.embed_label.config(text=os.path.basename(file_path))
    
    def clear_embedded_image(self):
        self.embedded_image_path = None
        self.embed_label.config(text="No image selected")
    
    def get_module_drawer(self):
        drawer_map = {
            "Square": SquareModuleDrawer(),
            "Gapped Square": GappedSquareModuleDrawer(size_ratio=Decimal(0.8)),
            "Circle": CircleModuleDrawer(),
            "Rounded": RoundedModuleDrawer(),
            "Vertical Bars": VerticalBarsDrawer(),
            "Horizontal Bars": HorizontalBarsDrawer()
        }
        return drawer_map.get(self.module_drawer_var.get(), SquareModuleDrawer())
    
    def get_color_mask(self):
        # Convert hex to RGB tuples
        fill_color = self.hex_to_rgb(self.fill_color_var.get())
        back_color = self.hex_to_rgb(self.back_color_var.get())
        
        mask_map = {
            "Solid": SolidFillColorMask(front_color=fill_color, back_color=back_color),
            "Radial Gradient": RadialGradiantColorMask(back_color=back_color, center_color=fill_color),
            "Square Gradient": SquareGradiantColorMask(back_color=back_color, center_color=fill_color),
            "Horizontal Gradient": HorizontalGradiantColorMask(back_color=back_color, left_color=fill_color),
            "Vertical Gradient": VerticalGradiantColorMask(back_color=back_color, top_color=fill_color)
        }
        return mask_map.get(self.color_mask_var.get(), SolidFillColorMask(front_color=fill_color, back_color=back_color))
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def generate_qr_code(self):
        try:
            # Get data
            data = self.data_var.get()
            if not data:
                messagebox.showerror("Error", "Please enter data for the QR code")
                return
            
            # Create QR code
            qr = qrcode.QRCode(
                version=None if self.version_var.get() == "Auto" else int(self.version_var.get()),
                error_correction={
                    "L": qrcode.constants.ERROR_CORRECT_L,
                    "M": qrcode.constants.ERROR_CORRECT_M,
                    "Q": qrcode.constants.ERROR_CORRECT_Q,
                    "H": qrcode.constants.ERROR_CORRECT_H
                }[self.error_correction_var.get()],
                box_size=self.box_size_var.get(),
                border=self.border_var.get()
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            # Generate image with styling
            module_drawer = self.get_module_drawer()
            color_mask = self.get_color_mask()
            
            if self.embedded_image_path:
                self.pil_image = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color_mask=color_mask,
                    embedded_image_path=self.embedded_image_path
                )
            else:
                self.pil_image = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color_mask=color_mask
                )
            
            # Display the QR code
            self.display_qr_code()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
    
    def display_qr_code(self):
        if self.pil_image:
            # Resize for display if needed
            display_size = min(400, self.pil_image.size[0])
            display_img = self.pil_image
            
            if display_img.size[0] > display_size:
                ratio = display_size / display_img.size[0]
                new_size = (int(display_img.size[0] * ratio), int(display_img.size[1] * ratio))
                display_img = display_img.resize(new_size, Image.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            self.qr_image = ImageTk.PhotoImage(display_img)
            self.qr_label.config(image=self.qr_image)
    
    def save_qr_code(self):
        if not self.pil_image:
            messagebox.showerror("Error", "No QR code has been generated")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.pil_image.save(file_path)
                messagebox.showinfo("Success", f"QR code saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save QR code: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()