# Conector Freshdesk para Ruvic

Conector Ruvic para gestión de tickets en Freshdesk: crear ticket, actualizar ticket, agregar nota y consultar por ID.

## Capacidades

1. `create_ticket(...)`.
2. `update_ticket(ticket_id, fields)`.
3. `add_note(ticket_id, body, private=True)`.
4. `get_ticket(ticket_id)`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./lib
```

Desde Git:

```bash
pip install git+https://github.com/tu-org/conector-freshdesk.git#subdirectory=lib
```

## Variables de entorno

| Variable | Obligatoria | Descripción | Default |
|---|---:|---|---|
| `RUVIC_FRESHDESK_DOMAIN` | Sí | Subdominio o dominio Freshdesk | — |
| `RUVIC_FRESHDESK_API_KEY` | Sí | API Key del agente | — |
| `RUVIC_FRESHDESK_VERIFY_SSL` | No | Verificar SSL | `true` |
| `RUVIC_FRESHDESK_TIMEOUT` | No | Timeout | `20` |
| `RUVIC_FRESHDESK_MAX_RESULTS` | No | Máximo resultados | `100` |

## Obtener API Key

1. Entra a Freshdesk.
2. Abre tu perfil de usuario.
3. Busca API Key.
4. Copia la key y guárdala como secreto.

Freshdesk usa Basic Auth: API Key como usuario y `X` como contraseña.

## Pruebas

```bash
python test_connection.py
python validate_local.py
```

`validate_local.py` crea un ticket real de prueba, lo consulta, lo actualiza y agrega una nota.

## Seguridad

- Nunca subas la API Key al repositorio.
- Usa un portal Freshdesk de prueba/trial para validación.
- No se implementa eliminación de tickets.
