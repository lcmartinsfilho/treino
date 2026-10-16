#!/usr/bin/env python3
"""Gera um epub só com as tabelas de treino.md: uma página por tabela e por pessoa.
Uso: build_epub.py treino.md treino.epub"""
import html
import sys
import uuid
import zipfile
from pathlib import Path

e = html.escape
CSS = (Path(__file__).parent / "epub.css").read_text(encoding="utf-8")
PEOPLE = [("Lucas", 3), ("Luiz", 4)]  # nome, índice da coluna no markdown


def parse(md):
    """Retorna [(titulo, [linhas])] com cada linha como lista de células."""
    sections = []
    for line in md.splitlines():
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif line.startswith("|") and sections:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            sections[-1][1].append(cells)
    return sections


def font_vw(header, rows):
    """Tamanho de fonte (em %) para a tabela inteira caber numa linha por célula."""
    em = 0.0
    for i in range(len(header)):
        w = max(len(header[i]) * 0.8, *(len(r[i]) * 0.58 for r in rows))
        em += w + 1.1  # preenchimento horizontal da célula
    # 1vw = 4.02px num iPhone em retrato; devolve % de uma base de 16px (vw não é respeitado pelo Apple Livros)
    return min(4.2, 90 / (em * 0.93)) * 4.02 / 16 * 100


def page(title, header, rows):
    vw = font_vw(header, rows)
    th = "".join(f"<th>{e(c)}</th>" for c in header)
    trs = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows)
    return ('<?xml version="1.0" encoding="utf-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="pt-BR">'
            f'<head><meta charset="utf-8"/><title>{e(title)}</title><link rel="stylesheet" href="style.css"/>'
            f'<style>body{{font-size:{vw:.0f}%}}</style></head>'
            f"<body><h1>{e(title)}</h1><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></body></html>")


def main(src, dst):
    sections = parse(Path(src).read_text(encoding="utf-8"))
    pages = []  # (arquivo, titulo, xhtml)
    for person, col in PEOPLE:
        for n, (name, rows) in enumerate(sections):
            header, body = rows[0], rows[1:]
            h = header[:3] + ["Carga"]
            b = [[r[0], r[1].split(" — ")[0]] + r[2:3] + [r[col]] for r in body]
            title = f"{person} · {name}"
            pages.append((f"{person.lower()}-{n}.xhtml", title, page(title, h, b)))

    manifest = "".join(f'<item id="p{i}" href="{f}" media-type="application/xhtml+xml"/>' for i, (f, _, _) in enumerate(pages))
    spine = "".join(f'<itemref idref="p{i}"/>' for i in range(len(pages)))
    opf = ('<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           f'<dc:identifier id="id">urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, "treino")}</dc:identifier>'
           '<dc:title>Treino</dc:title><dc:language>pt-BR</dc:language>'
           '<meta property="dcterms:modified">2000-01-01T00:00:00Z</meta></metadata><manifest>'
           '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
           f'<item id="css" href="style.css" media-type="text/css"/>{manifest}</manifest><spine>{spine}</spine></package>')
    items = "".join(f'<li><a href="{f}">{e(t)}</a></li>' for f, t, _ in pages)
    nav = ('<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
           f'<head><title>Treino</title></head><body><nav epub:type="toc"><ol>{items}</ol></nav></body></html>')
    with zipfile.ZipFile(dst, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("content.opf", opf)
        z.writestr("nav.xhtml", nav)
        z.writestr("style.css", CSS)
        for f, _, x in pages:
            z.writestr(f, x)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
