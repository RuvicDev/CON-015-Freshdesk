"""Validación local del conector Freshdesk contra Freshdesk real.

Requiere RUVIC_FRESHDESK_* apuntando a un portal Freshdesk de prueba.
Crea un ticket real de prueba, lo consulta, lo actualiza y agrega una nota.
"""
from __future__ import annotations
from ruvic_freshdesk_connector import FreshdeskClient, setup_logging
setup_logging("INFO")
client = FreshdeskClient()
print("== Ping =="); print(client.ping())
print("== Crear ticket ==")
ticket = client.create_ticket(subject="Prueba local Ruvic Freshdesk", description="Ticket creado por validate_local.py", email="cliente.prueba@example.com", priority=1, status=2)
print(ticket)
ticket_id = ticket["id"]
print("== Consultar ticket =="); print(client.get_ticket(ticket_id))
print("== Actualizar ticket =="); print(client.update_ticket(ticket_id, {"priority": 2}))
print("== Agregar nota =="); print(client.add_note(ticket_id, "Nota privada agregada por validate_local.py", private=True))
print("Validación Freshdesk completa. Ticket de prueba creado:", ticket_id)
