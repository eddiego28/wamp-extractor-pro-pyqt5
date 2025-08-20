
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore

HELP_MD = """
<h2>Ayuda — WAMP Extractor Pro</h2>
<p><b>Qué hace:</b> Extrae mensajes de <b>WAMP/WebSocket</b> y también
objetos JSON encontrados en el <b>payload TCP</b> (modo TCP-JSON) desde ficheros PCAP/PCAPNG.
Permite filtrar por IP/puerto y exportar a <b>CSV</b>, <b>NDJSON</b> y <b>Excel</b>.</p>

<h3>Pasos típicos</h3>
<ol>
<li>Menú <b>Archivo → Abrir PCAP/PCAPNG</b>.</li>
<li>Menú <b>Herramientas → Filtros / Modo…</b> para ajustar <i>src/dst IP</i>, puertos y el <i>modo</i>:
    <ul>
        <li><b>AUTO</b>: intenta WAMP y TCP-JSON.</li>
        <li><b>WAMP</b>: sólo WebSocket/WAMP.</li>
        <li><b>TCP-JSON</b>: reconstruye flujo TCP y busca objetos <b>JSON</b> balanceados.</li>
    </ul>
</li>
<li>Exporta con <b>Exportar → Excel</b> (dos hojas: Mensajes y Raw), <b>CSV</b> o <b>NDJSON</b>.</li>
</ol>

<h3>Excel profesional</h3>
<ul>
<li>Hoja <b>Mensajes</b>: columnas básicas + campos aplanados del JSON (sin args/kwargs crudos).</li>
<li>Los encabezados anidados comparten <b>mismo color</b> de fondo para identificar el grupo.</li>
<li>Hoja <b>Raw</b>: incluye <i>args</i>, <i>kwargs</i> y <i>raw</i>.</li>
<li>Hoja <b>Resumen</b>: conteo por <i>type</i> y <i>topic</i>.</li>
</ul>

<h3>Requisitos de sistema</h3>
<p>Necesitas <code>tshark</code> instalado y accesible en PATH. La app ya activa
la reensamblación TCP mediante <code>-o tcp.desegment_tcp_streams:true</code>.</p>

<h3>Consejos</h3>
<ul>
<li>Si tus mensajes WAMP están comprimidos, intentamos inflarlos automáticamente.</li>
<li>Para tráfico no-WAMP con JSON incrustado, usa <b>TCP-JSON</b>.</li>
<li>Puedes limitar el análisis a un <b>router WAMP concreto</b> poniendo su IP en SRC/DST.</li>
</ul>
"""

class HelpDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayuda")
        self.resize(720, 520)
        lay = QtWidgets.QVBoxLayout(self)
        view = QtWidgets.QTextBrowser(self)
        view.setOpenExternalLinks(True)
        view.setHtml(HELP_MD)
        lay.addWidget(view)
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        btn.rejected.connect(self.reject)
        lay.addWidget(btn)
