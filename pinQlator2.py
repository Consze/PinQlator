from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import QTimer,QStringListModel
from PyQt5.QtWidgets import QApplication
import pinQlatorFuncs as pfs
import sqlite3,socket
from datetime import datetime

#Iniciar interfaz
class GUI(QMainWindow):
    def __init__(self):
        #Cargar interfaz
        super(GUI,self).__init__()
        ui = uic.loadUi('ui/interfaz.ui',self)

        #Variables de clase
        self.llave_bloqueo = "temp/llave.lock"

        # Cargar el archivo CSS
        css = "ui/estilo.css"
        with open(css, "r") as f:
            hoja_estilo = f.read()
        ui.setStyleSheet(hoja_estilo)
        self.conn = sqlite3.connect("datos.db")
        self.setWindowIcon(QIcon("ui/logo.png"))
        self.show()

        #Conectar botones
        self.grilla_1.clicked.connect(lambda: self.entradaNumero("1"))
        self.grilla_2.clicked.connect(lambda: self.entradaNumero("2"))
        self.grilla_3.clicked.connect(lambda: self.entradaNumero("3"))
        self.grilla_4.clicked.connect(lambda: self.entradaNumero("4"))
        self.grilla_5.clicked.connect(lambda: self.entradaNumero("5"))
        self.grilla_6.clicked.connect(lambda: self.entradaNumero("6"))
        self.grilla_7.clicked.connect(lambda: self.entradaNumero("7"))
        self.grilla_8.clicked.connect(lambda: self.entradaNumero("8"))
        self.grilla_9.clicked.connect(lambda: self.entradaNumero("9"))
        self.grilla_suma.clicked.connect(lambda: self.entradaNumero("+"))
        self.grilla_resta.clicked.connect(lambda: self.entradaNumero("-"))
        self.ver_historial.clicked.connect(lambda: self.mostrar_historial())

        #Calculo
        self.ventana_historial = None
        nombre_computadora = socket.gethostname()
        fecha_actual = datetime.now()
        fecha_actual_str = fecha_actual.strftime('%Y-%m-%d')  # Formato: AAAA-MM-DD
        hora_actual_str = fecha_actual.strftime('%H:%M:%S')  # Formato: HH:MM:SS
        self.grilla_resultado.clicked.connect(lambda: self.almacenarItem((self.pantalla_2.text()).replace("|",""),fecha_actual_str,hora_actual_str,nombre_computadora))
        self.grilla_resultado.clicked.connect(lambda: self.mostrarResultado())

        #Crear temporizador
        self.cursor_visible = True
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.actualizarPantalla())
        self.timer.start(500)  # Actualizar cada 500 milisegundos (0.5 segundos)
            
        #Crear tabla de resultados en db  
        self.crearTablaResultados()

    #Crear tabla de resultados en db
    def crearTablaResultados(self):
        cursor = self.conn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resultado TEXT,
            fecha TEXT,
            hora TEXT,
            computadora TEXT
        )
        """
        #Ejecutar Query
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
        
    #Escribir en pantalla
    def entradaNumero(self, entrada):
        operadores = ["+","-","/","x"]
        estadoAnterior = str(self.pantalla_2.text())
        if (estadoAnterior[len(estadoAnterior)-1] in operadores) and (entrada in operadores):
            pass
        else:
            if estadoAnterior == "0" or estadoAnterior =="|0":
                estadoAnterior = ""
            elif (estadoAnterior[0] == "+" and len(estadoAnterior) > 1):
                estadoAnterior = estadoAnterior[1:len(estadoAnterior)]
            self.pantalla_2.setText(estadoAnterior + entrada)  

    #Escribir el resultado en pantalla
    def mostrarResultado(self):
        resultado = str(pfs.calcularResultado(self.pantalla_2.text()))
        self.pantalla_2.setText(resultado)

    #Animacion de cursor
    def actualizarPantalla(self):
        self.cursor_visible = not self.cursor_visible
        textoPrevio = self.pantalla_2.text()
        textoPrevio = textoPrevio.replace("|","")
        if self.cursor_visible:
            self.pantalla_2.setText("|" + textoPrevio)
        else:
            self.pantalla_2.setText(textoPrevio)
        
    #Almacenar item en db
    def almacenarItem(self,calculo,fecha,hora,computadora):
        cursor = self.conn.cursor()
        SQL = """ INSERT INTO resultados
            (resultado, fecha, hora, computadora)
            VALUES (?, ?, ?, ?)
        """
        parametros = (calculo,fecha,hora,computadora)
        cursor.execute(SQL,parametros)
        self.conn.commit()
        cursor.close()

    #Mostrar historial
    def mostrar_historial(self):
        self.ventana_historial = historial()
        self.ventana_historial.show()

    #Cerrar programa
    def closeEvent(self, event):
        try:
            pfs.os.remove(self.llave_bloqueo)
        finally:
            self.conn.close()
            event.accept()

#Historial
class historial(QMainWindow):
    def __init__(self):
        #Iniciar Ventana
        super(historial,self).__init__()
        ui_hist = uic.loadUi("ui/historial.ui",self)
        self.setWindowTitle("Historial")
        #CSS
        css = "ui/estilo.css"
        with open(css, "r") as f:
            hoja_estilo = f.read()
        ui_hist.setStyleSheet(hoja_estilo)

        #Conectar a db
        conn = sqlite3.connect("datos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resultados")
        columnas = cursor.fetchall()
        conn.close()

        #Procesar datos 
        data = QStandardItemModel()
        for columna in columnas:
            item = ""
            for posicion, nombre_columna in enumerate(cursor.description):
                valor_columna = columna[posicion]
                item += ", " + str(valor_columna) if len(item) > 1 else str(valor_columna)
            data.appendRow(QStandardItem(str(item)))

        #Cargar modelo de datos en lista
        self.lista.setModel(data)

#Control de excepciones
def control_excepcion(excepcion, borrar_llave):
    if borrar_llave:
        pfs.eliminar_llave_bloqueo()
    appAux = QApplication([])
    error = f"{str(excepcion)}"
    QMessageBox.critical(None, "Error", error)
    pfs.sys.exit(0)

#Secuencia de inicio
def main():
    try:
        app = QApplication([])
        window = GUI()
        app.setWindowIcon(window.windowIcon())
        pfs.sys.exit(app.exec_())
    except Exception as excepcion:
        control_excepcion(excepcion,True)


#-------------------------PROGRAMA PRINCIPAL-----------------------------
if __name__ == '__main__':
    llave_bloqueo = "temp/llave.lock"
    try:
        if pfs.comprobar_llave():
            control_excepcion("El programa ya esta abierto",False)
        else:
            open(llave_bloqueo, 'w').close()
            main()  
    except Exception as excepcion:
        control_excepcion(excepcion,True)