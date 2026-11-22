# Entornos virtuales en Python

Un entorno virtual es una carpeta con su propia instalación de Python y sus propias librerías. Sirve para que cada proyecto tenga las versiones que necesita sin afectar a los demás proyectos ni al Python del sistema.

## Crear y activar un entorno

Para crear un entorno se usa el módulo `venv`, que viene incluido con Python: `python -m venv .venv`. Esto crea la carpeta `.venv` dentro del proyecto.

En Windows se activa con `.venv\Scripts\activate`. En Linux y macOS se activa con `source .venv/bin/activate`. Cuando está activo, el nombre del entorno aparece al inicio de la línea de la terminal. Para salir se escribe `deactivate`.

## Guardar las dependencias

El comando `pip freeze > requirements.txt` guarda la lista de librerías instaladas con sus versiones. Otra persona puede instalar exactamente lo mismo con `pip install -r requirements.txt`.

La carpeta `.venv` no se sube a Git: se agrega al archivo `.gitignore`, porque ocupa mucho espacio y se puede recrear con el archivo de requisitos.
