* Siempre que se hagan cambios verificar si es necesario actualizar el README.md del proyecto.
* Activar el virtualenv (carpeta venv) que esta en la raiz del proyecto si no se encuentra una dependencia.
* Siempre que se genere codigo verificar si no hay que actualizar los archivos de logs.
* Siempre que se genere codigo verificar si no hay que actualizar los archivos de clean.
* Siempre que se genere codigo seguir las buenas practicas de programacion.
* Los scripts de examples o test visuales deben estar en la carpeta examples/scripts/[componente] osea si son para planetas examples/planets.
* Siempre verificar si se establecen parametros que deberian ser setados en un archivo de congfiguracion general usar config.py.
* Verificar que se esten utilizando correctamente las configuraciones de config.py
* Siempre que se incluyan nuevas caracteristicas revisar con presicion si no afecta alguna otra funcionalidad.
* Cada vez que se necesite generar codigo verificar si es necesario agregar un test para la nueva funcionalidad.
* Verificar que los test cubran los casos en los que realmente son utiles.
* Siempre que haya que crear texturas verificar si ya existen funciones de ruido que sean utiles, en caso contrario crearlas o adaptarlas evitando comprometer el funcionamiento del ruido en otras texturas.
* Los comentarios, mombres de variables, clases, metodos o funciones deben estar en ingles.
* Cada vez que haya un cambio en la funcionalidad verificar la pagina web que esta en la raiz del proyecto.
* Priorizar la inyeccion de dependencias donde se pueda.
* IMPORTANTE!: El arhivo index.html de la interface web es muy grande, cada vez que haya que hacer algun cambio en ese archivo recostruirlo de nuevo creando multiples partes y luego unificandolos en un solo archivo.
* Al trabajar con Jinja2 y Alpine.js simultáneamente, debes tener extremo cuidado con las llaves de cierre (}) ya que ambas tecnologías usan sintaxis similares que pueden crear conflictos. Jinja2 utiliza {{ }} para variables mientras Alpine.js emplea x-data="{}" y expresiones como :class="{ active: open }", lo que puede causar interpretación prematura o errores de renderizado. Para evitarlo: escapa las llaves de Alpine con la sintaxis de Jinja2 {{ '{{' }} y {{ '}}' }}, utiliza bloques {%- raw -%}...{%- endraw -%} alrededor del código Alpine cuando sea necesario, considera la sintaxis x-data="$data({...})" para objetos JavaScript complejos y documenta claramente las secciones donde ambas tecnologías interactúan.
