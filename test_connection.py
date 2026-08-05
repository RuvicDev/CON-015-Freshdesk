"""Prueba de conexión estándar del conector Freshdesk."""
from __future__ import annotations

def test_connection() -> tuple[bool, str]:
    """Prueba API Key y dominio consultando tickets."""
    try:
        from ruvic_freshdesk_connector import FreshdeskAuthError, FreshdeskClient, FreshdeskConfigError, FreshdeskDataError, FreshdeskNetworkError, FreshdeskSecurityError
    except ImportError:
        return False, "La librería ruvic-freshdesk-connector no está instalada. Instala con: pip install git+https://github.com/tu-org/conector-freshdesk.git#subdirectory=lib"
    try:
        client = FreshdeskClient(); client.ping()
    except ValueError as exc:
        return False, str(exc)
    except FreshdeskConfigError as exc:
        return False, f"Configuración inválida: {exc}"
    except FreshdeskAuthError as exc:
        return False, f"Autenticación o permisos Freshdesk inválidos: {exc}"
    except FreshdeskNetworkError as exc:
        return False, f"Error de red hacia Freshdesk: {exc}"
    except FreshdeskSecurityError as exc:
        return False, f"Bloqueo de seguridad: {exc}"
    except FreshdeskDataError as exc:
        return False, f"Freshdesk rechazó la solicitud: {exc}"
    except Exception as exc:
        return False, f"Error inesperado probando Freshdesk: {exc}"
    return True, f"Conexión exitosa a Freshdesk en {client.config.base_url}."
if __name__ == "__main__":
    ok, message = test_connection(); print(f"{'OK' if ok else 'FALLO'}: {message}"); raise SystemExit(0 if ok else 1)
