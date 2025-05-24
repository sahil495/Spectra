# i want to create a report of my project in which i want to excitidly show that after a working of different AI project i wanted to create something amazing or attractive then i create Spectra there are 7 profesional color anda their shades 100 of each i want to describe all core concepts of my project report should be easy to understand , professional ,attractive 
import os
import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QDialog, QLabel, QSpinBox, QCheckBox, QPushButton,
                             QGridLayout, QScrollArea, QFileDialog,QStyleOptionButton, 
                             QHBoxLayout,QStyle, QRadioButton, QButtonGroup,QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QPoint
from PyQt5.QtGui import (QColor, QPainter, QLinearGradient, QBrush, QFont, 
                        QFontMetrics, QPen, QConicalGradient)
        
import pyttsx3
        

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ColorCheckBox(QCheckBox):
    def __init__(self, color_name, color, parent=None):
        super().__init__(parent)
        self.color_name = color_name
        self.color = color
        self.setFixedSize(100, 40)  # थोड़ा बड़ा size
        self.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
            }
        """)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the checkbox indicator
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.rect = QRect(5, 10, 20, 20)
        self.style().drawPrimitive(QStyle.PE_IndicatorCheckBox, opt, painter, self)
        
        # Draw the color box with shadow effect
        color_rect = QRect(35, 5, 60, 30)
        
        # Shadow effect
        shadow = QColor(0, 0, 0, 100)
        painter.setPen(Qt.NoPen)
        painter.setBrush(shadow)
        painter.drawRoundedRect(color_rect.translated(2, 2), 5, 5)
        
        # Main color box
        painter.setBrush(self.color)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRoundedRect(color_rect, 5, 5)
        
        # Draw the color name with better styling
        font = QFont('Calibri', 14, QFont.Bold)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        elided_text = metrics.elidedText(self.color_name, Qt.ElideRight, 55)
        
        # Text shadow for better visibility
        painter.setPen(QColor(0, 0, 0, 150))
        painter.drawText(color_rect.adjusted(1, 1, 1, 1), Qt.AlignCenter, elided_text)
        
        # Main text
        text_color = Qt.black if self.color.lightness() > 150 else Qt.white
        painter.setPen(text_color)
        painter.drawText(color_rect, Qt.AlignCenter, elided_text)
        

class ColorTransitionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = []
        self.current_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_color)
        self.animation_duration = 3000  # 3 seconds per transition
        self.grid_rows = 1
        self.grid_cols = 5
        self.selected_shades = set()
        self.cell_states = {}  # Track animation state for each cell
        self.transition_directions = ['lr', 'rl', 'tb', 'bt']  # Possible directions
        self.active_cell = None  # Currently transitioning cell
        self.next_cell = (0, 0)  # Next cell to transition (start with 0,0)
        self.initial_display_done = False  # Flag for initial display
        self.speech_engine = self.init_speech_engine()
        
        
        
                
    def load_colors_from_file(self, filename):
        colors = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    if ' - ' in line:
                        name, hex_code = line.split(' - ')
                    else:
                        parts = line.rsplit(' ', 1)
                        if len(parts) == 2:
                            name, hex_code = parts
                        else:
                            continue
                    
                    name = name.strip()
                    hex_code = hex_code.strip()
                    
                    if QColor.isValidColor(hex_code):
                        colors.append((name, QColor(hex_code)))
        except Exception as e:
            print(f"Error loading colors from {filename}: {e}")
        return colors
    
    def load_all_shades(self, directory):
        self.all_shades = {}
        shade_files = {
            'blues': 'blues_shades.txt',
            'greens': 'green_shades.txt',
            'indigos': 'indigo_shades.txt',
            'oranges': 'orange_shades.txt',
            'reds': 'red_shades.txt',
            'violets': 'violet_shades.txt',
            'yellows': 'yellow_shades.txt'
        }
        
        for shade_name, filename in shade_files.items():
            # Use resource_path to handle both development and executable modes
            filepath = resource_path(filename)
            if os.path.exists(filepath):
                self.all_shades[shade_name] = self.load_colors_from_file(filepath)
            else:
                print(f"Warning: Color file not found - {filepath}")
    
    def set_colors(self, colors):
        self.colors = colors
        self.current_index = 0
        self.cell_states = {}  # Reset cell states
        self.active_cell = None
        self.next_cell = (0, 0)  # Reset to start from (0,0) again
        self.initial_display_done = False
        
        if self.colors:
            # Initialize all cells with unique colors initially
            color_indices = list(range(len(self.colors)))
            random.shuffle(color_indices)
            
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    if color_indices:  # If we have enough colors
                        color_idx = color_indices.pop()
                    else:  # If we have more cells than colors, start repeating
                        color_idx = random.randint(0, len(self.colors)-1)
                    
                    self.cell_states[(row, col)] = {
                        'progress': 1.0,  # Fully shown
                        'direction': random.choice(self.transition_directions),
                        'current_color_idx': color_idx,
                        'next_color_idx': (color_idx + 1) % len(self.colors),
                        'transitioning': False
                    }
            
            # After a delay, start transitioning
            QTimer.singleShot(1000, self.start_transitions)
    
    def start_transitions(self):
        self.initial_display_done = True
        self.start_next_transition()
    
    def start_next_transition(self):
        # Find the next cell to transition
        if self.active_cell is None:
            # Start from (0,0) if no active cell
            next_row, next_col = 0, 0
        else:
            # Move to next cell in row-major order
            current_row, current_col = self.active_cell
            next_col = current_col + 1
            next_row = current_row
            if next_col >= self.grid_cols:
                next_col = 0
                next_row += 1
                if next_row >= self.grid_rows:
                    next_row = 0
        
        # Set the next cell to transition
        self.next_cell = (next_row, next_col)
        
        # Only start transition if we have colors
        if self.colors:
            self.active_cell = self.next_cell
            cell_state = self.cell_states[self.active_cell]
            cell_state['transitioning'] = True
            cell_state['progress'] = 0
            cell_state['direction'] = random.choice(self.transition_directions)
            
            # Choose a new random color (different from current)
            current_idx = cell_state['current_color_idx']
            available_indices = [i for i in range(len(self.colors)) if i != current_idx]
            cell_state['next_color_idx'] = random.choice(available_indices)
            
            # Start the transition animation
            self.timer.start(12)  # ~60fps animation (16ms per frame)

    def init_speech_engine(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            # Add this line to enable proper event handling:
            engine.connect('finished-utterance', self.on_speech_finished)
            return engine
        except Exception as e:
            print(f"Error initializing speech engine: {e}")
            return None

    def on_speech_finished(self, name, completed):
        
        if completed:
            QTimer.singleShot(500, self.start_next_transition)  # Small delay after speech

    def speak_color_name(self, name):
        if self.speech_engine:
            try:
                self.speech_engine.stop()
                # Speak with a unique utterance ID
                self.speech_engine.say(name, 'color_name')
                self.speech_engine.runAndWait()  # Non-blocking
            except Exception as e:
                print(f"Error speaking color name: {e}")
                QTimer.singleShot(1000, self.start_next_transition)
        else:
            QTimer.singleShot(1000, self.start_next_transition)

    def next_color(self):
        if not self.colors or self.active_cell is None:
            return
            
        cell_state = self.cell_states[self.active_cell]
        cell_state['progress'] += 0.008
        
        if cell_state['progress'] >= 1.0:
            cell_state['progress'] = 1.0
            old_color_idx = cell_state['current_color_idx']
            cell_state['current_color_idx'] = cell_state['next_color_idx']
            cell_state['transitioning'] = False
            self.timer.stop()
            
            self.update()
            
            if old_color_idx != cell_state['current_color_idx']:
                color_name = self.colors[cell_state['current_color_idx']][0]
                self.speak_color_name(color_name)
        
        self.update()
        
    def closeEvent(self, event):
        if hasattr(self, 'speech_engine') and self.speech_engine:
            self.speech_engine.stop()
        super().closeEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.colors:
            return
            
        # Calculate cell size based on grid configuration
        cell_width = int(self.width() / self.grid_cols)
        cell_height = int(self.height() / self.grid_rows)
        
        # Draw each cell in the grid
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x = col * cell_width
                y = row * cell_height
                rect = QRect(int(x), int(y), cell_width, cell_height)
                
                # Get cell state
                state = self.cell_states.get((row, col), {
                    'progress': 1.0,
                    'direction': 'lr',
                    'current_color_idx': 0,
                    'next_color_idx': 1,
                    'transitioning': False
                })
                
                # Get colors and names for this cell
                current_color = self.colors[state['current_color_idx']][1]
                next_color = self.colors[state['next_color_idx']][1]
                current_name = self.colors[state['current_color_idx']][0]
                next_name = self.colors[state['next_color_idx']][0]
                
                # Draw the cell
                if state['transitioning']:
                    # Draw transitioning cell with animation
                    self.draw_transitioning_cell(painter, rect, current_color, next_color,
                                            state['progress'], state['direction'],
                                            current_name, next_name)
                else:
                    # Draw static cell
                    self.draw_static_cell(painter, rect, current_color, current_name)
                    
    
    def draw_transitioning_cell(self, painter, rect, current_color, next_color, progress, direction, current_name, next_name):
        # Create rectangles for outgoing and incoming colors
        outgoing_rect = QRect(rect)
        incoming_rect = QRect(rect)
        
        # Calculate positions based on direction
        if direction == 'lr':  # Left to right
            outgoing_rect.setWidth(int(rect.width() * (1 - progress)))
            incoming_rect.setLeft(int(rect.left() + rect.width() * (1 - progress)))
        elif direction == 'rl':  # Right to left
            outgoing_rect.setLeft(int(rect.left() + rect.width() * progress))
            incoming_rect.setRight(int(rect.left() + rect.width() * progress))
        elif direction == 'tb':  # Top to bottom
            outgoing_rect.setHeight(int(rect.height() * (1 - progress)))
            incoming_rect.setTop(int(rect.top() + rect.height() * (1 - progress)))
        else:  # Bottom to top
            outgoing_rect.setTop(int(rect.top() + rect.height() * progress))
            incoming_rect.setBottom(int(rect.top() + rect.height() * progress))
        
        # Draw outgoing color with its name
        painter.fillRect(outgoing_rect, current_color)
        self.draw_text_in_rect(painter, outgoing_rect, current_name)
        
        # Draw incoming color with its name
        painter.fillRect(incoming_rect, next_color)
        self.draw_text_in_rect(painter, incoming_rect, next_name)

    def draw_text_in_rect(self, painter, rect, text):
        # Always use black text with white shadow for maximum contrast
        font = QFont('Arial', 16, QFont.Bold)  # Larger, bolder font
        painter.setFont(font)
        
        # Text shadow for better visibility
        shadow_rect = QRect(rect.x()+1, rect.y()+1, rect.width(), rect.height())
        painter.setPen(QColor(255, 255, 255, 150))  # White shadow
        painter.drawText(shadow_rect, Qt.AlignCenter, text)
        
        # Main black text
        painter.setPen(Qt.black)
        painter.drawText(rect, Qt.AlignCenter, text)

    def draw_static_cell(self, painter, rect, color, color_name):
        # Draw solid color background
        painter.fillRect(rect, QBrush(color))
        self.draw_text_in_rect(painter, rect, color_name)
    
    def draw_cell_text(self, painter, rect, text, bg_color):
        # Always use black text
        painter.setPen(QPen(Qt.black))
        font = QFont('Calibri', 14)
        painter.setFont(font)
        
        # Center the text in the cell
        text_rect = QRect(rect)
        text_rect.adjust(5, 5, -5, -5)  # Add some padding
        
        # Use elided text if name is too long
        metrics = QFontMetrics(font)
        elided_text = metrics.elidedText(text, Qt.ElideRight, text_rect.width())
        painter.drawText(text_rect, Qt.AlignCenter, elided_text)
        

class ColorToggleButton(QPushButton):
    def __init__(self, color, name, parent=None):
        super().__init__(parent)
        self.color = color
        self.name = name
        self.setCheckable(True)
        self.setFixedSize(50, 50)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid black;
                border-radius: 5px;
            }}
            QPushButton:checked {{
                border: 4px solid #0066FF;
            }}
        """)
        
        
class ConfigDialog(QDialog):
    def __init__(self, all_shades, selected_shades, current_rows, current_cols, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Grid and Colors")
        self.setModal(True)
        self.setMinimumSize(600, 300)
        self.all_shades = all_shades
        self.selected_shades = selected_shades
        self.current_rows = current_rows
        self.current_cols = current_cols
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        # Grid configuration section
        self.create_grid_config_section(main_layout)
        
        # Color selection section
        self.create_color_selection_section(main_layout)
        
        # Button section
        self.create_button_section(main_layout)
        
        self.setLayout(main_layout)
        self.setStyleSheet(self.get_dialog_stylesheet())
    
    def create_grid_config_section(self, parent_layout):
        grid_group = QGroupBox("Grid Configuration")
        grid_group.setObjectName("configGroup")
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(15)
        
        # Rows selection
        rows_group = QGroupBox("Rows")
        rows_group.setObjectName("subGroup")
        rows_layout = QHBoxLayout()
        rows_layout.setContentsMargins(10, 15, 10, 10)
        self.rows_group = QButtonGroup(self)
        
        for i in range(1, 6):
            rb = QRadioButton(str(i))
            rb.setObjectName("gridRadio")
            self.rows_group.addButton(rb, i)
            rows_layout.addWidget(rb, alignment=Qt.AlignCenter)
            if i == self.current_rows:  # Set current selection
                rb.setChecked(True)
        
        rows_group.setLayout(rows_layout)
        grid_layout.addWidget(rows_group)
        
        # Columns selection
        cols_group = QGroupBox("Columns")
        cols_group.setObjectName("subGroup")
        cols_layout = QHBoxLayout()
        cols_layout.setContentsMargins(10, 15, 10, 10)
        self.cols_group = QButtonGroup(self)
        
        for i in range(1, 6):
            rb = QRadioButton(str(i))
            rb.setObjectName("gridRadio")
            self.cols_group.addButton(rb, i)
            cols_layout.addWidget(rb, alignment=Qt.AlignCenter)
            if i == self.current_cols:  # Set current selection
                rb.setChecked(True)
        
        cols_group.setLayout(cols_layout)
        grid_layout.addWidget(cols_group)
        
        grid_group.setLayout(grid_layout)
        parent_layout.addWidget(grid_group)
    
    def create_color_selection_section(self, parent_layout):
        color_group = QGroupBox("Select Color Shades")
        color_group.setObjectName("configGroup")
        
        # Create a horizontal layout for the color buttons
        color_buttons_layout = QHBoxLayout()
        color_buttons_layout.setContentsMargins(10, 5, 10, 5)
        color_buttons_layout.setSpacing(50)
        
        # Define the specific colors to show for each shade group
        color_map = {
            'blues': '#1a91ff',
            'greens': '#28b670',
            'indigos': '#3f51b5',
            'oranges': '#ff9800',
            'reds': '#f44336',
            'violets': '#9c27b0',
            'yellows': '#ffeb3b'
        }
        
        self.color_buttons = {}
        
        for shade_name in sorted(self.all_shades.keys()):
            if shade_name in color_map:
                btn_color = color_map[shade_name]
                
                # Create the color button
                btn = QPushButton()
                btn.setCheckable(True)
                btn.setFixedSize(50, 50)
                btn.setChecked(shade_name in self.selected_shades)
                btn.setObjectName("colorButton")
                btn.setToolTip(shade_name.capitalize())  # Show name as tooltip
                # Set button style with our predefined color
                btn.setStyleSheet(f"""
                    QPushButton#colorButton {{
                        background-color: {btn_color};
                        border: 2px solid #333;
                        border-radius: 20px;
                    }}
                    QPushButton#colorButton:checked {{
                        border: 4px solid #0066FF;
                        background-color: {btn_color};
                    }}
                """)
                
                self.color_buttons[shade_name] = btn
                color_buttons_layout.addWidget(btn)
                
        # Add stretch to push buttons to the left
        color_buttons_layout.addStretch()
        
        # Create a container widget for the scroll area
        container = QWidget()
        container.setLayout(color_buttons_layout)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll.setStyleSheet("""
            QScrollArea {
                border-radius: 5px;
                background: black;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        # Add to the group box layout
        group_layout = QVBoxLayout(color_group)
        group_layout.addWidget(scroll)
        
        # Add to parent layout
        parent_layout.addWidget(color_group)
        
    def create_button_section(self, parent_layout):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okButton")
        ok_btn.setFixedSize(120, 40)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(120, 40)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        
        parent_layout.addLayout(btn_layout)
    
    def get_dialog_stylesheet(self):
        return """
            QDialog {
                background-color: black;
                color: white;
                font-family: 'Segoe UI', 'Arial';
                font-size: 18px;
            }

            QGroupBox#configGroup {
                font: bold 18px 'Segoe UI';
                color: white;
                border: 1px solid #333;
                border-radius: 6px;
                margin-top: 10px;
                background-color: black;
            }

            QGroupBox#configGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color:white;
                background-color: black;
            }

            QGroupBox#subGroup {
                font: 18px 'Segoe UI';
                color: white;
                border: 1px solid #2a2a2a;
                border-radius: 5px;
                margin-top: 6px;
                background-color: black;
                padding: 6px;
            }

            QGroupBox#subGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 4px;
            }

            QRadioButton#gridRadio {
                font: 18px 'Segoe UI';
                color: white;
                spacing: 4px;
            }

            QRadioButton#gridRadio::indicator {
                width: 18px;
                height: 18px;
            }

            QPushButton#okButton, QPushButton#cancelButton {
                font: bold 18px 'Segoe UI';
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
                
            }

            QPushButton#okButton {
                background-color: #2e7d32;
                color: white;
            }

            QPushButton#okButton:hover {
                background-color: #388e3c;
            }

            QPushButton#okButton:pressed {
                background-color: #1b5e20;
            }

            QPushButton#cancelButton {
                background-color: #c62828;
                color: white;
            }

            QPushButton#cancelButton:hover {
                background-color: #d32f2f;
            }

            QPushButton#cancelButton:pressed {
                background-color: #b71c1c;
            }
        """

    
    def get_values(self):
        rows = self.rows_group.checkedId()
        cols = self.cols_group.checkedId()
        selected = [name for name, btn in self.color_buttons.items() if btn.isChecked()]
        return rows, cols, selected    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Transition Visualizer")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget setup
        self.central_widget = ColorTransitionWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize with default colors and grid
        self.all_shades = {}
        self.selected_shades = set()
        self.central_widget.grid_rows = 2  # Default rows
        self.central_widget.grid_cols = 2  # Default columns
        self.load_default_colors()
        
        # Start with some default shades
        self.update_displayed_colors()
    
    def load_default_colors(self):
        self.central_widget.load_all_shades(".")  # Load from current directory
        self.selected_shades = {'blues', 'reds', 'greens'}
    
    def update_displayed_colors(self):
        colors = []
        for shade_name in self.selected_shades:
            if shade_name in self.central_widget.all_shades:
                colors.extend(self.central_widget.all_shades[shade_name])
        
        if colors:
            self.central_widget.set_colors(colors)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            self.show_config_dialog()
        else:
            super().keyPressEvent(event)
    
    def show_config_dialog(self):
        dialog = ConfigDialog(
            self.central_widget.all_shades, 
            self.selected_shades,
            self.central_widget.grid_rows,  # Current rows
            self.central_widget.grid_cols,   # Current columns
            self
        )
        if dialog.exec_() == QDialog.Accepted:
            rows, cols, selected = dialog.get_values()
            self.central_widget.grid_rows = rows
            self.central_widget.grid_cols = cols
            self.selected_shades = set(selected)
            self.update_displayed_colors()

    
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        # Print current working directory and verify files
        print(f"Current directory: {os.getcwd()}")
        print("Checking for color files:")
        for f in ['blues_shades.txt', 'green_shades.txt', 'indigo_shades.txt',
                 'orange_shades.txt', 'red_shades.txt', 'violet_shades.txt',
                 'yellow_shades.txt']:
            print(f"- {f}: {'Found' if os.path.exists(resource_path(f)) else 'Missing'}")
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if sys.platform == "win32":
            input("Press Enter to exit...")
        sys.exit(1)