import json
import html
import zipfile
import argparse
import xml.etree.ElementTree as ET


TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def load_root(file_path: str) -> ET.Element:
    if file_path.endswith(".odt"):
        with zipfile.ZipFile(file_path, "r") as odt:
            with odt.open("content.xml") as content_xml:
                tree = ET.parse(content_xml)
                return tree.getroot()

    if file_path.endswith(".xml"):
        tree = ET.parse(file_path)
        return tree.getroot()

    raise ValueError("Only .odt and .xml files are supported")


def extract_zotero_citations(file_path: str) -> list[dict]:
    root = load_root(file_path)

    reference_mark_starts = root.findall(
        f".//{{{TEXT_NS}}}reference-mark-start"
    )

    results = []

    for mark in reference_mark_starts:
        name = mark.get(f"{{{TEXT_NS}}}name")

        if not name:
            continue

        if "ZOTERO_ITEM CSL_CITATION" not in name:
            continue

        decoded = html.unescape(name)

        marker = "CSL_CITATION"
        marker_index = decoded.find(marker)

        if marker_index == -1:
            continue

        after_marker = decoded[marker_index + len(marker):].strip()

        start = after_marker.find("{")
        if start == -1:
            continue

        decoder = json.JSONDecoder()
        citation_json, _ = decoder.raw_decode(after_marker[start:])

        results.append(citation_json)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")

    args = parser.parse_args()

    citations = extract_zotero_citations(args.file)

    print(json.dumps(citations, indent=2, ensure_ascii=False))