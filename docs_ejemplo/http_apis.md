# APIs REST y códigos HTTP

Una API REST expone recursos a través de URLs, y se usan los métodos HTTP para indicar la acción: `GET` para leer, `POST` para crear, `PUT` o `PATCH` para actualizar y `DELETE` para borrar.

## Códigos de estado más comunes

- **200 OK:** la petición salió bien.
- **201 Created:** se creó un recurso nuevo, normalmente después de un `POST`.
- **204 No Content:** salió bien pero no hay nada que devolver, típico al borrar.
- **400 Bad Request:** la petición está mal formada.
- **401 Unauthorized:** falta autenticarse o las credenciales no son válidas.
- **403 Forbidden:** estás autenticado pero no tienes permiso.
- **404 Not Found:** el recurso no existe.
- **422 Unprocessable Entity:** los datos tienen el formato correcto pero no pasan la validación.
- **429 Too Many Requests:** se superó el límite de peticiones; hay que esperar antes de reintentar.
- **500 Internal Server Error:** falló algo en el servidor.

## PUT frente a PATCH

`PUT` reemplaza el recurso completo, así que hay que enviar todos los campos. `PATCH` cambia solo los campos que se envían.
