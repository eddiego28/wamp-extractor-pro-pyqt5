
# -*- coding: utf-8 -*-
import os, json
from typing import List, Dict
from PyQt5 import QtWidgets, QtCore, QtGui
from .ui.main_window import MainWindow
from .ui.filters_dialog import FiltersDialog
from .ui.help_dialog import HelpDialog
from .core.pcap_parser import Filters
from .core.pcap_processor import process_pcap_to_records
from .io.ndjson_io import read_ndjson, write_ndjson
from .core.export_excel import export_to_xlsx
from .util.flatten import flatten_dict

class RecordsModel(QtGui.QStandardItemModel):
    COLS = ["time","ms","epoch","stream","src","dst","opcode","topic","type"]
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(self.COLS))
        self.setHorizontalHeaderLabels(self.COLS)

    def load(self, items: List[Dict]):
        self.setRowCount(0)
        for r in items:
            row = []
            for c in self.COLS:
                val = r.get(c, "")
                it = QtGui.QStandardItem(str(val))
                it.setEditable(False)
                row.append(it)
            self.appendRow(row)

class Controller(QtCore.QObject):
    def __init__(self, app):
        super().__init__()
        self.qt_app = app
        self.win = MainWindow(self)
        self.model = RecordsModel()
        self.win.set_model(self.model)
        self.records: List[Dict] = []
        self.filters = Filters(mode="AUTO")
        self.win.show()

    # ----------------- actions -----------------

    def open_pcap(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self.win, "Abrir PCAP/PCAPNG", "", "PCAP(*.pcap *.pcapng)")
        if not path: return
        self.win.show_message("Procesando PCAP…")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.records = process_pcap_to_records(path, self.filters)
            self.model.load(self.records)
            self.win.show_message(f"{len(self.records)} mensajes — {self.filters.to_display()}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.win, "Error", str(e))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def open_ndjson(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self.win, "Abrir NDJSON", "", "NDJSON(*.ndjson *.jsonl)")
        if not path: return
        items = read_ndjson(path)
        # formatea a records mínimos
        recs = []
        for obj in items:
            kwargs = obj if isinstance(obj, dict) else {"raw": obj}
            recs.append({
                "time":"", "ms":"", "epoch":0.0, "stream":"", "src":"", "dst":"",
                "opcode":"NDJSON","topic":"","type": (next(iter(kwargs.keys())) if isinstance(kwargs, dict) and kwargs else ""),
                "args": [], "kwargs": kwargs, "raw": json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj
            })
        self.records = recs
        self.model.load(self.records)
        self.win.show_message(f"{len(self.records)} registros NDJSON")

    def export_csv(self):
        if not self.records:
            QtWidgets.QMessageBox.information(self.win, "Info", "No hay registros para exportar.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.win, "Guardar CSV", "mensajes.csv", "CSV (*.csv)")
        if not path: return
        import csv
        # aplanar todas las claves
        base = ["time","ms","epoch","stream","src","dst","opcode","topic","type"]
        keys = set()
        flat_cache = []
        for r in self.records:
            flat = {}
            if isinstance(r.get("kwargs"), dict):
                flat.update(flatten_dict(r["kwargs"], "kw"))
            if isinstance(r.get("args"), (list, tuple)):
                flat.update(flatten_dict(list(r["args"]), "args"))
            flat_cache.append(flat)
            keys.update(flat.keys())
        keys = sorted(keys)
        headers = base + keys
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for r, flat in zip(self.records, flat_cache):
                row = [r.get(c,"") for c in base] + [flat.get(k,"") for k in keys]
                w.writerow(row)
        self.win.show_message(f"CSV guardado: {os.path.basename(path)}")

    def export_ndjson(self):
        if not self.records:
            QtWidgets.QMessageBox.information(self.win, "Info", "No hay registros para exportar.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.win, "Guardar NDJSON", "mensajes.ndjson", "NDJSON (*.ndjson *.jsonl)")
        if not path: return
        write_ndjson(path, self.records)
        self.win.show_message(f"NDJSON guardado: {os.path.basename(path)}")

    def export_xlsx(self):
        if not self.records:
            QtWidgets.QMessageBox.information(self.win, "Info", "No hay registros para exportar.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.win, "Guardar Excel", "mensajes.xlsx", "Excel (*.xlsx)")
        if not path: return
        export_to_xlsx(self.records, path)
        self.win.show_message(f"Excel guardado: {os.path.basename(path)}")

    def open_filters_dialog(self):
        dlg = FiltersDialog(self.filters, self.win)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_filters()
            self.filters = Filters(**data)
            self.win.show_message("Filtros actualizados")

    def show_help(self):
        HelpDialog(self.win).exec_()

    def show_about(self):
        QtWidgets.QMessageBox.information(self.win, "Acerca de",
            "WAMP Extractor Pro — PyQt5\n"
            "Extracción WAMP y TCP→JSON desde PCAP.\n"
            "Exporta CSV/NDJSON/Excel con hoja Raw y Resumen.\n"
        )
