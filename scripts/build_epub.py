#!/usr/bin/env python3
"""Gera um epub só com as tabelas de treino.md (sem capa, sem sumário). Uso: build_epub.py treino.md treino.epub"""
import html, re, sys, uuid, zipfile

CSS = open(__file__.replace("build_epub.py", "epub.css"), encoding="utf-8").read()
e = html.escape


def render(md):
    out, in_table = [], False
    for line in md.splitlines():
        if line.startswith("## "):
            out.append(f"<h2>{e(line[3:].strip())}</h2>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if not in_table:
                out.append("<table><thead><tr>" + "".join(f"<th>{e(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                in_table = True
            else:
                out.append("<tr>" + "".join(f"<td>{e(c)}</td>" for c in cells) + "</tr>")
        elif in_table:
            out.append("</tbody></table>")
            in_table = False
    if in_table:
        out.append("</tbody></table>")
    return "\n".join(out)


def main(src, dst):
    body = render(open(src, encoding="utf-8").read())
    page = ('<?xml version="1.0" encoding="utf-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="pt-BR">'
            '<head><meta charset="utf-8"/><title>Treino</title><link rel="stylesheet" href="style.css"/></head>'
            f"<body>{body}</body></html>")
    opf = ('<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           f'<dc:identifier id="id">urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, "treino")}</dc:identifier>'
           '<dc:title>Treino</dc:title><dc:language>pt-BR</dc:language>'
           '<meta property="dcterms:modified">2000-01-01T00:00:00Z</meta></metadata><manifest>'
           '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
           '<item id="css" href="style.css" media-type="text/css"/>'
           '<item id="c0" href="treino.xhtml" media-type="application/xhtml+xml"/></manifest>'
           '<spine><itemref idref="c0"/></spine></package>')
    nav = ('<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
           '<head><title>Treino</title></head><body><nav epub:type="toc"><ol><li><a href="treino.xhtml">Treino</a></li></ol></nav></body></html>')
    with zipfile.ZipFile(dst, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("content.opf", opf)
        z.writestr("nav.xhtml", nav)
        z.writestr("style.css", CSS)
        z.writestr("treino.xhtml", page)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
