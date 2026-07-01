"""ID Card Creator with PDF Export
Usage: python id_creator.py [options]
Options:
  --card-w WIDTH     Card width in inches (default: 3.5)
  --card-h HEIGHT    Card height in inches (default: 2.25)
  --cols COLS        Number of columns (default: 2)
  --rows ROWS        Number of rows (default: 5)
  --cli              Run in CLI mode (no GUI)
  --help             Show this help message
"""
import argparse
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import math
import os
import sys

# ============== CONFIGURATION CONSTANTS ==============
# All physical dimensions in inches unless noted
DEFAULT_CARD_WIDTH_INCHES = 3.5
DEFAULT_CARD_HEIGHT_INCHES = 2.25
DPI = 72  # Points per inch for PDF calculations

# Page dimensions in points (72 DPI)
PAGE_WIDTH = 595   # A4 width in points (8.27 inches)
PAGE_HEIGHT = 842  # A4 height in points (11.69 inches)

# Default grid layout
DEFAULT_COLS = 2
DEFAULT_ROWS = 5


class IDApp(ctk.CTk):
    """ID Card Creator Application"""
    
    def __init__(self, card_w_inches=DEFAULT_CARD_WIDTH_INCHES, 
                 card_h_inches=DEFAULT_CARD_HEIGHT_INCHES,
                 cols=DEFAULT_COLS, rows=DEFAULT_ROWS):
        super().__init__()
        
        # Store configuration as class constants
        self.CARD_W_INCHES = card_w_inches
        self.CARD_H_INCHES = card_h_inches
        self.CARD_W = int(self.CARD_W_INCHES * DPI)  # Convert to points
        self.CARD_H = int(self.CARD_H_INCHES * DPI)
        
        self.COLS = cols
        self.ROWS = rows
        self.MAX_PER_PAGE = self.COLS * self.ROWS
        
        # Page dimensions
        self.P_W = PAGE_WIDTH
        self.P_H = PAGE_HEIGHT
        
        # Internal Logic Data
        self.front_path = None
        self.back_path = None
        self.current_view = "front"

        # Calculate margins to center the grid on the page
        self._calculate_gaps()

        # UI Setup
        self.title("ID Creator Pro - Print Ready")
        self.geometry("1200x850")
        ctk.set_appearance_mode("dark")
        
        self._setup_ui()
        
        # Initialize preview
        self.update_preview()

    def _calculate_gaps(self):
        """Calculate horizontal and vertical gaps to center the grid"""
        total_cards_width = self.COLS * self.CARD_W
        total_cards_height = self.ROWS * self.CARD_H
        
        self.GAP_X = (self.P_W - total_cards_width) / (self.COLS + 1)
        self.GAP_Y = (self.P_H - total_cards_height) / (self.ROWS + 1)
        
        # Validate gaps are positive
        if self.GAP_X <= 0 or self.GAP_Y <= 0:
            print(f"WARNING: Gaps are too small or negative. Cards may not fit on page.")
            print(f"  GAP_X={self.GAP_X:.2f}, GAP_Y={self.GAP_Y:.2f}")

    def _setup_ui(self):
        """Setup all UI components"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Control Panel
        self.ctrl_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.ctrl_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.ctrl_frame, text="1. Load Assets", font=("Arial", 18, "bold")).pack(pady=(20,10))
        self.btn_f = ctk.CTkButton(self.ctrl_frame, text="Load Front Image", command=lambda: self.get_file('front'))
        self.btn_f.pack(pady=5)
        self.btn_b = ctk.CTkButton(self.ctrl_frame, text="Load Back Image", command=lambda: self.get_file('back'))
        self.btn_b.pack(pady=5)

        ctk.CTkLabel(self.ctrl_frame, text="2. Layout Options", font=("Arial", 18, "bold")).pack(pady=(30,10))
        self.seg_button = ctk.CTkSegmentedButton(self.ctrl_frame, values=["Front", "Back"], command=self.switch_view)
        self.seg_button.set("Front")
        self.seg_button.pack(pady=5, padx=20)

        self.show_marks = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.ctrl_frame, text="Enable Crop Marks", variable=self.show_marks, command=self.update_preview).pack(pady=5)
        
        self.show_safe = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.ctrl_frame, text="Show Printer Safe Zone", variable=self.show_safe, command=self.update_preview).pack(pady=5)

        ctk.CTkLabel(self.ctrl_frame, text="3. Quantity", font=("Arial", 18, "bold")).pack(pady=(30,10))
        self.num_entry = ctk.CTkEntry(self.ctrl_frame, width=100)
        self.num_entry.insert(0, str(self.MAX_PER_PAGE))
        self.num_entry.pack(pady=5)
        
        self.btn_autofill = ctk.CTkButton(self.ctrl_frame, text="Auto-Fill Page", fg_color="#3498db", command=self.autofill)
        self.btn_autofill.pack(pady=5)

        # Show current configuration
        self.config_label = ctk.CTkLabel(
            self.ctrl_frame, 
            text=f"Card: {self.CARD_W_INCHES}\" x {self.CARD_H_INCHES}\"\nGrid: {self.COLS}x{self.ROWS}",
            font=("Arial", 10)
        )
        self.config_label.pack(pady=5)

        self.btn_gen = ctk.CTkButton(self.ctrl_frame, text="EXPORT PDF", fg_color="#2ecc71", hover_color="#27ae60", 
                                     height=50, font=("Arial", 14, "bold"),
                                     command=self.generate_pdf)
        self.btn_gen.pack(pady=(20, 10))

        # Preview Canvas (Main Content Area)
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

    def get_file(self, side):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            if side == 'front':
                self.front_path = path
            else:
                self.back_path = path
            self.update_preview()

    def switch_view(self, value):
        self.current_view = value.lower()
        self.update_preview()

    def update_preview(self):
        self.canvas.delete("all")
        
        # Draw A4 page outline
        scale_x = self.canvas.winfo_width() / self.P_W
        scale_y = self.canvas.winfo_height() / self.P_H
        scale = min(scale_x, scale_y) * 0.95  # Small margin
        
        # Calculate centered position
        disp_w, disp_h = self.P_W * scale, self.P_H * scale
        offset_x = (self.canvas.winfo_width() - disp_w) / 2
        offset_y = (self.canvas.winfo_height() - disp_h) / 2
        
        # Draw page border
        self.canvas.create_rectangle(offset_x, offset_y, offset_x + disp_w, offset_y + disp_h,
                                    outline="#ffffff", width=2, dash=(5, 5))
        
        # Calculate quantity to show
        try:
            qty = min(int(self.num_entry.get()), self.MAX_PER_PAGE)
        except ValueError:
            qty = self.MAX_PER_PAGE
        
        # Draw cards
        for i in range(qty):
            row = i // self.COLS
            col = i % self.COLS
            
            x = offset_x + scale * (self.GAP_X + col * (self.CARD_W + self.GAP_X))
            y = offset_y + scale * (self.GAP_Y + row * (self.CARD_H + self.GAP_Y))
            w, h = self.CARD_W * scale, self.CARD_H * scale
            
            # Card outline
            self.canvas.create_rectangle(x, y, x + w, y + h, outline="#00ff00", width=2)
            
            # Draw crop marks if enabled
            if self.show_marks.get():
                # Corner crop marks
                mk = 10  # mark size
                for dx, dy in [(0,0), (w,0), (0,h), (w,h)]:
                    fx, fy = x + dx, y + dy
                    self.canvas.create_line(fx - mk, fy, fx + mk, fy, fill="#ff0000", width=2)  # Horizontal
                    self.canvas.create_line(fx, fy - mk, fx, fy + mk, fill="#ff0000", width=2)  # Vertical
            
            # Draw safe zone if enabled
            if self.show_safe.get():
                safe_margin = 0.2 * DPI * scale  # 0.2 inches
                self.canvas.create_rectangle(x + safe_margin, y + safe_margin,
                                            x + w - safe_margin, y + h - safe_margin,
                                            outline="#ffff00", dash=(2, 4), width=1)
            
            # Draw image if available for the current view
            img_path = None
            if self.current_view == 'front' and self.front_path:
                img_path = self.front_path
            elif self.current_view == 'back' and self.back_path:
                img_path = self.back_path
            
            if img_path and os.path.exists(img_path):
                try:
                    # Load and scale image to fit card
                    pil_img = Image.open(img_path)
                    
                    # Calculate scaling to fit within card dimensions (leaving some margin)
                    margin = 2
                    max_img_w = w - 2 * margin
                    max_img_h = h - 2 * margin
                    
                    img_w, img_h = pil_img.size
                    scale_w = max_img_w / img_w
                    scale_h = max_img_h / img_h
                    img_scale = min(scale_w, scale_h)  # Maintain aspect ratio
                    
                    new_w = img_w * img_scale
                    new_h = img_h * img_scale
                    
                    # Center the image in the card
                    img_x = x + margin + (max_img_w - new_w) / 2
                    img_y = y + margin + (max_img_h - new_h) / 2
                    
                    # Resize the image
                    resized_img = pil_img.resize((int(new_w), int(new_h)), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage and store reference to prevent garbage collection
                    photo = ImageTk.PhotoImage(resized_img)
                    
                    # Store reference to prevent garbage collection
                    if not hasattr(self, 'photo_refs'):
                        self.photo_refs = []
                    self.photo_refs.append(photo)
                    
                    # Display the image
                    self.canvas.create_image(img_x, img_y, anchor="nw", image=photo)
                except Exception as e:
                    # If there's an issue with the image, just draw placeholder text
                    cx, cy = x + w/2, y + h/2
                    self.canvas.create_text(cx, cy, text=f"ID {i+1}\n({'Front' if self.current_view == 'front' else 'Back'})", 
                                           fill="#ffffff", justify="center")
            else:
                # Placeholder text when no image is available
                cx, cy = x + w/2, y + h/2
                self.canvas.create_text(cx, cy, text=f"ID {i+1}\n({'Front' if self.current_view == 'front' else 'Back'})", 
                                       fill="#ffffff", justify="center")

    def autofill(self):
        self.num_entry.delete(0, "end")
        self.num_entry.insert(0, str(self.MAX_PER_PAGE))
        self.update_preview()

    def generate_pdf(self):
        try:
            qty = int(self.num_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for quantity")
            return
        
        if not self.front_path and not self.back_path:
            messagebox.showwarning("Warning", "Please load at least one image (front or back)")
            return
        
        # Ask for save location
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                               filetypes=[("PDF Files", "*.pdf")])
        if not save_path:
            return  # User cancelled
        
        # Import here to avoid issues if reportlab isn't installed
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        
        # Create PDF canvas
        c = canvas.Canvas(save_path, pagesize=A4)
        pdf_w, pdf_h = A4
        
        # Card dimensions in points
        card_w_points = self.CARD_W
        card_h_points = self.CARD_H
        
        # Calculate spacing to center the grid on the page
        total_cards_width = self.COLS * card_w_points
        total_cards_height = self.ROWS * card_h_points
        
        gap_x = (pdf_w - total_cards_width) / (self.COLS + 1)
        gap_y = (pdf_h - total_cards_height) / (self.ROWS + 1)
        
        # Get available images
        available_images = []
        if self.front_path:
            available_images.append(('front', self.front_path))
        if self.back_path:
            available_images.append(('back', self.back_path))
        
        total_pages_generated = 0
        
        # For each available image type, generate pages
        for img_type, img_path in available_images:
            cards_placed = 0
            
            while cards_placed < qty:
                cards_for_this_page = min(self.MAX_PER_PAGE, qty - cards_placed)
                
                if img_path and os.path.exists(img_path):
                    # Place cards on the current page
                    for row in range(self.ROWS):
                        for col in range(self.COLS):
                            if cards_placed >= qty:
                                break
                            
                            # Calculate position for this card
                            x = gap_x + col * (card_w_points + gap_x)
                            y = pdf_h - (gap_y + (row + 1) * card_h_points + row * gap_y)
                            
                            # Draw card outline
                            c.rect(x, y, card_w_points, card_h_points)
                            
                            # Draw image if exists
                            if img_path and os.path.exists(img_path):
                                try:
                                    pil_img = Image.open(img_path)
                                    
                                    # Calculate scaling to fit within card dimensions
                                    margin = 10
                                    max_img_w = card_w_points - 2 * margin
                                    max_img_h = card_h_points - 2 * margin
                                    
                                    img_w, img_h = pil_img.size
                                    scale_w = max_img_w / img_w
                                    scale_h = max_img_h / img_h
                                    scale = min(scale_w, scale_h)
                                    
                                    new_w = img_w * scale
                                    new_h = img_h * scale
                                    
                                    # Center the image in the card
                                    img_x = x + margin + (max_img_w - new_w) / 2
                                    img_y = y + (card_h_points - new_h) / 2
                                    
                                    c.drawImage(ImageReader(pil_img), img_x, img_y, width=new_w, height=new_h)
                                except Exception as e:
                                    c.drawString(x + 10, y + card_h_points / 2, f"Card {cards_placed + 1}")
                            else:
                                c.drawString(x + 10, y + card_h_points / 2, f"Card {cards_placed + 1}")
                            
                            # Draw crop marks if enabled
                            if self.show_marks.get():
                                mk_size = 10
                                # Top-left
                                c.line(x - mk_size, y, x + mk_size, y)
                                c.line(x, y - mk_size, x, y + mk_size)
                                # Top-right
                                c.line(x + card_w_points - mk_size, y, x + card_w_points + mk_size, y)
                                c.line(x + card_w_points, y - mk_size, x + card_w_points, y + mk_size)
                                # Bottom-left
                                c.line(x - mk_size, y + card_h_points, x + mk_size, y + card_h_points)
                                c.line(x, y + card_h_points - mk_size, x, y + card_h_points + mk_size)
                                # Bottom-right
                                c.line(x + card_w_points - mk_size, y + card_h_points, x + card_w_points + mk_size, y + card_h_points)
                                c.line(x + card_w_points, y + card_h_points - mk_size, x + card_w_points, y + card_h_points + mk_size)
                            
                            cards_placed += 1
                        
                        if cards_placed >= qty:
                            break
                
                # Add new page if more cards to place
                if cards_placed < qty:
                    c.showPage()
                    total_pages_generated += 1
                else:
                    if img_type != available_images[-1][0]:
                        c.showPage()
                    break

        # Save the PDF
        c.save()
        
        # Calculate total pages
        total_pages = 0
        if self.front_path:
            total_pages += (qty + self.MAX_PER_PAGE - 1) // self.MAX_PER_PAGE
        if self.back_path:
            total_pages += (qty + self.MAX_PER_PAGE - 1) // self.MAX_PER_PAGE
        
        messagebox.showinfo("Success", f"PDF saved successfully to:\n{save_path}\n\n"
                           f"Quantity: {qty} IDs\nTotal Pages: {total_pages}\nFormat: A4 sheet with {self.COLS}x{self.ROWS} layout ({self.MAX_PER_PAGE} per page)\n"
                           f"Contains: {'Front' if self.front_path else ''}{' and ' if self.front_path and self.back_path else ''}{'Back' if self.back_path else ''} pages")


def print_help():
    """Print help message (for CLI mode)"""
    print(__doc__)
    print("\nExamples:")
    print("  python id_creator.py                    # Default settings (3.5\"x2.25\" cards, 2x5 grid)")
    print("  python id_creator.py --card-w 3.375 --card-h 2.125  # Custom card size")
    print("  python id_creator.py --cols 3 --rows 4   # 3x4 grid (12 cards/page)")
    print("  python id_creator.py --help              # Show this help")


def run_cli():
    """Run in CLI mode (no GUI)"""
    print("ID Creator CLI Mode")
    print("-" * 40)
    print("Note: This is a GUI application. Use without --cli for full functionality.")
    print("\nConfiguration:")
    print(f"  Card Size: {DEFAULT_CARD_WIDTH_INCHES}\" x {DEFAULT_CARD_HEIGHT_INCHES}\"")
    print(f"  Grid: {DEFAULT_COLS} x {DEFAULT_ROWS} = {DEFAULT_COLS * DEFAULT_ROWS} cards/page")
    print(f"  Page: A4 ({PAGE_WIDTH} x {PAGE_HEIGHT} points)")
    print("\nTo run with GUI: python id_creator.py")
    print("For help: python id_creator.py --help")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='ID Card Creator - Create printable ID cards in PDF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python id_creator.py
  python id_creator.py --card-w 3.375 --card-h 2.125
  python id_creator.py --cols 3 --rows 4
  python id_creator.py --cli
        """
    )
    
    parser.add_argument('--card-w', type=float, default=DEFAULT_CARD_WIDTH_INCHES,
                       help=f'Card width in inches (default: {DEFAULT_CARD_WIDTH_INCHES})')
    parser.add_argument('--card-h', type=float, default=DEFAULT_CARD_HEIGHT_INCHES,
                       help=f'Card height in inches (default: {DEFAULT_CARD_HEIGHT_INCHES})')
    parser.add_argument('--cols', type=int, default=DEFAULT_COLS,
                       help=f'Number of columns (default: {DEFAULT_COLS})')
    parser.add_argument('--rows', type=int, default=DEFAULT_ROWS,
                       help=f'Number of rows (default: {DEFAULT_ROWS})')
    parser.add_argument('--cli', action='store_true',
                       help='Run in CLI mode (shows configuration only)')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    if args.cli:
        run_cli()
    else:
        # Validate dimensions
        if args.card_w <= 0 or args.card_h <= 0:
            print(f"ERROR: Card dimensions must be positive (got {args.card_w}x{args.card_h})")
            sys.exit(1)
        
        if args.cols <= 0 or args.rows <= 0:
            print(f"ERROR: Grid must have positive dimensions (got {args.cols}x{args.rows})")
            sys.exit(1)
        
        # Launch GUI
        app = IDApp(
            card_w_inches=args.card_w,
            card_h_inches=args.card_h,
            cols=args.cols,
            rows=args.rows
        )
        app.mainloop()