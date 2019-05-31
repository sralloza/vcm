# Instrucciones de instalación
Hay dos modos de instalación: la instalación normal y la instalación en un entorno virtual. Para ambas necesitan tener Python 3.6+ instalado. Si tienes más proyectos en Python instalador, lo mejor sería que optaras por la instalación en un entorno virtual. Si no, podrías conformarte con la instalación general.

Estaré trabajando en hacer el proceso de instalación más sencillo, e incluso reducirlo a un único ejecutable.

### Instalación en un entorno virtual

1. Descargar este repositorio de github (con git clone).
2. Crear una carpeta (donde sea) y añadirla al `%PATH%`.
3. Dentro de dicha carpeta, crear un fichero llamado `vcd.cmd`, con este contenido:
~~~
@echo off
[RUTA_CARPETA_CLONADA]/venv/Scripts/python.exe [RUTA_CARPETA_CLONADA]/cli.py %*
~~~

4. A continuación, dentro de la carpeta ejecutar el comando `virtualenv venv` para crear el entorno virtual.
5. Ejecutar el comando `"venv/scripts/activate.bat"` para activar el entorno virtual.
6. Para instalar todas las dependencias, usar el comando `python -m pip install -r requirements.txt --upgrade`.


### Instalación general
1. Descargar este repositorio de github (con git clone).
2. Crear una carpeta (donde sea) y añadirla al `%PATH%`.
3. Dentro de dicha carpeta, crear un fichero llamado `vcd.cmd`, con este contenido:
~~~
@echo off
python.exe [RUTA_CARPETA_CLONADA]/cli.py %*
~~~

4. Para instalar todas las dependencias, usar el comando `python -m pip install -r requirements.txt --upgrade`.

#Instrucciones de uso:

Al ejecutar el programa por primera vez, se crearán los ficheros de configuración y de credenciales, que están alojados en `%USER%/vcd-config.ini` y `%USER%/vcd-credentials.ini`, respectivamente.


##Ficheros de configuración
`vcd-credentials.ini` tiene sólo 2 líneas, en las que se especifica el usuario y contraseña del [campus virtual](https://www.campusvirtualuva.es).

`vcd-config.ini` tiene varias líneas:

- `root_folder` especifica la ruta absoluta de la carpeta donde se descargarán todos los ficheros. Si no existe dicha carpeta se creará.
- `timeout` configura el tiempo durante el cual se esperará a las peticiones HTTP. Si una petición sobrepasa ese tiempo, se repetirá la petición.
- `log_folder` te permite configurar la carpeta donde se guardarán los ficheros de log.
- `logging_level` te permite especificar el nivel de log (DEBUG, INFO, WARNING, ERROR y CRITICAL).


## Argumentos CLI (Command Line Interface)

El programa acepta los siguientes argumentos:

* `--root-folder FOLDER` permite especificar otra carpeta raíz (carpeta donde se descargarán los ficheros) distinta de la especificada en el fichero de configuración.
* `--nthreads N` permite especificar el número de hilos (threads) que descargarán ficheros simultáneamente. El número predeterminado es `50`.
* `--no-killer` evita que se inicie el hilo **killer**, que se encarga de esperar a que el usuario inserte una `q` por el teclado para mandar una orden al resto de hilos para que se apaguen (`Ctrl+C` no funciona).
* `-d` ó `--debug` abre el navegador la url ***localhost***. No se ha especificado antes, pero VCD viene integrado con un mecanismo de supervisión, que consiste en un servidor temporal HTTP alojado en *localhost*. Dicha URL envía información a tiempo real sobre cada hilo, y el estado en el que se encuentra. También existe la url *localhost/queue* que mostrará lo que está programado en la cola para el procesamiento.

## Durante la ejecución
Si durante la ejecución quieres ver el estado de cada hilo, puedes abrir la url localhost o puedes pulsar la tecla `w` o `o`. Si quieres parar el programa de forma natural, pulsa la tecla `q` o `k`.