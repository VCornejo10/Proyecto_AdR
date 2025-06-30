# Prueba de la api "user-service"

## Health

curl http://localhost/api/users/health

## Ingresar un usario

curl -X POST http://localhost/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"name":"*nombre*","email":"*email*"}'

- Valida que el Json venga con name y email
- Valida formato del correo (Al menos un caracter no espacio antes y después de '@' y un punto)
- Si el email ya existe (restricción UNIQUE) devuelve error

## Obtener usuarios

curl http://localhost/api/users/

## Obtener usuario por ID

curl http://localhost/api/users/*id usuario*

- Si el usario no existe retorna "Usuario no existe"