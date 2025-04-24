# Instrucciones para revisión y mantenimiento de código limpio

## Documentación y comentarios
* Verificar que los comentarios sean claros, precisos y agreguen valor real al código.
* Comprobar que no existan comentarios duplicados o redundantes que repitan lo que el código ya expresa claramente.
* Asegurar que los comentarios estén actualizados y reflejen el comportamiento actual del código.
* Eliminar comentarios obsoletos que ya no corresponden a la implementación actual.
* Revisar que los docstrings incluyan información sobre parámetros, valores de retorno y excepciones cuando sea apropiado.

## Organización del código
* Verificar que las importaciones estén organizadas por grupos lógicos (bibliotecas estándar, bibliotecas de terceros, módulos propios).
* Comprobar que las importaciones innecesarias o no utilizadas sean eliminadas.
* Asegurar que las clases y funciones estén ubicadas en los módulos correspondientes según su funcionalidad.
* Revisar que los métodos dentro de una clase sigan un orden lógico (ej. constructores, métodos públicos, métodos privados).
* Verificar que la estructura de directorios del proyecto refleje una separación adecuada de responsabilidades.

## Nomenclatura y estilo
* Confirmar que los nombres de variables, funciones y clases sean descriptivos y sigan las convenciones de estilo del proyecto.
* Revisar que haya consistencia en el estilo de nombrado (CamelCase, snake_case, etc.) según las convenciones adoptadas.
* Comprobar que la indentación sea consistente en todo el código.
* Asegurar que el código siga el formato establecido (espacios, líneas en blanco, longitud máxima de línea).
* Verificar que se usen constantes en lugar de valores literales dispersos en el código.

## Calidad del código
* Detectar y eliminar código duplicado, aplicando principios DRY (Don't Repeat Yourself).
* Identificar y remover código muerto o inalcanzable.
* Eliminar código redundante que realiza la misma operación múltiples veces.
* Revisar que no exista código comentado (usar sistemas de control de versiones en su lugar).
* Verificar que las funciones tengan una única responsabilidad claramente definida.
* Comprobar que las clases cumplan con el principio de responsabilidad única.

## Manejo de errores y robustez
* Asegurar que el código maneje adecuadamente casos excepcionales y condiciones de error.
* Verificar que las excepciones sean capturadas y procesadas apropiadamente.
* Comprobar que se utilice un sistema de logging consistente para registrar errores y eventos importantes.
* Revisar que los mensajes de error sean descriptivos y útiles para el diagnóstico.
* Asegurar que no se supriman excepciones sin un manejo adecuado.

## Rendimiento y optimización
* Identificar posibles cuellos de botella en el rendimiento.
* Revisar el uso eficiente de recursos (memoria, CPU, operaciones I/O).
* Comprobar que las optimizaciones no comprometan la legibilidad sin una buena justificación.
* Verificar que los algoritmos utilizados sean apropiados para el problema que resuelven.

## Pruebas
* Asegurar que el código tenga pruebas unitarias adecuadas.
* Verificar que las pruebas cubran tanto casos típicos como casos límite.
* Comprobar que las pruebas sean independientes entre sí y reproducibles.
* Revisar que las pruebas sean mantenibles y comprensibles.

## Seguridad
* Identificar y corregir posibles vulnerabilidades de seguridad.
* Asegurar que no se expongan datos sensibles en el código o logs.
* Verificar que se validen adecuadamente las entradas de usuario y datos externos.

## Control de versiones y colaboración
* Comprobar que los mensajes de commit sean descriptivos y sigan las convenciones establecidas.
* Revisar que los cambios estén atomizados en commits lógicos.
* Asegurar que se utilicen ramas y flujos de trabajo adecuados para características, correcciones y versiones.