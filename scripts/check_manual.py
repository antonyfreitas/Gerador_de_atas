#!/usr/bin/env python3
"""Verifica o Sumário de atualizações recentes do Manual Geral (página pública).

Grava em data/manual-status.json só: o mês mais recente, a lista de meses, datas e um hash.
Não guarda nenhum texto da página. Faz uma requisição por execução e respeita o robots.txt.
"""
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

URL = "https://www.churchofjesuschrist.org/study/manual/general-handbook/summary-of-recent-updates?lang=por"
ROBOTS = "https://www.churchofjesuschrist.org/robots.txt"
UA = "secretaria-ala-monitor/1.0 (verificacao semanal de uma pagina publica; uso pessoal)"
OUT = Path("data/manual-status.json")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
RX = re.compile(r"\b(" + "|".join(MESES) + r")\s+(?:de\s+)?(20\d\d)\b", re.I)


class Texto(HTMLParser):
    """Extrai o texto visível, ignorando scripts, menus e rodapés."""
    SKIP = {"script", "style", "noscript", "nav", "header", "footer", "svg", "button"}

    def __init__(self):
        super().__init__()
        self.skip = 0
        self.partes = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.partes.append(data.strip())


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def robots_ok():
    try:
        linhas = get(ROBOTS).splitlines()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True
        raise
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(linhas)
    return rp.can_fetch(UA, URL)


def analisar(html):
    p = Texto()
    p.feed(html)
    texto = re.sub(r"\s+", " ", " ".join(p.partes)).strip()
    meses = []
    for m in RX.finditer(texto):
        k = f"{m.group(2)}-{MESES.index(m.group(1).lower()) + 1:02d}"
        if k not in meses:
            meses.append(k)
    return texto, meses


def main():
    antes = {}
    if OUT.exists():
        try:
            antes = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            antes = {}
    if not robots_ok():
        sys.exit("O robots.txt não permite buscar esta página. Nada foi feito.")
    texto, meses = analisar(get(URL))
    if not meses:
        sys.exit("Nenhum mês encontrado (idioma ou layout mudou). Confira o Sumário à mão.")
    hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    topo = meses[0]
    th = hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]
    novo = bool(antes.get("ultimoMes")) and topo != antes["ultimoMes"]
    texto_mudou = bool(antes.get("textoHash")) and th != antes["textoHash"]
    saida = {
        "fonte": URL,
        "verificado": hoje,
        "ultimoMes": topo,
        "meses": meses[:6],
        "textoHash": th,
        "mudouEm": hoje if novo else antes.get("mudouEm"),
        "anterior": antes["ultimoMes"] if novo else antes.get("anterior"),
        "textoMudouEm": hoje if texto_mudou else antes.get("textoMudouEm"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Mês mais recente: {topo}. {'Mês novo detectado.' if novo else 'Sem mudança de mês.'}")


if __name__ == "__main__":
    main()
