# Copyright 2018 geehalel@gmail.com
#
# This file is part of npindi.
#
#    npindi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    npindi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with npindi.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import Qt, QObject, QFile, QIODevice
from PyQt5.QtWidgets import QSizePolicy, QLabel, QLineEdit, QDoubleSpinBox, QPushButton, QHBoxLayout, QSpacerItem, QCheckBox, QButtonGroup, QSlider, QFileDialog
from PyQt5.QtGui import QFont, QIcon
from indi.client.qt.indicommon import *
from indi.INDI import *
class INDI_E(QObject):
    def __init__(self, gprop, dprop):
        super().__init__()
        self.guiProp = gprop
        self.dataProp = dprop
        self.EHBox = QHBoxLayout()
        self.EHBox.setContentsMargins(0, 0, 0, 0)
        self.text = None
        self.read_w = None
        self.write_w = None
        self.spin_w = None
        self.slider_w = None
        self.push_w = None
        self.check_w = None
        self.browse_w = None
        self.led_w = None
        self.tp = None
        self.np = None
        self.sp = None
        self.bp = None
        self.blobDirty = False
    def removeWidgets(self):
        while self.EHBox.count() > 0:
            item = self.EHBox.takeAt(0)
            if not item: continue
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.EHBox.deleteLater()
        del(self.read_w)
        del(self.write_w)
        del(self.spin_w)
        del(self.slider_w)
        del(self.push_w)
        del(self.check_w)
        del(self.browse_w)
        del(self.led_w)
        del(self.EHBox)
    def getLabel(self):
        return self.label
    def getName(self):
        return self.name
    def getBLOBDirty(self):
        return self.blobDirty
    def setBLOBDirty(self, isDirty):
        self.blobDirty = isDirty
    def buildSwitch(self, groupB, sw):
        self.name = sw.name
        self.label = sw.label
        if not self.label:
            self.label = self.name
        self.sp = sw
        if groupB is None:
            return
        pgtype = self.guiProp.getGUIType()
        if pgtype == PGui.PG_BUTTONS:
            self.push_w = QPushButton(self.label, self.guiProp.getGroup().getContainer())
            self.push_w.setCheckable(True)
            groupB.addButton(self.push_w)
            self.syncSwitch()
            self.guiProp.addWidget(self.push_w)
            self.push_w.show()
            if sw.svp.p == INDI.IPerm.IP_RO:
                self.push_w.setEnabled(sw.s == INDI.ISState.ISS_ON)
        elif pgtype == PGui.PG_RADIO:
            self.check_w = QCheckBox(self.label, self.guiProp.getGroup().getContainer())
            groupB.addButton(self.check_w)
            self.syncSwitch()
            self.guiProp.addWidget(self.check_w)
            self.check_w.show()
            if sw.svp.p == INDI.IPerm.IP_RO:
                self.check_w.setEnabled(sw.s == INDI.ISState.ISS_ON)
    def buildMenuItem(self, sw):
        self.buildSwitch(None, sw)
    def buildText(self, itp):
        self.name = itp.name
        self.label = itp.label
        if not self.label:
            self.label = self.name
        self.setupElementLabel()
        if itp.text:
            self.text = itp.text if itp.text else ''
        self.tp = itp
        perm = self.dataProp.getPermission()
        if perm == INDI.IPerm.IP_RW:
            self.setupElementRead(ELEMENT_READ_WIDTH)
            self.setupElementWrite(ELEMENT_WRITE_WIDTH)
        elif perm == INDI.IPerm.IP_RO:
            self.setupElementRead(ELEMENT_FULL_WIDTH)
        elif perm == INDI.IPerm.IP_WO:
            self.setupElementWrite(ELEMENT_FULL_WIDTH)
        self.guiProp.addLayout(self.EHBox)
    def buildNumber(self, inp):
        scale = False
        self.name = inp.name
        self.label = inp.label
        if not self.label:
            self.label = self.name
        self.np = inp
        self.text = INDI.numberFormat(self.np.format, self.np.value)
        self.setupElementLabel()
        if self.np.step != 0 and ((self.np.max - self.np.min) // self.np.step <= 100):
            scale = True
        perm = self.dataProp.getPermission()
        if perm == INDI.IPerm.IP_RW:
            self.setupElementRead(ELEMENT_READ_WIDTH)
            if scale:
                self.setupElementScale(ELEMENT_WRITE_WIDTH)
            else:
                self.setupElementWrite(ELEMENT_WRITE_WIDTH)
        elif perm == INDI.IPerm.IP_RO:
            self.setupElementRead(ELEMENT_READ_WIDTH)
        elif perm == INDI.IPerm.IP_WO:
            if scale:
                self.setupElementScale(ELEMENT_FULL_WIDTH)
            else:
                self.setupElementWrite(ELEMENT_FULL_WIDTH)
        self.guiProp.addLayout(self.EHBox)
    def buildLight(self, ilp):
        self.name = ilp.name
        self.label = ilp.label
        if not self.label:
            self.label = self.name
        self.led_w = QLed(self.guiProp.getGroup().getContainer())
        self.led_w.setMaximumSize(16, 16)
        self.lp = ilp
        self.syncLight()
        self.EHBox.addWidget(self.led_w)
        self.setupElementLabel()
        self.guiProp.addLayout(self.EHBox)
    def buildBLOB(self, ibp):
        self.name = ibp.name
        self.label = ibp.label
        if not self.label:
            self.label = self.name
        self.setupElementLabel()
        self.text = 'INDI DATA STREAM'
        self.bp = ibp
        perm = self.dataProp.getPermission()
        if perm == INDI.IPerm.IP_RW:
            self.setupElementRead(ELEMENT_READ_WIDTH)
            self.setupElementWrite(ELEMENT_WRITE_WIDTH)
            self.setupBrowseButton()
        elif perm == INDI.IPerm.IP_RO:
            self.setupElementRead(ELEMENT_FULL_WIDTH)
        elif perm == INDI.IPerm.IP_WO:
            self.setupElementWrite(ELEMENT_FULL_WIDTH)
            self.setupBrowseButton()
        self.guiProp.addLayout(self.EHBox)
    def syncSwitch(self):
        pgtype = self.guiProp.getGUIType()
        if pgtype == PGui.PG_BUTTONS:
            if self.sp.s == INDI.ISState.ISS_ON:
                self.push_w.setChecked(True)
                buttonFont = self.push_w.font()
                buttonFont.setBold(True)
                self.push_w.setFont(buttonFont)
                if self.sp.svp.p == INDI.IPerm.IP_RO:
                    self.push_w.setEnabled(True)
            else:
                self.push_w.setChecked(False)
                buttonFont = self.push_w.font()
                buttonFont.setBold(False)
                self.push_w.setFont(buttonFont)
                if self.sp.svp.p == INDI.IPerm.IP_RO:
                    self.push_w.setEnabled(False)
        elif pgtype == PGui.PG_RADIO:
            if self.sp.s == INDI.ISState.ISS_ON:
                self.check_w.setChecked(True)
                if self.sp.svp.p == INDI.IPerm.IP_RO:
                    self.check_w.setEnabled(True)
            else:
                self.check_w.setChecked(False)
                if self.sp.svp.p == INDI.IPerm.IP_RO:
                    self.check_w.setEnabled(False)
    def syncText(self):
        if self.tp is None: return
        if self.tp.tvp.p != INDI.IPerm.IP_WO:
            self.read_w.setText(self.tp.text)
        else:
            self.write_w.setText(self.tp.text)
    def syncNumber(self):
        if self.np is None or self.read_w is None:
            return
        #QLoggingCategory.qCDebug(QLoggingCategory.NPINDI,'syncNumber '+self.np.format +':'+str(self.np.value)+' '+str(self.np.min)+' '+str(self.np.max))
        self.text = INDI.numberFormat(self.np.format, self.np.value)
        self.read_w.setText(self.text)
        if self.spin_w:
            if self.np.min != self.spin_w.minimum():
                self.setMin()
            if self.np.max != self.spin_w.maximum():
                self.setMax()
    def syncLight(self):
        if self.lp is None: return
        if self.lp.s == INDI.IPState.IPS_IDLE:
            self.led_w.setColor('gray')
        elif self.lp.s == INDI.IPState.IPS_OK:
            self.led_w.setColor('green')
        elif self.lp.s == INDI.IPState.IPS_BUSY:
            self.led_w.setColor('orange')
        elif self.lp.s == INDI.IPState.IPS_ALERT:
            self.led_w.setColor('red')
    def updateTP(self):
        if self.tp is None: return
        self.tp.text = self.write_w.text()
    def updateNP(self):
        if self.np is None: return
        if self.write_w is not None:
            if self.write_w.text() is None:
                return
            #QLoggingCategory.qCDebug(QLoggingCategory.NPINDI,'updateNP '+self.write_w.text().replace(',','.').strip())
            try:
                self.np.value = INDI.f_scan_sexa(self.write_w.text().replace(',','.').strip())
                #QLoggingCategory.qCDebug(QLoggingCategory.NPINDI,'updateNP '+str(self.np.value))
            except:
                pass
            return
        if self.spin_w is not None:
            self.np.value = self.spin_w.value()
    def setupElementLabel(self):
        self.label_w = QLabel(self.guiProp.getGroup().getContainer())
        self.label_w.setMinimumWidth(ELEMENT_LABEL_WIDTH)
        self.label_w.setMaximumWidth(ELEMENT_LABEL_WIDTH)
        self.label_w.setFrameShape(QLabel.Box)
        self.label_w.setTextFormat(Qt.RichText)
        self.label_w.setAlignment(Qt.AlignCenter)
        self.label_w.setWordWrap(True)
        if len(self.label) > MAX_LABEL_LENGTH:
            tempFont = QFont(self.label_w.font())
            tempFont.setPointSize(tempFont.pointSize() - MED_INDI_FONT)
            self.label_w.setFont(tempFont)
        self.label_w.setText(self.label)
        self.EHBox.addWidget(self.label_w)
    def setupElementScale(self, length):
        if self.np is None: return
        steps = (self.np.max -self.np.min) // self.np.step
        self.spin_w = QDoubleSpinBox(self.guiProp.getGroup().getContainer())
        self.spin_w.setRange(self.np.min, self.np.max)
        self.spin_w.setSingleStep(self.np.step)
        self.spin_w.setValue(self.np.value)
        self.spin_w.setDecimals(3)
        self.slider_w = QSlider(Qt.Horizontal, self.guiProp.getGroup().getContainer())
        self.slider_w.setRange(0, steps)
        self.slider_w.setPageStep(1)
        self.slider_w.setValue((self.np.value - self.np.min) // self.np.step)
        self.spin_w.valueChanged.connect(self.spinChanged)
        self.slider_w.sliderMoved.connect(self.sliderChanged)
        if length == ELEMENT_FULL_WIDTH:
            self.spin_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        else:
            self.spin_w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.spin_w.setMinimumWidth(int(length*0.45))
        self.slider_w.setMinimumWidth(int(length*0.55))
        self.EHBox.addWidget(self.slider_w)
        self.EHBox.addWidget(self.spin_w)
    def setupBrowseButton(self):
        self.browse_w = QPushButton(self.guiProp.getGroup().getContainer())
        self.browse_w.setIcon(QIcon.fromTheme('document-open'))
        if self.browse_w.icon() is None:
            self.browse_w.setText('Browse')
        self.browse_w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.browse_w.setMinimumWidth(MIN_SET_WIDTH)
        self.browse_w.setMaximumWidth(MAX_SET_WIDTH)
        self.EHBox.addWidget(self.browse_w)
        self.browse_w.clicked.connect(self.browseBlob)
    @QtCore.pyqtSlot(float)
    def spinChanged(self, value):
        slider_value = int((value - self.np.min) / self.np.step)
        self.slider_w.setValue(slider_value)
    @QtCore.pyqtSlot(int)
    def sliderChanged(self, value):
        if value is None: value = self.slider_w.sliderPosition()
        spin_value = (value * self.np.step) + self.np.min
        self.spin_w.setValue(spin_value)
    def setMin(self):
        if self.spin_w:
            self.spin_w.setMinimum(self.np.min)
            self.spin_w.setValue(self.np.value)
        if self.slider_w:
            self.slider_w.setMaximum((self.np.max-self.np.min)/self.np.step)
            self.slider_w.setMinimum(0)
            self.slider_w.setPageStep(1)
            self.slider_w.setValue((self.np.value-self.np.min)/self.np.step)
    def setMax(self):
        if self.spin_w:
            self.spin_w.setMaximum(self.np.max)
            self.spin_w.setValue(self.np.value)
        if self.slider_w:
            self.slider_w.setMaximum((self.np.max-self.np.min)/self.np.step)
            self.slider_w.setMinimum(0)
            self.slider_w.setPageStep(1)
            self.slider_w.setValue((self.np.value-self.np.min)/self.np.step)
    def setupElementRead(self, length):
        self.read_w = QLineEdit(self.guiProp.getGroup().getContainer())
        self.read_w.setMinimumWidth(length)
        self.read_w.setFocusPolicy(Qt.NoFocus)
        self.read_w.setCursorPosition(0)
        self.read_w.setAlignment(Qt.AlignCenter)
        self.read_w.setReadOnly(True)
        self.read_w.setText(self.text)
        self.EHBox.addWidget(self.read_w)
    def setupElementWrite(self, length):
        self.write_w = QLineEdit(self.guiProp.getGroup().getContainer())
        self.write_w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.write_w.setMinimumWidth(length)
        self.write_w.setMaximumWidth(length)
        self.write_w.setText(self.text)
        self.write_w.returnPressed.connect(self.guiProp.sendText)
        self.EHBox.addWidget(self.write_w)
    @QtCore.pyqtSlot()
    def browseBlob(self):
        currentURL, _ = QFileDialog.getOpenFileUrl(self.guiProp.getGroup().getDevice().guiManager)
        if not currentURL:
            return
        if currentURL.isValid():
            self.write_w.setText(currentURL.toLocalFile())
        fp = QFile()
        fp.setFileName(currentURL.toLocalFile())
        filename = currentURL.toLocalFile()
        self.bp.format = '.' + filename.split('.')[-1]
        if not fp.open(QIODevice.ReadOnly):
            QLoggingCategory.qCWarning(QLoggingCategory.NPINDI, 'Can not open file %s for reading.' % filename)
            return
        self.bp.bloblen = self.bp.size = fp.size()
        self.bp.blob = fp.readAll()
        self.blobDirty = True
    def getWriteField(self):
        if self.write_w:
            return self.write_w.text()
        else:
            return None
    def getReadField(self):
        if self.read_w:
            return self.read_w.text()
        else:
            return None
