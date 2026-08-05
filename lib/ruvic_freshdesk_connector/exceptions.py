"""Excepciones propias del conector Freshdesk."""

class FreshdeskConnectorError(Exception):
    """Error base del conector Freshdesk."""

class FreshdeskConfigError(FreshdeskConnectorError):
    """Falta configuración requerida o algún valor de configuración es inválido."""

class FreshdeskAuthError(FreshdeskConnectorError):
    """API key inválida, dominio incorrecto o permisos insuficientes."""

class FreshdeskNetworkError(FreshdeskConnectorError):
    """Error de red, DNS, SSL, timeout o Freshdesk no alcanzable."""

class FreshdeskDataError(FreshdeskConnectorError):
    """Solicitud inválida, ticket inexistente, payload inválido o límite Freshdesk alcanzado."""

class FreshdeskSecurityError(FreshdeskConnectorError):
    """Operación bloqueada por reglas de seguridad del conector."""
