
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui

class MessagesTable(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setStyleSheet("""
            QTableView { gridline-color:#555; }
            QTableView::item:selected { background:#444; }
            QHeaderView::section {
                background:#333; color:#ddd; padding:6px 8px; border:0;
                font-weight:600;
            }
        """)

class MainWindow(QtWidgets.QMainWindow):
    requestOpenPcap = QtCore.pyqtSignal()
    requestOpenNdjson = QtCore.pyqtSignal()
    requestExportCsv = QtCore.pyqtSignal()
    requestExportNdjson = QtCore.pyqtSignal()
    requestExportXlsx = QtCore.pyqtSignal()
    requestFilters = QtCore.pyqtSignal()
    requestHelp = QtCore.pyqtSignal()
    requestAbout = QtCore.pyqtSignal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("WAMP Extractor Pro — PyQt5")
        self.resize(1200, 700)

        self.table = MessagesTable(self)
        self.setCentralWidget(self.table)

        self._build_menu_toolbar()
        self._apply_dark_theme()

        self.status = self.statusBar()
        self.status.showMessage("Listo")

        self.requestOpenPcap.connect(self.controller.open_pcap)
        self.requestOpenNdjson.connect(self.controller.open_ndjson)
        self.requestExportCsv.connect(self.controller.export_csv)
        self.requestExportNdjson.connect(self.controller.export_ndjson)
        self.requestExportXlsx.connect(self.controller.export_xlsx)
        self.requestFilters.connect(self.controller.open_filters_dialog)
        self.requestHelp.connect(self.controller.show_help)
        self.requestAbout.connect(self.controller.show_about)

    def _build_menu_toolbar(self):
        menubar = self.menuBar()
        mArchivo = menubar.addMenu("&Archivo")
        mExport = menubar.addMenu("&Exportar")
        mHerr = menubar.addMenu("&Herramientas")
        mAyuda = menubar.addMenu("&Ayuda")

        actOpenPcap = QtWidgets.QAction("Abrir PCAP/PCAPNG", self)
        actOpenNdjson = QtWidgets.QAction("Abrir NDJSON", self)
        actExportCSV = QtWidgets.QAction("Exportar CSV", self)
        actExportNDJ = QtWidgets.QAction("Exportar NDJSON", self)
        actExportXLSX = QtWidgets.QAction("Exportar Excel", self)
        actFilters = QtWidgets.QAction("Filtros / Modo…", self)
        actHelp = QtWidgets.QAction("Ver ayuda", self)
        actAbout = QtWidgets.QAction("Acerca de", self)

        actOpenPcap.setShortcut("Ctrl+O")
        actExportXLSX.setShortcut("Ctrl+E")
        actFilters.setShortcut("Ctrl+F")
        actHelp.setShortcut("F1")

        actOpenPcap.triggered.connect(self.requestOpenPcap.emit)
        actOpenNdjson.triggered.connect(self.requestOpenNdjson.emit)
        actExportCSV.triggered.connect(self.requestExportCsv.emit)
        actExportNDJ.triggered.connect(self.requestExportNdjson.emit)
        actExportXLSX.triggered.connect(self.requestExportXlsx.emit)
        actFilters.triggered.connect(self.requestFilters.emit)
        actHelp.triggered.connect(self.requestHelp.emit)
        actAbout.triggered.connect(self.requestAbout.emit)

        mArchivo.addAction(actOpenPcap)
        mArchivo.addAction(actOpenNdjson)
        mExport.addAction(actExportCSV)
        mExport.addAction(actExportNDJ)
        mExport.addAction(actExportXLSX)
        mHerr.addAction(actFilters)
        mAyuda.addAction(actHelp)
        mAyuda.addAction(actAbout)

        tb = QtWidgets.QToolBar("Principal", self)
        tb.setIconSize(QtCore.QSize(18, 18))
        tb.setMovable(False)
        tb.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.addToolBar(QtCore.Qt.TopToolBarArea, tb)
        tb.addAction(actOpenPcap)
        tb.addAction(actOpenNdjson)
        tb.addSeparator()
        tb.addAction(actExportCSV)
        tb.addAction(actExportNDJ)
        tb.addAction(actExportXLSX)
        tb.addSeparator()
        tb.addAction(actFilters)
        tb.addSeparator()
        tb.addAction(actHelp)

        tb.setStyleSheet("""
            QToolBar { background:#2b2b2b; border:0; padding:4px; spacing:6px; }
            QToolBar QToolButton { color:#e6e6e6; background:transparent; padding:6px 10px; }
            QToolBar QToolButton:hover { background:#3a3a3a; }
            QToolBar QToolButton:pressed { background:#444; }
        """)
        menubar.setStyleSheet("""
            QMenuBar { background:#2b2b2b; color:#e6e6e6; }
            QMenuBar::item:selected { background:#3a3a3a; }
            QMenu { background:#2b2b2b; color:#e6e6e6; }
            QMenu::item:selected { background:#3a3a3a; }
        """)

    def _apply_dark_theme(self):
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor(35, 35, 35))
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor(28, 28, 28))
        pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(32, 32, 32))
        pal.setColor(QtGui.QPalette.Text, QtGui.QColor(220, 220, 220))
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        pal.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(230, 230, 230))
        pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(230, 230, 230))
        pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(68, 68, 68))
        pal.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
        self.setPalette(pal)

    def set_model(self, model: QtCore.QAbstractItemModel):
        self.table.setModel(model)
        header = self.table.horizontalHeader()
        # ajusta algunas columnas
        for cid in range(model.columnCount()):
            header.setSectionResizeMode(cid, QtWidgets.QHeaderView.ResizeToContents)

    def show_message(self, text, timeout_ms=3000):
        self.statusBar().showMessage(text, timeout_ms)
