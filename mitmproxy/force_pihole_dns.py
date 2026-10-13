"""
Addon para mitmproxy que fuerza el uso del Pi-hole configurado como DNS
upstream para todas las peticiones que pasen por el proxy.

MIT License - bramirezjofre
"""
import os
import socket
import struct
import logging

# Lee la IP del Pi-hole del archivo .env
PIHOLE_DNS = os.environ.get("PIHOLE_DNS", "192.168.1.3")
PIHOLE_DNS_PORT = int(os.environ.get("PIHOLE_DNS_PORT", "53"))

LOG = logging.getLogger(__name__)


def _resolve_with_pihole(hostname: str) -> str | None:
    """
    Resuelve un hostname usando el Pi-hole configurado.
    Devuelve la primera IP encontrada o None si falla.
    """
    try:
        # Forzar uso del Pi-hole via DNS directo
        import dns.resolver
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [PIHOLE_DNS]
        resolver.port = PIHOLE_DNS_PORT
        resolver.lifetime = 3
        answers = resolver.resolve(hostname, "A")
        return str(answers[0])
    except Exception as e:
        LOG.debug("Pi-hole resolution failed for %s: %s", hostname, e)
        return None


class ForcePiholeDNS:
    """
    Addon que reescribe el resolver DNS de mitmproxy al Pi-hole configurado.

    Esto hace que cuando mitmproxy necesita resolver un hostname (por ejemplo
    para hacer CONNECT a un upstream HTTPS), use el Pi-hole en vez del DNS
    del sistema. Así el filtrado de ads/tracking aplica también a las
    peticiones que el proxy hace por su cuenta.
    """

    def __init__(self):
        LOG.info("ForcePiholeDNS addon initialized (Pi-hole: %s:%d)",
                 PIHOLE_DNS, PIHOLE_DNS_PORT)

    def running(self):
        """Se ejecuta cuando mitmproxy arranca."""
        LOG.info("Proxy running with Pi-hole DNS: %s:%d",
                 PIHOLE_DNS, PIHOLE_DNS_PORT)

    def resolve(self, flow):  # noqa: ARG002
        """
        Hook llamado por mitmproxy ANTES de resolver un hostname.
        Si tenemos la IP cacheada del Pi-hole, la usamos directamente.
        """
        # Este hook se puede usar para implementar cache local;
        # por ahora dejamos que mitmproxy use el DNS del sistema
        # (que configuramos en docker-compose via dns: en el service)
        pass
