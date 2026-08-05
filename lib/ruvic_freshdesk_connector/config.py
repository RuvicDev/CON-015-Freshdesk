"""Configuración del conector leída desde variables de entorno.

Prefijo: RUVIC_FRESHDESK_
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from .exceptions import FreshdeskConfigError

ENV_PREFIX = "RUVIC_FRESHDESK_"

def _to_bool(value: str, default: bool) -> bool:
    raw = (value or "").strip().lower()
    if raw == "": return default
    if raw in {"true", "1", "yes", "y", "on"}: return True
    if raw in {"false", "0", "no", "n", "off"}: return False
    raise FreshdeskConfigError("Configuración inválida: VERIFY_SSL debe ser true/false.")

@dataclass(frozen=True)
class FreshdeskConfig:
    """Parámetros para autenticar y usar Freshdesk API v2."""
    domain: str
    api_key: str
    verify_ssl: bool = True
    timeout: int = 20
    max_results: int = 100

    @property
    def base_url(self) -> str:
        """URL base de la API Freshdesk v2."""
        d = self.domain.strip().rstrip("/")
        if d.startswith("https://"):
            return d + "/api/v2"
        return f"https://{d}.freshdesk.com/api/v2" if "." not in d else f"https://{d}/api/v2"

    @classmethod
    def from_env(cls) -> "FreshdeskConfig":
        """Construye la configuración desde variables RUVIC_FRESHDESK_*.

        Raises:
            ValueError: si faltan variables requeridas.
            FreshdeskConfigError: si un valor opcional es inválido.
        """
        domain = os.environ.get(f"{ENV_PREFIX}DOMAIN", "").strip()
        api_key = os.environ.get(f"{ENV_PREFIX}API_KEY", "").strip()
        missing = [n for n, v in ((f"{ENV_PREFIX}DOMAIN", domain), (f"{ENV_PREFIX}API_KEY", api_key)) if not v]
        if missing:
            raise ValueError("Faltan variables de entorno del conector freshdesk: " + ", ".join(missing) + ". Configura el conector en Settings → Conectores.")
        try:
            timeout = int(os.environ.get(f"{ENV_PREFIX}TIMEOUT", "20").strip() or "20")
            max_results = int(os.environ.get(f"{ENV_PREFIX}MAX_RESULTS", "100").strip() or "100")
            verify_ssl = _to_bool(os.environ.get(f"{ENV_PREFIX}VERIFY_SSL", "true"), default=True)
        except ValueError as exc:
            raise FreshdeskConfigError("RUVIC_FRESHDESK_TIMEOUT y RUVIC_FRESHDESK_MAX_RESULTS deben ser enteros.") from exc
        if timeout <= 0 or timeout > 120:
            raise FreshdeskConfigError("RUVIC_FRESHDESK_TIMEOUT debe estar entre 1 y 120 segundos.")
        if max_results <= 0 or max_results > 1000:
            raise FreshdeskConfigError("RUVIC_FRESHDESK_MAX_RESULTS debe estar entre 1 y 1000.")
        return cls(domain=domain, api_key=api_key, verify_ssl=verify_ssl, timeout=timeout, max_results=max_results)
