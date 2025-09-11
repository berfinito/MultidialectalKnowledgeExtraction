from __future__ import annotations
import argparse, bz2, html, re
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict, Any, Iterable, Optional

import pandas as pd
from tqdm import tqdm

from mdke.utils.io import Paths, ensure_dirs, load_yaml, save_jsonl, get_logger
from mdke.utils.metrics import token_split, normalize_text_basic, latin_hawar_ratio

WIKI_PREFIX = {"tr": "trwiki", "kmr": "kuwiki", "zza": "diqwiki"}

# Core wiki markup
_comment = re.compile(r"<!--.*?-->", flags=re.DOTALL)
_ref = re.compile(r"<ref[^>/]*?/?>.*?</ref>|<ref[^>]*?/>", flags=re.DOTALL | re.IGNORECASE)
_html = re.compile(r"<[^>]+>")
_table = re.compile(r"\{\|.*?\|\}", flags=re.DOTALL)
_template = re.compile(r"\{\{[^{}]*\}\}")
_heading = re.compile(r"^={1,6}\s*(.*?)\s*={1,6}$", flags=re.MULTILINE)
_link = re.compile(r"\[\[([^\[\]]+)\]\]")

# Multi-line localized namespaces (DOTALL)
_filelink = re.compile(
    r"\[\[(?:(?:File|Image|Media|Dosya|Resim|Wêne|Medya|Şekil):[\s\S]*?)\]\]",
    flags=re.IGNORECASE | re.DOTALL,
)
_category = re.compile(
    r"\[\[(?:(?:Category|Kategori(?:ye)?|Kategorî):[\s\S]*?)\]\]",
    flags=re.IGNORECASE | re.DOTALL,
)
_template_link = re.compile(
    r"\[\[(?:(?:Template|Şablon):[\s\S]*?)\]\]",
    flags=re.IGNORECASE | re.DOTALL,
)
_interwiki = re.compile(
    r"\[\[(?:[a-z]{2,3}(?:-[a-z]{2,3})?|wikt|wiktionary|commons|wikidata|wikibooks|wikinews|wikiquote|wikisource|wikiversity|wikivoyage|meta):[\s\S]*?\]\]",
    flags=re.IGNORECASE | re.DOTALL,
)

# External links, bare URLs
_external_link = re.compile(r"\[(https?:\/\/[^\s\]]+)(\s+[^\]]+)?\]")
_bare_url = re.compile(r"https?://[^\s\]]+", flags=re.IGNORECASE)

# Style attributes
_style_attrs = re.compile(
    r"(^|[|])\s*(?:align|colspan|rowspan|bgcolor|background(?:-color)?|color|nowrap|border|style|valign|width|height|class)\s*[:=]\s*[-#\w%\"'.]+",
    flags=re.IGNORECASE | re.MULTILINE,
)
_style_freeform = re.compile(
    r"\b(?:align|colspan|rowspan|bgcolor|background(?:-color)?|color|nowrap|border|style|valign|width|height|class)\b(?:\s*[:=]\s*|[\s\|]+)?[#\w%\"'.-]*",
    flags=re.IGNORECASE,
)
_hex_color = re.compile(r"#[0-9a-fA-F]{3,8}")

_ns_plain_line = re.compile(
    r"(?mi)^(?:Category|Kategori(?:ye)?|Kategorî|Portal|Portalê|Wêne|Resim|Dosya|Media|Medya|Şekil)\s*:\s*[^\n]+$"
)
_table_row_or_cell = re.compile(r"(?m)^\s*(?:\|\-|\||!).*$")
_list_marker = re.compile(r"(?m)^[*#;:]+\s*")
_citation_brackets = re.compile(r"\[(?:\d{1,3}|[ivxlcdm]{1,6})\]", flags=re.IGNORECASE)

# Bare file/media namespace (no [[ ]])
_bare_file_ns = re.compile(
    r"(?:^|[\s(])(?:File|Image|Media|Dosya|Resim|Wêne|Medya|Şekil)\s*:\s*[^\]\r\n]+",
    flags=re.IGNORECASE | re.MULTILINE,
)

# Residual bracket tokens
_bracket_tokens = re.compile(r"\[\[|\]\]|\{\{|\}\}")

# Residual media tokens (küçükresim, thumb, orientation, direction words)
_residual_media = re.compile(
    r"\b(?:küçükresim|thumb(?:nail)?|upright=?\d*(?:\.\d+)?|left|right|sağ|sol|center|frameless)\b",
    flags=re.IGNORECASE,
)

def _link_repl(m: re.Match) -> str:
    parts = m.group(1).split("|")
    return parts[-1] if len(parts) >= 2 else parts[0]

def clean_wikitext(text: str, max_template_passes: int = 8) -> str:
    s = text or ""
    s = html.unescape(s).replace("\u00A0", " ")
    s = re.sub(r"&\s*nbsp;?", " ", s, flags=re.IGNORECASE)

    s = _comment.sub(" ", s)
    s = _ref.sub(" ", s)
    s = _table.sub(" ", s)

    for _ in range(max_template_passes):
        before = s
        s = _template.sub(" ", s)
        if s == before:
            break

    s = _filelink.sub(" ", s)
    s = _category.sub(" ", s)
    s = _template_link.sub(" ", s)
    s = _interwiki.sub(" ", s)

    s = _external_link.sub(lambda m: (m.group(2) or " ").strip(), s)
    s = _link.sub(_link_repl, s)

    s = _table_row_or_cell.sub(" ", s)
    s = _bare_file_ns.sub(" ", s)

    s = _style_attrs.sub(" ", s)
    s = _style_freeform.sub(" ", s)
    s = _hex_color.sub(" ", s)

    s = _heading.sub(r"\1", s)
    s = _html.sub(" ", s)

    s = _ns_plain_line.sub(" ", s)
    s = _list_marker.sub("", s)

    s = _citation_brackets.sub(" ", s)
    s = _bare_url.sub(" ", s)
    s = _bracket_tokens.sub(" ", s)

    # Remove residual media/control tokens
    s = _residual_media.sub(" ", s)

    s = re.sub(r"[^\S\r\n]+", " ", s)
    s = re.sub(r"\n{2,}", "\n\n", s)
    return s.strip()

def paragraphs(s: str) -> Iterable[str]:
    if not s:
        return
    for p in re.split(r"\n\s*\n", s):
        p = p.strip()
        if p:
            yield p

def iter_pages(bz2_path: Path):
    with bz2.open(bz2_path, "rb") as f:
        context = ET.iterparse(f, events=("end",))
        for event, elem in context:
            if elem.tag.endswith("page"):
                yield elem
                elem.clear()

def extract_page_info(page_elem: ET.Element) -> Optional[Dict[str, Any]]:
    def find(tag: str) -> Optional[ET.Element]:
        for child in page_elem.iter():
            if child.tag.endswith(tag):
                return child
        return None
    ns = find("ns")
    if ns is None or ns.text != "0":
        return None
    for child in page_elem:
        if child.tag.endswith("redirect"):
            return None
    title_el = find("title")
    id_el = find("id")
    text_el = None
    for child in page_elem.iter():
        if child.tag.endswith("text"):
            text_el = child
    if title_el is None or id_el is None or text_el is None:
        return None
    return {"page_id": int(id_el.text), "title": title_el.text or "", "text": text_el.text or ""}

def run(cfg, lang: str, limit_pages: Optional[int], min_tokens: int,
        out_tag: str = "", max_digit_ratio: float = 0.6):
    logger = get_logger(f"wiki_ingest_{lang}")
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    bz2_path = paths.raw / f"wiki/{lang}/{WIKI_PREFIX[lang]}-latest-pages-articles.xml.bz2"
    if not bz2_path.exists():
        raise FileNotFoundError(f"Missing dump: {bz2_path}")

    out_tag = f"_{out_tag}" if out_tag else ""
    out_jsonl = paths.interim / f"text/wiki_{lang}{out_tag}.jsonl"
    out_parquet = paths.processed / f"wiki_{lang}{out_tag}.parquet"
    out_csv = paths.processed / f"wiki_{lang}{out_tag}.csv"

    items = []
    stats = {"pages": 0, "paras": 0, "kept": 0, "skipped_short": 0, "skipped_digit": 0}

    for page in tqdm(iter_pages(bz2_path), desc=f"wiki[{lang}]"):
        info = extract_page_info(page)
        if not info:
            continue
        stats["pages"] += 1
        cleaned = clean_wikitext(info["text"])
        pid = info["page_id"]; title = info["title"]

        for pi, para in enumerate(paragraphs(cleaned)):
            toks = token_split(para)
            stats["paras"] += 1
            if len(toks) < min_tokens:
                stats["skipped_short"] += 1
                continue
            digit_ratio = (sum(ch.isdigit() for ch in para) / max(1, len(para)))
            if digit_ratio > max_digit_ratio:
                stats["skipped_digit"] += 1
                continue
            items.append({
                "doc_id": f"{pid}-p{pi}",
                "page_id": pid,
                "title": title,
                "lang": lang,
                "source": "wiki",
                "text": para,
                "text_norm": normalize_text_basic(para),
                "n_chars": len(para),
                "n_tokens": len(toks),
            })
            stats["kept"] += 1
        if limit_pages and stats["pages"] >= limit_pages:
            break

    save_jsonl(items, out_jsonl)
    df = pd.DataFrame(items)
    try:
        out_parquet.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_parquet, index=False)
        written = str(out_parquet)
    except Exception:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        written = str(out_csv)

    lh = float(latin_hawar_ratio([it["text"] for it in items])) if items else 0.0
    logger.info(
        f"Pages={stats['pages']} Paras={stats['paras']} Kept={stats['kept']} "
        f"Short={stats['skipped_short']} Digit={stats['skipped_digit']} latin_hawar={lh:.3f}"
    )
    logger.info(f"JSONL -> {out_jsonl}")
    logger.info(f"Table -> {written}")
    return {"stats": stats, "latin_hawar_ratio": lh,
            "out": {"jsonl": str(out_jsonl), "table": written}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--limit_pages", type=int, default=None)
    ap.add_argument("--min_tokens", type=int, default=5)
    ap.add_argument("--max_digit_ratio", type=float, default=0.6,
                    help="Skip paragraphs with digit-char ratio above this")
    ap.add_argument("--tag", type=str, default="")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    res = run(cfg, args.lang, args.limit_pages, args.min_tokens,
              args.tag, args.max_digit_ratio)
    print(res)

if __name__ == "__main__":
    main() 