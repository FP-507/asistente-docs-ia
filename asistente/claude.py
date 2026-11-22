"""Pregunta a Claude usando solo los fragmentos encontrados, con citas a la fuente."""

from dataclasses import dataclass, field

import anthropic

from .buscador import Fragmento

MODELO = "claude-opus-5-5"

SISTEMA = """Eres un asistente que responde preguntas usando únicamente los documentos
que te entrega el usuario. Responde en español, de forma breve y clara.
Si los documentos no contienen la respuesta, dilo directamente en lugar de inventarla."""


@dataclass
class Respuesta:
    texto: str
    fuentes: list[tuple[str, str]] = field(default_factory=list)  # (título, texto citado)
    rechazada: bool = False


def construir_contenido(pregunta: str, fragmentos: list[Fragmento]) -> list[dict]:
    """Cada fragmento va como un documento con citas activadas, antes de la pregunta."""
    documentos = [
        {
            "type": "document",
            "source": {"type": "text", "media_type": "text/plain", "data": f.texto},
            "title": f.titulo,
            "citations": {"enabled": True},
        }
        for f in fragmentos
    ]
    return [*documentos, {"type": "text", "text": pregunta}]


def interpretar(mensaje) -> Respuesta:
    """Convierte la respuesta de la API en texto con marcas [n] y una lista de fuentes."""
    if mensaje.stop_reason == "refusal":
        return Respuesta("Claude no pudo responder esta pregunta.", rechazada=True)

    partes: list[str] = []
    fuentes: list[tuple[str, str]] = []
    indice: dict[tuple[str, str], int] = {}

    for bloque in mensaje.content:
        if bloque.type != "text":
            continue
        partes.append(bloque.text)
        for cita in getattr(bloque, "citations", None) or []:
            clave = (cita.document_title, cita.cited_text.strip())
            if clave not in indice:
                fuentes.append(clave)
                indice[clave] = len(fuentes)
            partes.append(f" [{indice[clave]}]")

    return Respuesta("".join(partes).strip(), fuentes)


def preguntar(
    pregunta: str, fragmentos: list[Fragmento], client: anthropic.Anthropic | None = None
) -> Respuesta:
    if not fragmentos:
        return Respuesta("No encontré nada relacionado en tus documentos.")

    client = client or anthropic.Anthropic()
    mensaje = client.beta.messages.create(
        model=MODELO,
        max_tokens=16000,
        system=SISTEMA,
        output_config={"effort": "low"},
        # Si el modelo rechaza la pregunta, la API la reintenta con otro modelo.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": construir_contenido(pregunta, fragmentos)}],
    )
    return interpretar(mensaje)
