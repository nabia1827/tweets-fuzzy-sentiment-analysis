from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QFrame,  QMenu, QAction
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QIcon, QTextCursor, QTextCharFormat

import math
import nuevo

class DonutChart(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(150, 90)
        self.angle = 180  # Ángulo inicial (apuntando hacia arriba)
        self.animation_timer = QTimer(self)
        self.porcentaje = 1
        self.animation_timer.timeout.connect(self.updateAngle)
        self.animation_duration = 3000  # Duración de la animación en milisegundos (5 segundos)
        self.animation_step = 10  # Intervalo de actualización en milisegundos
        self.animation_frame_count = self.animation_duration / self.animation_step
        self.animation_current_frame = 0
        self.color = QColor(22,141,227)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        outer_radius = int(min(rect.width(), rect.height()) * 0.4)
        center = rect.center()



        start_angle = 0
        span_angle = 180 * 16

        pen = QPen(self.color)
        pen.setWidth(0)
        painter.setPen(pen)

        painter.setBrush(QBrush(Qt.white))
        painter.drawPie(int(center.x() - outer_radius), int(center.y() - outer_radius),
                        int(outer_radius * 2), int(outer_radius * 2), start_angle, span_angle)

        inner_radius = int(outer_radius * 0.6)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(center, inner_radius, inner_radius)

        arrow_length = int(outer_radius * 0.7)
        arrow_x = center.x() + arrow_length * math.cos(math.radians(self.angle))
        arrow_y = center.y() - arrow_length * math.sin(math.radians(self.angle))

        pen = QPen(Qt.black)
        pen.setWidth(5)
        painter.setPen(pen)

        painter.setBrush(QBrush(Qt.black))
        painter.setPen(QPen(pen))
        painter.drawLine(center, QPoint(int(arrow_x), int(arrow_y)))

    def updateAngle(self):
        # Calcular el siguiente ángulo de la aguja# Gira hacia la derecha (de -90 a 90 grados)
        self.angle = 180 - ((self.porcentaje/100)*90 * self.animation_current_frame / (self.animation_frame_count / 2))

        self.update()
        self.animation_current_frame += 1

        # Detener la animación al llegar al final
        if self.animation_current_frame > self.animation_frame_count:
            self.animation_timer.stop()

    def startAnimation(self):
        # Iniciar la animación con un temporizador
        self.animation_current_frame = 0  # Reiniciar la animación
        self.animation_timer.start(self.animation_step)



class inicio(QtWidgets.QMainWindow):
    def __init__(self):
        super(inicio, self).__init__()

        uic.loadUi('Inicio.ui', self)
        central_widget = self.centralWidget()

        self.frame_clasicos = central_widget.findChild(QtWidgets.QFrame, 'clasico')
        self.frame_covid = central_widget.findChild(QtWidgets.QFrame, 'covid')

        self.frame_clasicos.mousePressEvent = self.direccionar_emotionclass
        self.frame_covid.mousePressEvent = self.direccionar_textclass

        self.frame_clasicos.installEventFilter(self)
        self.frame_covid.installEventFilter(self)


    def direccionar_emotionclass(self, event):
        self.emotionclass = emotion_class()
        self.emotionclass.show()
        self.hide()


    def direccionar_textclass(self, event):
        self.textclass = text_class()
        self.textclass.show()
        self.hide()
        

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        elif event.type() == QtCore.QEvent.Leave:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        return super().eventFilter(obj, event)


class emotion_class(QtWidgets.QMainWindow):
    def __init__(self):
        super(emotion_class, self).__init__()

        uic.loadUi('EmotionClass.ui', self)
        central_widget = self.centralWidget()

        self.tweet = self.findChild(QtWidgets.QPlainTextEdit, 'editor')
  

        # Create an instance of DonutChart
        self.donut_chart_positivo = DonutChart()
        self.donut_chart_negativo = DonutChart()
        self.donut_chart_negativo.color = QColor(17,124,213)

        # Find the 'positivo' QFrame and set it as the parent for the DonutChart
        self.positivo = self.findChild(QtWidgets.QFrame, 'positivo')
        self.donut_chart_positivo.setParent(self.positivo)
        
        self.negativo = self.findChild(QtWidgets.QFrame, 'negativo')
        self.donut_chart_negativo.setParent(self.negativo)

        # Set the geometry of the DonutChart to match the 'positivo' frame
        self.donut_chart_positivo.setGeometry(self.positivo.rect())
        self.donut_chart_negativo.setGeometry(self.negativo.rect())

        

        self.progress_bars_targets = {}
        self.progress_bars = {}

        self.progress_bars['miedo'] = self.findChild(QtWidgets.QProgressBar, 'miedo')
        self.progress_bars['ira'] = self.findChild(QtWidgets.QProgressBar, 'ira')
        self.progress_bars['anticipacion'] = self.findChild(QtWidgets.QProgressBar, 'anticipacion')
        self.progress_bars['confianza'] = self.findChild(QtWidgets.QProgressBar, 'confianza')
        self.progress_bars['sorpresa'] = self.findChild(QtWidgets.QProgressBar, 'sorpresa')
        self.progress_bars['tristeza'] = self.findChild(QtWidgets.QProgressBar, 'tristeza')
        self.progress_bars['asco'] = self.findChild(QtWidgets.QProgressBar, 'asco')
        self.progress_bars['alegria'] = self.findChild(QtWidgets.QProgressBar, 'alegria')


        self.volver = self.findChild(QtWidgets.QLabel, 'volver')
        self.calcular = self.findChild(QtWidgets.QPushButton, 'calcular')
        self.limpiar = self.findChild(QtWidgets.QPushButton, 'limpiar')

        self.volver.installEventFilter(self)
        self.calcular.installEventFilter(self)
        self.limpiar.installEventFilter(self)

        self.volver.mousePressEvent = self.clickboton_volver
        self.calcular.clicked.connect(self.clickboton_calcular)
        self.limpiar.clicked.connect(self.clickboton_limpiar)
        self.tweet.textChanged.connect(self.check_last_character)

        self.createContextMenu()


    def clickboton_volver(self, event):
        self.inicio = inicio()
        self.inicio.show()
        self.hide()


    def clickboton_calcular(self):
        
        self.donut_chart_positivo.porcentaje = 40
        self.donut_chart_positivo.startAnimation()

        self.donut_chart_negativo.porcentaje = 40
        self.donut_chart_negativo.startAnimation()

        text = self.tweet.toPlainText()
        print("Texto en QPlainTextEdit:")
        print(text)
        print("calulando")
        self.progress_bars_targets['miedo'] = 42
        self.progress_bars_targets['ira'] = 18
        self.progress_bars_targets['anticipacion'] = 18
        self.progress_bars_targets['confianza'] = 18
        self.progress_bars_targets['sorpresa'] = 38
        self.progress_bars_targets['tristeza'] = 18
        self.progress_bars_targets['asco'] = 99
        self.progress_bars_targets['alegria'] = 58

        self.start_animations()
        

    def clickboton_limpiar(self):
        self.tweet.clear()

    def start_animations(self):
        for bar_name, target_percentage in self.progress_bars_targets.items():
            self.progress_bars[bar_name].setValue(0)
            self.start_animation(bar_name, target_percentage)

    def start_animation(self, bar_name, target_percentage):
        current_percentage = 0  # El porcentaje actual
        increment = 1 if target_percentage > current_percentage else -1

        # Crea un temporizador para la animación
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.update_progress(bar_name, target_percentage, timer, increment))
        timer.start(20)  # Cambia el valor según la velocidad deseada

    def update_progress(self, bar_name, target_percentage, timer, increment):
        current_percentage = self.progress_bars[bar_name].value()

        # Incrementa o decrementa el porcentaje actual
        current_percentage += increment

        # Establece el porcentaje en el QProgressBar
        self.progress_bars[bar_name].setValue(current_percentage)

        # Detiene la animación cuando se alcanza el porcentaje deseado
        if current_percentage == target_percentage:
            timer.stop()

    def createContextMenu(self):
        self.emoji_menu = QMenu(self)

        # Agregar emojis al menú contextual
        self.addEmojiAction('😀', 'Sonrisa')
        self.addEmojiAction('😍', 'Ojos de corazon')
        self.addEmojiAction('👍', 'Me gusta')
        self.addEmojiAction('👎', 'No me gusta')

        self.emoji_menu.setStyleSheet("""
            QMenu {
                border: none;
                background-color: white;
            }
            QMenu::item {
                padding: 5px 20px; /* Ajusta el espaciado según tu preferencia */
            }
                                      
            QMenu::item:selected {
                background-color: #B2E1FF;
            }
                                      
                                      
        """)

        # Asociar el menú contextual con el QPlainTextEdit
        self.tweet.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tweet.customContextMenuRequested.connect(self.showContextMenu)


    def addEmojiAction(self, emoji, description):
        emoji_action = QAction(emoji + ' ' + description, self)
        emoji_action.setIcon(QIcon())  # Puedes proporcionar un icono personalizado si lo deseas
        emoji_action.triggered.connect(lambda _, emoji=emoji: self.insertEmoji(emoji))
        self.emoji_menu.addAction(emoji_action)

    def showContextMenu(self, pos):
        global_pos = self.tweet.mapToGlobal(pos)
        self.emoji_menu.exec_(global_pos)

    def insertEmoji(self, emoji):
        cursor = self.tweet.textCursor()
        cursor.insertText(emoji)
        self.tweet.setTextCursor(cursor)

    def check_last_character(self):
        text = self.tweet.toPlainText()
        cursor = self.tweet.textCursor()

        # Crear un formato de texto con el color azul
        format_blue = QTextCharFormat()
        format_blue.setForeground(QColor(27, 157, 240))  # Color azul

        format_back = QTextCharFormat()
        format_back.setForeground(QColor(0, 0, 0))  # Color negro

        # Verificar si el último carácter es "#" y cambiar su color
        if text.endswith("#"):
            # Desactivar temporalmente la señal textChanged
            self.tweet.textChanged.disconnect(self.check_last_character)
            cursor.deletePreviousChar()
            cursor.movePosition(QTextCursor.End)
            cursor.setCharFormat(format_blue)
            cursor.insertText("#a", format_blue)
            cursor.deletePreviousChar()
            # Reactivar la señal textChanged
            self.tweet.textChanged.connect(self.check_last_character)
            
        elif text.endswith(" "):
            self.tweet.textChanged.disconnect(self.check_last_character)
            cursor.deletePreviousChar()
            cursor.movePosition(QTextCursor.End)
            cursor.setCharFormat(format_back)
            cursor.insertText(" ", format_back)            # Reactivar la señal textChanged
            self.tweet.textChanged.connect(self.check_last_character)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        elif event.type() == QtCore.QEvent.Leave:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            
        return super().eventFilter(obj, event)





class text_class(QtWidgets.QMainWindow):
    def __init__(self):
        super(text_class, self).__init__()

        uic.loadUi('TextClass.ui', self)
        central_widget = self.centralWidget()

        self.tweet = self.findChild(QtWidgets.QPlainTextEdit, 'editor')

        self.volver = self.findChild(QtWidgets.QLabel, 'volver')
        self.resultado = self.findChild(QtWidgets.QLabel, 'result_final')
        
        
        
        self.calcular = self.findChild(QtWidgets.QPushButton, 'calcular')
        self.limpiar = self.findChild(QtWidgets.QPushButton, 'limpiar')

        self.calcular.installEventFilter(self)
        self.limpiar.installEventFilter(self)

        self.volver.installEventFilter(self)
        self.calcular.installEventFilter(self)
        self.limpiar.installEventFilter(self)

        self.volver.mousePressEvent = self.clickboton_volver
        self.calcular.clicked.connect(self.clickboton_calcular)
        self.limpiar.clicked.connect(self.clickboton_limpiar)

        self.progress_bars_targets = {}
        self.progress_bars = {}
        self.labels_bar = {}
        
        self.labels_bar['dem_relev'] = self.findChild(QtWidgets.QLabel, 'relevante')
        self.labels_bar['muy_relev'] = self.findChild(QtWidgets.QLabel, 'm_relevante')
        self.labels_bar['med_relev'] = self.findChild(QtWidgets.QLabel, 'med_relevante')
        self.labels_bar['poco_relev'] = self.findChild(QtWidgets.QLabel, 'poco_relevante')
        self.labels_bar['irrelevante'] = self.findChild(QtWidgets.QLabel, 'Irrelevante')



        self.progress_bars['dem_relev'] = self.findChild(QtWidgets.QProgressBar, 'demrelevante')
        self.progress_bars['muy_relev'] = self.findChild(QtWidgets.QProgressBar, 'muyrelevante')
        self.progress_bars['med_relev'] = self.findChild(QtWidgets.QProgressBar, 'mediana_relevante')
        self.progress_bars['poco_relev'] = self.findChild(QtWidgets.QProgressBar, 'pocorelevante')
        self.progress_bars['irrelevante'] = self.findChild(QtWidgets.QProgressBar, 'p_irrelevante')


        self.dem_reser = self.findChild(QtWidgets.QLabel, 'volver')
        self.createContextMenu()
        self.tweet.textChanged.connect(self.check_last_character)



    def clickboton_volver(self, event):
        self.inicio = inicio()
        self.inicio.show()
        self.hide()

    def clickboton_calcular(self):

        print("holitas")
        self.progress_bars_targets['dem_relev'] = 42
        self.progress_bars_targets['muy_relev'] = 18
        self.progress_bars_targets['med_relev'] = 18
        self.progress_bars_targets['poco_relev'] = 18
        self.progress_bars_targets['irrelevante'] = 38


        self.start_animations()

        self.resultado.setText("Poco Relevante")


    def clickboton_limpiar(self):
        self.tweet.clear()
    

    def start_animations(self):
        for bar_name, target_percentage in self.progress_bars_targets.items():
            self.progress_bars[bar_name].setValue(0)
            self.start_animation(bar_name, target_percentage)

    def start_animation(self, bar_name, target_percentage):
        current_percentage = 0  # El porcentaje actual
        increment = 1 if target_percentage > current_percentage else -1

        # Crea un temporizador para la animación
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.update_progress(bar_name, target_percentage, timer, increment))
        timer.start(20)  # Cambia el valor según la velocidad deseada

    def update_progress(self, bar_name, target_percentage, timer, increment):
        current_percentage = self.progress_bars[bar_name].value()

        # Incrementa o decrementa el porcentaje actual
        current_percentage += increment

        # Establece el porcentaje en el QProgressBar
        self.progress_bars[bar_name].setValue(current_percentage)
        self.labels_bar[bar_name].setText(str(current_percentage))



        # Detiene la animación cuando se alcanza el porcentaje deseado
        if current_percentage == target_percentage:
            timer.stop()


    def createContextMenu(self):
        self.emoji_menu = QMenu(self)

        # Agregar emojis al menú contextual
        self.addEmojiAction('😀', 'Sonrisa')
        self.addEmojiAction('😍', 'Ojos de corazon')
        self.addEmojiAction('👍', 'Me gusta')
        self.addEmojiAction('👎', 'No me gusta')

        self.emoji_menu.setStyleSheet("""
            QMenu {
                border: none;
                background-color: white;
            }
            QMenu::item {
                padding: 5px 20px; /* Ajusta el espaciado según tu preferencia */
            }
                                      
            QMenu::item:selected {
                background-color: #B2E1FF;
            }
                                      
                                      
        """)

        # Asociar el menú contextual con el QPlainTextEdit
        self.tweet.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tweet.customContextMenuRequested.connect(self.showContextMenu)


    def addEmojiAction(self, emoji, description):
        emoji_action = QAction(emoji + ' ' + description, self)
        emoji_action.setIcon(QIcon())  # Puedes proporcionar un icono personalizado si lo deseas
        emoji_action.triggered.connect(lambda _, emoji=emoji: self.insertEmoji(emoji))
        self.emoji_menu.addAction(emoji_action)

    def showContextMenu(self, pos):
        global_pos = self.tweet.mapToGlobal(pos)
        self.emoji_menu.exec_(global_pos)

    def insertEmoji(self, emoji):
        cursor = self.tweet.textCursor()
        cursor.insertText(emoji)
        self.tweet.setTextCursor(cursor)


    def check_last_character(self):
        text = self.tweet.toPlainText()
        cursor = self.tweet.textCursor()

        # Crear un formato de texto con el color azul
        format_blue = QTextCharFormat()
        format_blue.setForeground(QColor(27, 157, 240))  # Color azul

        format_back = QTextCharFormat()
        format_back.setForeground(QColor(0, 0, 0))  # Color negro

        # Verificar si el último carácter es "#" y cambiar su color
        if text.endswith("#"):
            # Desactivar temporalmente la señal textChanged
            self.tweet.textChanged.disconnect(self.check_last_character)
            cursor.deletePreviousChar()
            cursor.movePosition(QTextCursor.End)
            cursor.setCharFormat(format_blue)
            cursor.insertText("#a", format_blue)
            cursor.deletePreviousChar()
            # Reactivar la señal textChanged
            self.tweet.textChanged.connect(self.check_last_character)
            
        elif text.endswith(" "):
            self.tweet.textChanged.disconnect(self.check_last_character)
            cursor.deletePreviousChar()
            cursor.movePosition(QTextCursor.End)
            cursor.setCharFormat(format_back)
            cursor.insertText(" ", format_back)            # Reactivar la señal textChanged
            self.tweet.textChanged.connect(self.check_last_character)
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        elif event.type() == QtCore.QEvent.Leave:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            
        return super().eventFilter(obj, event)

    
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ventana = inicio()
    ventana.show()
    app.exec()