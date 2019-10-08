# How to install
There are two diferent ways: normal instalation and virtualv instalation. Both need to have Python 3.6+ installed. If you have more python scripts running, it would be better to install it in a virual environment.

In the future, The program will be just a folder. In a future, of course.

### Virtualenv install
1. Create a folder whenever you want.
2. Inside that folder we will create the virtual environment. To do so, open the terminal and type `virtualenv venv`.
3. Activate the environment using `call venv/scripts/activate.bat`.
4. Install the program with `python -m pip install git+https://github.com/sralloza/vcm.git@dev`
5. Inside that folder, create another folder and add it to the `PATH`. If you don't know how to add folders to the `PATH`, visit [this site](https://docs.alfresco.com/4.2/tasks/fot-addpath.html).
6. Finally, create a file named `vcm.cmd` in that 

```
@echo off
"drive:/path/to/your/folder/venv/scripts/python.exe" %*
```
7. Done. To use the program, type `vcm -h`


### General install
1. Run `python -m pip install git+https://github.com/sralloza/vcm.git@dev`
2. Done. To use the program, just type `vcm -h`

# How to use
Al execute the program for the first time, the configuration and credential files will be automatically created. You can find them in `%USER%/vcm-config.ini` and `%USER%/vcm-credentials.ini`.

## Config files

## Command Line Interface arguments

## During the execution

<!-- ## Ficheros de configuración
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
Si durante la ejecución quieres ver el estado de cada hilo, puedes abrir la url localhost o puedes pulsar la tecla `w` o `o`. Si quieres parar el programa de forma natural, pulsa la tecla `q` o `k`. -->