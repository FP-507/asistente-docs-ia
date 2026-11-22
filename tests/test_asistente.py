from pathlib import Path
from types import SimpleNamespace as NS

from asistente.buscador import Buscador, cargar_documentos, fragmentar, normalizar
from asistente.claude import MODELO, construir_contenido, interpretar, preguntar

DOCS = Path(__file__).parent.parent / "docs_ejemplo"


def test_normalizar_quita_tildes_y_stopwords():
    assert normalizar("¿Cómo creo un Entorno virtual?") == ["creo", "entorno", "virtual"]


def test_fragmentar_respeta_el_tamano():
    texto = "\n\n".join(f"Párrafo {i} " + "x" * 300 for i in range(10))
    partes = fragmentar(texto, "a.md", max_chars=1000)
    assert len(partes) > 1
    assert all(len(p.texto) <= 1000 for p in partes)
    assert partes[0].titulo == "a.md (parte 1)"


def test_buscador_encuentra_el_documento_correcto():
    buscador = Buscador(cargar_documentos(DOCS))
    assert buscador.buscar("¿Cómo activo el entorno virtual en Windows?")[0].archivo == "entornos_virtuales.md"
    assert buscador.buscar("qué significa el código 404")[0].archivo == "http_apis.md"
    assert buscador.buscar("deshacer un commit en una rama compartida")[0].archivo == "git_basico.md"


def test_buscador_sin_resultados():
    assert Buscador(cargar_documentos(DOCS)).buscar("receta de lasaña") == []


def test_contenido_pone_documentos_antes_de_la_pregunta():
    frag = fragmentar("Hola mundo", "x.md")
    contenido = construir_contenido("¿Qué dice?", frag)
    assert contenido[0]["type"] == "document"
    assert contenido[0]["citations"] == {"enabled": True}
    assert contenido[-1] == {"type": "text", "text": "¿Qué dice?"}


def cita(titulo, texto):
    return NS(document_title=titulo, cited_text=texto)


def test_interpretar_numera_citas_sin_repetir():
    mensaje = NS(
        stop_reason="end_turn",
        content=[
            NS(type="thinking", thinking=""),
            NS(type="text", text="Se activa con activate", citations=[cita("a.md (parte 1)", "activate")]),
            NS(type="text", text=". Y se sale con deactivate", citations=[cita("a.md (parte 1)", "activate")]),
            NS(type="text", text=".", citations=None),
        ],
    )
    r = interpretar(mensaje)
    assert r.texto == "Se activa con activate [1]. Y se sale con deactivate [1]."
    assert r.fuentes == [("a.md (parte 1)", "activate")]


def test_interpretar_rechazo():
    r = interpretar(NS(stop_reason="refusal", content=[]))
    assert r.rechazada


def test_preguntar_sin_fragmentos_no_llama_a_la_api():
    assert "No encontré" in preguntar("x", [], client=None).texto


def test_preguntar_envia_la_peticion_correcta():
    enviado = {}

    class Falso:
        def create(self, **kwargs):
            enviado.update(kwargs)
            return NS(stop_reason="end_turn", content=[NS(type="text", text="ok", citations=[])])

    cliente = NS(beta=NS(messages=Falso()))
    r = preguntar("¿Qué es Git?", fragmentar("Git guarda versiones.", "git.md"), client=cliente)
    assert r.texto == "ok"
    assert enviado["model"] == MODELO
    assert enviado["fallbacks"] == "default"
    assert enviado["messages"][0]["content"][-1]["text"] == "¿Qué es Git?"
