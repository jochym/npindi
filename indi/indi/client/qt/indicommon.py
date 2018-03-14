import enum
INDI_MAX_TRIES = 3
PROPERTY_LABEL_WIDTH = 100
ELEMENT_LABEL_WIDTH = 175
ELEMENT_READ_WIDTH = 175
ELEMENT_WRITE_WIDTH = 175
ELEMENT_FULL_WIDTH = 175
MIN_SET_WIDTH = 50
MAX_SET_WIDTH = 110
MED_INDI_FONT = 2
MAX_LABEL_LENGTH = 20
class DriverSource(enum.Enum):
    PRIMARY_XML = 0
    THIRD_PARTY_XML = 1
    EM_XML = 2
    HOST_SOURCE = 3
    GENERATED_SOURCE = 4
class ServerMode(enum.Enum):
    SERVER_CLIENT = 0
    SERVER_ONLY = 1
class PGui(enum.Enum):
    PG_NONE = 0
    PG_TEXT = 1
    PG_NUMERIC = 2
    PG_BUTTONS = 3
    PG_RADIO = 4
    PG_MENU = 5
    PG_LIGHTS = 6
    PG_BLOB = 7
class DeviceFamily(enum.Enum):
    """
    Devices families that we explicitly support (i.e. with std properties)
    """
    KSTARS_TELESCOPE = 0
    KSTARS_CCD = 1
    KSTARS_FILTER = 2
    KSTARS_VIDEO = 3
    KSTARS_FOCUSER = 4
    KSTARS_ROTATOR = 5
    KSTARS_DOME = 6
    KSTARS_ADAPTIVE_OPTICS = 7
    KSTARS_RECEIVERS = 8
    KSTARS_GPS = 9
    KSTARS_WEATHER = 10
    KSTARS_AUXILIARY = 11
    KSTARS_UNKNOWN = 12

from PyQt5 import QtCore
# PyQt5 lacks QLoggingCategory
# QLoggingCategory.Q_LOGGING_CATEGORY(NPINDI, 'npindi')
class QLoggingCategory(enum.Enum):
    NPINDI = 'npindi'
    def qCCritical(cat, msg):
        QtCore.qCritical(cat.value+': '+msg)
    def qCDebug(cat, msg):
        QtCore.qDebug(cat.value+': '+msg)
    def qCInfo(cat, msg):
        #QtCore.qInfo(cat.value+': '+msg)
        QtCore.qDebug(cat.value+': '+msg)
    def qCWarning(cat, msg):
        QtCore.qWarning(cat.value+': '+msg)