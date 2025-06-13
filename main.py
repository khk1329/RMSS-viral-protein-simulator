import sys
import multiprocessing
from PySide6.QtWidgets import QApplication
from simulation_GUI import CovSimulator

if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = CovSimulator()
    window.show()
    sys.exit(app.exec())
