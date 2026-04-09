import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_proverb_post(image_path, quote_text, author_name, logo_path, output_name):
    POST_WIDTH, POST_HEIGHT = 1080, 1350
    PADDING = 80

    # -------------------------------
    # 1. LOAD & CROP
    # -------------------------------
    img = Image.open(image_path).convert("RGBA")

    ratio = POST_WIDTH / POST_HEIGHT
    if img.width / img.height > ratio:
        new_h = POST_HEIGHT
        new_w = int(img.width * (POST_HEIGHT / img.height))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        img = img.crop(((new_w - POST_WIDTH)//2, 0, (new_w + POST_WIDTH)//2, POST_HEIGHT))
    else:
        new_w = POST_WIDTH
        new_h = int(img.height * (POST_WIDTH / img.width))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        img = img.crop((0, (new_h - POST_HEIGHT)//2, POST_WIDTH, (new_h + POST_HEIGHT)//2))

    # Cinematic blur
    img = img.filter(ImageFilter.GaussianBlur(3))

    # -------------------------------
    # 2. DARK GRADIENT
    # -------------------------------
    gradient = Image.new('L', (1, POST_HEIGHT))
    for y in range(POST_HEIGHT):
        gradient.putpixel((0, y), int(255 * (y / POST_HEIGHT)))

    alpha = gradient.resize((POST_WIDTH, POST_HEIGHT))
    black = Image.new('RGBA', (POST_WIDTH, POST_HEIGHT), (0, 0, 0, 220))
    img = Image.composite(black, img, alpha).convert("RGB")

    draw = ImageDraw.Draw(img)

    # -------------------------------
    # 3. FONTS
    # -------------------------------
    font_path = "fonts/dejavu-sans-bold.ttf"
    quote_font = ImageFont.truetype(font_path, 95)
    author_font = ImageFont.truetype(font_path, 45)

    # -------------------------------
    # 4. HIGHLIGHT WORDS
    # -------------------------------
    power_words = ["sweat", "bleed", "war"]

    def highlight(text):
        return " ".join([
            f"*{w}*" if re.sub(r'\W', '', w).lower() in power_words else w
            for w in text.split()
        ])

    quote_text = highlight(quote_text)
    words = re.findall(r'\*\w+\*|\S+', quote_text)

    # -------------------------------
    # 5. WRAP TEXT
    # -------------------------------
    max_width = POST_WIDTH - PADDING * 2
    lines, current, width = [], [], 0

    for word in words:
        clean = word.replace("*", "")
        w = draw.textlength(clean + " ", font=quote_font)

        if width + w <= max_width:
            current.append(word)
            width += w
        else:
            lines.append(current)
            current = [word]
            width = w

    lines.append(current)

    # -------------------------------
    # 6. CENTERING
    # -------------------------------
    ascent, descent = quote_font.getmetrics()
    line_height = ascent + descent + 30
    total_h = len(lines) * line_height + 200
    y = (POST_HEIGHT - total_h) // 2

    # -------------------------------
    # 7. TEXT
    # -------------------------------
    for line in lines:
        line_w = sum(draw.textlength(w.replace("*","") + " ", font=quote_font) for w in line)
        x = (POST_WIDTH - line_w) // 2

        for word in line:
            clean = word.replace("*", "")
            color = (255,120,60) if "*" in word else (255,255,255)

            # soft shadow
            draw.text((x+3, y+3), clean, font=quote_font, fill=(0,0,0))

            # main
            draw.text((x, y), clean, font=quote_font, fill=color)

            x += draw.textlength(clean + " ", font=quote_font)

        y += line_height

    # -------------------------------
    # 8. AUTHOR
    # -------------------------------
    y += 40
    author = f"— {author_name.upper()}"

    bbox = draw.textbbox((0,0), author, font=author_font)
    ax = (POST_WIDTH - (bbox[2]-bbox[0])) // 2

    draw.text((ax, y), author, font=author_font, fill=(180,180,180))

    # -------------------------------
    # 9. LOGO
    # -------------------------------
    # 8. ADD FLOATING CIRCULAR LOGO (TOP RIGHT)
    try:
        # Load your already circular logo
        logo = Image.open(logo_path).convert("RGBA")
        
        # Resize logo
        logo_w = 120
        logo_h = int(logo.height * (logo_w / logo.width))
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Shadow Settings
        blur_radius = 25
        offset = (15, 15)  # Shadow offset (x, y)
        shadow_opacity = 140 # 0 to 255
        
        # Create a shadow image based on the logo's alpha channel
        # This makes the shadow perfectly circular because your logo is circular
        shadow = Image.new("RGBA", (logo_w + blur_radius * 2, logo_h + blur_radius * 2), (0, 0, 0, 0))
        
        # Extract the alpha channel of the logo to use as a mask for the shadow
        logo_alpha = logo.split()[3]
        
        # Paste a solid black shape using the logo's transparency mask
        shadow.paste((0, 0, 0, shadow_opacity), (blur_radius, blur_radius), mask=logo_alpha)
        
        # Apply blur to the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Coordinates for top-right
        lx = POST_WIDTH - logo_w - PADDING
        ly = PADDING
        
        # Paste Shadow first (with the blur offset correction), then Logo
        img.paste(shadow, (lx + offset[0] - blur_radius, ly + offset[1] - blur_radius), shadow)
        img.paste(logo, (lx, ly), logo)
        
    except FileNotFoundError:
        print("Logo not found, skipping...")

    # -------------------------------
    # SAVE
    # -------------------------------
    img.save(output_name, quality=95)
    print("🔥 FINAL PREMIUM POST CREATED:", output_name)

# RUN
if __name__ == "__main__":
    create_proverb_post(
        image_path="images/image3.jpg",
        quote_text="The more you sweat in training the less you bleed in war",
        author_name="Unknown",
        logo_path="profile.png",
        output_name="premium_post.jpg"
    )
