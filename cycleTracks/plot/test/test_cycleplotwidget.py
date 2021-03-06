from cycleTracks.plot import CyclePlotWidget
from cycleTracks.test import MockParent
from PyQt5.QtCore import Qt, QPoint
import random
import pytest

pytest_plugin = "pytest-qt"

class Click:
    def __init__(self, pos, double):
        self._double = double
        self._pos = pos
        
    def double(self):
        return self._double
    
    def pos(self):
        return self._pos


class TestCyclePlotWidget:
    
    @pytest.fixture
    def setup(self, qtbot):
        self.parent = MockParent()
        
        self.widget = CyclePlotWidget(self.parent)
        qtbot.addWidget(self.widget)
        self.widget.showMaximized()
        
    @pytest.fixture
    def setup_reduced_points(self, qtbot):
        self.parent = MockParent(size=50)
        
        self.widget = CyclePlotWidget(self.parent)
        qtbot.addWidget(self.widget)
        self.widget.showMaximized()
        
        
    def test_switch_series(self, setup, qtbot):
        
        plotLabel = self.widget.plotLabel
        
        def callback(name):
            return name == key
        
        keys = list(plotLabel.data.keys())
        random.shuffle(keys)
        if keys[0] == 'distance':
            # make sure 'distance' ins't first, as nothing will change in that case
            name = keys.pop(0)
            keys.append(name)
        
        for key in keys:
            dct = plotLabel.data[key]
            label = dct['widget']
            
            with qtbot.waitSignal(plotLabel.labelClicked, check_params_cb=callback):
                qtbot.mouseClick(label, Qt.LeftButton)
                
            if key != 'date':
                axis = self.widget.plotWidget.plotItem.getAxis('left')
                axisLabel = axis.labelText
                assert axisLabel == self.parent.data.quickNames[key]
                
                
    def test_month_zoom(self, setup, qtbot):
    
        axis = self.widget.plotWidget.plotItem.getAxis('bottom')
        
        click = Click(pos=axis.pos(), double=True)
        with qtbot.waitSignal(axis.axisDoubleClicked):
            axis.mouseClickEvent(click)
        
    def test_mouse_hover(self, setup_reduced_points, qtbot):
        qtbot.wait(10) # wait for widget to be maximized so we can get the right size
        
        size = self.widget.size()
        y = size.height() // 2

        idx = None
        plotWidget = self.widget.plotWidget
        plotLabel = self.widget.plotLabel
        
        for x in range(0, size.width(), 5):
            pos = QPoint(x, y)
            qtbot.mouseMove(plotWidget, pos)
        
            if plotWidget.currentPoint and idx != plotWidget.currentPoint['index']:
                idx = plotWidget.currentPoint['index']
                pt = plotWidget.dataItem.scatter.data[idx]
                
                dateLabel = plotLabel.data['date']['widget']
                expected = f"<div style='font-size: {dateLabel.fontSize}pt'>"
                expected += f"{self.widget.plotWidget.currentPoint['date']}</div>"
                assert dateLabel.text() == expected
                
                distLabel = plotLabel.data['distance']['widget']
                expected = f"<div style='font-size: {distLabel.fontSize}pt; "
                expected += f"color: {distLabel.colour}'>"
                expected += f"Distance: {self.widget.plotWidget.currentPoint['distance']} km</div>"
                assert distLabel.text() == expected
                
        # move mouse back to middle before next text
        pos = QPoint(size.width()//2, y)
        qtbot.mouseMove(plotWidget, pos)