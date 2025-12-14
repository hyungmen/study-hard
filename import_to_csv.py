#!/usr/bin/env python3
import argparse
import csv
import json
from itertools import zip_longest


def json_to_rows(obj):
    # obj can be a list of dicts or a dict of lists
    if isinstance(obj, list):
        rows = obj
    elif isinstance(obj, dict):
        # convert dict of lists to list of dicts
        keys = list(obj.keys())
        lists = [obj[k] for k in keys]
        rows = []
        for vals in zip_longest(*lists, fillvalue=None):
            rows.append({k: v for k, v in zip(keys, vals)})
    else:
        raise ValueError("Unsupported JSON structure: expected list or dict")
    return rows


def read_input(path):
    if path.endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        rows = json_to_rows(data)
        return rows
    else:
        # default: treat as CSV/TSV and just copy to output with detection
        # detect delimiter by inspecting first line
        with open(path, 'r', encoding='utf-8') as f:
            sample = f.read(2048)
        if '\t' in sample and sample.count('\t') > sample.count(','):
            delim = '\t'
        else:
            delim = ','
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delim)
            return list(reader)


def write_csv(rows, out_path):
    if not rows:
        # write empty file
        open(out_path, 'w', encoding='utf-8').close()
        return
    # determine fieldnames: preserve order from first row then add others
    fieldnames = []
    for r in rows:
        for k in r.keys():
            if k not in fieldnames:
                fieldnames.append(k)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # ensure all keys present
            out = {k: ('' if r.get(k) is None else r.get(k)) for k in fieldnames}
            writer.writerow(out)


def main():
    p = argparse.ArgumentParser(description='Import data to CSV (from JSON/CSV/TSV)')
    p.add_argument('input', help='Input file path (JSON, CSV, TSV)')
    p.add_argument('output', help='Output CSV path')
    args = p.parse_args()

    rows = read_input(args.input)
    write_csv(rows, args.output)


if __name__ == '__main__':
    main()
