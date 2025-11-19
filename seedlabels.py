#!/usr/bin/env python3
"""
Seed Label Generator CLI Tool

This CLI tool generates seed labels and prints them to a Brother label printer.
Based on the seed label generator lambda function.
"""

import argparse
import tempfile
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


def wrap_text(text, font, max_width, draw):
    """
    Wrap text to fit within a specified width and preserve explicit newlines.
    
    Splits input on '\n' into paragraphs, wraps each paragraph to the
    available width, and preserves blank lines as empty strings in the
    returned list.
    """
    lines = []
    # Split into paragraphs by explicit newlines
    paragraphs = text.split('\n')

    for para in paragraphs:
        # Preserve blank lines
        if not para.strip():
            lines.append('')
            continue

        words = para.split()
        current_line = []

        for word in words:
            # Try adding the word to current line
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        # Add the last line of the paragraph
        if current_line:
            lines.append(' '.join(current_line))

    return lines


def generate_seed_label(name, variety, notes="", sow_start_month=None, sow_end_month=None, month=None, year=None, use_red=False):
    """
    Generate a seed label image
    
    Args:
        name: Seed name (e.g., "Tomato")
        variety: Variety/colour (e.g., "Cherry Red")
        notes: Additional notes (e.g., "Heirloom variety")
        sow_start_month: Optional string for month to start/sow the seeds (e.g., "Oct" or "October")
        sow_end_month: Optional string for month to end sowing (e.g., "Dec" or "December")
        month: Optional three-letter month name for this seed entry (e.g., "Jan", "Feb", "Mar")
        year: Optional integer representing the year for this seed entry
        use_red: Whether to print the seed name in red (default: False)
    
    Returns:
        PIL Image object of the generated label
    """
    
    # Label dimensions for 62mm x 29mm
    label_width = 696
    label_height = 326
    
    # Create a new image with white background for black and white printing
    img = Image.new('RGB', (label_width, label_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fall back to default if not available
    # Try multiple font paths for cross-platform compatibility
    font_paths = [
        # Linux/Lambda paths
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
        # Bundled fonts in Lambda layer or same directory
        ("./fonts/DejaVuSans-Bold.ttf", "./fonts/DejaVuSans.ttf", 
         "./fonts/DejaVuSans-Oblique.ttf", "./fonts/DejaVuSansMono-Bold.ttf"),
        # Windows paths
        ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/ariali.ttf", "C:/Windows/Fonts/consolab.ttf"),
        ("arialbd.ttf", "arial.ttf", "ariali.ttf", "consolab.ttf"),
    ]
    
    font_bold = None
    font_regular = None
    font_italic = None
    font_mono = None
    font_loaded_from = None
    
    for bold_path, regular_path, italic_path, mono_path in font_paths:
        try:
            font_bold = ImageFont.truetype(bold_path, 48)  # Larger main title
            font_regular = ImageFont.truetype(regular_path, 32)  # Larger variety text
            font_italic = ImageFont.truetype(italic_path, 24)  # Larger notes
            font_small = ImageFont.truetype(regular_path, 20)  # Larger date
            font_sow_bold = ImageFont.truetype(bold_path, 22)  # Larger sow label
            font_sow_italic = ImageFont.truetype(regular_path, 22)  # Larger sow months
            font_mono = ImageFont.truetype(mono_path, 18)
            font_loaded_from = bold_path
            print(f"Successfully loaded fonts from: {bold_path}")
            break
        except Exception as e:
            print(f"Failed to load fonts from {bold_path}: {str(e)}")
            continue
    
    # Fallback to default font if no truetype fonts found
    if font_bold is None:
        print("WARNING: Using fallback default fonts - text will be very small")
        font_bold = ImageFont.load_default()
        font_regular = ImageFont.load_default()
        font_italic = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_sow_bold = ImageFont.load_default()
        font_sow_italic = ImageFont.load_default()
        font_mono = ImageFont.load_default()
        font_loaded_from = "default"
    
    # No QR code for CLI version, use full label width for text
    text_area_width = label_width - 40
    padding_left = 20
    padding_top = 15
    line_spacing = 50  # Increased spacing between lines
    notes_line_height = 28  # Increased spacing for notes

    # Draw seed name in bold with wrapping
    max_name_width = text_area_width - padding_left
    wrapped_name = wrap_text(name, font_bold, max_name_width, draw)
    current_y = padding_top
    name_color = "red" if use_red else "black"
    for line in wrapped_name:
        draw.text((padding_left, current_y), line, fill=name_color, font=font_bold)
        current_y += line_spacing

    # Draw variety in standard font with wrapping
    max_variety_width = text_area_width - padding_left
    wrapped_variety = wrap_text(variety, font_regular, max_variety_width, draw)
    for line in wrapped_variety:
        draw.text((padding_left, current_y), line, fill="black", font=font_regular)
        current_y += line_spacing
    
    # Draw optional start/sow month (styled)
    if sow_start_month or sow_end_month:
        # Place the sow month below the variety
        sow_y = current_y
        
        # Build the sow information string
        if sow_start_month and sow_end_month:
            sow_text = f"Sow: {sow_start_month} — {sow_end_month}"
        elif sow_start_month:
            sow_text = f"Sow: {sow_start_month}"
        else:
            # Only end provided
            sow_text = f"Sow End: {sow_end_month}"

        # Draw the entire sow line in a readable font
        draw.text((padding_left, sow_y), sow_text, fill="black", font=font_sow_bold)

        notes_y = current_y + line_spacing + 5  # Extra spacing before notes
    else:
        notes_y = current_y
    
    # Draw notes in italic with wrapping (if provided)
    if notes:
        max_notes_width = text_area_width - padding_left
        wrapped_notes = wrap_text(notes, font_italic, max_notes_width, draw)
        
        for i, line in enumerate(wrapped_notes):
            draw.text((padding_left, notes_y + (i * notes_line_height)), line, fill="black", font=font_italic)
        
        notes_offset = line_spacing
    else:
        notes_offset = 0
    
    # Draw date above branding at bottom (only if month and year are provided)
    if month is not None and year is not None:
        date_str = f"{month}-{year}"
        draw.text((padding_left, label_height - 45), date_str, fill="black", font=font_small)
    
    return img


def print_label(image, printer_ip="192.168.1.232", model="QL-810W", label_size="62", use_red=False):
    """
    Print the label image using brother_ql
    
    Args:
        image: PIL Image object to print
        printer_ip: IP address of the Brother printer
        model: Brother printer model
        label_size: Label size (default: "62" for 62mm)
        use_red: Whether to use red ink (for printers that support it)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a temporary file to store the image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image.save(temp_file.name, format='PNG')
            temp_filename = temp_file.name
        
        # Construct the brother_ql command
        cmd = [
            "brother_ql",
            "-p", f"tcp://{printer_ip}",
            "-m", model,
            "print",
            "-l", label_size
        ]
        
        if use_red:
            cmd.append("--red")
        
        cmd.append(temp_filename)
        
        print(f"Printing label with command: {' '.join(cmd)}")
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up the temporary file
        os.unlink(temp_filename)
        
        if result.returncode == 0:
            print("Label printed successfully!")
            return True
        else:
            print(f"Error printing label: {result.stderr}")
            return False
    
    except FileNotFoundError:
        print("Error: brother_ql command not found. Please install brother_ql package:")
        print("pip install git+https://github.com/BenDutton/brother_ql.git")
        return False
    except Exception as e:
        print(f"Error printing label: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate and print seed labels to a Brother label printer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Tomato" "Cherry Red" --notes "Heirloom variety"
  %(prog)s "Lettuce" "Buttercrunch" --sow-start "Mar" --sow-end "Jul"
  %(prog)s "Basil" "Sweet Genovese" --month 3 --year 2024 --red
  %(prog)s "Carrot" "Nantes" --printer-ip "192.168.1.100" --model "QL-720NW"
        """
    )
    
    # Required arguments
    parser.add_argument("name", help="Seed name (e.g., 'Tomato')")
    parser.add_argument("variety", help="Variety/colour (e.g., 'Cherry Red')")
    
    # Optional arguments
    parser.add_argument("--notes", help="Additional notes (e.g., 'Heirloom variety')", default="")
    parser.add_argument("--sow-start", dest="sow_start_month", 
                       help="Month to start sowing (e.g., 'Mar', 'March')")
    parser.add_argument("--sow-end", dest="sow_end_month", 
                       help="Month to end sowing (e.g., 'Jul', 'July')")
    parser.add_argument("--month", 
                       help="Three-letter month name for this seed entry (e.g., 'Jan', 'Feb', 'Mar')")
    parser.add_argument("--year", type=int, 
                       help="Year for this seed entry")
    
    # Printer configuration
    parser.add_argument("--printer-ip", default="192.168.1.232",
                       help="IP address of Brother printer (default: 192.168.1.232)")
    parser.add_argument("--model", default="QL-810W",
                       help="Brother printer model (default: QL-810W)")
    parser.add_argument("--label-size", default="62",
                       help="Label size in mm (default: 62)")
    parser.add_argument("--red", action="store_true",
                       help="Use red ink for printing")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate label but don't print (save as image instead)")
    
    args = parser.parse_args()
    
    # Validate month if provided
    valid_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if args.month is not None:
        if args.month not in valid_months:
            print(f"Error: Month must be one of: {', '.join(valid_months)}")
            sys.exit(1)
    
    print(f"Generating label for: {args.name} - {args.variety}")
    if args.notes:
        print(f"Notes: {args.notes}")
    if args.sow_start_month or args.sow_end_month:
        sow_info = []
        if args.sow_start_month:
            sow_info.append(f"Start: {args.sow_start_month}")
        if args.sow_end_month:
            sow_info.append(f"End: {args.sow_end_month}")
        print(f"Sowing: {', '.join(sow_info)}")
    if args.month and args.year:
        print(f"Date: {args.month}-{args.year}")
    
    # Generate the label
    try:
        image = generate_seed_label(
            name=args.name,
            variety=args.variety,
            notes=args.notes,
            sow_start_month=args.sow_start_month,
            sow_end_month=args.sow_end_month,
            month=args.month,
            year=args.year,
            use_red=args.red
        )
        
        if args.dry_run:
            # Save to file instead of printing
            filename = f"seed_label_{args.name}_{args.variety}.png".replace(" ", "_").replace("/", "_")
            image.save(filename)
            print(f"Label saved as: {filename}")
        else:
            # Print the label
            success = print_label(
                image, 
                printer_ip=args.printer_ip,
                model=args.model,
                label_size=args.label_size,
                use_red=args.red
            )
            
            if not success:
                print("Failed to print label. Use --dry-run to save as image instead.")
                sys.exit(1)
    
    except Exception as e:
        print(f"Error generating label: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()