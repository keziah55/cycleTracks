from cycleTracks.data import CycleDataViewer, CycleData
from cycleTracks.util import monthYearToFloat, hourMinSecToFloat
from cycleTracks.test import makeDataFrame, MockParent
from PyQt5.QtWidgets import QMessageBox
import random
import tempfile
import pandas as pd
import pytest

pytest_plugin = "pytest-qt"

class TestCycleDataViewer:
    
    @pytest.fixture
    def setup(self, qtbot):
        self.parent = MockParent()
        
        self.widget = CycleDataViewer(self.parent)
        qtbot.addWidget(self.widget)
        self.widget.setGeometry(100, 100, 500, 600)
        self.widget.show()
        
    def test_sort(self, setup, qtbot):
        
        columns = self.widget.headerLabels
        columns = random.sample(columns, k=len(columns))
        if columns[0] == 'Date':
            # should already be sorted by Date, so make sure this isn't the first
            # column to be clicked here
            item = columns.pop(0)
            columns.append(item)
            
        for column in columns:
            idx = self.widget.headerLabels.index(column)
            
            expected = [item.text(idx) for item in self.widget.topLevelItems]
            
            if column == 'Date':
                expected = sorted(expected, key=monthYearToFloat)
            elif column == 'Time':
                expected = sorted(expected, key=hourMinSecToFloat)
            else:
                expected = sorted(expected, key=float)
            
            for _ in range(2):
                expected.reverse()
                with qtbot.waitSignal(self.widget.viewerSorted):
                    self.widget.header().sectionClicked.emit(idx)
                items = [item.text(idx) for item in self.widget.topLevelItems]
                assert items == expected
                
            
    def test_new_data(self, setup, qtbot):
        
        # expand some headers
        min_expanded = 3
        num = len(self.widget.topLevelItems) // 4
        num = max(min_expanded, num)
        expanded = random.sample(self.widget.topLevelItems, num)
        for item in expanded:
            self.widget.expandItem(item)
        expanded = [item.text(0) for item in expanded]
            
        # new data
        tmpfile = tempfile.NamedTemporaryFile()
        makeDataFrame(100, path=tmpfile.name)
        df = pd.read_csv(tmpfile.name, parse_dates=['Date'])
        data = CycleData(df)
        self.parent.data = data    
        
        self.widget.newData()
        
        for item in self.widget.topLevelItems:
            if item.isExpanded():
                assert item.text(0) in expanded
        
        
    def test_combine_data(self, setup, qtbot, monkeypatch):
        
        ret = self.widget.combineRows()
        assert ret is None
        
        # pick a top-level item
        item = random.sample(self.widget.topLevelItems, k=1)[0]
        idx = random.sample(range(item.childCount()), k=1)[0]
        item = item.child(idx)
        self.widget.setCurrentItem(item)
        
        ret = self.widget.combineRows()
        assert ret is None
        
        # pick another
        item = random.sample(self.widget.topLevelItems, k=1)[0]
        idx = random.sample(range(item.childCount()), k=1)[0]
        item = item.child(idx)
        item.setSelected(True)
        
        assert len(self.widget.selectedItems()) == 2
        
        date0, date1 = [item.text(0) for item in self.widget.selectedItems()]
        
        assert date0 != date1
        
        monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.Yes)
        with qtbot.assertNotEmitted(self.widget.data.dataChanged):
            self.widget.combineRows()
        
        gears = [item.text(5) for item in self.widget.selectedItems()]
        
        while len(set(gears)) == 1:
            # gears are the same, so select more items until gears differ
            item = random.sample(self.widget.topLevelItems, k=1)[0]
            idx = random.sample(range(item.childCount()), k=1)[0]
            item = item.child(idx)
            item.setSelected(True)
            gears = [item.text(5) for item in self.widget.selectedItems()]
        
        for item in self.widget.selectedItems():
            # set the same date on all selected items, so only gears differ
            item.setText(0, date0)
        
        monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.Yes)
        with qtbot.assertNotEmitted(self.widget.data.dataChanged):
            self.widget.combineRows()
        