import qrcode
from PIL import Image, ImageDraw, ImageFont
import io

def generate_qr_code(url, classroom_name):
    """Generate QR code with classroom information"""
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Create a larger image to add text
    width, height = qr_img.size
    new_width = width
    new_height = height + 80  # Add space for text
    
    # Create new image with white background
    img = Image.new('RGB', (new_width, new_height), 'white')
    
    # Paste QR code
    img.paste(qr_img, (0, 40))
    
    # Add text
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a nice font
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 16)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 12)
    except:
        try:
            # Try DejaVu fonts as fallback
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            # Fallback to default font
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
    
    # School name
    school_text = "SENAI Morvan Figueiredo"
    bbox = draw.textbbox((0, 0), school_text, font=font_title)
    text_width = bbox[2] - bbox[0]
    x = (new_width - text_width) // 2
    draw.text((x, 5), school_text, fill="black", font=font_title)
    
    # Classroom name
    classroom_text = classroom_name
    bbox = draw.textbbox((0, 0), classroom_text, font=font_subtitle)
    text_width = bbox[2] - bbox[0]
    x = (new_width - text_width) // 2
    draw.text((x, 25), classroom_text, fill="black", font=font_subtitle)
    
    # Instructions at bottom
    instruction_text = "Escaneie para acessar informações da sala"
    bbox = draw.textbbox((0, 0), instruction_text, font=font_subtitle)
    text_width = bbox[2] - bbox[0]
    x = (new_width - text_width) // 2
    draw.text((x, new_height - 20), instruction_text, fill="gray", font=font_subtitle)
    
    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer
