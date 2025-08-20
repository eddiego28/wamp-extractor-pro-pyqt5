
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore

class FiltersDialog(QtWidgets.QDialog):
    def __init__(self, current, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtros / Modo")
        self.resize(460, 220)
        form = QtWidgets.QFormLayout(self)

        self.edSrc = QtWidgets.QLineEdit(current.src_ip)
        self.edDst = QtWidgets.QLineEdit(current.dst_ip)
        self.edSport = QtWidgets.QLineEdit(current.src_port)
        self.edDport = QtWidgets.QLineEdit(current.dst_port)
        self.cbMode = QtWidgets.QComboBox()
        self.cbMode.addItems(["AUTO","WAMP","TCPJSON"])
        idx = self.cbMode.findText(current.mode)
        if idx >= 0: self.cbMode.setCurrentIndex(idx)

        form.addRow("IP origen:", self.edSrc)
        form.addRow("IP destino:", self.edDst)
        form.addRow("Puerto origen:", self.edSport)
        form.addRow("Puerto destino:", self.edDport)
        form.addRow("Modo:", self.cbMode)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_filters(self):
        return {
            "src_ip": self.edSrc.text().strip(),
            "dst_ip": self.edDst.text().strip(),
            "src_port": self.edSport.text().strip(),
            "dst_port": self.edDport.text().strip(),
            "mode": self.cbMode.currentText()
        }
