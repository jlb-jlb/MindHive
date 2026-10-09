#!/usr/bin/env python3
"""
Render PDF pages to enumerated image files in an Obsidian attachments folder
and create a Markdown note that embeds those images.

Dependencies:
    Preferred:
        python -m pip install pymupdf

    Fallback:
        python -m pip install pdf2image pillow
        plus Poppler on PATH, providing pdftoppm/pdfinfo

Example:
    python pdf_to_obsidian_images.py ^
        --vault "C:\\Users\\me\\Documents\\MyVault" ^
        --attachments "attachments" ^
        --output "Notes\\Imported PDF.md" ^
        "C:\\Users\\me\\Downloads\\document.pdf"
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.parse import quote


IMAGE_FORMATS = {"png", "jpg", "jpeg"}
BACKENDS = {"auto", "pymupdf", "pdf2image"}
ALT_TEXT_MODES = {"none", "extracted"}
TEXT_OUTPUT_MODES = {"none", "block"}


def slugify(value: str) -> str:
    """Return a filesystem-friendly name while keeping it readable."""
    value = re.sub(r"[^\w .-]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip(" .-_")
    return value or "pdf"


def resolve_inside_vault(vault: Path, value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = vault / path

    resolved = path.resolve()
    try:
        resolved.relative_to(vault)
    except ValueError:
        raise SystemExit(f"{label} must be inside the Obsidian vault: {resolved}")

    return resolved


def attachment_subdir_path(template: str, pdf_path: Path) -> Path:
    template = template.strip().strip("/\\")
    if not template:
        return Path()

    try:
        rendered = template.format(
            pdf_stem=slugify(pdf_path.stem),
            pdf_name=slugify(pdf_path.name),
        )
    except KeyError as exc:
        raise SystemExit(
            "Unknown --attachment-subdir template variable: "
            f"{exc}. Supported variables: {{pdf_stem}}, {{pdf_name}}"
        )

    parts: list[str] = []
    for part in re.split(r"[\\/]+", rendered):
        part = part.strip()
        if not part or part == ".":
            continue
        if part == "..":
            raise SystemExit("--attachment-subdir cannot contain '..'")
        safe_part = slugify(part)
        if safe_part:
            parts.append(safe_part)

    return Path(*parts) if parts else Path()


def unique_path(path: Path, overwrite: bool, reserved: set[Path]) -> Path:
    if path not in reserved and (overwrite or not path.exists()):
        reserved.add(path)
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if candidate not in reserved and (overwrite or not candidate.exists()):
            reserved.add(candidate)
            return candidate
        counter += 1


def markdown_alt_text(text: str, fallback: str) -> str:
    alt_text = re.sub(r"\s+", " ", text).strip() or fallback
    return (
        alt_text.replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def markdown_text_block(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    longest_backtick_run = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest_backtick_run + 1)
    return f"{fence}text\n{text}\n{fence}"


def extract_page_text(page) -> str:
    try:
        return page.get_text("text", sort=True)
    except TypeError:
        return page.get_text("text")


def html_alt_text(text: str, fallback: str) -> str:
    alt_text = re.sub(r"\s+", " ", text).strip() or fallback
    return html.escape(alt_text, quote=True)


def obsidian_link(vault: Path, image_path: Path, style: str, alt_text: str = "") -> str:
    relative = image_path.relative_to(vault).as_posix()
    if style == "html":
        src = html.escape(quote(relative), quote=True)
        alt = html_alt_text(alt_text, image_path.stem)
        return f'<img src="{src}" alt="{alt}">'

    if alt_text or style == "markdown":
        escaped = quote(relative)
        alt = markdown_alt_text(alt_text, image_path.stem)
        return f"![{alt}]({escaped})"

    return f"![[{relative}]]"


def page_markdown(
    vault: Path,
    image_path: Path,
    link_style: str,
    alt_text_mode: str,
    text_output_mode: str,
    page_text: str,
) -> str:
    alt_text = page_text if alt_text_mode == "extracted" else ""
    image_markdown = obsidian_link(vault, image_path, link_style, alt_text)
    if text_output_mode == "block" and page_text.strip():
        return f"{image_markdown}\n\n{markdown_text_block(page_text)}"
    return image_markdown


def latest_download_pdf() -> Path:
    downloads = Path.home() / "Downloads"
    pdfs = [
        path
        for path in downloads.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    ]
    if not pdfs:
        raise SystemExit(f"No PDF files found in Downloads: {downloads}")
    return max(pdfs, key=lambda path: path.stat().st_mtime).resolve()


def load_render_backend(requested: str):
    errors: list[str] = []

    if requested in {"auto", "pymupdf"}:
        try:
            import fitz  # PyMuPDF

            return "pymupdf", fitz
        except ImportError as exc:
            errors.append(f"PyMuPDF unavailable: {exc}")
            if requested == "pymupdf":
                raise SystemExit(
                    "Missing dependency: PyMuPDF. Install it with:\n"
                    "    python -m pip install pymupdf"
                )

    if requested in {"auto", "pdf2image"}:
        try:
            import pdf2image

            return "pdf2image", pdf2image
        except ImportError as exc:
            errors.append(f"pdf2image unavailable: {exc}")
            if requested == "pdf2image":
                raise SystemExit(
                    "Missing dependencies: pdf2image and Pillow. Install them with:\n"
                    "    python -m pip install pdf2image pillow\n"
                    "Poppler must also be installed and on PATH."
                )

    raise SystemExit(
        "No PDF rendering backend is available.\n"
        "Install PyMuPDF with:\n"
        "    python -m pip install pymupdf\n"
        "Or install pdf2image/Pillow and Poppler.\n\n"
        + "\n".join(errors)
    )


def render_pdf_with_pymupdf(
    pdf_path: Path,
    vault: Path,
    attachments_dir: Path,
    dpi: int,
    image_format: str,
    overwrite: bool,
    link_style: str,
    alt_text_mode: str,
    text_output_mode: str,
    fitz_module,
    reserved_images: set[Path],
) -> tuple[str, list[str]]:
    links: list[str] = []
    base_name = slugify(pdf_path.stem)
    extension = "jpg" if image_format == "jpeg" else image_format
    zoom = dpi / 72
    matrix = fitz_module.Matrix(zoom, zoom)

    with fitz_module.open(pdf_path) as document:
        page_count = document.page_count
        page_digits = max(3, len(str(page_count)))

        for index, page in enumerate(document, start=1):
            image_name = f"{base_name}-{index:0{page_digits}d}.{extension}"
            image_path = unique_path(
                attachments_dir / image_name,
                overwrite,
                reserved_images,
            )
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pixmap.save(image_path)
            page_text = (
                extract_page_text(page)
                if alt_text_mode == "extracted" or text_output_mode == "block"
                else ""
            )
            links.append(
                page_markdown(
                    vault,
                    image_path,
                    link_style,
                    alt_text_mode,
                    text_output_mode,
                    page_text,
                )
            )

    return pdf_path.stem, links


def render_pdf_with_pdf2image(
    pdf_path: Path,
    vault: Path,
    attachments_dir: Path,
    dpi: int,
    image_format: str,
    overwrite: bool,
    link_style: str,
    alt_text_mode: str,
    text_output_mode: str,
    pdf2image_module,
    reserved_images: set[Path],
) -> tuple[str, list[str]]:
    links: list[str] = []
    base_name = slugify(pdf_path.stem)
    extension = "jpg" if image_format == "jpeg" else image_format
    save_format = "JPEG" if extension == "jpg" else "PNG"

    try:
        info = pdf2image_module.pdfinfo_from_path(str(pdf_path))
    except Exception as exc:
        raise SystemExit(
            "Could not inspect PDF with pdf2image. Make sure Poppler is installed "
            f"and pdftoppm/pdfinfo are on PATH.\n{exc}"
        )

    page_count = int(info["Pages"])
    page_digits = max(3, len(str(page_count)))
    text_document = None
    if alt_text_mode == "extracted" or text_output_mode == "block":
        try:
            import fitz

            text_document = fitz.open(pdf_path)
        except ImportError:
            print(
                "Warning: PyMuPDF is unavailable, so extracted alt text will be empty.",
                file=sys.stderr,
            )

    try:
        for index in range(1, page_count + 1):
            image_name = f"{base_name}-{index:0{page_digits}d}.{extension}"
            image_path = unique_path(
                attachments_dir / image_name,
                overwrite,
                reserved_images,
            )
            pages = pdf2image_module.convert_from_path(
                str(pdf_path),
                dpi=dpi,
                first_page=index,
                last_page=index,
                fmt="jpeg" if extension == "jpg" else "png",
            )
            if not pages:
                raise SystemExit(f"Could not render page {index} from {pdf_path}")

            image = pages[0]
            if save_format == "JPEG" and image.mode != "RGB":
                image = image.convert("RGB")
            image.save(image_path, save_format)

            page_text = ""
            if text_document is not None:
                page_text = extract_page_text(text_document[index - 1])
            links.append(
                page_markdown(
                    vault,
                    image_path,
                    link_style,
                    alt_text_mode,
                    text_output_mode,
                    page_text,
                )
            )
    finally:
        if text_document is not None:
            text_document.close()

    return pdf_path.stem, links


def build_markdown(title: str, rendered: list[tuple[str, list[str]]]) -> str:
    lines = [f"# {title}", ""]

    for pdf_title, links in rendered:
        if len(rendered) > 1:
            lines.extend([f"## {pdf_title}", ""])

        for link in links:
            lines.extend([link, ""])

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render PDF pages into an Obsidian vault attachments folder and "
            "write a Markdown note embedding the generated images."
        )
    )
    parser.add_argument(
        "pdfs",
        nargs="*",
        help=(
            "One or more PDF files to render. If omitted, the newest PDF in "
            "the current user's Downloads folder is used."
        ),
    )
    parser.add_argument(
        "--vault",
        required=True,
        help="Path to the Obsidian vault root.",
    )
    parser.add_argument(
        "--attachments",
        default="attachments",
        help=(
            "Attachments folder inside the vault. Relative paths are resolved "
            "from the vault root. Default: attachments"
        ),
    )
    parser.add_argument(
        "--attachment-subdir",
        default="{pdf_stem}",
        help=(
            "Subfolder under the attachments folder for rendered images. "
            "Supports {pdf_stem} and {pdf_name}. Use an empty value to write "
            "directly into the attachments folder. Default: {pdf_stem}"
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        help=(
            "Markdown note path inside the vault, for example "
            "'Notes/Imported PDF.md'."
        ),
    )
    parser.add_argument(
        "--title",
        help="Markdown note title. Defaults to the output file name.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Render DPI for PDF pages. Default: 200",
    )
    parser.add_argument(
        "--format",
        choices=sorted(IMAGE_FORMATS),
        default="jpg",
        help="Output image format. Default: jpg",
    )
    parser.add_argument(
        "--backend",
        choices=sorted(BACKENDS),
        default="auto",
        help="PDF rendering backend. Default: auto",
    )
    parser.add_argument(
        "--link-style",
        choices=["wiki", "markdown", "html"],
        default="html",
        help=(
            "Image embed style. HTML is safest for full extracted alt text. "
            "Default: html"
        ),
    )
    parser.add_argument(
        "--alt-text",
        choices=sorted(ALT_TEXT_MODES),
        default="extracted",
        help=(
            "Alt text mode for generated image links. With --link-style html, "
            "full extracted page text is stored in an HTML alt attribute and "
            "does not break image links. Default: extracted"
        ),
    )
    parser.add_argument(
        "--text-output",
        choices=sorted(TEXT_OUTPUT_MODES),
        default="none",
        help=(
            "Where to write extracted PDF page text. 'block' writes a fenced "
            "text block after each image so chatbots can read it without "
            "risking broken image links. Default: none"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing image files and the Markdown note.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    vault = Path(args.vault).expanduser().resolve()
    if not vault.exists() or not vault.is_dir():
        print(f"Vault does not exist or is not a directory: {vault}", file=sys.stderr)
        return 1

    if args.dpi < 36:
        print("--dpi must be at least 36", file=sys.stderr)
        return 1

    attachments_dir = resolve_inside_vault(vault, args.attachments, "--attachments")
    output_md = resolve_inside_vault(vault, args.output, "--output")

    if output_md.exists() and not args.overwrite:
        print(
            f"Output note already exists: {output_md}\n"
            "Pass --overwrite to replace it.",
            file=sys.stderr,
        )
        return 1

    pdf_inputs = [pdf for pdf in args.pdfs if pdf.strip()]
    if not pdf_inputs:
        pdf_paths = [latest_download_pdf()]
        print(f"No PDF path supplied; using newest Downloads PDF: {pdf_paths[0]}")
    else:
        pdf_paths = [Path(pdf).expanduser().resolve() for pdf in pdf_inputs]
    for pdf_path in pdf_paths:
        if not pdf_path.exists() or not pdf_path.is_file():
            print(f"PDF does not exist or is not a file: {pdf_path}", file=sys.stderr)
            return 1
        if pdf_path.suffix.lower() != ".pdf":
            print(f"Not a PDF file: {pdf_path}", file=sys.stderr)
            return 1

    backend_name, backend_module = load_render_backend(args.backend)

    output_md.parent.mkdir(parents=True, exist_ok=True)

    rendered: list[tuple[str, list[str]]] = []
    image_dirs: set[Path] = set()
    reserved_images: set[Path] = set()
    for pdf_path in pdf_paths:
        image_dir = attachments_dir / attachment_subdir_path(args.attachment_subdir, pdf_path)
        image_dir.mkdir(parents=True, exist_ok=True)
        image_dirs.add(image_dir)

        if backend_name == "pymupdf":
            result = render_pdf_with_pymupdf(
                pdf_path=pdf_path,
                vault=vault,
                attachments_dir=image_dir,
                dpi=args.dpi,
                image_format=args.format,
                overwrite=args.overwrite,
                link_style=args.link_style,
                alt_text_mode=args.alt_text,
                text_output_mode=args.text_output,
                fitz_module=backend_module,
                reserved_images=reserved_images,
            )
        else:
            result = render_pdf_with_pdf2image(
                pdf_path=pdf_path,
                vault=vault,
                attachments_dir=image_dir,
                dpi=args.dpi,
                image_format=args.format,
                overwrite=args.overwrite,
                link_style=args.link_style,
                alt_text_mode=args.alt_text,
                text_output_mode=args.text_output,
                pdf2image_module=backend_module,
                reserved_images=reserved_images,
            )
        rendered.append(result)

    title = args.title or output_md.stem
    output_md.write_text(build_markdown(title, rendered), encoding="utf-8")

    image_count = sum(len(links) for _, links in rendered)
    print(f"Used PDF backend: {backend_name}")
    if len(image_dirs) == 1:
        print(f"Wrote {image_count} image(s) to: {next(iter(image_dirs))}")
    else:
        print(f"Wrote {image_count} image(s) under: {attachments_dir}")
    print(f"Wrote Markdown note to: {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
