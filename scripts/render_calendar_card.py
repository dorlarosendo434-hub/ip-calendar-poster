#!/usr/bin/env python3
"""Render a verified monthly calendar onto a blank watercolor card image."""

from __future__ import annotations

import argparse
import calendar
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
REFERENCE_WIDTH = 3072
PRESET_FONT_FILES = {
    "font_title": "LXGWWenKai-Medium.ttf",
    "font_english": "LXGWWenKai-Medium.ttf",
    "font_cn_bold": "SourceHanSansSC-Heavy.otf",
    "font_number": "SourceHanSerifSC-SemiBold.otf",
    "font_cn": "SourceHanSansSC-Regular.otf",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Overlay a Monday-first monthly calendar on a blank watercolor card."
    )
    parser.add_argument("--base", required=True, type=Path, help="Blank card base image")
    parser.add_argument("--data", required=True, type=Path, help="Verified calendar JSON")
    parser.add_argument("--out", required=True, type=Path, help="Output PNG path")
    parser.add_argument("--width", type=int, default=3072)
    parser.add_argument("--height", type=int, default=4096)
    parser.add_argument("--left", type=float, default=0.155, help="Usable card left ratio")
    parser.add_argument("--right", type=float, default=0.815, help="Usable card right ratio")
    parser.add_argument("--top", type=float, default=0.491, help="Usable card top ratio")
    parser.add_argument(
        "--bottom",
        type=float,
        default=0.886,
        help="Lower safe boundary for the adaptive date grid, as an image-height ratio",
    )
    parser.add_argument(
        "--date-label-gap-px",
        type=int,
        default=20,
        help="Visible vertical gap at 3072px output width; scales with output width",
    )
    parser.add_argument("--font-dir", type=Path, help="Directory containing the four fonts for the default style")
    parser.add_argument("--font-cn", type=Path, help="Open-source font for daily labels")
    parser.add_argument("--font-cn-bold", type=Path, help="Open-source font for weekdays")
    parser.add_argument("--font-title", type=Path, help="Open-source title font")
    parser.add_argument("--title-stroke-px", type=int, default=3, help="Same-color title stroke at 3072px width")
    parser.add_argument("--weekday-size-px", type=int, default=56, help="Weekday font size at 3072px width")
    parser.add_argument(
        "--font-number", "--font-serif-bold", type=Path,
        help="Open-source font for Gregorian date numbers",
    )
    parser.add_argument(
        "--font-english", "--font-serif-italic", type=Path,
        help="Open-source font for the English month",
    )
    parser.add_argument("--font-serif", type=Path, help=argparse.SUPPRESS)  # Legacy, unused.
    args = parser.parse_args()
    if args.font_dir is not None:
        for field, filename in PRESET_FONT_FILES.items():
            if getattr(args, field) is None:
                setattr(args, field, args.font_dir / filename)
    if any(font is None for font in (args.font_cn, args.font_cn_bold, args.font_number, args.font_english)):
        parser.error("provide --font-dir or all of --font-cn, --font-cn-bold, --font-number and --font-english")
    return args


def cover_resize(image: Image.Image, width: int, height: int) -> Image.Image:
    target_ratio = width / height
    source_ratio = image.width / image.height
    if source_ratio > target_ratio:
        crop_width = round(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    elif source_ratio < target_ratio:
        crop_height = round(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise FileNotFoundError(f"Font not found: {path}")
    return ImageFont.truetype(str(path), size=size)


def draw_center(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    stroke_width: int = 0,
) -> None:
    draw.text(xy, text, font=font, fill=fill, anchor="mm", stroke_width=stroke_width)


def validate_data(data: dict) -> tuple[int, int, str, dict[int, str], dict[int, str]]:
    year = int(data["year"])
    month = int(data["month"])
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    english_month = str(data.get("english_month") or calendar.month_name[month])
    labels = {}
    for day, label in data["labels"].items():
        day_number = int(day)
        if day_number in labels:
            raise ValueError(f"duplicate day in labels: {day}")
        if not isinstance(label, str) or not label.strip() or len(label.splitlines()) != 1:
            raise ValueError(f"day {day} must have a non-empty, single-line calendar label")
        labels[day_number] = label.strip()
    kinds = {int(day): str(kind) for day, kind in data.get("kinds", {}).items()}
    total_days = calendar.monthrange(year, month)[1]
    expected = set(range(1, total_days + 1))
    actual = set(labels)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"labels must cover every day exactly once; missing={missing}, extra={extra}")
    return year, month, english_month, labels, kinds


def render(args: argparse.Namespace) -> None:
    data = json.loads(args.data.read_text(encoding="utf-8"))
    year, month, english_month, labels, kinds = validate_data(data)

    base = Image.open(args.base).convert("RGB")
    canvas = cover_resize(base, args.width, args.height)
    draw = ImageDraw.Draw(canvas)

    x0, x1 = args.left * args.width, args.right * args.width
    y0, y1 = args.top * args.height, args.bottom * args.height
    card_width = x1 - x0
    center_x = (x0 + x1) / 2

    palette = data.get("palette", {})
    deep_brown = str(palette.get("primary", "#44362F"))
    soft_brown = str(palette.get("secondary", "#78655B"))
    terracotta = str(palette.get("accent", "#A65149"))
    pine_green = str(palette.get("solar_term", "#536C5A"))
    divider = str(palette.get("divider", "#C8B5A7"))

    title_font = load_font(args.font_title or args.font_cn_bold, round(args.width * 0.039))
    english_font = load_font(args.font_english, round(args.width * 0.017))
    weekday_size = max(1, round(args.weekday_size_px * args.width / REFERENCE_WIDTH))
    weekday_font = load_font(args.font_cn_bold, weekday_size)
    title_stroke = max(0, round(args.title_stroke_px * args.width / REFERENCE_WIDTH))

    draw_center(
        draw,
        (center_x, y0 + args.height * 0.038),
        f"{year}年{month}月",
        title_font,
        deep_brown,
        stroke_width=title_stroke,
    )
    draw_center(
        draw,
        (center_x, y0 + args.height * 0.080),
        english_month,
        english_font,
        terracotta,
    )

    column_width = card_width / 7
    weekday_y = y0 + args.height * 0.126
    for column, weekday in enumerate(WEEKDAYS):
        color = terracotta if column >= 5 else deep_brown
        draw_center(
            draw,
            (x0 + column_width * (column + 0.5), weekday_y),
            weekday,
            weekday_font,
            color,
        )

    divider_y = y0 + args.height * 0.147
    draw.line(
        (x0 + column_width * 0.10, divider_y, x1 - column_width * 0.10, divider_y),
        fill=divider,
        width=max(2, round(args.width * 0.001)),
    )

    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    grid_top = y0 + args.height * 0.165
    # The date area is divided by the month's real week count. This naturally
    # gives four-row months more breathing room, keeps five-row months balanced,
    # and compresses six-row months without inventing placeholder rows.
    week_count = len(weeks)
    row_height = (y1 - grid_top) / week_count
    number_size = round(min(args.width * 0.032, row_height * 0.56))
    label_size = round(min(args.width * 0.014, row_height * 0.25))
    number_font = load_font(args.font_number, number_size)
    label_font = load_font(args.font_cn, label_size)

    # Center the two-line date block while preserving a true visible gap between
    # the glyph bounding boxes. Using font-size ratios alone can make the lines
    # appear stuck together because different fonts have different ascenders and
    # descenders.
    number_bbox = number_font.getbbox("88", anchor="mm")
    label_bbox = label_font.getbbox("节气", anchor="mm")
    number_height = number_bbox[3] - number_bbox[1]
    label_height = label_bbox[3] - label_bbox[1]
    date_label_gap = max(
        1, round(args.date_label_gap_px * args.width / REFERENCE_WIDTH)
    )
    date_block_height = number_height + date_label_gap + label_height

    for row_index, week in enumerate(weeks):
        row_center = grid_top + row_height * (row_index + 0.5)
        block_top = row_center - date_block_height / 2
        number_y = block_top - number_bbox[1]
        label_y = block_top + number_height + date_label_gap - label_bbox[1]
        for column, day in enumerate(week):
            if day == 0:
                continue
            x = x0 + column_width * (column + 0.5)
            number_color = terracotta if column >= 5 else deep_brown
            kind = kinds.get(day, "lunar")
            label_color = (
                terracotta
                if kind == "festival"
                else pine_green
                if kind == "solar_term"
                else soft_brown
            )
            draw_center(
                draw,
                (x, number_y),
                str(day),
                number_font,
                number_color,
            )
            draw_center(
                draw,
                (x, label_y),
                labels[day],
                label_font,
                label_color,
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, format="PNG", dpi=(300, 300), optimize=True)


def main() -> None:
    render(parse_args())


if __name__ == "__main__":
    main()
