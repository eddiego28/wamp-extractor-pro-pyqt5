# WAMP Extractor Pro — PyQt5

Extractor y visor de mensajes **WAMP/WebSocket** y **TCP→JSON** desde capturas PCAP/PCAPNG o ficheros NDJSON.
Exporta a **CSV** y **Excel (XLSX)** con columnas aplanadas y una hoja *Raw*.
Incluye filtros por IP/puertos, y un **modo TCP-JSON** para frames que contengan objetos JSON en el payload TCP.

## Requisitos
- Python 3.9+
- `PyQt5`, `openpyxl`
- `tshark` (Wireshark CLI) disponible en PATH. Activar *Reassembly* de TCP en el comando que lanza la app (lo hacemos nosotros por CLI).

## Instalación
```bash
pip install -r requirements.txt
python -m src.main
```

## Uso rápido
1. Menú **Archivo → Abrir PCAP/PCAPNG** (o **Abrir NDJSON** si ya tienes NDJSON).
2. Menú **Herramientas → Filtros / Modo…** para limitar IPs/puertos o elegir *Modo: WAMP* o *TCP-JSON* o *AUTO*.
3. La tabla mostrará `time`, `ms`, `epoch`, `stream`, `src`, `dst`, `opcode`, `topic`, `type`.
4. Exporta con **Exportar → Excel**, **CSV** o **NDJSON**.
   - Excel crea dos hojas: **Mensajes** (sin `args/kwargs`) y **Raw** (con `args`, `kwargs` y `raw`). Los encabezados anidados comparten color de fondo por grupo.
