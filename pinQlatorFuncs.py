#Dependencias
import sys
import os


#Calcula un resultado
def calcularResultado(entrada):
    entrada = entrada.replace("|", "")
    numeros = []
    signo = 1
    resultado = 0 
    numero_actual = ""

    try:
        for caracter in entrada:
            if caracter.isdigit():
                numero_actual += caracter
            elif caracter == "-":
                if not numero_actual:
                    signo = -1
                else:
                    # Si hay un número parcial almacenado, lo guardamos antes de cambiar de signo
                    numeros.append(int(numero_actual) * signo)
                    numero_actual = ""
                    signo = -1
            elif caracter == "+":
                if not numero_actual:
                    signo = 1
                else:
                    # Si hay un número parcial almacenado, lo guardamos antes de cambiar de signo
                    numeros.append(int(numero_actual) * signo)
                    numero_actual = ""
                    signo = 1
            else:
                # Si encontramos un carácter que no es dígito ni un signo, guardamos el número parcial antes de continuar
                if numero_actual:
                    numeros.append(int(numero_actual) * signo)
                    numero_actual = ""
                    signo = 1

        # Si al final de la cadena hay un número parcial, lo almacenamos
        if numero_actual:
            numeros.append(int(numero_actual) * signo)
            
            #Sumar todos los terminos
            for termino in numeros:
                resultado = resultado + termino

    except:
        resultado = 0

    return resultado


llave_bloqueo = "temp/llave.lock"
#Crear archivo de ejecucion
def crear_llave_bloqueo():
    open(llave_bloqueo, 'w').close

#Eliminar llave de ejecucion
def eliminar_llave_bloqueo():
    try:
        os.remove(llave_bloqueo)
    except OSError:
        pass

#Comprobar ejecucion
def comprobar_llave():
    return os.path.exists(llave_bloqueo)