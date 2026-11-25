"""Audit keyword coverage and approximate a speaker-disjoint train/test split."""

import argparse
import csv
import hashlib
import json
import re


FIELDS = ["speaker", "utterance", "text"]
TOKEN = re.compile(r"[^\W_]+")


def tokens(text):
    return TOKEN.findall(text.casefold())


def speaker_split(speaker, seed, test_percent):
    payload = json.dumps([seed, speaker], ensure_ascii=False).encode("utf-8")
    rank = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return "test" if rank * 100 < (1 << 64) * test_percent else "train"


def audit(stream, keywords, seed, test_percent):
    normalized = [tokens(word) for word in keywords]
    if not normalized or any(len(word) != 1 for word in normalized):
        raise ValueError("Provide at least one single-token keyword.")
    targets = {word[0] for word in normalized}
    if len(targets) != len(normalized):
        raise ValueError("Keywords must be distinct after case folding.")
    if not 0 <= test_percent <= 100:
        raise ValueError("Test percentage must be between 0 and 100.")

    rows = csv.DictReader(stream, delimiter="\t", strict=True)
    if rows.fieldnames != FIELDS:
        raise ValueError("Expected TSV columns in order: speaker, utterance, text.")
    counts = {
        name: {"rows": 0, "unmatched": 0, "ambiguous": 0,
               "keywords": dict.fromkeys(sorted(targets), 0)}
        for name in ("train", "test")
    }
    speakers = {name: set() for name in counts}
    utterances = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Wrong number of columns at line {rows.line_num}.")
        speaker = row["speaker"].strip()
        utterance = row["utterance"].strip()
        if not speaker or not utterance:
            raise ValueError(f"Empty speaker or utterance ID at line {rows.line_num}.")
        if utterance in utterances:
            raise ValueError(f"Duplicate utterance ID at line {rows.line_num}.")
        utterances.add(utterance)
        name = speaker_split(speaker, seed, test_percent)
        speakers[name].add(speaker)
        count = counts[name]
        count["rows"] += 1
        matched = targets.intersection(tokens(row["text"]))
        if not matched:
            count["unmatched"] += 1
        elif len(matched) > 1:
            count["ambiguous"] += 1
        else:
            count["keywords"][matched.pop()] += 1
    for name, count in counts.items():
        count["speakers"] = len(speakers[name])
    return {"rows": len(utterances), "splits": counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tsv", help="UTF-8 input with speaker, utterance and text columns")
    parser.add_argument("--keywords", nargs="+", required=True)
    parser.add_argument("--seed", default="example")
    parser.add_argument("--test-percent", type=int, default=40)
    args = parser.parse_args()
    try:
        with open(args.tsv, encoding="utf-8", newline="") as stream:
            report = audit(stream, args.keywords, args.seed, args.test_percent)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
