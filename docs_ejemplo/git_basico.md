# Git básico

Git es un sistema de control de versiones: guarda el historial de cambios de un proyecto para poder volver atrás, comparar versiones y trabajar en equipo.

## Flujo diario

1. `git status` muestra qué archivos cambiaron.
2. `git add archivo.py` prepara un archivo para el próximo commit. `git add .` prepara todos.
3. `git commit -m "mensaje"` guarda una versión con un mensaje que explica el cambio.
4. `git push` sube los commits al repositorio remoto, por ejemplo GitHub.

Un buen mensaje de commit describe el porqué del cambio en una línea corta, por ejemplo "Corrige el cálculo del total con descuento".

## Ramas

Una rama es una línea de trabajo independiente. Se crea con `git switch -c nombre-rama`. Cuando el trabajo está listo, se une a la rama principal con `git merge nombre-rama` o abriendo un pull request en GitHub para que otra persona lo revise.

## Deshacer cambios

`git restore archivo.py` descarta los cambios no guardados de un archivo. `git revert <commit>` crea un nuevo commit que deshace uno anterior sin borrar el historial, por eso es la opción segura en ramas compartidas.
