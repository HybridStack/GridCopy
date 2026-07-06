import streamlit as st
from PIL import Image, ImageDraw
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="GridCopy Pro", page_icon="🪪", layout="wide")

CARD_W_INCHES = 3.5
CARD_H_INCHES = 2.25
DPI = 72
CARD_W = int(CARD_W_INCHES * DPI)
CARD_H = int(CARD_H_INCHES * DPI)
COLS = 2
ROWS = 5
MAX_PER_PAGE = COLS * ROWS
PAGE_W, PAGE_H = A4


def calculate_gaps():
    total_w = COLS * CARD_W
    total_h = ROWS * CARD_H
    gap_x = (PAGE_W - total_w) / (COLS + 1)
    gap_y = (PAGE_H - total_h) / (ROWS + 1)
    return gap_x, gap_y


def create_preview(front_img_data, back_img_data, view, qty, show_crop, show_safe):
    GAP_X, GAP_Y = calculate_gaps()
    scale = 1.2
    preview_w = int(PAGE_W * scale)
    preview_h = int(PAGE_H * scale)

    img = Image.new("RGB", (preview_w, preview_h), "#18181b")
    draw = ImageDraw.Draw(img)
    s = scale

    img_data = front_img_data if view == "Front" else back_img_data

    for i in range(qty):
        row = i // COLS
        col = i % COLS

        x = s * (GAP_X + col * (CARD_W + GAP_X))
        y = s * (GAP_Y + row * (CARD_H + GAP_Y))
        w = CARD_W * s
        h = CARD_H * s

        cx, cy = x + w / 2, y + h / 2

        draw.rectangle([x, y, x + w, y + h], outline="#3f3f46", width=2)

        if img_data:
            try:
                card_img = Image.open(img_data)
                card_img.thumbnail((int(w - 6), int(h - 6)), Image.Resampling.LANCZOS)
                paste_x = int(x + (w - card_img.width) / 2)
                paste_y = int(y + (h - card_img.height) / 2)
                if card_img.mode == "RGBA":
                    img.paste(card_img, (paste_x, paste_y), card_img)
                else:
                    img.paste(card_img, (paste_x, paste_y))
            except Exception:
                pass

        if show_crop:
            mk = s * 8
            for dx, dy in [(0, 0), (w, 0), (0, h), (w, h)]:
                fx, fy = x + dx, y + dy
                draw.line([(fx - mk, fy), (fx + mk, fy)], fill="#ef4444", width=2)
                draw.line([(fx, fy - mk), (fx, fy + mk)], fill="#ef4444", width=2)

        if show_safe:
            safe = 0.2 * DPI * s
            draw.rectangle(
                [x + safe, y + safe, x + w - safe, y + h - safe],
                outline="#f59e0b",
                width=1,
            )

    return img


def generate_pdf_bytes(front_img_data, back_img_data, qty):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    GAP_X, GAP_Y = calculate_gaps()

    images = []
    if front_img_data:
        images.append(("Front", front_img_data))
    if back_img_data:
        images.append(("Back", back_img_data))

    if not images:
        return None

    for _, img_data in images:
        cards_placed = 0
        while cards_placed < qty:
            for row in range(ROWS):
                for col in range(COLS):
                    if cards_placed >= qty:
                        break
                    x = GAP_X + col * (CARD_W + GAP_X)
                    y = PAGE_H - (GAP_Y + (row + 1) * CARD_H + row * GAP_Y)

                    c.rect(x, y, CARD_W, CARD_H)

                    try:
                        img = Image.open(img_data)
                        margin = 10
                        max_w = CARD_W - 2 * margin
                        max_h = CARD_H - 2 * margin
                        iw, ih = img.size
                        s = min(max_w / iw, max_h / ih)
                        nw, nh = iw * s, ih * s
                        ix = x + margin + (max_w - nw) / 2
                        iy = y + (CARD_H - nh) / 2
                        c.drawImage(ImageReader(img), ix, iy, width=nw, height=nh)
                    except Exception:
                        pass

                    cards_placed += 1
                if cards_placed >= qty:
                    break
            if cards_placed < qty:
                c.showPage()

    c.save()
    buf.seek(0)
    return buf


st.title("GridCopy Pro")
st.markdown("Upload images and generate printable A4 PDF sheets of ID cards.")

# Initialize session state
if "front_img" not in st.session_state:
    st.session_state.front_img = None
if "back_img" not in st.session_state:
    st.session_state.back_img = None

with st.sidebar:
    st.header("1. Upload Images")
    front = st.file_uploader(
        "Front Image", type=["png", "jpg", "jpeg", "bmp"], key="front_uploader"
    )
    back = st.file_uploader(
        "Back Image", type=["png", "jpg", "jpeg", "bmp"], key="back_uploader"
    )

    if front:
        st.session_state.front_img = front.getvalue()
    if back:
        st.session_state.back_img = back.getvalue()

    st.divider()

    st.header("2. View")
    view = st.segmented_control("View", ["Front", "Back"], default="Front")

    st.divider()

    st.header("3. Quantity")
    qty = st.number_input(
        "Copies",
        min_value=1,
        max_value=MAX_PER_PAGE,
        value=MAX_PER_PAGE,
        label_visibility="collapsed",
    )

    st.divider()

    st.header("4. Options")
    show_crop = st.checkbox("Crop marks", value=False)
    show_safe = st.checkbox("Safe zone", value=False)

    st.divider()

    st.header("5. Export")

    front_data = st.session_state.front_img
    back_data = st.session_state.back_img

    if st.button("Generate PDF", type="primary", use_container_width=True):
        if not front_data and not back_data:
            st.error("Please upload at least one image (front or back)")
        else:
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf_bytes(
                    io.BytesIO(front_data) if front_data else None,
                    io.BytesIO(back_data) if back_data else None,
                    qty,
                )
                if pdf_bytes:
                    front_label = "Front" if front_data else ""
                    back_label = "Back" if back_data else ""
                    label = f"ID_Cards_{front_label}_{back_label}".strip().replace(
                        " ", "_"
                    ).replace("__", "_").strip("_")
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"{label}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("PDF ready for download!")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Layout Preview")
    front_data = st.session_state.front_img
    back_data = st.session_state.back_img
    preview = create_preview(
        io.BytesIO(front_data) if front_data else None,
        io.BytesIO(back_data) if back_data else None,
        view,
        qty,
        show_crop,
        show_safe,
    )
    st.image(preview, use_container_width=True)

with col2:
    st.subheader("Preview Info")
    st.markdown(
        f"""
- **Card size:** {CARD_W_INCHES}" × {CARD_H_INCHES}"
- **Page:** A4 ({PAGE_W:.0f} × {PAGE_H:.0f} pt)
- **Grid:** {COLS} × {ROWS} ({MAX_PER_PAGE} cards/page)
- **Copies:** {qty}
- **Front image:** {"✅" if front_data else "❌"} Loaded
- **Back image:** {"✅" if back_data else "❌"} Loaded
    """
    )

    with st.expander("How to use"):
        st.markdown(
            """
1. Upload front/back images in the sidebar
2. Choose view (Front/Back) for preview
3. Set number of copies (1–10)
4. Toggle crop marks and safe zone if needed
5. Click **Generate PDF** then download
            """
        )
