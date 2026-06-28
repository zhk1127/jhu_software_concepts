"""Clean and normalize GradCafe applicant records for database loading."""

import json
import re
import html as html_lib


INPUT_FILE = "applicant_data.json"
OUTPUT_FILE = "cleaned_applicant_data.json"
LOG_FILE = "cleaning_log.txt"


def load_data(filename=INPUT_FILE):
    """Load JSON applicant records from disk."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data, filename=OUTPUT_FILE):
    """Save cleaned applicant records to disk as JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def clean_text(value):
    """Normalize text values and remove empty placeholders."""
    if value is None:
        return None

    cleaned = str(value)
    cleaned = html_lib.unescape(cleaned)
    cleaned = cleaned.replace("\n", " ")
    cleaned = cleaned.replace("\t", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def extract_gpa_from_comments(comments):
    """Extract a GPA value from free-text comments when available."""
    if not comments:
        return None

    cleaned_comments = clean_text(comments)

    match = re.search(
        r"\bGPA[:\s]+([0-4]\.\d{1,2})\b",
        cleaned_comments,
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return None


def make_llm_program_field(program, university):
    """Create a normalized program field for LLM-enhanced records."""
    program = clean_text(program)
    university = clean_text(university)

    if program and university:
        return f"{program}, {university}"
    if program:
        return program
    if university:
        return university

    return ""


def clean_record(record):
    """Clean and normalize a single applicant record."""
    cleaned = record.copy()

    original_program = record.get("program")
    original_university = record.get("university")
    original_comments = record.get("comments")

    cleaned["original_program"] = original_program
    cleaned["original_university"] = original_university

    cleaned["program"] = make_llm_program_field(
        original_program,
        original_university,
    )

    cleaned["comments"] = clean_text(original_comments)

    if record.get("GPA") is None:
        cleaned["gpa_from_comments"] = extract_gpa_from_comments(
            original_comments
        )
    else:
        cleaned["gpa_from_comments"] = None

    return cleaned


def clean_data(input_records):
    """Clean a collection of applicant records."""
    return [clean_record(record) for record in input_records]


def write_log(original_records, output_records, filename=LOG_FILE):
    """Write a cleaning summary log to disk."""
    comment_change_count = 0
    missing_gpa_found_count = 0
    examples = []

    for original, cleaned in zip(original_records, output_records):
        if original.get("comments") != cleaned.get("comments"):
            comment_change_count += 1

        gpa_from_comments = cleaned.get("gpa_from_comments")

        if gpa_from_comments is not None:
            missing_gpa_found_count += 1

            if len(examples) < 10:
                examples.append((original, cleaned))

    with open(filename, "w", encoding="utf-8") as f:
        f.write("Cleaning Log\n")
        f.write("============\n\n")
        f.write(f"Input records: {len(original_records)}\n")
        f.write(f"Output records: {len(output_records)}\n")
        f.write(f"Records prepared for LLM input: {len(output_records)}\n")
        f.write(f"Comment fields changed by text cleaning: {comment_change_count}\n")
        f.write(
            "Missing GPA values found in comments by regex: "
            f"{missing_gpa_found_count}\n\n"
        )

        f.write("Notes\n")
        f.write("-----\n")
        f.write(
            "The program and university fields were combined into a single "
            "program field to match the input format expected by the TinyLlama "
            "standardizer. The original values are preserved as "
            "original_program and original_university.\n\n"
        )

        f.write("Examples Where Regex Found Missing GPA Information\n")
        f.write("--------------------------------------------------\n\n")

        for i, (original, cleaned) in enumerate(examples, start=1):
            f.write(f"Example {i}\n")
            f.write(f"URL: {original.get('url')}\n")
            f.write("Before:\n")
            f.write(f"  GPA: {original.get('GPA')}\n")
            f.write(f"  comments: {original.get('comments')}\n")
            f.write("After:\n")
            f.write(f"  GPA: {cleaned.get('GPA')}\n")
            f.write(
                f"  gpa_from_comments: {cleaned.get('gpa_from_comments')}\n"
            )
            f.write("\n")


if __name__ == "__main__":  # pragma: no cover
    records = load_data()
    cleaned_output = clean_data(records)

    save_data(cleaned_output)
    write_log(records, cleaned_output)

    print(f"Loaded {len(records)} records.")
    print(f"Saved {len(cleaned_output)} records to {OUTPUT_FILE}")
    print(f"Wrote cleaning summary to {LOG_FILE}")
