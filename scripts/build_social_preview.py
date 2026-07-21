"""Generate the GitHub social preview image for vonnerco/automation-solutions.

Output: .github/social-preview.png  (1600x1200, 4:3, PNG)

Re-run from the repo root:
    /tmp/.imgvenv/bin/python scripts/build_social_preview.py

The brand-neutral palette lives in PALETTE below — swap those hex values
to match a real brand and re-run. No other code changes required.
"""
from __future__ import annotations

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required. Activate the venv:\n"
             "  /tmp/.imgvenv/bin/python scripts/build_social_preview.py\n"
             "or install with:  pip install Pillow")

# --- Brand-neutral palette (swap freely) --------------------------------
PALETTE = {
    "bg":          "#0d1117",   # near-black navy
    "bg_accent":   "#161b22",   # slightly lighter for vignette
    "card":        "#161b22",   # step-card background
    "card_border": "#30363d",   # step-card border
    "accent":      "#4493f8",   # electric blue (rule, arrows, accent text)
    "accent_dim":  "#1f6feb",   # secondary accent
    "fg":          "#e6edf3",   # primary text
    "muted":       "#8b949e",   # secondary text
    "chip_bg":     "#1f6feb",
    "chip_fg":     "#ffffff",
}

W, H = 1600, 1200
OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".github", "social-preview.png"))


# --- Font discovery ------------------------------------------------------
def find_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    """Try a list of font paths/names, falling back to PIL default."""
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_DISPLAY = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
], 96)

FONT_TITLE = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
], 28)

FONT_BODY = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "DejaVuSans.ttf",
], 22)

FONT_SMALL = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "DejaVuSans.ttf",
], 20)

FONT_TINY = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "DejaVuSans.ttf",
], 18)


# --- Drawing helpers -----------------------------------------------------
def text_w(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_h(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def fill_vignette(img: Image.Image, base: str, accent: str) -> None:
    """Cheap vignette: solid base color, then a faint radial overlay."""
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], fill=base)
    # Soft top-left and bottom-right tint using large translucent rects
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([-300, -300, 700, 700], fill=(*_hex_to_rgb(accent), 28))
    od.ellipse([W - 700, H - 700, W + 300, H + 300], fill=(*_hex_to_rgb(accent), 18))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def draw_logo(draw: ImageDraw.ImageDraw, x: int, y: int) -> int:
    """Draw a small V monogram and the wordmark. Returns the right edge x."""
    # V monogram in a rounded square
    box = 56
    draw.rounded_rectangle([x, y, x + box, y + box], radius=12, fill=PALETTE["accent"])
    vx, vy = x + box // 2, y + box // 2 + 4
    draw.line([(x + 12, y + 14), (vx, y + box - 12)], fill="white", width=5)
    draw.line([(vx, y + box - 12), (x + box - 12, y + 14)], fill="white", width=5)
    # Wordmark
    text = "Vonnerco Automation Solutions"
    draw.text((x + box + 16, y + 8), text, font=FONT_TITLE, fill=PALETTE["fg"])
    return x + box + 16 + text_w(draw, text, FONT_TITLE)


def draw_step_card(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int,
                   glyph: str, title: str, subtitle: str) -> None:
    # Card background with rounded corners
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18,
                           fill=PALETTE["card"], outline=PALETTE["card_border"], width=2)
    # Glyph circle
    cy = y + 56
    draw.ellipse([x + (w - 64) // 2, cy - 32, x + (w - 64) // 2 + 64, cy + 32],
                 fill=PALETTE["accent_dim"], outline=PALETTE["accent"], width=2)
    bbox = draw.textbbox((0, 0), glyph, font=FONT_TITLE)
    gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - gw) // 2, cy - gh // 2 - 2), glyph, font=FONT_TITLE, fill="white")
    # Title
    tw = text_w(draw, title, FONT_BODY)
    draw.text((x + (w - tw) // 2, cy + 50), title, font=FONT_BODY, fill=PALETTE["fg"])
    # Subtitle
    sw = text_w(draw, subtitle, FONT_TINY)
    draw.text((x + (w - sw) // 2, cy + 84), subtitle, font=FONT_TINY, fill=PALETTE["muted"])


def draw_arrow(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int) -> None:
    draw.line([(x1, y1), (x2, y2)], fill=PALETTE["accent"], width=4)
    # Arrowhead
    head = 12
    draw.polygon([
        (x2, y2),
        (x2 - head, y2 - head // 2),
        (x2 - head, y2 + head // 2),
    ], fill=PALETTE["accent"])


def draw_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
              bg: str, fg: str) -> int:
    pad_x, pad_y = 18, 10
    w = text_w(draw, text, FONT_SMALL) + pad_x * 2
    h = 38
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw.text((x + pad_x, y + pad_y - 2), text, font=FONT_SMALL, fill=fg)
    return x + w


# --- Main ---------------------------------------------------------------
def main() -> None:
    img = Image.new("RGB", (W, H), PALETTE["bg"])
    fill_vignette(img, PALETTE["bg"], PALETTE["accent"])
    draw = ImageDraw.Draw(img)

    # Top brand row
    draw_logo(draw, x=80, y=72)

    # Top-right chips
    chip_y = 92
    cx = W - 80
    for label in ("n8n", "AI", "APIs"):
        chip_w = text_w(draw, label, FONT_SMALL) + 36
        draw.rounded_rectangle([cx - chip_w, chip_y, cx, chip_y + 38],
                               radius=19, outline=PALETTE["card_border"], width=2)
        draw.text((cx - chip_w + 18, chip_y + 8), label, font=FONT_SMALL, fill=PALETTE["fg"])
        cx -= chip_w + 12

    # Headline rule and title
    rule_y = 280
    draw.rectangle([80, rule_y, 80 + 96, rule_y + 4], fill=PALETTE["accent"])
    draw.text((200, rule_y - 18), "PORTFOLIO · OPEN SOURCE", font=FONT_SMALL, fill=PALETTE["muted"])

    title = "AI-Powered Workflows"
    tw = text_w(draw, title, FONT_DISPLAY)
    title_y = 340
    draw.text(((W - tw) // 2, title_y), title, font=FONT_DISPLAY, fill=PALETTE["fg"])

    sub = "n8n automations · AI integrations · reusable templates"
    sw = text_w(draw, sub, FONT_BODY)
    draw.text(((W - sw) // 2, title_y + 130), sub, font=FONT_BODY, fill=PALETTE["muted"])

    # Step diagram (4 cards)
    steps = [
        ("⚡", "Trigger",  "Webhook · Manual · Schedule"),
        ("✓",  "Validate", "Parse & shape payload"),
        ("🧠", "AI Extract", "Local LLM via Ollama"),
        ("✓",  "Decide",   "Auto-approve or review"),
    ]
    card_w, card_h = 280, 220
    gap = 40
    total = card_w * 4 + gap * 3
    start_x = (W - total) // 2
    cy = 720

    for i, (glyph, title_, sub_) in enumerate(steps):
        x = start_x + i * (card_w + gap)
        draw_step_card(draw, x, cy, card_w, card_h, glyph, title_, sub_)
        if i < len(steps) - 1:
            ax1 = x + card_w + 4
            ax2 = x + card_w + gap - 4
            draw_arrow(draw, ax1, cy + card_h // 2, ax2, cy + card_h // 2)

    # Bottom: URL on the left, tagline on the right
    bottom_y = H - 88
    url = "github.com/vonnerco/automation-solutions"
    draw.text((80, bottom_y), url, font=FONT_BODY, fill=PALETTE["accent"])

    right = "Built with n8n · Local-first · Demo-grade, production-shaped"
    rw = text_w(draw, right, FONT_BODY)
    draw.text((W - 80 - rw, bottom_y), right, font=FONT_BODY, fill=PALETTE["muted"])

    # Subtle bottom hairline
    draw.rectangle([80, bottom_y - 24, W - 80, bottom_y - 22], fill=PALETTE["card_border"])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"Wrote {OUT}  ({os.path.getsize(OUT) / 1024:.1f} KB, {W}x{H})")


if __name__ == "__main__":
    main()
