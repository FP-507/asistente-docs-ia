"""Búsqueda local de fragmentos relevantes (sin embeddings ni servicios externos).

Divide los documentos en fragmentos por párrafos y los ordena con BM25,
el mismo algoritmo clásico que usan muchos buscadores de texto.
"""

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

EXTENSIONES = {".md", ".txt"}
STOPWORDS = set(
    """a al algo como con cual cuales cuando de del el ella en entre es esa ese esta este
    esto fue ha hay la las le les lo los mas me mi mis muy no o para pero por que qué se
    ser si sin sobre su sus te tu un una uno unos y ya yo son cómo""".split()
)


@dataclass
class Fragmento:
    archivo: str
    numero: int
    texto: str

    @property
    def titulo(self) -> str:
        return f"{self.archivo} (parte {self.numero})"


def normalizar(texto: str) -> list[str]:
    """Minúsculas, sin tildes, sin palabras vacías."""
    sin_tildes = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return [p for p in re.findall(r"[a-z0-9]+", sin_tildes) if p not in STOPWORDS and len(p) > 1]


def fragmentar(texto: str, archivo: str, max_chars: int = 1200) -> list[Fragmento]:
    parrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    fragmentos, actual = [], ""
    for parrafo in parrafos:
        if actual and len(actual) + len(parrafo) > max_chars:
            fragmentos.append(actual)
            actual = ""
        actual = f"{actual}\n\n{parrafo}" if actual else parrafo
    if actual:
        fragmentos.append(actual)
    return [Fragmento(archivo, i + 1, t) for i, t in enumerate(fragmentos)]


def cargar_documentos(carpeta: Path) -> list[Fragmento]:
    fragmentos: list[Fragmento] = []
    for ruta in sorted(carpeta.rglob("*")):
        if ruta.suffix.lower() in EXTENSIONES and ruta.is_file():
            nombre = ruta.relative_to(carpeta).as_posix()
            fragmentos += fragmentar(ruta.read_text(encoding="utf-8"), nombre)
    return fragmentos


class Buscador:
    def __init__(self, fragmentos: list[Fragmento], k1: float = 1.5, b: float = 0.75):
        self.fragmentos = fragmentos
        self.k1, self.b = k1, b
        self.terminos = [Counter(normalizar(f.texto)) for f in fragmentos]
        self.largos = [sum(t.values()) for t in self.terminos]
        self.largo_medio = sum(self.largos) / len(self.largos) if self.largos else 0
        frecuencia_doc = Counter(t for terminos in self.terminos for t in terminos)
        n = len(fragmentos)
        self.idf = {t: math.log(1 + (n - df + 0.5) / (df + 0.5)) for t, df in frecuencia_doc.items()}

    def puntuar(self, consulta: list[str], i: int) -> float:
        terminos, largo = self.terminos[i], self.largos[i]
        puntaje = 0.0
        for t in consulta:
            if t not in terminos:
                continue
            tf = terminos[t]
            norm = self.k1 * (1 - self.b + self.b * largo / self.largo_medio)
            puntaje += self.idf[t] * tf * (self.k1 + 1) / (tf + norm)
        return puntaje

    def buscar(self, pregunta: str, k: int = 5) -> list[Fragmento]:
        consulta = normalizar(pregunta)
        puntajes = [(self.puntuar(consulta, i), i) for i in range(len(self.fragmentos))]
        mejores = sorted((p for p in puntajes if p[0] > 0), reverse=True)[:k]
        return [self.fragmentos[i] for _, i in mejores]
