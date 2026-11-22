"""Uso:
    python -m asistente "¿Cómo creo un entorno virtual?"
    python -m asistente --docs mis_apuntes/        # modo conversación
    python -m asistente --solo-buscar "códigos 404"  # sin llamar a la API
"""

import argparse
import sys
from pathlib import Path

import anthropic

from .buscador import Buscador, cargar_documentos
from .claude import preguntar

CARPETA_EJEMPLO = Path(__file__).parent.parent / "docs_ejemplo"


def responder(buscador: Buscador, pregunta: str, k: int, solo_buscar: bool) -> None:
    fragmentos = buscador.buscar(pregunta, k)
    if solo_buscar:
        for f in fragmentos:
            print(f"\n── {f.titulo}\n{f.texto[:300]}…")
        return

    try:
        r = preguntar(pregunta, fragmentos)
    except anthropic.AuthenticationError:
        sys.exit("Credenciales inválidas. Configura ANTHROPIC_API_KEY (ver README).")
    except anthropic.RateLimitError:
        print("Demasiadas solicitudes; espera un momento e inténtalo de nuevo.")
        return
    except anthropic.APIConnectionError:
        print("No hay conexión con la API de Claude.")
        return
    except anthropic.APIStatusError as error:
        print(f"Error de la API ({error.status_code}): {error.message}")
        return

    print(f"\n{r.texto}")
    if r.fuentes:
        print("\nFuentes:")
        for i, (titulo, cita) in enumerate(r.fuentes, 1):
            resumen = cita if len(cita) < 110 else cita[:107] + "…"
            print(f"  [{i}] {titulo}: “{resumen}”")


def main(argv: list[str] | None = None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="asistente", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pregunta", nargs="?", help="Si se omite, abre el modo conversación")
    parser.add_argument("--docs", type=Path, default=CARPETA_EJEMPLO, help="Carpeta con .md o .txt")
    parser.add_argument("-k", type=int, default=5, help="Fragmentos a enviar (por defecto 5)")
    parser.add_argument("--solo-buscar", action="store_true", help="Muestra los fragmentos sin usar la API")
    args = parser.parse_args(argv)

    fragmentos = cargar_documentos(args.docs)
    if not fragmentos:
        sys.exit(f"No hay archivos .md o .txt en {args.docs}")
    buscador = Buscador(fragmentos)
    print(f"{len(fragmentos)} fragmentos cargados desde {args.docs}")

    if args.pregunta:
        responder(buscador, args.pregunta, args.k, args.solo_buscar)
        return

    print("Escribe tu pregunta (o 'salir').")
    while True:
        try:
            pregunta = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pregunta.lower() in {"salir", "exit", "q"}:
            break
        if pregunta:
            responder(buscador, pregunta, args.k, args.solo_buscar)


if __name__ == "__main__":
    main()
