---
name: freshdesk
description: "Usa la librería ruvic_freshdesk_connector para gestionar tickets de soporte en Freshdesk: crear tickets, actualizar tickets, agregar notas y consultar tickets por ID. Úsala cuando el usuario pida operar tickets Freshdesk o helpdesk."
triggers:
- freshdesk
- ticket freshdesk
- helpdesk
- soporte
- crear ticket
- actualizar ticket
---

# Conector Freshdesk (ruvic_freshdesk_connector)

## Regla crítica de credenciales

El código generado NUNCA hardcodea credenciales. Siempre se leen de variables de entorno:

| Variable | Contenido |
|---|---|
| `RUVIC_FRESHDESK_DOMAIN` | Dominio/subdominio Freshdesk |
| `RUVIC_FRESHDESK_API_KEY` | API Key Freshdesk |
| `RUVIC_FRESHDESK_VERIFY_SSL` | Verificación SSL opcional |
| `RUVIC_FRESHDESK_TIMEOUT` | Timeout opcional |
| `RUVIC_FRESHDESK_MAX_RESULTS` | Máximo de resultados |

Si estas variables NO existen, el conector no está configurado: no generes código que lo use; indica al usuario que lo configure en Settings → Conectores. Nunca uses variables con alias `_DEFAULT_`, `_TEST_` o `_PRODUCCION_`.

## Conexión

```python
from ruvic_freshdesk_connector import FreshdeskClient
client = FreshdeskClient()
```

## Capacidad 1 — Crear ticket

```python
ticket = client.create_ticket(
    subject="Error de acceso",
    description="El usuario no puede iniciar sesión.",
    email="cliente@example.com",
    priority=2,
    status=2,
)
print(ticket["id"])
```

## Capacidad 2 — Actualizar ticket

```python
updated = client.update_ticket(ticket_id=123, fields={"priority": 3, "status": 2})
print(updated)
```

## Capacidad 3 — Agregar nota

```python
note = client.add_note(ticket_id=123, body="Se contactó al usuario y se escaló a N2.", private=True)
print(note)
```

## Capacidad 4 — Consultar ticket por ID

```python
ticket = client.get_ticket(123)
print(ticket)
```

## Manejo de errores

```python
from ruvic_freshdesk_connector import FreshdeskAuthError, FreshdeskConfigError, FreshdeskDataError, FreshdeskNetworkError
try:
    ticket = client.get_ticket(123)
except FreshdeskConfigError as exc:
    print(f"Configuración inválida: {exc}")
except FreshdeskAuthError:
    print("API Key, dominio o permisos Freshdesk inválidos")
except FreshdeskNetworkError:
    print("No se pudo alcanzar Freshdesk")
except FreshdeskDataError as exc:
    print(f"Freshdesk rechazó la solicitud: {exc}")
```

## Buenas prácticas al generar código

1. Lee credenciales SOLO de `RUVIC_FRESHDESK_*`.
2. Nunca imprimas API Keys.
3. Confirma con el usuario antes de crear o actualizar tickets reales.
4. Usa IDs numéricos de ticket devueltos por Freshdesk para actualizar, comentar o consultar.
5. No implementes eliminación de tickets; no está soportada en este conector.
