#!/usr/bin/env python3
import itertools
import os
import shutil
import time
from math import ceil

def ensure_free_space(min_free_gb: float) -> bool:
    total, used, free = shutil.disk_usage(".")
    return (free / (1024**3)) >= min_free_gb

def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:.2f} {u}"
        x /= 1024
    return f"{x:.2f} TB"

def estimate_total_bytes(prefixes, middle_length, suffixes, newline_bytes=1) -> int:
    """
    Estimate output size:
    avg_line_len = avg(len(prefix)+middle_length+len(suffix)) + newline
    total_bytes ≈ total_lines * avg_line_len
    """
    avg_prefix_len = sum(len(p) for p in prefixes) / max(1, len(prefixes))
    avg_suffix_len = sum(len(s) for s in suffixes) / max(1, len(suffixes))
    avg_line_len = int(round(avg_prefix_len + middle_length + avg_suffix_len + newline_bytes))
    total_lines = len(prefixes) * (26 ** middle_length) * len(suffixes)
    return total_lines * avg_line_len

def generate(prefixes, middle_length, suffixes, output_file,
             resume_from=None,
             min_free_gb=1.0,
             show_progress=True,
             progress_every=50000,
             split_every_lines=None):
    """
    Generates: prefix + (lowercase-only middle) + suffix

    split_every_lines:
      - None => write to one file (output_file)
      - int  => split into multiple files, each with N lines
               ex: output_file="wordlist.txt" -> wordlist_part001.txt, etc.
    """
    lowercase = [chr(c) for c in range(ord('a'), ord('z') + 1)]

    total_lines = len(prefixes) * (len(lowercase) ** middle_length) * len(suffixes)

    # Print plan before starting
    est_bytes = estimate_total_bytes(prefixes, middle_length, suffixes)
    print(f"Generating {total_lines:,} entries")
    print(f"Prefixes: {prefixes}")
    print(f"Lowercase-only middle length: {middle_length}")
    print(f"Suffixes: {suffixes}")
    print(f"Estimated output size: ~{human_bytes(est_bytes)}")

    # If splitting, print how many files to expect
    if split_every_lines:
        parts = ceil(total_lines / split_every_lines)
        print(f"Splitting: {split_every_lines:,} lines per file (~{parts} files)")
    print()

    done = 0
    started = resume_from is None

    start_time = time.time()
    last_time = start_time
    last_done = 0

    # output management
    base_name, ext = os.path.splitext(output_file)
    part_index = 1
    part_lines_written = 0

    def open_part_file(idx: int):
        if not split_every_lines:
            mode = "a" if resume_from else "w"
            return open(output_file, mode)
        else:
            fname = f"{base_name}_part{idx:03d}{ext or '.txt'}"
            # If resuming into split mode, safest is append (so you don't overwrite).
            # For fresh run, overwrite part001.
            mode = "a" if resume_from else ("w" if idx == 1 else "w")
            return open(fname, mode)

    out = open_part_file(part_index)

    try:
        for p in prefixes:
            for combo in itertools.product(lowercase, repeat=middle_length):
                mid = "".join(combo)
                for suf in suffixes:
                    if not ensure_free_space(min_free_gb):
                        print(f"\nStopped: free disk space fell below {min_free_gb} GB.")
                        print(f"Resume from: prefix={p!r}, middle={mid!r}, suffix={suf!r}")
                        return

                    # Resume: skip until exact match
                    if not started:
                        if (p, mid, suf) == resume_from:
                            started = True
                        else:
                            done += 1
                            continue

                    # Split logic
                    if split_every_lines and part_lines_written >= split_every_lines:
                        out.close()
                        part_index += 1
                        part_lines_written = 0
                        out = open_part_file(part_index)

                    out.write(p + mid + suf + "\n")
                    done += 1
                    part_lines_written += 1

                    # Progress + speed + ETA
                    if show_progress and (done % progress_every == 0 or done == total_lines):
                        now = time.time()
                        dt = now - last_time
                        dp = done - last_done
                        speed = (dp / dt) if dt > 0 else 0.0  # lines/sec

                        elapsed = now - start_time
                        remaining = total_lines - done
                        eta_sec = int(remaining / speed) if speed > 0 else -1

                        if eta_sec >= 0:
                            eta_h = eta_sec // 3600
                            eta_m = (eta_sec % 3600) // 60
                            eta_s = eta_sec % 60
                            eta_str = f"{eta_h:02d}:{eta_m:02d}:{eta_s:02d}"
                        else:
                            eta_str = "??:??:??"

                        pct = int(done / total_lines * 100)
                        print(
                            f"Processed {done:,}/{total_lines:,} ({pct}%) | "
                            f"{speed:,.0f} lines/s | ETA {eta_str}",
                            end="\r"
                        )

                        last_time = now
                        last_done = done

    finally:
        out.close()

    print("\nDone!")

if __name__ == "__main__":
    # --- YOU EDIT THESE ---
    base_prefix = "Ea"     # can include uppercase
    middle_length = 6      # lowercase-only chars count
    suffixes = ["1$"]      # you can add more: ["1$", "!", "2026!"]
    output_file = "wordlist.txt"

    # Prefix variants (optional). If you only want exactly "Da", set: prefixes = ["Da"]
    prefix_variants = [
        base_prefix,
        base_prefix[:1].upper() + base_prefix[1:],
        base_prefix.lower(),
        base_prefix.upper(),
    ]
    prefixes = list(dict.fromkeys(prefix_variants))

    # Optional resume point
    resume_from = None  # example: ("Da", "abcz", "1$")

    # Safety + UX settings
    min_free_gb = 1.0
    progress_every = 50000

    # Optional splitting: set to an int like 5_000_000 lines per file, or None for one file
    split_every_lines = None  # example: 2_000_000

    generate(
        prefixes=prefixes,
        middle_length=middle_length,
        suffixes=suffixes,
        output_file=output_file,
        resume_from=resume_from,
        min_free_gb=min_free_gb,
        show_progress=True,
        progress_every=progress_every,
        split_every_lines=split_every_lines
    )
