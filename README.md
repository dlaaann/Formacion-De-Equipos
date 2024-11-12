Este archivo está dedicado a explicar cómo usar/ejecutar correctamente los scripts del repositorio. Para ello, por cada script se proporciona el comando que debe ejecutarse en la línea de comandos de Windows, ya que
todo el código ha sido desarrollado y probado en dicho sistema operativo. Cabe mencionar también que para el desarrollo de todo el código se ha utilizado la versión 3.11 de Python.

## GRASP.py
Comando -> py GRASP.py --instancia A --tiempo_limite B --lambda_ C --alfa D --estrategia_bl E
A continuación se explica en qué consisten los parámetros:
  --instancia: se proporciona la dirección en la que se encuentra una instancia (archivo .txt) que contenga información sobre unos alumnos (sus puntuaciones Belbin y su género) a partir de los cuales se desean formar
  equipos. Para tener mayor claridad sobre el contenido que debe tener una instancia, mirar las carpetas de instancias del repositorio. Un ejemplo de lo que se puede pasar a este parámetro es: "./instancias/instancia_40_5 (1).txt".
  Las comillas son necesarias para este parámetro.
  --tiempo_limite: se establece el tiempo límite de ejecución del algoritmo. Debe estar en segundos. Por ejemplo, si se desea ejecutar el algoritmo por un minuto, a este parámetro se le debe proporcionar el valor 60.
  --lambda_: el valor de este parámetro determina si lo que se quiere priorizar es la formación de equipos que favorezcan más la cobertura de roles que el balance de géneros, o viceversa. Se puede proporcionar cualquier
  valor entre 0 y 1, incluidos estos dos. Cuanto mayor es este valor, mayor prioridad se dará a la formación de equipos que favorezcan más la cobertura de roles que el balance de géneros.
  --alfa: se proporciona el valor del parámetro alfa característico del algoritmo. El valor proporcionado debe estar entre 0 y 1, incluidos estos dos.
  -- estrategia_bl: se establece la estrategia que se quiere utilizar para la fase de búsqueda local del algoritmo. Los valores que se pueden introducir son "best-improving" o "first-improving".

  Este script ni ninguno de los otros dos ha sido desarrollado para controlar errores en la introducción de los valores de los parámetros. Por tanto, se recomienda atenerse a lo indicado.
