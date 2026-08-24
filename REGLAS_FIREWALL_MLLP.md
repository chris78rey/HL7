# Reglas de Firewall para Integración HL7 MLLP

Este documento describe reglas de firewall en pseudocódigo para permitir la comunicación HL7 sobre MLLP entre un cliente y un servidor, asegurando que los mensajes y los ACKs no sean bloqueados.

## Reglas de firewall en pseudocódigo para toda la ruta HL7 MLLP

A continuación se presentan reglas genéricas en pseudocódigo que deben aplicarse en:
- El servidor donde corre el MLLP de RIS/PACS
- Cualquier firewall o equipo de red intermedio
- El cliente que envía el mensaje HL7

**Basado en tu configuración actual:**
- IP del cliente ORM: 172.16.60.74
- IP del servidor RIS/PACS: 172.16.60.71
- Puerto MLLP: 6661

```
# En el servidor RIS/PACS (destino HL7)
PERMITIR ENTRADA TCP DESDE 172.16.60.74 AL PUERTO 6661
PERMITIR SALIDA TCP HACIA 172.16.60.74 DESDE EL PUERTO 6661
PERMITIR TRÁFICO RELACIONADO/ESTABLECIDO

# En la red intermedia (firewall, router, etc.)
PERMITIR PASO TCP DESDE 172.16.60.74 HACIA 172.16.60.71 PUERTO 6661
PERMITIR PASO TCP DESDE 172.16.60.71 HACIA 172.16.60.74 PUERTO 6661
PERMITIR TRÁFICO RELACIONADO/ESTABLECIDO

# En el cliente HL7 (origen)
PERMITIR SALIDA TCP HACIA 172.16.60.71 AL PUERTO 6661
PERMITIR ENTRADA TCP DESDE 172.16.60.71 DESDE EL PUERTO 6661
PERMITIR TRÁFICO RELACIONADO/ESTABLECIDO
```

**Notas:**
- "TRÁFICO RELACIONADO/ESTABLECIDO" significa permitir respuestas a conexiones ya permitidas.
- Aplica estas reglas en todos los puntos de la ruta para evitar bloqueos de mensajes o ACKs.

---

## Diagnóstico de problemas de ACK y uso de las reglas

Si no se recibe el ACK del servidor, revisa lo siguiente en cada punto de la ruta:

### 1. En el servidor RIS/PACS
- Verifica que la regla "PERMITIR ENTRADA TCP DESDE 172.16.60.74 AL PUERTO 6661" esté activa.
- Verifica que la regla "PERMITIR SALIDA TCP HACIA 172.16.60.74 DESDE EL PUERTO 6661" esté activa.
- Asegúrate de que el proceso MLLP esté escuchando en el puerto correcto.
- Revisa logs del servidor para ver si el mensaje fue recibido y si el ACK fue generado.

### 2. En la red intermedia (firewall, router, etc.)
- Verifica que el tráfico TCP pase en ambos sentidos entre cliente y servidor en el puerto 6661.
- Si hay NAT, asegúrate de que las respuestas se enruten correctamente.
- Si hay inspección de paquetes, asegúrate de que no se bloqueen paquetes de respuesta.

### 3. En el cliente HL7
- Verifica que la regla "PERMITIR SALIDA TCP HACIA 172.16.60.71 AL PUERTO 6661" esté activa.
- Verifica que la regla "PERMITIR ENTRADA TCP DESDE 172.16.60.71 DESDE EL PUERTO 6661" esté activa.
- Usa herramientas como `tcpdump` o `wireshark` para ver si el ACK llega a la interfaz de red.
- Si el ACK llega a la red pero no a la aplicación, revisa firewalls locales o problemas de redirección.

### 4. Consejos generales
- Usa `telnet 172.16.60.71 6661` para probar conectividad básica.
- Usa `tcpdump` o `wireshark` en cliente y servidor para ver si el ACK sale y llega.
- Consulta logs de firewall para ver si algún paquete es bloqueado.
- Si hay balanceadores o proxies, revisa sus reglas y registros.

**Resumen:**
- Aplica y revisa las reglas en todos los puntos.
- El bloqueo del ACK puede estar en el servidor, la red intermedia o el cliente.
- El diagnóstico debe ser paso a paso, verificando cada eslabón de la cadena.

---
