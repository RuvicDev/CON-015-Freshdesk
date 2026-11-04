"""Cliente para Freshdesk API v2.

Capacidades:
- create_ticket(): crear ticket.
- update_ticket(): actualizar ticket.
- add_note(): agregar nota a un ticket.
- get_ticket(): consultar ticket por ID.

Freshdesk usa HTTP Basic Auth: API key como usuario y `X` como contraseña.
"""
from __future__ import annotations
from typing import Any
import requests
from requests import Response
from .config import FreshdeskConfig
from .exceptions import FreshdeskAuthError, FreshdeskDataError, FreshdeskNetworkError
from .logging_utils import get_logger

# Nombres aceptados para los códigos estándar de Freshdesk. Los números se envían tal cual
# (Freshdesk admite estados personalizados por encima de 5).
_STATUS_ALIASES = {
    "abierto": 2, "open": 2,
    "pendiente": 3, "pending": 3,
    "resuelto": 4, "resolved": 4,
    "cerrado": 5, "closed": 5,
}
_PRIORITY_ALIASES = {
    "baja": 1, "low": 1,
    "media": 2, "medium": 2,
    "alta": 3, "high": 3,
    "urgente": 4, "urgent": 4,
}

_VALID_TEXT = {
    "status": "2 (Abierto), 3 (Pendiente), 4 (Resuelto), 5 (Cerrado)",
    "priority": "1 (Baja), 2 (Media), 3 (Alta), 4 (Urgente)",
}

def _parse_id(value: Any, name: str = "ticket_id") -> int:
    """Convierte un ID a entero positivo con un error claro si no lo es."""
    try:
        number = int(str(value).strip().lstrip("#"))
    except (TypeError, ValueError):
        raise FreshdeskDataError(f"{name} debe ser un número entero positivo; se recibió '{value}'.") from None
    if number <= 0:
        raise FreshdeskDataError(f"{name} debe ser mayor que cero; se recibió '{value}'.")
    return number


def _parse_code(field: str, value: Any, aliases: dict[str, int]) -> int:
    text = str(value).strip()
    if text.lower() in aliases:
        return aliases[text.lower()]
    try:
        return int(text)
    except ValueError:
        valid = _VALID_TEXT[field]
        raise FreshdeskDataError(f"{field} '{value}' no válido. Valores aceptados: {valid}.") from None


def _normalize_fields(fields: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(fields)
    if "status" in normalized:
        normalized["status"] = _parse_code("status", normalized["status"], _STATUS_ALIASES)
    if "priority" in normalized:
        normalized["priority"] = _parse_code("priority", normalized["priority"], _PRIORITY_ALIASES)
    return normalized


def _readable_error(response: Response) -> str:
    """Convierte el JSON de validación de Freshdesk en un texto legible."""
    try:
        payload = response.json()
    except ValueError:
        return response.text[:500]
    if isinstance(payload, dict) and isinstance(payload.get("errors"), list):
        parts = []
        for err in payload["errors"]:
            if isinstance(err, dict):
                field = err.get("field") or "general"
                parts.append(f"{field}: {err.get('message') or err.get('code')}")
        if parts:
            return f"{payload.get('description') or 'Error de validación'} — " + "; ".join(parts)
    return str(payload)[:500]


class FreshdeskClient:
    """Cliente para gestión de tickets en Freshdesk.

    Args:
        config: configuración opcional. Si se omite, lee RUVIC_FRESHDESK_*.

    Ejemplo:
        >>> client = FreshdeskClient()
        >>> client.get_ticket(123)
        {'id': 123, 'subject': 'Error de acceso'}
    """
    def __init__(self, config: FreshdeskConfig | None = None) -> None:
        self.config = config or FreshdeskConfig.from_env()
        self._logger = get_logger()
        self._session = requests.Session()
        self._session.auth = (self.config.api_key, "X")
        self._session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _url(self, path: str) -> str:
        clean = path if path.startswith("/") else f"/{path}"
        return self.config.base_url + clean

    def _handle_response(self, response: Response) -> Any:
        if response.status_code in {401, 403}:
            raise FreshdeskAuthError(f"Freshdesk rechazó autenticación o permisos ({response.status_code}). Revisa dominio, API key y permisos del agente.")
        if response.status_code == 404:
            raise FreshdeskDataError("No se encontró el recurso en Freshdesk (404). Verifica que el ticket_id exista.")
        if response.status_code == 429:
            raise FreshdeskDataError("Freshdesk aplicó rate limiting (429). Espera y reintenta más tarde.")
        if response.status_code >= 400:
            raise FreshdeskDataError(f"Freshdesk rechazó la solicitud (HTTP {response.status_code}): {_readable_error(response)}")
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise FreshdeskDataError("Freshdesk respondió contenido no JSON cuando se esperaba JSON.") from exc

    def _request(self, method: str, path: str, json_body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self._session.request(method=method.upper(), url=self._url(path), json=json_body, params={k: v for k, v in (params or {}).items() if v is not None}, timeout=self.config.timeout, verify=self.config.verify_ssl)
        except requests.exceptions.SSLError as exc:
            raise FreshdeskNetworkError("Error SSL conectando con Freshdesk. Verifica certificado o RUVIC_FRESHDESK_VERIFY_SSL.") from exc
        except requests.exceptions.Timeout as exc:
            raise FreshdeskNetworkError(f"Timeout conectando con Freshdesk ({self.config.timeout}s).") from exc
        except requests.exceptions.RequestException as exc:
            raise FreshdeskNetworkError(f"No se pudo conectar con Freshdesk: {exc}.") from exc
        return self._handle_response(response)

    def ping(self) -> bool:
        """Verifica conexión consultando un ticket como máximo.

        Returns:
            True si Freshdesk responde correctamente.
        Ejemplo:
            >>> client.ping()
            True
        """
        self._request("GET", "/tickets", params={"per_page": 1})
        self._logger.info("Ping exitoso a Freshdesk")
        return True

    def create_ticket(self, subject: str, description: str, email: str, priority: int = 1, status: int = 2, custom_fields: dict[str, Any] | None = None, **extra_fields: Any) -> dict[str, Any]:
        """Crea un ticket en Freshdesk.

        Args:
            subject: asunto del ticket.
            description: descripción HTML/texto del ticket.
            email: correo del solicitante.
            priority: prioridad Freshdesk (1 baja, 2 media, 3 alta, 4 urgente).
            status: estado Freshdesk (2 abierto por defecto).
            custom_fields: campos personalizados `cf_*` opcionales.
            extra_fields: otros campos soportados por Freshdesk.
        Returns:
            Ticket creado como dict.
        Ejemplo:
            >>> client.create_ticket('Error login', 'No puedo entrar', 'cliente@example.com')
            {'id': 123, 'subject': 'Error login'}
        """
        if not subject.strip(): raise FreshdeskDataError("subject no puede estar vacío.")
        if not description.strip(): raise FreshdeskDataError("description no puede estar vacío.")
        if "@" not in email: raise FreshdeskDataError("email debe ser un correo válido.")
        payload = {"subject": subject, "description": description, "email": email, "priority": priority, "status": status, **extra_fields}
        payload = _normalize_fields(payload)
        if custom_fields:
            payload["custom_fields"] = custom_fields
        data = self._request("POST", "/tickets", json_body=payload)
        self._logger.info("Ticket Freshdesk creado")
        return dict(data)

    def update_ticket(self, ticket_id: int, fields: dict[str, Any]) -> dict[str, Any]:
        """Actualiza un ticket existente.

        Args:
            ticket_id: ID numérico del ticket.
            fields: campos a actualizar, por ejemplo `status`, `priority`, `custom_fields`.
        Returns:
            Ticket actualizado.
        Ejemplo:
            >>> client.update_ticket(123, {'priority': 3, 'status': 2})
            {'id': 123, 'priority': 3}
        """
        ticket_id = _parse_id(ticket_id)
        if not fields: raise FreshdeskDataError("fields no puede estar vacío.")
        fields = _normalize_fields(fields)
        data = self._request("PUT", f"/tickets/{ticket_id}", json_body=fields)
        self._logger.info("Ticket Freshdesk actualizado")
        return dict(data)

    def add_note(self, ticket_id: int, body: str, private: bool = True) -> dict[str, Any]:
        """Agrega una nota a un ticket Freshdesk.

        Args:
            ticket_id: ID numérico del ticket.
            body: contenido de la nota.
            private: True para nota privada, False para nota pública.
        Returns:
            Nota creada.
        Ejemplo:
            >>> client.add_note(123, 'Se escaló al equipo N2')
            {'id': 456, 'body': 'Se escaló al equipo N2'}
        """
        ticket_id = _parse_id(ticket_id)
        if not body.strip(): raise FreshdeskDataError("body no puede estar vacío.")
        data = self._request("POST", f"/tickets/{ticket_id}/notes", json_body={"body": body, "private": bool(private)})
        self._logger.info("Nota agregada a ticket Freshdesk")
        return dict(data)

    def get_ticket(self, ticket_id: int, include: str | None = None) -> dict[str, Any]:
        """Consulta un ticket por ID.

        Args:
            ticket_id: ID numérico del ticket.
            include: recursos relacionados opcionales según Freshdesk.
        Returns:
            Ticket como dict.
        Ejemplo:
            >>> client.get_ticket(123)
            {'id': 123, 'subject': 'Error login'}
        """
        ticket_id = _parse_id(ticket_id)
        data = self._request("GET", f"/tickets/{ticket_id}", params={"include": include})
        self._logger.info("Ticket Freshdesk consultado")
        return dict(data)
