import multiprocessing
import threading
from queue import Queue
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog, QDoubleSpinBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QTextCursor, QValidator
from ui.Mutation_simulator_GUI import Ui_CovSimulatorGUI
from simulation_core import simulate_multiple_cycles, load_sequence_from_fasta, load_sequences_from_fasta_list
from multiprocessing import Manager

class HybridSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDecimals(18)
        self.setKeyboardTracking(False)

    def validate(self, text, pos):
        try:
            float(text)
            return QValidator.Acceptable, text, pos
        except ValueError:
            return QValidator.Intermediate, text, pos

    def textFromValue(self, value):
        return f"{value:.15f}".rstrip('0').rstrip('.')

    def valueFromText(self, text):
        try:
            return float(text)
        except ValueError:
            return 0.0            
        
class CovSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CovSimulatorGUI()
        self.ui.setupUi(self)
        
        self.closing_allowed = True 
        self.ui.CancelBtn.hide()
        
        self.manager = Manager()
        self.stop_event = self.manager.Event()

        self.process_queue = multiprocessing.Queue()

        self.gui_queue = Queue()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_queue)
        self.timer.start(100)
        
        old_spinbox = self.ui.mutationRate
        parent_layout = self.ui.mutationLayout
        
        for i in range(parent_layout.count()):
            item = parent_layout.itemAt(i)
            if item and item.widget() == old_spinbox:
                parent_layout.takeAt(i)
                old_spinbox.deleteLater()
                break
        
        self.hybrid_mutation_rate = HybridSpinBox()
        self.hybrid_mutation_rate.setObjectName("mutationRate")
        self.hybrid_mutation_rate.setDecimals(18)
        self.hybrid_mutation_rate.setValue(0.00000376)
        self.hybrid_mutation_rate.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.hybrid_mutation_rate.setStyleSheet("""
            QDoubleSpinBox { background-color: white; }
        """)
        
        parent_layout.insertWidget(i, self.hybrid_mutation_rate)
        self.ui.mutationRate = self.hybrid_mutation_rate

        self.input_path = None
        self.target_paths = []
        self.output_folder = None

        self.ui.loadInputBtn.clicked.connect(self.load_input_file)
        self.ui.loadTargetBtn.clicked.connect(self.load_target_file)
        self.ui.chooseOutputFolderBtn.clicked.connect(self.choose_output_folder)
        self.ui.startBtn.clicked.connect(self.start_simulation_process)
        self.ui.CancelBtn.clicked.connect(self.handle_cancel)

        self.queue = multiprocessing.Queue()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_queue)
        self.timer.start(100)

    def log(self, message):
        self.ui.logOutput.append(str(message))
        cursor = self.ui.logOutput.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.logOutput.setTextCursor(cursor)
        self.ui.logOutput.ensureCursorVisible()

    def poll_queue(self):
        while not self.gui_queue.empty():
            try:
                msg_type, content = self.gui_queue.get_nowait()
    
                if msg_type == 'log':
                    self.log(content)
    
                elif msg_type == 'progress':
                    current, total = content
                    self.ui.progressBar.setMaximum(total)
                    self.ui.progressBar.setValue(current)
    
                elif msg_type == 'done':
                    self.closing_allowed = True
                    self.ui.progressBar.setMaximum(100)
                    self.ui.progressBar.setValue(100)
                    
                    QApplication.alert(self)
                    
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Finished")
                    msg_box.setText("Simulation completed successfully!")
                    msg_box.setIcon(QMessageBox.Information)
                    ok_button = msg_box.addButton(QMessageBox.Ok)
                    ok_button.setCursor(Qt.PointingHandCursor)
                    ok_button.setStyleSheet("""
                        QPushButton {
                            font-size: 13px;
                            font-weight: bold;
                            padding: 6px 12px;
                            min-width: 20px;
                            min-height: 10px;
                        }
                    """)
                    msg_box.activateWindow()
                    msg_box.exec()
    
                    if isinstance(self.gui_queue, multiprocessing.queues.Queue):
                        try:
                            self.gui_queue.close()
                            self.gui_queue.join_thread()
                        except Exception as e:
                            print(f"Queue closing error: {e}")
    
                    QApplication.quit()
    
            except Exception as e:
                print(f"Queue error: {e}")

    def load_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Input FASTA File", "", "FASTA Files (*.fasta *.fa *.fna)")
        if file_path:
            self.input_path = file_path
            self.ui.inputLabel.setText(file_path)

    def load_target_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Target FASTA file", "", "FASTA Files (*.fasta *.fa *.fna)")
        if files:
            self.target_paths = files
            self.ui.targetLabel.setText(", ".join(files))

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.ui.outputFolderLabel.setText(folder)
            
    def transfer_queue_data(self):
        while True:
            msg = self.process_queue.get()
            self.gui_queue.put(msg)
            if msg[0] == 'done':
                break
            
    def start_simulation_process(self):
        if not self.input_path or not self.target_paths or not self.output_folder:
            QMessageBox.warning(self, "Missing Input", "Please set all input files and output folder.")
            return
        
        mutation_rate_str = self.ui.mutationRate.text()
        
        self.ui.loadInputBtn.setEnabled(False)
        self.ui.loadTargetBtn.setEnabled(False)
        self.ui.chooseOutputFolderBtn.setEnabled(False)
        self.ui.startBtn.setEnabled(False)

        self.ui.CancelBtn.show()
        self.closing_allowed = False

        self.process_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(
            target=simulate_multiple_cycles,
            args=(
                load_sequence_from_fasta(self.input_path),
                load_sequences_from_fasta_list(self.target_paths),
                self.ui.cyclesSpinBox.value(),
                self.ui.replicationsSpinBox.value(),
                self.ui.mutationRate.value() / 100.0,
                self.ui.subRatio.value(),
                self.ui.indelRatio.value(),
                self.ui.tranRatio.value(),
                self.ui.transvRatio.value()
            ),
            kwargs={
                'queue': self.process_queue,
                'output_folder': self.output_folder,
                'top_k': self.ui.topKSpinBox.value(),
                'mutation_rate_str': mutation_rate_str,
                'stop_event': self.stop_event
            }
        )
        self.process.start()
        self.ui.progressBar.setRange(0, 0)
    
        threading.Thread(target=self.transfer_queue_data, daemon=True).start()
        
    def closeEvent(self, event):
        if not self.closing_allowed:
            caution_box = QMessageBox(self)
            caution_box.setWindowTitle("Simulation Running")
            caution_box.setText("Cannot close the window during simulation.")
            caution_box.setIcon(QMessageBox.Information)
            ok_button = caution_box.addButton(QMessageBox.Ok)
            ok_button.setCursor(Qt.PointingHandCursor)
            ok_button.setStyleSheet("""
                QPushButton {
                    font-size: 13px;
                    font-weight: bold;
                    padding: 6px 12px;
                    min-width: 20px;
                    min-height: 10px;
                }
            """)
            caution_box.activateWindow()
            caution_box.exec()
            event.ignore()
            return
    
        event.accept()
    
    def handle_cancel(self):
        msg_box = QMessageBox(self)
        msg_box.setText("Simulation is running.\nDo you want to stop it?")
        msg_box.setWindowTitle("Stop Simulation")
        msg_box.setIcon(QMessageBox.Warning)
    
        yes_button = msg_box.addButton(QMessageBox.Yes)
        no_button = msg_box.addButton(QMessageBox.No)
        
        for button in [yes_button, no_button]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 13px;
                    font-weight: bold;
                    padding: 6px 12px;
                    min-width: 10px;
                    min-height: 5px;
                    border-radius: 6px;
                }
            """)
            
        msg_box.setDefaultButton(no_button)
        msg_box.exec()
    
        if msg_box.clickedButton() == yes_button:
            if hasattr(self, 'stop_event'):
                self.stop_event.set() 
            self.ui.CancelBtn.setEnabled(False)
            self.log("   ---------------- Stopping simulation... Please wait.----------------")
