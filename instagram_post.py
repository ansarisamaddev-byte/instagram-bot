import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

def create_proverb_post(image_path, quote_text, author_name, logo_path, output_name):
    POST_WIDTH, POST_HEIGHT = 1080, 1350
    BASE_PADDING = 80 

    # 1. Process and Crop the Background Image
    try:
        orig_bg = Image.open(image_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Background image not found at '{image_path}'")
        return

    if orig_bg.width / orig_bg.height > POST_WIDTH / POST_HEIGHT:
        new_height = POST_HEIGHT
        new_width = int(POST_HEIGHT * orig_bg.width / orig_bg.height)
        img_resized = orig_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        left = (new_width - POST_WIDTH) / 2
        post_image = img_resized.crop((left, 0, left + POST_WIDTH, POST_HEIGHT))
    else:
        new_width = POST_WIDTH
        new_height = int(POST_WIDTH * orig_bg.height / orig_bg.width)
        img_resized = orig_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        top = (new_height - POST_HEIGHT) / 2
        post_image = img_resized.crop((0, top, POST_WIDTH, top + POST_HEIGHT))

    post_image = post_image.convert("RGB")

    # 2. Add dark overlay for text readability
    overlay = Image.new('RGBA', (POST_WIDTH, POST_HEIGHT), (0, 0, 0, 110)) 
    post_image = Image.alpha_composite(post_image.convert('RGBA'), overlay).convert('RGB')

    # 3. Setup Fonts
    font_paths = ["C:\\Windows\\Fonts\\impact.ttf", "impact.ttf", "arialbd.ttf"]
    font_path = next((f for f in font_paths if os.path.exists(f)), None)
    if not font_path:
        raise OSError("Could not find a valid bold font.")

    quote_font = ImageFont.truetype(font_path, 80)
    author_font = ImageFont.truetype(font_path, 60)
    draw = ImageDraw.Draw(post_image)
    
    quote_color = (255, 255, 255) 
    highlight_color = (255, 100, 80) 

    # 4. Process the Quote Text
    words = re.findall(r'\*\w+\*|\S+', quote_text)
    wrapped_lines = []
    current_line = []
    current_line_width = 0
    max_text_width = POST_WIDTH - (BASE_PADDING * 2)

    for word in words:
        clean_word = word.replace("*", "")
        word_width = draw.textlength(clean_word, font=quote_font)
        space_width = draw.textlength(" ", font=quote_font)
        if current_line_width + word_width <= max_text_width:
            current_line.append(word)
            current_line_width += word_width + space_width
        else:
            wrapped_lines.append(current_line)
            current_line = [word]
            current_line_width = word_width + space_width
    wrapped_lines.append(current_line)

    # 5. Centering Calculations
    ascent, descent = quote_font.getmetrics()
    quote_line_height = ascent + descent + 15
    quote_block_height = len(wrapped_lines) * quote_line_height
    author_display_name = f"— {author_name}"
    author_bbox = draw.textbbox((0, 0), author_display_name, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    
    MIDDLE_PADDING_Y = 60
    total_content_height = quote_block_height + MIDDLE_PADDING_Y + author_height + 40
    current_y = (POST_HEIGHT / 2) - (total_content_height / 2)

    # 6. Draw Quote
    for line in wrapped_lines:
        line_draw_width = sum([draw.textlength(w.replace("*", "") + " ", font=quote_font) for w in line])
        current_x = (POST_WIDTH - line_draw_width) / 2
        for word in line:
            clean_word = word.replace("*", "")
            color = highlight_color if "*" in word else quote_color
            draw.text((current_x, current_y), clean_word, font=quote_font, fill=color)
            current_x += draw.textlength(clean_word + " ", font=quote_font)
        current_y += quote_line_height
        
    current_y += (MIDDLE_PADDING_Y / 2)

    # 7. Draw Author
    author_x = (POST_WIDTH - (author_bbox[2] - author_bbox[0])) / 2
    draw.text((author_x, current_y), author_display_name, font=author_font, fill=(255, 255, 255))
    current_y += author_height + 30
    line_len = 200
    draw.line([((POST_WIDTH-line_len)/2, current_y), ((POST_WIDTH+line_len)/2, current_y)], fill=(255, 255, 255), width=3)

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
        lx = POST_WIDTH - logo_w - BASE_PADDING
        ly = BASE_PADDING
        
        # Paste Shadow first (with the blur offset correction), then Logo
        post_image.paste(shadow, (lx + offset[0] - blur_radius, ly + offset[1] - blur_radius), shadow)
        post_image.paste(logo, (lx, ly), logo)
        
    except FileNotFoundError:
        print("Logo not found, skipping...")

    # 9. Final Save
    post_image.convert("RGB").save(output_name, quality=95)
    print(f"Success! Saved to {output_name}")

if __name__ == "__main__":
    # Ensure background.jpg and logo.png exist locally.
    create_proverb_post(
        image_path="images/image1.jpg",
        # Use *asterisks* to define highlighted words (like best/now)
        quote_text='"The *best* time to plant a tree was 20 years ago. The second *best* time is *now*."',
        author_name="Chinese Proverb",
        logo_path="profile.png", # Path to your transparent page logo
        output_name="page_proverb.jpg"
    )