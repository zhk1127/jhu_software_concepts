import json

DATA_FILE = "llm_extend_applicant_data_full.jsonl"

TARGET_UNIVERSITIES = {
    "Georgetown University",
    "Massachusetts Institute of Technology",
    "MIT",
    "Stanford University",
    "Carnegie Mellon University",
}

matching_ids = []
total_records = 0

with open(DATA_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        item = json.loads(line)
        total_records += 1

        status = item.get("status")
        term = item.get("term")
        degree = item.get("Degree")

        # These are the LLM-generated fields.
        llm_program = item.get("llm-generated-program") or ""
        llm_university = item.get("llm-generated-university") or ""

        if (
            status == "Accepted"
            and degree == "PhD"
            and "2026" in str(term)
            and llm_program.lower() == "computer science"
            and llm_university in TARGET_UNIVERSITIES
        ):
            pid = item.get("raw_record", {}).get("id")
            matching_ids.append(pid)

            print(
                pid,
                "| original:",
                item.get("program"),
                "| LLM program:",
                llm_program,
                "| LLM university:",
                llm_university,
            )

print("\nQ9")
print("Total LLM-processed records:", total_records)
print("Q8 count using LLM-generated fields:", len(matching_ids))

print("\nMatching IDs:")
for pid in sorted(matching_ids):
    print(pid)