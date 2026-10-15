#!/usr/bin/env python3
"""Converte a planilha de treino em Markdown. Uso: xlsx_to_md.py entrada.xlsx saida.md"""
import datetime
import sys

import openpyxl


def fmt(v):
    if isinstance(v, datetime.datetime):  # Excel converte "5/5" em data
        return f"{v.day}/{v.month}"
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v).strip().replace("|", "\\|")


def main(src, out):
    wb = openpyxl.load_workbook(src, data_only=True)
    lines = ["# Treino - Dom Core", ""]
    for ws in wb:
        rows = [[fmt(c) for c in r if c is not None] for r in ws.iter_rows(values_only=True)]
        rows = [r for r in rows if r]
        if not rows:
            continue
        lines += [f"## {ws.title}", "", "| Exercício | Séries | Cargas |", "|---|---|---|"]
        for r in rows:
            series = r[1] if len(r) > 1 else ""
            cargas = " · ".join(r[2:])
            lines.append(f"| {r[0]} | {series} | {cargas} |")
        lines.append("")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
