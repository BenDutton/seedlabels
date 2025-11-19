# Seed Labels

A CLI tool for generating and printing seed labels to Brother label printers.

## Features

- Generate professional seed labels with name, variety, notes, and sowing information
- Print directly to Brother QL-series label printers over network
- Support for red ink printing on compatible models
- Customizable printer settings (IP, model, label size)
- Dry-run mode to preview labels before printing

## Installation

1. Install the required dependencies:
```bash
pip install pillow
pip install git+https://github.com/BenDutton/brother_ql.git
```

2. Clone this repository:
```bash
git clone https://github.com/BenDutton/seedlabels.git
cd seedlabels
```

## Usage

### Basic Usage
```bash
python seeds.py "Tomato" "Cherry Red"
```

### With Notes and Sowing Information
```bash
python seeds.py "Lettuce" "Buttercrunch" --notes "Fast growing" --sow-start "Mar" --sow-end "Jul"
```

### With Red Ink
```bash
python seeds.py "Basil" "Sweet Genovese" --red
```

### Custom Printer IP
```bash
python seeds.py "Carrot" "Nantes" --printer-ip "192.168.1.100"
```

### Dry Run (Save as Image)
```bash
python seeds.py "Pepper" "Jalapeño" --dry-run
```

### Full Example
```bash
python seeds.py "Pepper" "Jalapeño" \
  --notes "Hot variety" \
  --sow-start "Feb" \
  --sow-end "Apr" \
  --month 3 \
  --year 2024 \
  --red \
  --printer-ip "192.168.1.232"
```

## Command Line Arguments

### Required Arguments
- `name` - Seed name (e.g., "Tomato")
- `variety` - Variety/colour (e.g., "Cherry Red")

### Optional Arguments
- `--notes` - Additional notes about the seed
- `--sow-start` - Month to start sowing (e.g., "Mar", "March")
- `--sow-end` - Month to end sowing (e.g., "Jul", "July")
- `--month` - Month number (1-12) for this seed entry
- `--year` - Year for this seed entry

### Printer Configuration
- `--printer-ip` - IP address of Brother printer (default: 192.168.1.232)
- `--model` - Brother printer model (default: QL-810W)
- `--label-size` - Label size in mm (default: 62)
- `--red` - Use red ink for printing (flag)
- `--dry-run` - Generate label but don't print (save as image instead)

## Supported Printers

This tool works with Brother QL-series label printers that support network printing, including:
- QL-810W
- QL-820NWB
- QL-720NW
- And other compatible models

## Label Specifications

- Designed for 62mm x 29mm labels
- Resolution: 696 x 326 pixels
- Format: PNG
- Color: Black and white (with optional red for supported printers)

## Requirements

- Python 3.6+
- Pillow (PIL)
- brother_ql (from BenDutton fork)
- Brother QL-series label printer with network connectivity

## License

MIT
