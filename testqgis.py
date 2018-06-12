import qgis
from qgis.core import *
from PyQt4.QtCore import QFileInfo, QTimer, QSize
from PyQt4.QtGui import QApplication
from PyQt4.QtXml import *
from qgis.gui import *
import sys

sys.path.append('/Applications/QGIS.app/Contents/Resources/python/plugins')

QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS/", True)
# Qapplication (instead of QgsApplication) or errors
app = QApplication([], True)
QgsApplication.initQgis()

file_ = QFileInfo('/Users/guilhem/Documents/hiking/queblette.qgs')
project = QgsProject.instance()
project.read(file_)

#layers = QgsMapLayerRegistry.instance().mapLayers()

canvas = QgsMapCanvas()
canvas.resize(QSize(500, 500))
canvas.show()
# just the  specific layers
#canvas_layers = map(QgsMapCanvasLayer, layers.values())
#canvas.setLayerSet(canvas_layers)

# or all layers
root = QgsProject.instance().layerTreeRoot()
bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
bridge.setCanvasLayers()
canvas.refresh()
canvas.zoomToFullExtent()

template_file = file('web.qpt')
template_content = template_file.read()
template_file.close()
document = QDomDocument()
document.setContent(template_content)

composition = QgsComposition(canvas.mapSettings())
composition.loadFromTemplate(document)

map_items = composition.composerMapItems()
map_item = map_items[0]
map_item.setMapCanvas(canvas)
map_item.zoomToExtent(canvas.extent())
composition.refreshItems()
composition.exportAsPDF('web.pdf')
QgsProject.instance().clear()
