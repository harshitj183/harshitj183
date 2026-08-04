import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

def get_dot_path(dithered_img):
    """
    Generate a single combined SVG <path> data string for all dithered dots
    to keep SVG file size extremely small.
    Each dot is represented as a 1.2x1.2px rectangle.
    """
    path_data = []
    width, height = dithered_img.size
    pixels = np.array(dithered_img)
    
    for y in range(height):
        for x in range(width):
            if pixels[y, x] == 0:  # Active dot (black in 1-bit)
                # Left align visual map starting at offset, scale size by 1.2
                dx = 70 + x * 1.2
                dy = 120 + y * 1.2
                path_data.append(f"M {dx:.1f} {dy:.1f} h 1.2 v 1.2 h -1.2 z")
                
    return " ".join(path_data)

def dither_image(image_path, dark_mode=True):
    # Load image and convert to RGB
    img = Image.open(image_path).convert("RGB")
    
    # 1. Background Segmentation (for Dark Mode)
    # The avatar profileLOgo.png has a distinct solid yellow background: #FFCC00 (approx RGB: 255, 204, 0)
    # Sample the color from the top left pixel to be highly accurate
    bg_rgb = img.getpixel((5, 5))
    
    # Resize to target 300x340 grid
    img_resized = img.resize((300, 340), Image.Resampling.LANCZOS)
    
    # Apply contrast adjustments and filters as requested:
    # "Contrast 1.3x only, with autocontrast(cutoff=1) + UnsharpMask(radius=3, percent=140)"
    img_contrast = ImageOps.autocontrast(img_resized, cutoff=1)
    img_contrast = img_contrast.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    
    # Adjust contrast manually to 1.3x
    enhancer = ImageEnhance.Contrast(img_contrast)
    img_filtered = enhancer.enhance(1.3)
    
    # Convert filtered to grayscale for dithering
    gray_img = img_filtered.convert("L")
    gray_pixels = np.array(gray_img, dtype=float)
    
    # Resized RGB image to check background distance
    rgb_pixels = np.array(img_filtered)
    
    # Euclidean distance to yellow background in RGB space
    bg_dist = np.linalg.norm(rgb_pixels - np.array(bg_rgb), axis=2)
    bg_mask = bg_dist < 60  # Mask true for background pixels
    
    # Post-processing mask: binary closing / fill holes
    from scipy.ndimage import binary_closing, binary_fill_holes
    bg_mask_closed = binary_closing(bg_mask, structure=np.ones((3, 3)))
    subject_mask = ~binary_fill_holes(bg_mask_closed)
    
    # Floyd-Steinberg dithering with Serpentine order
    h, w = gray_pixels.shape
    out = np.zeros_like(gray_pixels, dtype=int)
    
    for y in range(h):
        # Serpentine scan order
        x_range = range(w) if y % 2 == 0 else range(w - 1, -1, -1)
        for x in x_range:
            old_val = gray_pixels[y, x]
            
            # Determine threshold
            if dark_mode:
                # Segment background out: if background, make it black (no dots)
                if not subject_mask[y, x]:
                    new_val = 255  # White in grayscale = no dot in output path
                else:
                    new_val = 0 if old_val < 128 else 255
            else:
                # Light mode: keep background, dither everything
                new_val = 0 if old_val < 128 else 255
                
            out[y, x] = new_val
            err = old_val - new_val
            
            # Distribute error to neighbors (Floyd-Steinberg coefficients)
            # Serpentine direction changes neighbor offsets
            if y % 2 == 0:
                # Scan direction: Right
                if x + 1 < w:
                    gray_pixels[y, x + 1] += err * 7 / 16
                if y + 1 < h:
                    if x - 1 >= 0:
                        gray_pixels[y + 1, x - 1] += err * 3 / 16
                    gray_pixels[y + 1, x] += err * 5 / 16
                    if x + 1 < w:
                        gray_pixels[y + 1, x + 1] += err * 1 / 16
            else:
                # Scan direction: Left
                if x - 1 >= 0:
                    gray_pixels[y, x - 1] += err * 7 / 16
                if y + 1 < h:
                    if x + 1 < w:
                        gray_pixels[y + 1, x + 1] += err * 3 / 16
                    gray_pixels[y + 1, x] += err * 5 / 16
                    if x - 1 >= 0:
                        gray_pixels[y + 1, x - 1] += err * 1 / 16
                        
    # Convert numpy array back to 1-bit Image
    dithered_img = Image.fromarray(out.astype(np.uint8)).convert("1")
    return dithered_img

def generate_svg(dithered_img, dark_mode=True):
    # Palette definition from theme.md
    if dark_mode:
        bg_color = "#0A101F"
        terminal_bg = "#111827"
        text_primary = "#22D3EE"      # Cyan UI chrome
        text_secondary = "#8C98B7"    # Slate leaders
        portrait_color = "#A78BFA"    # Light Purple dots
        accent_color = "#10B981"      # Green pill / status
        text_white = "#ccd6f5"
        border_color = "#1f305e"
    else:
        bg_color = "#f3f8fd"
        terminal_bg = "#ffffff"
        text_primary = "#0891B2"      # Darker Cyan UI chrome
        text_secondary = "#4d598c"    # Muted secondary text
        portrait_color = "#7C3AED"    # Deep Purple dots
        accent_color = "#10B981"      # Green status
        text_white = "#1f305e"
        border_color = "#d7e8f9"

    dot_path = get_dot_path(dithered_img)
    
    # System Info layout lines
    info_rows = [
        ("Subject", "Harshit Jaiswal"),
        ("Role", "SDE | AI & Full Stack Engineer"),
        ("Origin", "Gurugram, Delhi NCR, India"),
        ("Education", "B.Tech CSE @ KR Mangalam University (2023-2027)"),
        ("Status", "Building + Learning + Shipping"),
        ("ToolChain", "VS Code, Git, Docker, Postman, Linux"),
        ("Core.Lang", "JavaScript, TypeScript, C++, Python, SQL"),
        ("Core.Frontend", "React, Next.js, HTML5, CSS3, Tailwind CSS"),
        ("Core.Backend", "Node.js, FastAPI, Bun.js, Express.js"),
        ("Core.Database", "PostgreSQL, MongoDB, MySQL, Firebase"),
        ("Core.Infra", "Docker, GitHub Actions, Nginx, AWS, Cloudflare"),
        ("Grid.Mail", "harshitj183@gmail.com"),
        ("Grid.Portfolio", "harshitj183.in"),
        ("Grid.LinkedIn", "linkedin.com/in/harshitj183"),
        ("Grid.GitHub", "github.com/harshitj183"),
        ("Grid.LeetCode", "leetcode.com/harshitj183")
    ]
    
    # Generate SVG content
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">')
    
    # Styles for animation & fonts
    svg.append('''  <style>
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }
    .live-pulse {
      animation: pulse 1.8s infinite ease-in-out;
    }
    .terminal-text {
      font-family: "Fira Code", "SF Mono", "Courier New", monospace;
      font-size: 14px;
      font-weight: 500;
    }
  </style>''')
    
    # Background
    svg.append(f'  <rect width="1180" height="610" rx="12" fill="{bg_color}" />')
    
    # Terminal Window Container
    svg.append(f'  <rect x="20" y="20" width="1140" height="570" rx="10" fill="{terminal_bg}" stroke="{border_color}" stroke-width="2" />')
    
    # Terminal Title Bar
    svg.append(f'  <path d="M 20 50 L 1160 50" stroke="{border_color}" stroke-width="1.5" />')
    
    # Terminal Dots (Close, Minimize, Maximize)
    svg.append(f'  <circle cx="45" cy="35" r="6" fill="#ff5f56" />')
    svg.append(f'  <circle cx="65" cy="35" r="6" fill="#ffbd2e" />')
    svg.append(f'  <circle cx="85" cy="35" r="6" fill="#27c93f" />')
    
    # Terminal Title Text
    svg.append(f'  <text x="590" y="40" fill="{text_secondary}" font-family="monospace" font-size="14" text-anchor="middle" font-weight="600">profile.sh --live</text>')
    
    # Visual Map Portrait Frame Border
    svg.append(f'  <rect x="50" y="90" width="400" height="460" rx="6" fill="none" stroke="{border_color}" stroke-width="1.5" />')
    svg.append(f'  <rect x="70" y="82" width="90" height="16" fill="{terminal_bg}" />')
    svg.append(f'  <text x="75" y="94" fill="{text_primary}" class="terminal-text" font-size="12" font-weight="bold">VISUAL.MAP</text>')
    
    # Draw Dithered Portrait Dots
    svg.append(f'  <path d="{dot_path}" fill="{portrait_color}" shape-rendering="crispEdges" />')
    
    # Right Side: System Info Panel Frame
    svg.append(f'  <rect x="490" y="90" width="640" height="460" rx="6" fill="none" stroke="{border_color}" stroke-width="1.5" />')
    svg.append(f'  <rect x="510" y="82" width="100" height="16" fill="{terminal_bg}" />')
    svg.append(f'  <text x="515" y="94" fill="{text_primary}" class="terminal-text" font-size="12" font-weight="bold">SYSTEM.INFO</text>')
    
    # Pulse Badge & Colored Pill
    svg.append(f'  <g transform="translate(930, 70)">')
    # Pulse Red Circle
    svg.append(f'    <circle cx="10" cy="12" r="5" fill="#ef4444" class="live-pulse" />')
    svg.append(f'    <text x="22" y="16" fill="#ef4444" font-family="monospace" font-size="11" font-weight="bold">LIVE</text>')
    # Colored pill with handle
    svg.append(f'    <rect x="70" y="2" width="110" height="20" rx="10" fill="{accent_color}" />')
    svg.append(f'    <text x="125" y="15" fill="#ffffff" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">@harshitj183</text>')
    svg.append(f'  </g>')
    
    # Write each neofetch metadata line using the textLength alignment trick
    start_y = 135
    for i, (label, val) in enumerate(info_rows):
        y_pos = start_y + i * 25
        
        # Format text line: key, dots, val
        svg.append(f'  <text x="520" y="{y_pos}" class="terminal-text" textLength="580" lengthAdjust="spacingAndGlyphs">')
        svg.append(f'    <tspan fill="{text_primary}">{label.ljust(15, ".")}</tspan>')
        svg.append(f'    <tspan fill="{text_secondary}">{"." * 30}</tspan>')
        svg.append(f'    <tspan fill="{text_white}"> {val}</tspan>')
        svg.append(f'  </text>')
        
    svg.append(f'</svg>')
    
    return "\n".join(svg)

def main():
    repo_root = "/home/harshitj183/harshitj183"
    avatar_path = os.path.join(repo_root, "badge", "profileLOgo.png")
    
    print("Generating dark dithered portrait...")
    dark_dithered = dither_image(avatar_path, dark_mode=True)
    dark_svg = generate_svg(dark_dithered, dark_mode=True)
    
    print("Generating light dithered portrait...")
    light_dithered = dither_image(avatar_path, dark_mode=False)
    light_svg = generate_svg(light_dithered, dark_mode=False)
    
    with open(os.path.join(repo_root, "dark.svg"), "w") as f:
        f.write(dark_svg)
        
    with open(os.path.join(repo_root, "light.svg"), "w") as f:
        f.write(light_svg)
        
    print("Successfully generated dark.svg and light.svg!")

if __name__ == "__main__":
    main()
