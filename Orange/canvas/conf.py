import itertools
import logging

import pkg_resources

from PyQt4.QtGui import QPixmap, QFont, QFontMetrics, QColor, QPainter
from PyQt4.QtCore import Qt, QCoreApplication, QPoint, QRect
from OrangeCanvas import config

from . import discovery, widgetsscheme


WIDGETS_ENTRY = "orange.widgets"
MENU_ENTRY = "orange.menu"

#: Parameters for searching add-on packages in PyPi using xmlrpc api.
ADDON_PYPI_SEARCH_SPEC = {"keywords": "oasys"}
#: Entry points by which add-ons register with pkg_resources.
ADDONS_ENTRY = "orangecontrib"

# Add a default for our extra default-working-dir setting.
config.spec += [
    config.config_slot("output/default-working-dir", str, "",
                       "Default working directory")
]


class oasysconf(config.default):
    OrganizationDomain = ""
    ApplicationName = "OASYS"
    ApplicationVersion = "1.0"

    @staticmethod
    def splash_screen():
        path = pkg_resources.resource_filename(
            __name__, "icons/orange-splash-screen.png")
        pm = QPixmap(path)

        version = QCoreApplication.applicationVersion()
        size = 21 if len(version) < 5 else 16
        font = QFont("Helvetica")
        font.setPixelSize(size)
        font.setBold(True)
        font.setItalic(True)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        metrics = QFontMetrics(font)
        br = metrics.boundingRect(version).adjusted(-5, 0, 5, 0)
        br.moveCenter(QPoint(436, 224))

        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setFont(font)
        p.setPen(QColor("#231F20"))
        p.drawText(br, Qt.AlignCenter, version)
        p.end()
        return pm, QRect(88, 193, 200, 20)

    @staticmethod
    def widgets_entry_points():
        ep_menu_iter = pkg_resources.iter_entry_points(MENU_ENTRY)
        ep_iter = pkg_resources.iter_entry_points(WIDGETS_ENTRY)
        return itertools.chain(ep_menu_iter, ep_iter)

    @staticmethod
    def addon_entry_points():
        return pkg_resources.iter_entry_points(ADDONS_ENTRY)

    @staticmethod
    def addon_pypi_search_spec():
        return dict(ADDON_PYPI_SEARCH_SPEC)

    @staticmethod
    def tutorials_entry_points():
        default_ep = pkg_resources.EntryPoint(
            "Orange", "Orange.canvas.application.tutorials",
            dist=pkg_resources.get_distribution("Orange"))

        return itertools.chain(
            (default_ep,), pkg_resources.iter_entry_points(""))

    widget_discovery = discovery.WidgetDiscovery
    workflow_constructor = widgetsscheme.WidgetsScheme


def omenus():
    """
    Return an iterator of Orange.menu.OMenu instances registered
    by 'orange.menu' pkg_resources entry point.
    """
    log = logging.getLogger(__name__)
    for ep in pkg_resources.iter_entry_points(MENU_ENTRY):
        try:
            menu = ep.load()
        except pkg_resources.ResolutionError:
            log.info("Error loading a 'orange.menu' entry point.", exc_info=True)
        except Exception:
            log.exception("Error loading a 'orange.menu' entry point.")
        else:
            if "MENU" in menu.__dict__:
                yield from discovery.omenus_from_package(menu)


def menu_registry():
    """
    Return the the OASYS extension menu registry.
    """
    return discovery.MenuRegistry(list(omenus()))
