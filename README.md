# EMM-6 Microphone Calibration

Tools for adjusting Dayton Audio EMM-6 calibration files.

## Setup

```bash
uv sync
```

## Usage

Subtract interpolated correction values from a calibration file:

```bash
# Using the CLI entry point
uv run adjust-cal <calibration_file> <reference_file> <start_freq> [--fade-in]

# Or directly
uv run python3 emm6/adjust_cal.py <calibration_file> <reference_file> <start_freq> [--fade-in]
```

### Arguments

- `calibration_file` — file to adjust (overwritten in place)
- `reference_file` — reference correction data (e.g. `0over90_100hz+.txt`)
- `start_freq` — frequency (Hz) at which full correction begins

### Options

- `--fade-in` — linearly fade correction from 20 Hz (0%) to `start_freq` (100%). Without this flag, frequencies below `start_freq` are left intact.

### Example

```bash
uv run adjust-cal 34814_90deg.txt 0over90_100hz+.txt 100
uv run adjust-cal 34814_90deg.txt 0over90_100hz+.txt 60 --fade-in
```
