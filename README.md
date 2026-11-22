# Asistente de Documentos con IA

Haz preguntas sobre tus propios apuntes o documentos (`.md` o `.txt`) y recibe respuestas con **citas exactas** de dónde sale cada dato. Usa la API de Claude (Anthropic) y un buscador local con el algoritmo BM25.

![tests](https://github.com/FP-507/asistente-docs-ia/actions/workflows/tests.yml/badge.svg)

Ejemplo del formato de salida (el texto exacto de la respuesta varía):

```
$ python -m asistente "¿Cuál es la diferencia entre PUT y PATCH?"

PUT reemplaza el recurso completo y hay que enviar todos los campos [1],
mientras que PATCH solo cambia los campos que se envían [2].

Fuentes:
  [1] http_apis.md (parte 1): “PUT reemplaza el recurso completo, así que hay que enviar todos los campos.”
  [2] http_apis.md (parte 1): “PATCH cambia solo los campos que se envían.”
```

## Cómo funciona

```
tus documentos ──► fragmentos ──► BM25 elige los 5 más relevantes ──► Claude responde con citas
```

1. **Fragmenta** cada documento por párrafos (unos 1200 caracteres por fragmento).
2. **Busca** localmente los fragmentos más relacionados con la pregunta con BM25, sin enviar todos tus archivos a la API.
3. **Pregunta** a Claude enviando solo esos fragmentos como documentos con citas activadas, con la instrucción de no inventar si la respuesta no está.
4. **Muestra** la respuesta con marcas `[n]` y el texto exacto citado de cada fuente.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Necesitas una clave de la API de Anthropic (se crea en <https://platform.claude.com>):

```bash
set ANTHROPIC_API_KEY=tu-clave      # Windows (cmd)
export ANTHROPIC_API_KEY=tu-clave   # Linux/macOS
```

## Uso

```bash
python -m asistente "¿Cómo creo un entorno virtual?"   # usa docs_ejemplo/
python -m asistente --docs mis_apuntes/                # modo conversación
python -m asistente --solo-buscar "código 429"         # solo el buscador, sin API
```

## Detalles técnicos

- Modelo `claude-opus-5-5` con esfuerzo `low`, suficiente para responder preguntas cortas.
- Si el modelo rechaza una pregunta, la API la reintenta con otro modelo (parámetro `fallbacks`).
- Manejo de errores de autenticación, límite de peticiones y conexión.
- Los tests usan un cliente falso: no gastan créditos ni necesitan clave.

## Tests

```bash
pip install pytest
pytest -v
```

## Qué aprendí

- La idea de RAG (*retrieval-augmented generation*): buscar primero y darle al modelo solo el contexto relevante.
- Cómo funciona BM25: frecuencia del término, rareza (IDF) y normalización por largo.
- Usar citas para que las respuestas de una IA se puedan verificar.
- Probar código que depende de una API externa usando objetos falsos.

## Estructura

```
asistente/
  buscador.py   # fragmentación y BM25
  claude.py     # petición a la API e interpretación de citas
  __main__.py   # línea de comandos
docs_ejemplo/   # documentos de prueba
tests/
```

## Para retomar el proyecto

Arquitectura, decisiones técnicas, cómo extenderlo y pendientes: [DESARROLLO.md](DESARROLLO.md).
