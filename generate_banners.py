import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

def get_dither_paths(dithered_img, num_groups=12):
    """
    Split the dithered image dots into progressive horizontal bands/groups
    to animate the portrait scanning/fade-in.
    Returns a list of SVG path data strings.
    """
    width, height = dithered_img.size
    pixels = np.array(dithered_img)
    
    group_paths = [[] for _ in range(num_groups)]
    band_height = height / num_groups
    
    for y in range(height):
        # Determine which animation group this row belongs to (from top to bottom)
        group_idx = int(y / band_height)
        if group_idx >= num_groups:
            group_idx = num_groups - 1
            
        for x in range(width):
            if pixels[y, x] == 0:  # Active dot (black in 1-bit)
                # Position coordinates inside the VISUAL.MAP frame
                # Map width: 300 grid pixels -> scaled by 1.24 to ~372px
                # Map height: 340 grid pixels -> scaled by 1.35 to ~459px
                # Left offset starts at x=50, y=105 inside the frame
                dx = 50 + x * 1.24
                dy = 105 + y * 1.35
                group_paths[group_idx].append(f"M {dx:.1f} {dy:.1f} h 1.2 v 1.3 h -1.2 z")
                
    return [" ".join(p) for p in group_paths]

def dither_image(image_path, dark_mode=True):
    # Load image and convert to RGB
    img = Image.open(image_path).convert("RGB")
    
    # Background color is yellow: approx RGB (255, 204, 0)
    bg_rgb = img.getpixel((5, 5))
    
    # Target grid resolution (300x340)
    img_resized = img.resize((300, 340), Image.Resampling.LANCZOS)
    
    # Autocontrast + UnsharpMask
    img_contrast = ImageOps.autocontrast(img_resized, cutoff=1)
    img_contrast = img_contrast.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    
    # Contrast adjustment (1.3x)
    enhancer = ImageEnhance.Contrast(img_contrast)
    img_filtered = enhancer.enhance(1.3)
    
    # Gray conversion
    gray_img = img_filtered.convert("L")
    gray_pixels = np.array(gray_img, dtype=float)
    
    # Segmentation mask
    rgb_pixels = np.array(img_filtered)
    bg_dist = np.linalg.norm(rgb_pixels - np.array(bg_rgb), axis=2)
    bg_mask = bg_dist < 60
    
    from scipy.ndimage import binary_closing, binary_fill_holes
    bg_mask_closed = binary_closing(bg_mask, structure=np.ones((3, 3)))
    subject_mask = ~binary_fill_holes(bg_mask_closed)
    
    # Serpentine Floyd-Steinberg dithering
    h, w = gray_pixels.shape
    out = np.zeros_like(gray_pixels, dtype=int)
    
    for y in range(h):
        x_range = range(w) if y % 2 == 0 else range(w - 1, -1, -1)
        for x in x_range:
            old_val = gray_pixels[y, x]
            if dark_mode:
                if not subject_mask[y, x]:
                    new_val = 255
                else:
                    new_val = 0 if old_val < 128 else 255
            else:
                new_val = 0 if old_val < 128 else 255
                
            out[y, x] = new_val
            err = old_val - new_val
            
            if y % 2 == 0:
                if x + 1 < w:
                    gray_pixels[y, x + 1] += err * 7 / 16
                if y + 1 < h:
                    if x - 1 >= 0:
                        gray_pixels[y + 1, x - 1] += err * 3 / 16
                    gray_pixels[y + 1, x] += err * 5 / 16
                    if x + 1 < w:
                        gray_pixels[y + 1, x + 1] += err * 1 / 16
            else:
                if x - 1 >= 0:
                    gray_pixels[y, x - 1] += err * 7 / 16
                if y + 1 < h:
                    if x + 1 < w:
                        gray_pixels[y + 1, x + 1] += err * 3 / 16
                    gray_pixels[y + 1, x] += err * 5 / 16
                    if x - 1 >= 0:
                        gray_pixels[y + 1, x - 1] += err * 1 / 16
                        
    dithered_img = Image.fromarray(out.astype(np.uint8)).convert("1")
    return dithered_img

def make_text_row(label, value, y_pos, text_primary, text_secondary, text_white, begin_time):
    total_chars = 75
    dots_count = total_chars - len(label) - len(value)
    if dots_count < 5:
        dots_count = 5
    dots = "." * dots_count
    
    return f'''<g opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin_time:.2f}s" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin_time:.2f}s" fill="freeze"/>
  <text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve" class="terminal-text">
    <tspan fill="{text_primary}">{label} </tspan>
    <tspan fill="{text_secondary}">{dots}</tspan>
    <tspan fill="{text_white}" font-weight="600"> {value}</tspan>
  </text>
</g>'''

def generate_svg(dithered_img, dark_mode=True):
    # Palette parameters matching style
    if dark_mode:
        bg_outer = "#070B16"
        panel_start = "#0A101F"
        panel_end = "#0C1426"
        title_bar_bg = "#0B1222"
        border_color = "rgba(255,255,255,0.10)"
        frame_border = "rgba(34,211,238,0.35)"
        text_primary = "#22D3EE"      # Cyan
        text_secondary = "rgba(148,163,184,0.35)" # Dotted leaders opacity
        text_white = "#F8FAFC"
        text_muted = "#94A3B8"
        portrait_color = "#A78BFA"    # Purple dots
        accent_color = "#7C3AED"      # Email pill
        glow_filter = 'filter="url(#glow3)"'
    else:
        bg_outer = "#f0f4f8"
        panel_start = "#ffffff"
        panel_end = "#f4f8fc"
        title_bar_bg = "#e2ecf5"
        border_color = "rgba(0,0,0,0.08)"
        frame_border = "rgba(8,145,178,0.35)"
        text_primary = "#0891B2"      # Darker Cyan
        text_secondary = "rgba(77,89,140,0.35)"
        text_white = "#1f305e"        # Deep navy
        text_muted = "#4d598c"
        portrait_color = "#7C3AED"    # Deep Purple dots
        accent_color = "#0891B2"      # Email pill
        glow_filter = ''

    # Get progressive scanning paths
    num_groups = 12
    paths = get_dither_paths(dithered_img, num_groups)
    
    # System Info data rows
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
        ("Core.Infra", "Docker, GitHub Actions, Nginx, AWS, Cloudflare")
    ]
    
    contact_rows = [
        ("Grid.Mail", "harshitj183@gmail.com"),
        ("Grid.Portfolio", "harshitj183.in"),
        ("Grid.LinkedIn", "linkedin.com/in/harshitj183"),
        ("Grid.GitHub", "@harshitj183"),
        ("Grid.LeetCode", "leetcode.com/harshitj183")
    ]

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" role="img" aria-label="Harshit Jaiswal — profile.sh --live">')
    
    # Definitions
    svg.append('''<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#7C3AED"><animate attributeName="stop-color" values="#7C3AED;#22D3EE;#10B981;#7C3AED" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="#22D3EE"><animate attributeName="stop-color" values="#22D3EE;#10B981;#7C3AED;#22D3EE" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#7C3AED;#22D3EE;#10B981" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{}"/>
  <stop offset="1" stop-color="{}"/>
</linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
</defs>'''.format(panel_start, panel_end))

    # CSS Styles
    svg.append('''<style>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}
.live-pulse {
  animation: pulse 1.8s infinite ease-in-out;
}
.terminal-text {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}
</style>''')

    # Window Background
    svg.append(f'<rect x="2" y="2" width="1176" height="606" rx="18" fill="{bg_outer}"/>')
    svg.append(f'<g clip-path="url(#winClip)">')
    svg.append(f'<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>')
    svg.append(f'<rect x="2" y="2" width="1176" height="46" fill="{title_bar_bg}"/>')
    svg.append(f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{border_color}"/>')
    
    # Terminal dots
    svg.append(f'<circle cx="30" cy="25" r="5.5" fill="#ff5f56"/>')
    svg.append(f'<circle cx="50" cy="25" r="5.5" fill="#ffbd2e"/>')
    svg.append(f'<circle cx="70" cy="25" r="5.5" fill="#27c93f"/>')
    
    # Title Bar Text
    svg.append(f'<text x="590" y="29" text-anchor="middle" font-size="12" fill="{text_muted}">harshitj183@gmail.com - % ./profile.sh --live</text>')
    
    # Left Frame Border
    svg.append(f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{text_muted}">VISUAL.MAP</text>')
    if dark_mode:
        svg.append(f'<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="{text_primary}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>')
    svg.append(f'<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="{frame_border}" stroke-width="1.5"/>')
    
    # Portrait progressive shimmer fade-in
    svg.append(f'<g fill="{portrait_color}" shape-rendering="crispEdges">')
    for i, path_data in enumerate(paths):
        # Staggered entry for each horizontal band of dithered portrait
        begin_time = 0.20 + i * 0.08
        svg.append(f'<g opacity="0">')
        svg.append(f'  <animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin_time:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>')
        svg.append(f'  <path d="{path_data}"/>')
        svg.append(f'</g>')
    svg.append(f'</g>')
    
    # Right Frame Info Panel (no border frame, floating clean text)
    # Header system info
    svg.append(f'<text x="470" y="74" font-size="10" letter-spacing="3" fill="{text_muted}">SYSTEM.INFO</text>')
    
    # Live Indicator on the top right of panel
    svg.append(f'<g opacity="0">')
    svg.append(f'  <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.70s" fill="freeze"/>')
    svg.append(f'  <circle cx="1110" cy="70" r="4.5" fill="#ef4444" class="live-pulse" />')
    svg.append(f'  <text x="1120" y="74" fill="#ef4444" font-size="11" font-weight="bold" font-family="monospace">LIVE</text>')
    svg.append(f'</g>')
    
    # Colored Email Pill
    svg.append(f'<g opacity="0">')
    svg.append(f'  <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.80s" fill="freeze"/>')
    svg.append(f'  <rect x="470" y="90" width="200" height="22" rx="11" fill="{accent_color}" />')
    svg.append(f'  <text x="570" y="105" fill="#ffffff" font-size="12" font-weight="bold" text-anchor="middle" class="terminal-text">harshitj183@gmail.com</text>')
    svg.append(f'</g>')
    
    # Write core info rows
    start_y = 135
    begin_delay = 0.90
    for idx, (label, val) in enumerate(info_rows):
        y_pos = start_y + idx * 23
        row_svg = make_text_row(label, val, y_pos, text_primary, text_secondary, text_white, begin_delay + idx * 0.10)
        svg.append(row_svg)
        
    # Contact Header Separator
    sep_idx = len(info_rows)
    sep_y = start_y + sep_idx * 23
    svg.append(f'''<g opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{(begin_delay + sep_idx * 0.10):.2f}s" fill="freeze"/>
  <text x="470" y="{sep_y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve" class="terminal-text">
    <tspan fill="{text_muted}">- Contact </tspan>
    <tspan fill="{text_secondary}">---------------------------------------------------------------------</tspan>
  </text>
</g>''')

    # Write contact/social rows
    contact_start_y = sep_y + 23
    contact_begin_delay = begin_delay + (sep_idx + 1) * 0.10
    for idx, (label, val) in enumerate(contact_rows):
        y_pos = contact_start_y + idx * 23
        row_svg = make_text_row(label, val, y_pos, text_primary, text_secondary, text_white, contact_begin_delay + idx * 0.10)
        svg.append(row_svg)
        
    # Bottom command line prompt
    bottom_idx = len(contact_rows)
    bottom_y = contact_start_y + bottom_idx * 23
    svg.append(f'''<g opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{(contact_begin_delay + bottom_idx * 0.10):.2f}s" fill="freeze"/>
  <text x="470" y="{bottom_y}" font-size="14" fill="{text_muted}" class="terminal-text">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="{text_primary}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
</g>''')

    svg.append(f'</g>') # End winClip group
    
    # Outer animated neon border
    if dark_mode:
        svg.append(f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>')
    svg.append(f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>')
    
    svg.append(f'</svg>')
    
    return "\n".join(svg)

def main():
    repo_root = "/home/harshitj183/harshitj183"
    avatar_path = os.path.join(repo_root, "badge", "profileLOgo.png")
    
    print("Generating dark dithered portrait terminal banner...")
    dark_dithered = dither_image(avatar_path, dark_mode=True)
    dark_svg = generate_svg(dark_dithered, dark_mode=True)
    
    print("Generating light dithered portrait terminal banner...")
    light_dithered = dither_image(avatar_path, dark_mode=False)
    light_svg = generate_svg(light_dithered, dark_mode=False)
    
    with open(os.path.join(repo_root, "dark.svg"), "w") as f:
        f.write(dark_svg)
        
    with open(os.path.join(repo_root, "light.svg"), "w") as f:
        f.write(light_svg)
        
    print("Successfully generated animated dark.svg and light.svg terminal banners!")

if __name__ == "__main__":
    main()
