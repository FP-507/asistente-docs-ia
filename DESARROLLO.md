# Notas de desarrollo · Asistente de Documentos con IA

Guía para retomar el proyecto: cómo está armado, por qué y cómo cambiarlo.

## Puesta en marcha

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
set ANTHROPIC_API_KEY=...                         # PowerShell: $env:ANTHROPIC_API_KEY = "..."
python -m asistente "¿Cómo creo un entorno virtual?"
python -m asistente --solo-buscar "código 429"     # prueba el buscador sin gastar créditos
pytest -q                                           # no necesita clave ni red
```

## Flujo (RAG sin base vectorial)

```
--docs carpeta ──► cargar_documentos() ──► Fragmento[] ──► Buscador (BM25) ──► top-k
                                                                              │
             Respuesta(texto con [n], fuentes) ◄── interpretar() ◄── API de Claude (documentos con citas)
```

| Archivo | Responsabilidad | Piezas clave |
|---|---|---|
| `asistente/buscador.py` | Leer, fragmentar e indexar, sin red | `normalizar`, `fragmentar` (por párrafos, ~1 200 caracteres), `cargar_documentos`, `Buscador` (BM25 con `k1=1.5`, `b=0.75`) |
| `asistente/claude.py` | Armar la petición e interpretar la respuesta | `MODELO`, `SISTEMA`, `construir_contenido`, `interpretar`, `preguntar(pregunta, fragmentos, client=None)` |
| `asistente/__main__.py` | CLI y modo conversación; traduce los errores de la API a mensajes | `responder`, `main` |

## Decisiones

- **BM25 local en vez de embeddings.** No requiere otro servicio ni dependencias, es explicable y funciona bien con apuntes cortos. Solo los fragmentos elegidos se envían a la API, no todos los archivos.
- **Normalización:** minúsculas, sin tildes (`unicodedata`) y sin palabras vacías en español, para que "cómo" y "como" coincidan.
- **Fragmentos por párrafos:** un fragmento nunca corta un párrafo a la mitad; el título `archivo (parte n)` es lo que se muestra en las fuentes.
- **Citas de la API:** cada fragmento va como un bloque `document` con `citations.enabled`, **antes** de la pregunta. `interpretar()` recorre los bloques de texto, numera cada cita sin repetir (`(título, texto citado)`) e inserta `[n]` en la respuesta.
- **Respuesta acotada:** el prompt de sistema pide responder solo con los documentos y decirlo si no está la respuesta.
- **Rechazos:** si `stop_reason == "refusal"`, se devuelve un mensaje claro (`Respuesta.rechazada`). La petición también pide reintento con otro modelo del lado del servidor (parámetros `betas` y `fallbacks` en `preguntar`).
- **Cliente inyectable:** `preguntar(..., client=...)` permite que los tests usen un cliente falso.

## Tests

`tests/test_asistente.py` (9 tests): normalización, tamaño de fragmentos, que BM25 encuentre el documento correcto y devuelva vacío si no hay coincidencias, que los documentos vayan antes de la pregunta, numeración de citas sin repetir, manejo de rechazo, que sin fragmentos no se llame a la API, y la forma exacta de la petición con un cliente falso. La CI los corre sin clave.

## Cómo extenderlo

- **Otros formatos (PDF, Word):** agregar la extensión a `EXTENSIONES` y convertir a texto en `cargar_documentos` (por ejemplo con `pypdf`) antes de `fragmentar`.
- **Cambiar de modelo o esfuerzo:** constante `MODELO` y `output_config` en `claude.py`. Revisar la documentación vigente de la API antes de cambiar parámetros beta.
- **Búsqueda semántica:** reemplazar o combinar `Buscador.buscar` con embeddings; el resto del flujo no cambia porque solo recibe `Fragmento[]`.
- **Interfaz web:** `preguntar()` ya devuelve un objeto con texto y fuentes; se puede exponer con FastAPI.

## Pendientes

- El índice se reconstruye en cada ejecución; con muchos documentos convendría guardarlo en disco.
- No hay memoria de conversación: cada pregunta del modo interactivo es independiente.
- Las stopwords son una lista corta escrita a mano.
