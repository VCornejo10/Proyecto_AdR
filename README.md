# Proyecto Microservicios con Flask, Docker y Nginx Proxy Manager

Este proyecto contiene dos microservicios construidos con Flask:  
- **user-service:** Servicio de usuarios con API REST  
- **task-service:** Servicio de tareas que depende del servicio de usuarios  

Ambos servicios se ejecutan en contenedores Docker y están expuestos a través de un proxy reverso Nginx Proxy Manager.

## Requisitos

- Docker
- Docker Compose

## Iniciar el proyecto

1. Clona este repositorio y navega a la carpeta raíz del proyecto.

2. Construye y levanta los contenedores Docker con "docker compose up --build -d"

3. Espera unos segundos para que los servicios se inicien correctamente.

## URLs de los servicios (configuradas con Nginx Proxy Manager)

- Usuarios: http://users.localhost/api/users/
- Tareas: http://tasks.localhost/api/tasks/

## Pruebas básicas con curl

### Servicio de usuarios

- Verificar salud: curl http://users.localhost/health
- Crear un usuario: curl -X POST http://users.localhost/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Victor", "email": "victor@example.com"}'
- Listar usuarios: curl http://users.localhost/api/users/

### Servicio de tareas
- Verificar salud: curl http://tasks.localhost/health
- Crear una tarea (requiere que el usuario con user_id exista): curl -X POST http://tasks.localhost/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Hacer informe", "user_id": 1}'
- curl http://tasks.localhost/api/tasks/

## Parar y eliminar contenedores
docker compose down

## Notas
- Asegúrate de que las entradas DNS o el archivo hosts de tu sistema resuelvan users.localhost y tasks.localhost a 127.0.0.1.
- Si usas Windows, modifica C:\Windows\System32\drivers\etc\hosts con permisos de administrador.
- Si usas Linux/macOS, modifica /etc/hosts con permisos de administrador.

## Problemas comunes
- Error 404 o 301: Revisa que Nginx Proxy Manager tenga configurados correctamente los proxies con la barra / al final en las rutas.
- No se encuentra contenedor: Usa docker ps para verificar que los servicios estén corriendo.
- Variables de entorno: Revisa que estén definidas correctamente en docker-compose.yml.


