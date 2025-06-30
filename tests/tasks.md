# Prueba de la api "task-service"

## Health

curl http://localhost/api/task/health

## Crear tarea

curl -X POST http://localhost/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"*nombre tarea¨*","user_id":*id usuario*}'

- Valida que el título y user_id estén presentes
- Valida que el status sea uno de los permitidos si se especifica. Por defecto el status es 'pendiente' (pendiente, en progreso, completada)
- Valida que el usuario exista antes de crear la tarea

## Listar tareas

curl http://localhost/api/tasks/

### Filtrar por usuario
curl http://localhost/api/tasks/?user_id=*id usuario*

## Obtener Tarea por ID

curl http://localhost/api/tasks/*id tarea*

- Si no existe el id, devuelve error 404

## Actualizar estado de tarea

curl -X PUT http://localhost/api/tasks/*id tarea* \
  -H "Content-Type: application/json" \
  -d '{"status": "*estado*"}'

- Estado = (pendiente, en progreso, completada)