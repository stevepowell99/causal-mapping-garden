from pathlib import Path
import pandas as pd

# Script purpose: Read the first 3 rows of an Excel file and output one .txt per row
# Each line: **Column header**: column text
# Special handling:
# - One-hot groups:
#   - Columns starting with "MCQType of change_" → **MCQType of change**: label1, label2
#   - Columns starting with "TypeOfChangeCluster_" → **TypeOfChangeCluster**: label1, label2
# - Binary columns:
#   - "The change was unintended" → YES if 1 else NO
#   - "Outcome is negative" → YES if 1 else NO

# Update this path if needed; current default is the user's provided file
INPUT_XLSX = r"C:\Users\Zoom\My Drive (hello@causalmap.app)\Causal Map\01-09 Projects and Proposals\03 - Consultancy projects\Intrac SCC Alastair\CM project - shared with Intrac\Harvested Outcomes 2021-2025\Master dataset_SCC Alliance OH FINAL.xlsx"


def is_marked_one(value) -> bool:
    """Return True if the cell represents 1 (supports numeric 1 or string '1')."""
    if pd.isna(value):
        return False
    if isinstance(value, (int, float)):
        try:
            return float(value) == 1.0
        except Exception:
            return False
    if isinstance(value, str):
        return value.strip() == "1"
    return False


def row_to_text_lines(headers, values):
    """Convert a row into lines, grouping specific one-hot columns by prefix."""
    lines = []

    # Define grouped prefixes and their display names
    group_prefixes = {
        "MCQType of change_": "MCQType of change",
        "TypeOfChangeCluster_": "TypeOfChangeCluster",
    }
    grouped_values = {display: [] for display in group_prefixes.values()}

    # Define binary columns requiring YES/NO output
    yes_no_columns = {
        "The change was unintended",
        "Outcome is negative",
    }

    non_group_pairs = []
    for col, val in zip(headers, values):
        col_str = str(col)
        matched = False
        for prefix, display in group_prefixes.items():
            if col_str.startswith(prefix):
                label = col_str[len(prefix):]
                if is_marked_one(val):
                    grouped_values[display].append(label)
                matched = True
                break
        if not matched:
            if col_str in yes_no_columns:
                # Map 1 → YES, else NO
                cell_text = "YES" if is_marked_one(val) else "NO"
            else:
                # Normalize cell text; treat NaN/None as empty and flatten newlines
                cell_text = "" if pd.isna(val) else str(val)
                cell_text = cell_text.replace("\r\n", " ").replace("\n", " ")
            non_group_pairs.append((col_str, cell_text))

    # Emit non-group columns
    for col_str, cell_text in non_group_pairs:
        lines.append(f"**{col_str}**: {cell_text}")

    # Emit grouped columns if any values are marked
    for display, labels in grouped_values.items():
        if labels:
            lines.append(f"**{display}**: {', '.join(labels)}")

    return lines


def write_text_document(output_path: Path, text_lines):
    """Write plain text lines to the given path."""
    content = "\n".join(text_lines) + "\n"
    output_path.write_text(content, encoding="utf-8")


def main():
    # Resolve output directory relative to this script's location
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read Excel and restrict to the first 3 rows
    df = pd.read_excel(INPUT_XLSX)
#    df = df.head(3)

    # Generate one .txt per row: row_1.txt, row_2.txt, row_3.txt
    headers = list(df.columns)
    for row_idx in range(len(df)):
        values = [df.iloc[row_idx][col] for col in headers]
        text_lines = row_to_text_lines(headers, values)
        out_file = output_dir / f"row_{row_idx + 1}.txt"
        write_text_document(out_file, text_lines)


if __name__ == "__main__":
    main()


