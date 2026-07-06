"""
ID Creator Pro - Redesigned UI
Calm and Technical aesthetic inspired by Linear
"""
import argparse
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import time
from random import random

# ============== DESIGN TOKENS (Linear-style) ==============
# NEVER hard-code hex values - always use these tokens
class DesignTokens:
    # Colors
    bg = "#0D0D0F"           # Main background
    surface = "#18181B"       # Card/panel surface
    surface_elevated = "#1F1F23"  # Elevated surfaces
    border = "#27272A"        # Borders
    border_focus = "#3F3F46"  # Focus state border
    
    # Text
    text_primary = "#FAFAFA"  # Primary text
    text_secondary = "#A1A1AA"  # Secondary text
    text_tertiary = "#71717A"   # Tertiary/disabled text
    
    # Accent (single accent color, used sparingly)
    accent = "#6366F1"        # Indigo - primary actions
    accent_hover = "#818CF8"  # Accent hover
    accent_pressed = "#4F46E5"  # Accent pressed
    
    # Semantic
    success = "#22C55E"      # Success green
    warning = "#F59E0B"      # Warning amber
    error = "#EF4444"         # Error red
    
    # Spacing (8px grid)
    s1 = 4     # 0.5x
    s2 = 8     # 1x (base)
    s3 = 12    # 1.5x
    s4 = 16    # 2x
    s5 = 20    # 2.5x
    s6 = 24    # 3x
    s8 = 32    # 4x
    s10 = 40   # 5x
    s12 = 48   # 6x
    
    # Radii
    radius_sm = 6
    radius_md = 8
    radius_lg = 12
    
    # Typography
    font_sm = ("Inter", 12)
    font_md = ("Inter", 14)
    font_lg = ("Inter", 16)
    font_xl = ("Inter", 20)
    font_2xl = ("Inter", 24)

# Apply tokens globally
tokens = DesignTokens()

# ============== CONFIGURATION ==============
DEFAULT_CARD_WIDTH_INCHES = 3.5
DEFAULT_CARD_HEIGHT_INCHES = 2.25
DPI = 72
PAGE_WIDTH = 595
PAGE_HEIGHT = 842
DEFAULT_COLS = 2
DEFAULT_ROWS = 5


# ============== REUSABLE COMPONENTS ==============

class LinearButton(ctk.CTkButton):
    """Button with proper hover, focus, disabled states"""
    
    def __init__(self, master, text="", variant="primary", size="md", **kwargs):
        self.variant = variant
        self.size = size
        
        # Variant styles
        variants = {
            "primary": {
                "fg_color": tokens.accent,
                "hover_color": tokens.accent_hover,
                "text_color": "#FFFFFF",
            },
            "secondary": {
                "fg_color": tokens.surface_elevated,
                "hover_color": tokens.border_focus,
                "text_color": tokens.text_primary,
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": tokens.surface_elevated,
                "text_color": tokens.text_secondary,
            },
            "danger": {
                "fg_color": tokens.error,
                "hover_color": "#F87171",
                "text_color": "#FFFFFF",
            },
        }
        
        # Size styles
        sizes = {
            "sm": {"height": 32, "font": ("Inter", 12)},
            "md": {"height": 40, "font": ("Inter", 14)},
            "lg": {"height": 48, "font": ("Inter", 16)},
        }
        
        style = variants.get(variant, variants["primary"])
        size_style = sizes.get(size, sizes["md"])
        
        super().__init__(
            master,
            text=text,
            command=kwargs.pop("command", None),
            **style,
            **size_style,
            corner_radius=tokens.radius_md,
            **kwargs
        )


class LinearInput(ctk.CTkEntry):
    """Input with proper focus states"""
    
    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            fg_color=tokens.surface,
            bg_color=tokens.surface,
            text_color=tokens.text_primary,
            placeholder_text_color=tokens.text_tertiary,
            border_color=tokens.border,
            border_width=1,
            corner_radius=tokens.radius_md,
            font=tokens.font_md,
            height=40,
            **kwargs
        )
        self.bind("<FocusIn>", self._on_focus)
        self.bind("<FocusOut>", self._on_blur)
    
    def _on_focus(self, event):
        self.configure(border_color=tokens.accent)
    
    def _on_blur(self, event):
        self.configure(border_color=tokens.border)


class LinearCheckbox(ctk.CTkCheckBox):
    """Checkbox with proper states"""
    
    def __init__(self, master, text="", **kwargs):
        super().__init__(
            master,
            text=text,
            fg_color=tokens.accent,
            hover_color=tokens.accent_hover,
            text_color=tokens.text_primary,
            border_color=tokens.border,
            corner_radius=tokens.radius_sm,
            font=tokens.font_md,
            **kwargs
        )


class LinearSegmentedButton(ctk.CTkSegmentedButton):
    """Segmented button with Linear styling"""
    
    def __init__(self, master, values=None, **kwargs):
        super().__init__(
            master,
            values=values or [],
            fg_color=tokens.surface,
            selected_color=tokens.accent,
            selected_hover_color=tokens.accent_hover,
            unselected_color=tokens.surface_elevated,
            unselected_hover_color=tokens.border_focus,
            text_color=tokens.text_primary,
            font=tokens.font_md,
            corner_radius=tokens.radius_md,
            height=36,
            **kwargs
        )


class StatusBadge(ctk.CTkLabel):
    """Status badge (loaded/not loaded states)"""
    
    def __init__(self, master, loaded=False, **kwargs):
        color = tokens.success if loaded else tokens.text_tertiary
        text = "✓ Loaded" if loaded else "Not loaded"
        super().__init__(
            master,
            text=text,
            font=tokens.font_sm,
            text_color=color,
            **kwargs
        )


class SectionHeader(ctk.CTkLabel):
    """Section header with consistent styling"""
    
    def __init__(self, master, text="", **kwargs):
        super().__init__(
            master,
            text=text,
            font=("Inter", 11, "bold"),
            text_color=tokens.text_tertiary,
            **kwargs
        )


class CardPreview(ctk.CTkFrame):
    """Preview card for images"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=tokens.surface,
            border_color=tokens.border,
            border_width=1,
            corner_radius=tokens.radius_md,
            **kwargs
        )


# ============== TOAST NOTIFICATION ==============

class Toast:
    """Toast notification - Linear style"""
    
    def __init__(self, parent, message, toast_type="info", duration=3000):
        self.window = ctk.CTkToplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        
        # Position at top-right
        parent.update_idletasks()
        x = parent.winfo_x() + parent.winfo_width() - 320
        y = parent.winfo_y() + 20
        self.window.geometry(f"300x60+{x}+{y}")
        
        # Colors by type
        colors = {
            "success": (tokens.success, "#052e16"),
            "error": (tokens.error, "#450a0a"),
            "warning": (tokens.warning, "#451a03"),
            "info": (tokens.accent, "#1e1b4b"),
        }
        accent, bg = colors.get(toast_type, colors["info"])
        
        self.window.configure(fg_color=bg)
        
        # Frame
        frame = ctk.CTkFrame(self.window, fg_color="transparent", corner_radius=0)
        frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Indicator bar
        indicator = ctk.CTkFrame(frame, fg_color=accent, width=3, corner_radius=0)
        indicator.pack(side="left", fill="y", padx=(0, 12))
        
        # Text
        label = ctk.CTkLabel(
            frame,
            text=message,
            font=tokens.font_md,
            text_color=tokens.text_primary,
            anchor="w"
        )
        label.pack(side="left", fill="both", expand=True, pady=12)
        
        # Animate in
        self._animate_in()
        
        # Auto-dismiss
        self.window.after(duration, self._dismiss)
    
    def _animate_in(self):
        for i in range(10):
            self.window.attributes("-alpha", i / 10)
            self.window.update()
            time.sleep(0.02)
    
    def _dismiss(self):
        for i in range(10, -1, -1):
            self.window.attributes("-alpha", i / 10)
            self.window.update()
            time.sleep(0.02)
        self.window.destroy()


# ============== LOADING OVERLAY ==============

class LoadingOverlay:
    """Full-screen loading overlay"""
    
    def __init__(self, parent, message="Loading..."):
        self.window = ctk.CTkToplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-alpha", 0)
        
        parent.update_idletasks()
        x = parent.winfo_x()
        y = parent.winfo_y()
        self.window.geometry(f"{parent.winfo_width()}x{parent.winfo_height()}+{x}+{y}")
        
        self.window.configure(fg_color="#0D0D0FCC")
        
        # Content
        frame = ctk.CTkFrame(self.window, fg_color=tokens.surface, corner_radius=tokens.radius_lg)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Spinner indicator
        spinner = ctk.CTkLabel(
            frame,
            text="⟳",
            font=("Inter", 24),
            text_color=tokens.accent
        )
        spinner.pack(pady=(20, 10))
        
        self.label = ctk.CTkLabel(
            frame,
            text=message,
            font=tokens.font_md,
            text_color=tokens.text_primary
        )
        self.label.pack(pady=(0, 20))
        
        # Animate in
        for i in range(10):
            self.window.attributes("-alpha", i / 10)
            self.window.update()
            time.sleep(0.02)
    
    def update_message(self, message):
        self.label.configure(text=message)
        self.window.update()
    
    def dismiss(self):
        for i in range(10, -1, -1):
            self.window.attributes("-alpha", i / 10)
            self.window.update()
            time.sleep(0.02)
        self.window.destroy()


# ============== MAIN APPLICATION ==============

class IDCreatorApp(ctk.CTk):
    """ID Creator - Calm and Technical UI"""
    
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.CARD_W_INCHES = DEFAULT_CARD_WIDTH_INCHES
        self.CARD_H_INCHES = DEFAULT_CARD_HEIGHT_INCHES
        self.CARD_W = int(self.CARD_W_INCHES * DPI)
        self.CARD_H = int(self.CARD_H_INCHES * DPI)
        self.COLS = DEFAULT_COLS
        self.ROWS = DEFAULT_ROWS
        self.MAX_PER_PAGE = self.COLS * self.ROWS
        
        # State
        self.front_path = None
        self.back_path = None
        self.copies = self.MAX_PER_PAGE
        
        # Calculate layout
        self._calculate_gaps()
        
        # Window setup
        self.title("GridCopy Pro - Print Ready")
        self.geometry("1200x800")
        self.configure(fg_color=tokens.bg)
        
        self._setup_ui()
        self._update_preview()
    
    def _calculate_gaps(self):
        total_w = self.COLS * self.CARD_W
        total_h = self.ROWS * self.CARD_H
        self.GAP_X = (PAGE_WIDTH - total_w) / (self.COLS + 1)
        self.GAP_Y = (PAGE_HEIGHT - total_h) / (self.ROWS + 1)
    
    def _setup_ui(self):
        """Setup the UI layout"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ============== LEFT SIDEBAR ==============
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=tokens.surface,
            corner_radius=0,
            width=320
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Header
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=64)
        header.pack(fill="x", padx=tokens.s6, pady=(tokens.s6, tokens.s4))
        
        ctk.CTkLabel(
            header,
            text="GridCopy Pro",
            font=tokens.font_xl,
            text_color=tokens.text_primary
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Print Ready",
            font=tokens.font_sm,
            text_color=tokens.text_tertiary
        ).pack(anchor="w")
        
        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=tokens.border).pack(fill="x", padx=tokens.s6)
        
        # Scrollable content
        self.sidebar_content = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=tokens.surface_elevated,
            scrollbar_button_hover_color=tokens.border_focus
        )
        self.sidebar_content.pack(fill="both", expand=True, pady=tokens.s4)
        
        # ============== SECTION: IMAGES ==============
        SectionHeader(self.sidebar_content, text="IMAGES").pack(anchor="w", pady=(0, tokens.s2))
        
        self.btn_front = LinearButton(
            self.sidebar_content,
            text="Load Front Image",
            variant="secondary",
            command=lambda: self._load_image("front")
        )
        self.btn_front.pack(fill="x", pady=(0, tokens.s2))
        
        self.badge_front = StatusBadge(self.sidebar_content)
        self.badge_front.pack(anchor="w", pady=(0, tokens.s4))
        
        self.btn_back = LinearButton(
            self.sidebar_content,
            text="Load Back Image",
            variant="secondary",
            command=lambda: self._load_image("back")
        )
        self.btn_back.pack(fill="x", pady=(0, tokens.s2))
        
        self.badge_back = StatusBadge(self.sidebar_content)
        self.badge_back.pack(anchor="w", pady=(0, tokens.s6))
        
        # ============== SECTION: VIEW ==============
        SectionHeader(self.sidebar_content, text="VIEW").pack(anchor="w", pady=(0, tokens.s2))
        
        self.seg_view = LinearSegmentedButton(
            self.sidebar_content,
            values=["Front", "Back"]
        )
        self.seg_view.set("Front")
        self.seg_view.pack(fill="x", pady=(0, tokens.s6))
        
        # ============== SECTION: COPIES ==============
        SectionHeader(self.sidebar_content, text="NUMBER OF COPIES").pack(anchor="w", pady=(0, tokens.s2))
        
        self.input_copies = LinearInput(
            self.sidebar_content,
            placeholder=f"1 - {self.MAX_PER_PAGE}"
        )
        self.input_copies.insert(0, str(self.MAX_PER_PAGE))
        self.input_copies.pack(fill="x", pady=(0, tokens.s3))
        self.input_copies.bind("<KeyRelease>", lambda e: self._update_preview())
        
        # Quick select buttons (1-10)
        copies_frame = ctk.CTkFrame(self.sidebar_content, fg_color="transparent")
        copies_frame.pack(fill="x", pady=(0, tokens.s6))
        
        for i in range(2):
            for j in range(5):
                qty = i * 5 + j + 1
                btn = ctk.CTkButton(
                    copies_frame,
                    text=str(qty),
                    command=lambda q=qty: self._set_copies(q),
                    width=44,
                    height=36,
                    corner_radius=tokens.radius_sm,
                    fg_color=tokens.surface_elevated,
                    hover_color=tokens.border_focus,
                    text_color=tokens.text_primary,
                    font=tokens.font_sm
                )
                btn.grid(row=i, column=j, padx=2, pady=2)
        
        # ============== SECTION: OPTIONS ==============
        SectionHeader(self.sidebar_content, text="OPTIONS").pack(anchor="w", pady=(0, tokens.s2))
        
        self.check_marks = LinearCheckbox(
            self.sidebar_content,
            text="Show crop marks",
            command=self._update_preview
        )
        self.check_marks.pack(anchor="w", pady=tokens.s1)
        
        self.check_safe = LinearCheckbox(
            self.sidebar_content,
            text="Show safe zone",
            command=self._update_preview
        )
        self.check_safe.pack(anchor="w", pady=tokens.s6)
        
        # ============== SECTION: INFO ==============
        SectionHeader(self.sidebar_content, text="LAYOUT INFO").pack(anchor="w", pady=(0, tokens.s2))
        
        info_text = f"""Card: {self.CARD_W_INCHES}" × {self.CARD_H_INCHES}"
Grid: {self.COLS} × {self.ROWS} ({self.MAX_PER_PAGE}/page)
A4: 8.27" × 11.69" (595 × 842 pt)"""
        
        info_label = ctk.CTkLabel(
            self.sidebar_content,
            text=info_text,
            font=tokens.font_sm,
            text_color=tokens.text_secondary,
            justify="left"
        )
        info_label.pack(anchor="w", pady=(0, tokens.s8))
        
        # ============== EXPORT BUTTON ==============
        self.btn_export = LinearButton(
            self.sidebar_content,
            text="Export to PDF",
            variant="primary",
            size="lg",
            command=self._export_pdf
        )
        self.btn_export.pack(fill="x", pady=tokens.s4)
        
        # ============== RIGHT PREVIEW PANEL ==============
        self.preview_panel = ctk.CTkFrame(
            self,
            fg_color=tokens.bg,
            corner_radius=0
        )
        self.preview_panel.grid(row=0, column=1, sticky="nsew")
        
        # Preview header
        preview_header = ctk.CTkFrame(self.preview_panel, fg_color="transparent")
        preview_header.pack(fill="x", padx=tokens.s6, pady=tokens.s4)
        
        ctk.CTkLabel(
            preview_header,
            text="Preview",
            font=tokens.font_md,
            text_color=tokens.text_secondary
        ).pack(side="left")
        
        self.preview_count = ctk.CTkLabel(
            preview_header,
            text="10 cards",
            font=tokens.font_sm,
            text_color=tokens.text_tertiary
        )
        self.preview_count.pack(side="right")
        
        # Preview canvas
        self.preview_canvas = ctk.CTkCanvas(
            self.preview_panel,
            bg=tokens.bg,
            highlightthickness=0,
            bd=0
        )
        self.preview_canvas.pack(fill="both", expand=True, padx=tokens.s6, pady=(0, tokens.s6))
    
    def _load_image(self, side):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if path:
            if side == "front":
                self.front_path = path
                self.badge_front.configure(text="✓ Front loaded", text_color=tokens.success)
            else:
                self.back_path = path
                self.badge_back.configure(text="✓ Back loaded", text_color=tokens.success)
            
            Toast(self, f"Loaded {side} image", "success")
            self._update_preview()
    
    def _set_copies(self, qty):
        self.input_copies.delete(0, "end")
        self.input_copies.insert(0, str(qty))
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview canvas"""
        self.preview_canvas.delete("all")
        
        # Get copies
        try:
            copies = int(self.input_copies.get())
        except ValueError:
            copies = self.MAX_PER_PAGE
        
        copies = max(1, min(copies, self.MAX_PER_PAGE))
        self.preview_count.configure(text=f"{copies} card{'s' if copies != 1 else ''}")
        
        # Canvas dimensions
        cw = self.preview_canvas.winfo_width() or 800
        ch = self.preview_canvas.winfo_height() or 600
        
        # Calculate scale to fit A4
        scale_x = cw / PAGE_WIDTH
        scale_y = ch / PAGE_HEIGHT
        scale = min(scale_x, scale_y) * 0.9
        
        # Center offset
        disp_w = PAGE_WIDTH * scale
        disp_h = PAGE_HEIGHT * scale
        offset_x = (cw - disp_w) / 2
        offset_y = (ch - disp_h) / 2
        
        # Draw page background
        self.preview_canvas.create_rectangle(
            offset_x, offset_y, offset_x + disp_w, offset_y + disp_h,
            fill=tokens.surface_elevated,
            outline=tokens.border,
            width=1
        )
        
        # Determine which image to show
        view = self.seg_view.get().lower()
        img_path = self.front_path if view == "front" else self.back_path
        
        # Draw cards
        for i in range(copies):
            row = i // self.COLS
            col = i % self.COLS
            
            # Card position
            x = offset_x + scale * (self.GAP_X + col * (self.CARD_W + self.GAP_X))
            y = offset_y + scale * (self.GAP_Y + row * (self.CARD_H + self.GAP_Y))
            w = self.CARD_W * scale
            h = self.CARD_H * scale
            
            # Card background
            self.preview_canvas.create_rectangle(
                x, y, x + w, y + h,
                fill=tokens.surface,
                outline=tokens.border,
                width=1
            )
            
            # Show image if loaded
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img_w, img_h = img.size
                    s = min((w - 8) / img_w, (h - 8) / img_h)
                    new_w, new_h = int(img_w * s), int(img_h * s)
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    if not hasattr(self, '_photo_refs'):
                        self._photo_refs = []
                    self._photo_refs.append(photo)
                    
                    self.preview_canvas.create_image(
                        x + (w - new_w) / 2, y + (h - new_h) / 2,
                        image=photo,
                        anchor="nw"
                    )
                except:
                    self._draw_card_placeholder(i + 1)
            else:
                self._draw_card_placeholder(i + 1)
            
            # Crop marks
            if self.check_marks.get():
                mk = 8 * scale
                self.preview_canvas.create_line(x - mk, y, x + mk, y, fill=tokens.error, width=1)
                self.preview_canvas.create_line(x, y - mk, x, y + mk, fill=tokens.error, width=1)
                self.preview_canvas.create_line(x + w - mk, y, x + w + mk, y, fill=tokens.error, width=1)
                self.preview_canvas.create_line(x + w, y - mk, x + w, y + mk, fill=tokens.error, width=1)
                self.preview_canvas.create_line(x - mk, y + h, x + mk, y + h, fill=tokens.error, width=1)
                self.preview_canvas.create_line(x, y + h - mk, x, y + h + mk, fill=tokens.error, width=1)
                self.preview_canvas.create_line(x + w - mk, y + h, x + w + mk, y + h, fill=tokens.error, width=1)
                self.preview_canvas.create_line(x + w, y + h - mk, x + w, y + h + mk, fill=tokens.error, width=1)
    
    def _draw_card_placeholder(self, number):
        """Draw placeholder when no image"""
        pass  # Cards show empty by default
    
    def _export_pdf(self):
        """Export to PDF with loading overlay"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        
        # Validate
        try:
            copies = int(self.input_copies.get())
        except ValueError:
            Toast(self, "Invalid copy number", "error")
            return
        
        if not self.front_path and not self.back_path:
            Toast(self, "Load at least one image", "warning")
            return
        
        # Get save path
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        
        if not save_path:
            return
        
        # Show loading
        loading = LoadingOverlay(self, "Generating PDF...")
        
        def do_export():
            try:
                c = canvas.Canvas(save_path, pagesize=A4)
                
                images = []
                if self.front_path:
                    images.append(self.front_path)
                if self.back_path:
                    images.append(self.back_path)
                
                total = len(images) * copies
                count = 0
                
                for img_path in images:
                    cards_placed = 0
                    
                    while cards_placed < copies:
                        loading.update_message(f"Processing card {count + 1}/{total}")
                        
                        for row in range(self.ROWS):
                            for col in range(self.COLS):
                                if cards_placed >= copies:
                                    break
                                
                                x = self.GAP_X + col * (self.CARD_W + self.GAP_X)
                                y = PAGE_HEIGHT - (self.GAP_Y + (row + 1) * self.CARD_H + row * self.GAP_Y)
                                
                                c.rect(x, y, self.CARD_W, self.CARD_H)
                                
                                try:
                                    img = Image.open(img_path)
                                    margin = 10
                                    max_w = self.CARD_W - 2 * margin
                                    max_h = self.CARD_H - 2 * margin
                                    s = min(max_w / img.size[0], max_h / img.size[1])
                                    new_w = img.size[0] * s
                                    new_h = img.size[1] * s
                                    img_x = x + margin + (max_w - new_w) / 2
                                    img_y = y + (self.CARD_H - new_h) / 2
                                    c.drawImage(ImageReader(img), img_x, img_y, width=new_w, height=new_h)
                                except:
                                    pass
                                
                                cards_placed += 1
                                count += 1
                            
                            if cards_placed < copies:
                                c.showPage()
                        
                        if cards_placed < copies:
                            c.showPage()
                
                c.save()
                
                self.after(0, loading.dismiss)
                self.after(100, lambda: Toast(self, f"PDF saved!", "success"))
                self.after(100, lambda: messagebox.showinfo("Success", f"Saved to:\n{save_path}"))
                
            except Exception as e:
                self.after(0, loading.dismiss)
                self.after(100, lambda: Toast(self, f"Error: {e}", "error"))
        
        threading.Thread(target=do_export, daemon=True).start()


# ============== ENTRY POINT ==============
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    
    parser = argparse.ArgumentParser(description="ID Creator")
    parser.add_argument('--card-w', type=float, default=DEFAULT_CARD_WIDTH_INCHES)
    parser.add_argument('--card-h', type=float, default=DEFAULT_CARD_HEIGHT_INCHES)
    parser.add_argument('--cols', type=int, default=DEFAULT_COLS)
    parser.add_argument('--rows', type=int, default=DEFAULT_ROWS)
    
    args = parser.parse_args()
    
    app = IDCreatorApp()
    app.mainloop()