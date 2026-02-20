#!/usr/bin/env python3
"""Subtract interpolated correction values from a calibration file.

Usage: adjust-cal <calibration_file> <reference_file> <start_freq> [--fade-in]
"""
import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Subtract interpolated correction from a calibration file.")
    parser.add_argument("cal_file", help="Calibration file to adjust (overwritten in place)")
    parser.add_argument("ref_file", help="Reference correction file")
    parser.add_argument("start_freq", type=float, help="Frequency (Hz) at which full correction begins")
    parser.add_argument("--fade-in", action="store_true",
                        help="Linearly fade correction from 20 Hz (0%%) to start_freq (100%%)")
    args = parser.parse_args()

    # Read calibration file (tab-separated, header + blank line + data)
    freqs_cal = []
    vals_cal = []
    with open(args.cal_file) as f:
        lines = f.readlines()

    header_line = lines[0]
    blank_line = lines[1]

    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) == 2:
            freqs_cal.append(float(parts[0]))
            vals_cal.append(float(parts[1]))

    # Read reference file (space-separated, comments start with *)
    freqs_ref = []
    vals_ref = []
    with open(args.ref_file) as f:
        for line in f:
            if line.startswith('*') or line.strip() == '':
                continue
            parts = line.strip().split()
            if len(parts) == 2:
                freqs_ref.append(float(parts[0]))
                vals_ref.append(float(parts[1]))

    freqs_ref = np.array(freqs_ref)
    vals_ref = np.array(vals_ref)
    log_freqs_ref = np.log10(freqs_ref)

    sf = args.start_freq

    # Get correction value at start_freq for fade-in
    correction_at_sf = float(np.interp(np.log10(sf), log_freqs_ref, vals_ref))

    if args.fade_in:
        print(f"Fade-in enabled: 20 Hz (0%) -> {sf} Hz (100%)")
        print(f"Correction value at {sf} Hz: {correction_at_sf:+.3f} dB")

    # Process
    new_vals = []
    for freq, val in zip(freqs_cal, vals_cal):
        if freq >= sf:
            interp_val = float(np.interp(np.log10(freq), log_freqs_ref, vals_ref))
            new_val = round(val - interp_val, 1)
        elif args.fade_in and freq > 20.0:
            blend = (freq - 20.0) / (sf - 20.0)
            new_val = round(val - correction_at_sf * blend, 1)
        else:
            new_val = val
        new_vals.append(new_val)

    # Write back
    with open(args.cal_file, "w") as f:
        f.write(header_line)
        f.write(blank_line)
        for freq, val in zip(freqs_cal, new_vals):
            f.write(f"{freq:.2f}\t{val}\n")

    # Report
    print(f"Done. {len(freqs_cal)} points total.")

    if args.fade_in:
        print(f"\nFade-in zone (20-{sf} Hz):")
        for freq, orig, nv in zip(freqs_cal, vals_cal, new_vals):
            if freq <= sf + 2:
                blend = 0.0 if freq <= 20.0 else min((freq - 20.0) / (sf - 20.0), 1.0)
                if freq >= sf:
                    added = float(np.interp(np.log10(freq), log_freqs_ref, vals_ref))
                else:
                    added = correction_at_sf * blend
                print(f"  {freq:8.2f} Hz: orig={orig:+.1f}  added={added:+.3f}  blend={blend:.0%}  result={nv:+.1f}")

    print("\nSamples at key frequencies:")
    for freq, orig, nv in zip(freqs_cal, vals_cal, new_vals):
        if any(abs(freq - t) < 1.5 for t in [100, 1000, 5000, 10000, 15000, 20000]):
            interp_val = float(np.interp(np.log10(freq), log_freqs_ref, vals_ref))
            print(f"  {freq:10.2f} Hz: orig={orig:+.1f}  ref={interp_val:+.3f}  result={nv:+.1f}")


if __name__ == "__main__":
    main()
