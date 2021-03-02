#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window for cycleTracks.
"""

import os
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot as Slot
import pandas as pd
from .plot import CyclePlotWidget
from .data import CycleData, CycleDataViewer, AddCycleData


class CycleTracks(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.file = self.getFile()
        self.sep = ','
        if not os.path.exists(self.file):
            header = ['Date', 'Time', 'Distance (km)', 'Calories', 'Gear']
            s = self.sep.join(header)
            with open(self.file, 'w') as fileobj:
                fileobj.write(s+'\n')
                
        self.df = pd.read_csv(self.file, sep=self.sep, parse_dates=['Date'])
        self.backup()

        self.data = CycleData(self.df)

        self.viewer = CycleDataViewer(self)
        self.addData = AddCycleData()
        self.plot = CyclePlotWidget(self)
        
        self.addData.newData.connect(self.data.append)
        self.data.dataChanged.connect(self.viewer.newData)
        self.data.dataChanged.connect(self.plot.newData)
        self.addData.newData.connect(self.backup)
        self.data.dataChanged.connect(self.save)
        self.plot.pointSelected.connect(self.viewer.highlightItem)
        self.viewer.itemSelected.connect(self.plot.setCurrentPointFromDate)
        
        dockWidgets = [(self.viewer, Qt.LeftDockWidgetArea, "Monthly Data"),
                       (self.addData, Qt.LeftDockWidgetArea, "Add Data")]
        
        for widget, area, title in dockWidgets:
            self.createDockWidget(widget, area, title=title)
            
        self.setCentralWidget(self.plot)
        
        self.createActions()
        self.createMenus()
        self.statusBar()
        self.statusTimeout = 2000
        
        self.setWindowTitle('Cycle Tracks')
        self.showMaximized()
            
    @staticmethod
    def getFile():
        home = os.path.expanduser('~')
        path = os.path.join(home, '.cycletracks')
        os.makedirs(path, exist_ok=True)
        file = os.path.join(path, 'cycletracks.csv')
        return file
        
    @Slot()
    def save(self):
        self.data.df.to_csv(self.file, sep=self.sep, index=False)
        self.statusBar().showMessage("Data saved", msecs=self.statusTimeout)
        
    @Slot()
    def backup(self):
        bak = self.file + '.bak'
        self.df.to_csv(bak, sep=self.sep, index=False)
        
    def createDockWidget(self, widget, area, title=None):
        dock = QDockWidget()
        dock.setWidget(widget)
        if title is not None:
            dock.setWindowTitle(title)
        self.addDockWidget(area, dock)
        if not hasattr(self, "dockWidgets"):
            self.dockWidgets = []
        self.dockWidgets.append(dock)
        
    def createActions(self):
        
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                               statusTip="Exit the application", 
                               triggered=self.close)
            
        self.saveAct = QAction("&Save", self, shortcut="Ctrl+S", 
                               statusTip="Save data", triggered=self.save)
        
        self.combineAct = QAction("&Combine", self, shortcut="Ctrl+Shift+C", 
                                  statusTip="Combine the selected rows in the viewer",
                                  triggered=self.viewer.combineRows)
        
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.combineAct)
        
        self.viewMenu = self.menuBar().addMenu("&View")
        self.panelMenu = self.viewMenu.addMenu("&Panels")
        for dock in self.dockWidgets:
            self.panelMenu.addAction(dock.toggleViewAction())
    