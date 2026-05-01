#!/usr/bin/env python3
"""
Claude Code先生 ブランドアセット一括生成

Pillowで以下のサイズの画像を一気に生成:
  - logo-square-1080.png      (1080x1080)  IG/FB/noteプロフィール用
  - logo-cover-1640x624.png   (1640x624)   FBカバー用
  - logo-x-banner-1500x500.png(1500x500)   Xバナー用
  - logo-story-1080x1920.png  (1080x1920)  IGストーリー用
  - note-header-1280x680.png  (1280x680)   noteヘッダー用
  - og-image-1200x630.png     (1200x630)   公式サイト OG画像

実行:
  cd /Users/ryose/.local/scripts/orchestrator/setup/site/assets
  python3 generate_brand_assets.py
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = Path(__file__).parent.resolve()

# Tokyo Night palette
BG = (26, 27, 38)         # #1a1b26
BG_GRAD_END = (45, 48, 80) # 微妙なグラデ用
ACCENT = (122, 162, 247)  # #7aa2f7
ACCENT2 = (187, 154, 247) # #bb9af7
TEXT = (192, 202, 245)    # #c0caf5
TEXT_DIM = (169, 177, 214) # #a9b1d6
TEXT_FAINT = (86, 95, 137) # #565f89

# 日本語対応フォントを優先（ヒラギノ等は日本語＋ASCII両対応）
FONT_BOLD_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]
FONT_MONO_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]


def _load_font(candidates: list, size: int) -> ImageFont.FreeTypeFont:
    for fp in candidates:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _gradient_bg(w: int, h: int, c1: tuple = BG, c2: tuple = BG_GRAD_END) -> Image.Image:
    """対角グラデーション背景"""
    img = Image.new("RGB", (w, h), c1)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _glow_circles(img: Image.Image, w: int, h: int):
    """背景にぼかしたアクセント色の円を配置（雰囲気作り）"""
    overlay = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(overlay)
    # 左上に青のglow
    r1 = max(w, h) // 3
    draw.ellipse([-r1 // 2, -r1 // 2, r1, r1], fill=ACCENT)
    # 右下に紫のglow
    r2 = max(w, h) // 4
    draw.ellipse([w - r2, h - r2, w + r2 // 2, h + r2 // 2], fill=ACCENT2)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 8))
    return Image.blend(img, overlay, 0.35)


def _draw_centered_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                       cx: int, cy: int, fill=TEXT):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - bbox[1]), text, fill=fill, font=font)


def make_square_logo(out: Path, size: int = 1080):
    """正方形ロゴ（IG/FB/noteプロフィール用）"""
    img = _gradient_bg(size, size)
    img = _glow_circles(img, size, size)
    draw = ImageDraw.Draw(img)

    # 中央に大きく "CC"
    cc_font = _load_font(FONT_BOLD_CANDIDATES, size // 3)
    _draw_centered_text(draw, "CC", cc_font, size // 2, size // 2 - size // 12, fill=ACCENT)

    # サブテキスト
    sub_font = _load_font(FONT_BOLD_CANDIDATES, size // 18)
    _draw_centered_text(draw, "Claude Code 社長 兼 先生", sub_font, size // 2, size // 2 + size // 4, fill=TEXT)

    # 装飾: 下部にAIタグ
    accent_font = _load_font(FONT_MONO_CANDIDATES, size // 28)
    _draw_centered_text(draw, "経営しながら教える", accent_font,
                       size // 2, size // 2 + size // 3, fill=TEXT_FAINT)

    img.save(out, "PNG", optimize=True)
    print(f"✓ {out.name}")


def make_facebook_cover(out: Path, w: int = 1640, h: int = 624):
    """Facebook カバー画像"""
    img = _gradient_bg(w, h)
    img = _glow_circles(img, w, h)
    draw = ImageDraw.Draw(img)

    # 左寄せロゴ + テキスト
    logo_font = _load_font(FONT_BOLD_CANDIDATES, h // 3)
    title_text = "💼 Claude Code 社長 兼 先生"
    bbox = draw.textbbox((0, 0), title_text, font=logo_font)
    draw.text((80, h // 4), title_text, fill=ACCENT, font=logo_font)

    sub_font = _load_font(FONT_BOLD_CANDIDATES, h // 12)
    sub_text = "経営しながら教える、Claude Codeで何でも作る人"
    draw.text((80, h // 4 + (bbox[3] - bbox[1]) + 30), sub_text, fill=TEXT, font=sub_font)

    url_font = _load_font(FONT_MONO_CANDIDATES, h // 18)
    draw.text((80, h - 70), "ryoseiimai.github.io/claude-code-sensei", fill=TEXT_FAINT, font=url_font)

    img.save(out, "PNG", optimize=True)
    print(f"✓ {out.name}")


def make_x_banner(out: Path, w: int = 1500, h: int = 500):
    """Xバナー"""
    img = _gradient_bg(w, h)
    img = _glow_circles(img, w, h)
    draw = ImageDraw.Draw(img)

    title_font = _load_font(FONT_BOLD_CANDIDATES, h // 4)
    draw.text((60, h // 6), "💼 Claude Code 社長 兼 先生", fill=ACCENT, font=title_font)

    sub_font = _load_font(FONT_BOLD_CANDIDATES, h // 12)
    draw.text((60, h // 6 + h // 4 + 20), "Claude Codeで会社経営する過程を全公開。", fill=TEXT, font=sub_font)
    draw.text((60, h // 6 + h // 4 + 70), "Build in Public で経営しながら教える。", fill=TEXT_DIM, font=sub_font)

    schedule_font = _load_font(FONT_MONO_CANDIDATES, h // 18)
    draw.text((60, h - 60),
              "朝08:00 Tips  /  昼12:15 ハック  /  夜20:30 雑談",
              fill=TEXT_FAINT, font=schedule_font)

    img.save(out, "PNG", optimize=True)
    print(f"✓ {out.name}")


def make_story_image(out: Path, w: int = 1080, h: int = 1920):
    """IGストーリー用 縦長画像"""
    img = _gradient_bg(w, h)
    img = _glow_circles(img, w, h)
    draw = ImageDraw.Draw(img)

    # 上部に絵文字
    em_font = _load_font(FONT_BOLD_CANDIDATES, w // 4)
    _draw_centered_text(draw, "💼", em_font, w // 2, h // 4, fill=ACCENT)

    # 中央タイトル
    title_font = _load_font(FONT_BOLD_CANDIDATES, w // 12)
    _draw_centered_text(draw, "Claude Code 社長 兼 先生", title_font, w // 2, h // 2 - 80, fill=ACCENT)

    # サブ
    sub_font = _load_font(FONT_BOLD_CANDIDATES, w // 24)
    _draw_centered_text(draw, "経営しながら教える", sub_font,
                       w // 2, h // 2 + 20, fill=TEXT)

    # 下部CTA
    cta_font = _load_font(FONT_MONO_CANDIDATES, w // 28)
    _draw_centered_text(draw, "→ プロフィールから公式サイトへ",
                       cta_font, w // 2, h - 200, fill=TEXT_FAINT)

    img.save(out, "PNG", optimize=True)
    print(f"✓ {out.name}")


def make_note_header(out: Path, w: int = 1280, h: int = 680):
    """noteヘッダー画像"""
    img = _gradient_bg(w, h)
    img = _glow_circles(img, w, h)
    draw = ImageDraw.Draw(img)

    title_font = _load_font(FONT_BOLD_CANDIDATES, h // 4)
    _draw_centered_text(draw, "💼 Claude Code 社長 兼 先生", title_font, w // 2, h // 2 - 60, fill=ACCENT)

    sub_font = _load_font(FONT_BOLD_CANDIDATES, h // 14)
    _draw_centered_text(draw, "Claude Codeで会社経営する過程を全公開",
                       sub_font, w // 2, h // 2 + 80, fill=TEXT)

    img.save(out, "PNG", optimize=True)
    print(f"✓ {out.name}")


def make_og_image(out: Path, w: int = 1200, h: int = 630):
    """OGP用画像（公式サイトSNSシェア時のサムネ）"""
    img = _gradient_bg(w, h)
    img = _glow_circles(img, w, h)
    draw = ImageDraw.Draw(img)

    title_font = _load_font(FONT_BOLD_CANDIDATES, h // 5)
    _draw_centered_text(draw, "💼 Claude Code 社長 兼 先生", title_font, w // 2, h // 2 - 40, fill=ACCENT)

    sub_font = _load_font(FONT_BOLD_CANDIDATES, h // 16)
    _draw_centered_text(draw, "Claude Codeで会社経営する過程を全公開、Build in Public",
                       sub_font, w // 2, h // 2 + 80, fill=TEXT)

    img.save(out, "PNG", optimize=True)
    print(f"✓ {out.name}")


def main():
    print(f"出力先: {OUT_DIR}")
    make_square_logo(OUT_DIR / "logo-square-1080.png")
    make_facebook_cover(OUT_DIR / "logo-cover-1640x624.png")
    make_x_banner(OUT_DIR / "logo-x-banner-1500x500.png")
    make_story_image(OUT_DIR / "logo-story-1080x1920.png")
    make_note_header(OUT_DIR / "note-header-1280x680.png")
    make_og_image(OUT_DIR / "og-image-1200x630.png")
    print("done.")


if __name__ == "__main__":
    main()
