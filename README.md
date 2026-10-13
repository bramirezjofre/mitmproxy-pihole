# mitmproxy-pihole

Proxy HTTPS transparente + onboarding por portal web para que TVs Android y
cualquier device de la LAN use un Pi-hole como DNS, sin instalar apps ni
cambiar la configuración de red.

## ¿Cómo funciona?

```
[TV Android] --HTTP/HTTPS--> [mitmproxy en este server] ---> Internet
                                  |
                                  +-- DNS forzado a Pi-hole (RPi o server-18)
```

El device solo tiene que:

1. Configurar la red WiFi con proxy `http://<IP-del-server>:8080` (un solo campo)
2. Abrir `http://mitm.it` (o la URL que el contenedor sirve) en el navegador
3. Click en "iOS" / "Android" → "Download certificate"
4. Aceptar la instalación (Android TV pide OK una vez)

A partir de ahí **todo el tráfico HTTPS pasa por el proxy, y el DNS lo
resuelve el Pi-hole de la red local**.

## Stack

- `mitmproxy` (image oficial `mitmproxy/mitmproxy`)
- `caddy` (servidor web para la página de onboarding)
- `python3` (script que genera el `.env` y mantiene la CA sincronizada)

## Setup rápido

```bash
# 1. Clonar
git clone https://github.com/bramirezjofre/mitmproxy-pihole.git
cd mitmproxy-pihole

# 2. Configurar
cp .env.example .env
nano .env   # poner la IP del Pi-hole y el puerto del proxy

# 3. Levantar
docker compose up -d

# 4. Ver logs
docker compose logs -f mitmproxy
```

## Configurar el device

- **WiFi → Proxy → Manual**:
  - Hostname: la IP del server donde corre (ej. `192.168.1.4`)
  - Puerto: `8080`
- Abrir navegador y entrar a `http://mitm.it` o `http://<ip-del-server>:8081`
- Descargar e instalar el certificado
- Aceptar cuando Android pida confirmación

## Archivos

- `docker-compose.yaml` — servicios del proyecto
- `mitmproxy/` — addon Python que fuerza DNS a Pi-hole
- `onboarding/` — página estática servida por Caddy
- `Caddyfile` — config de Caddy para el portal
- `.env.example` — template de variables (sin secretos)

## Limitaciones

- Apps con **certificate pinning** (Netflix, algunos banking apps) no se
  pueden interceptar — van a fallar o a bypasear el proxy
- El device tiene que soportar **WiFi con proxy manual** (todas las TVs
  Android modernas lo hacen)
- HTTPS es interceptado por el proxy, así que el device ve un cert del
  proxy (no el cert original del sitio) — instalar el CA del proxy en el
  device es lo que lo hace transparente

## Seguridad

- El archivo `.env` está en `.gitignore` — **nunca commitearlo**
- El `.env.example` solo tiene placeholders
- La CA (`mitmproxy-ca-cert.pem`) también está en `.gitignore` — cada
  deploy genera la suya
