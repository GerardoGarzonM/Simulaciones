# Simulaciones.
En este repositorio están los archivos para la simulación de la interacción depredador presa.
# Introducción.
Este programa utiliza el lenguaje de programación Python, junto con las librerías  `numpy`, `pandas`, `math`, y `plotly`. Como primer punto, hablaré sobre las cosas que se utilizan para simplificar el modelo.
1. Se trabaja en un espacio que se asume son celdas de tamaño fijo, en este caso, cada celda es un cuadrado de 1 km de lado.
2. Se asume que los individuos de tipo *presa* no se mueven de la celda en la que se añaden, esto ya que las presas tienen un movimiento promedio mucho menor comparado con el de los individuos de tipo *depredador*.
3. Se asume que los depredadores cuyo patrón de movimiento es de tipo *cíclico* forman patrones regulares en sus movimientos (véase )
# Secciones del programa.
## Primera sección.
En esta sección se importan las librerías necesarias, y ademas se inicializan las clases que se utilizarán, así como la función que se encargará del patrón de movimiento cíclico. En el programa se utilizan 2 clases generales, y dentro de una de estas hay 2 subclases
### Clase 1. Presa.
Para esta clase, se utilizan varias propiedades:
- Posición x. Como su nombre lo indica, es el valor de la posición de la presa sobre el eje horizontal.
- Posición y. Igual a la posición x, sólo que esta es en el eje vertical.
- Estado. Este valor nos indica si el individuo está vivo o muerto, un valor de 1 significa que esta vivo, y un valor de 0 indica que está muerto.
- Probabilidad. Este valor nos indica la probabilidad de que, dado que un depredador haya detectado a este individuo, pueda escapar.
- Id de especie. Con este valor podemos etiquetar a las especies sin usar necesariamente su nombre.
### Clase 2. Depredador.
Esta clase tiene más propiedades que la anterior, ya que este tipo de individuos sí van a presentar diferentes patrones de movimiento. En este caso se usan las siguientes propiedades:
- Posición x. Funciona igual que con las presas.
- Posición y. Funciona igual que en las presas, solo que en este caso tanto la posición x como la posición y sí van a cambiar en el tiempo.
- Estado. Funciona igual que en la parte de presas.
- Desplazamiento. Esta propiedad nos dice el desplazamiento promedio que realiza un individuo de esa especie, debe estar en km/día.
- Desviación estándar. Este valor nos indica la desviación estándar que tiene el promedio del desplazamiento, debe ser un número positivo, un valor pequeño quiere decir que los valores de desplazamientos tomados estarán en su mayoría cerca de la media (el desplazamiento promedio), un valor grande indica que los valores de desplazamiento estarán extendidos en un rango más amplio de valores.
- Conducta. Esta propiedad nos dice qué tipo de patrón de movimiento sigue esta especie, un valor de 1 nos indica que es de movimiento cíclico, un valor de 0 nos indica que es de tipo aleatorio.
- Probabilidad. Aunque el valor es homónimo con una propiedad de las presas, su función es diferente, en este caso nos indica cuál es la probabilidad de que cuando haya una presa lo suficientemente cerca, este individuo la detecte.
Ahora, con estas 2 clases definidas, podemos pasar a las subclases.
### Subclase 1. Movimiento Aleatorio.
En esta subclase de depredadores, tenemos que el movimiento no seguirá un patrón específico, aunque se moverá una distancia relativamente fija (aunque depende del valor de la desviación), la dirección en la que se mueve es completamente aleatoria, y puede depender de diversos factores, como si encuentra alguna presa. Esta subclase tiene sólo dos parámetros extra:
- Punto x. Por defecto, será el punto de aparición del individuo, sobre el eje horizontal.
- Punto y. Lo mismo que el punto x, pero en el eje vertical, estos valores se pueden usar para imponer la condición de que cierta especie, a pesar de su comportamiento aleatorio, nunca se aleje más de cierta distancia de su punto de origen.
### Subclase 2. Movimiento Cíclico.
Para esta subclase, la premisa es que tendremos un punto (el punto de origen), y después de cierto tiempo el individuo regresará a un lugar cercano a ese punto, para luego repetir el ciclo. Esta subclase utiliza las siguientes propiedades:
- Punto x. Este es el punto sobre el eje horizontal al que el individuo intentará regresar en su ciclo de movimiento.
- Punto y. Lo mismo que el punto x, pero es un punto sobre el eje vertical.
- Tiempo de ciclo. Este valor es el numero de días que le toma regresar a su lugar de origen, se toma como constante.
- Contador. Esta es una variable auxiliar, sirve para que el programa mantenga un registro de cuántos días faltan para que el individuo complete su ciclo de movimiento.
### Función para movimiento cíclico.
Para implementar el movimiento cíclico, se utiliza una función llamada `mov_ciclico`, a continuación se da una descripción de su funcionamiento. Como primera parte, los argumentos que toma esta función son los siguientes:
- x. Es la posición x del individuo con movimiento cíclico.
- y. Lo mismo, pero con la posición y.
- Contador. Es el valor de la variable auxiliar de mismo nombre que nos ayuda a mantener el tiempo que falta para el término del ciclo.
- Tiempo. Este es el valor de la constante del tiempo que duran los ciclos de movimiento de esa especie.
- Centro. Este valor es la distancia de movimiento promedio que se desplaza el individuo por día. 
- Desviación estándar. Tiene la misma función que la propiedad homónima de la clase depredador, ya que tomaremos los desplazamientos con una cierta variación, nos dice qué tan cerca o lejos del valor central se van a tomar los valores de distancia viajada.
En esta función, se trabaja en coordenadas polares en vez de cartesianas, es decir, en vez de describir los puntos con coordenadas (x,y), se usa la distancia del punto al origen, y el ángulo que forma con el eje horizontal. Lo primero que hace la función es definir el valor de una variable, la cual será la distancia que viajará el individuo, esta se tomará de una distribución normal con media `centro` y con desviación estándar `desv`. Después, se checa el valor del `contador`, con eso tendremos dos casos
##### Contador con valor de cero.
En este caso, significa que el individuo está en su punto de origen. Entonces se cambia el valor a `tiempo - 1`, para que en la siguiente iteración se haga el otro caso. Después de esto, se eligen dos números enteros aleatorios entre -1 y 1, el primer número, llamado `h`, nos dice hacia qué dirección horizontal se moverá el individuo
-`h=1`. Entonces habrá un desplazamiento horizontal a la derecha.
- `h=0`. Entonces no habrá desplazamiento en la dirección horizontal.
- `h=-1`. Entonces habrá un desplazamiento horizontal a la izquierda.
Y a su vez, estos se combinan con el resultado de la variable `v`, que nos dirá el movimiento en el eje vertical que habrá
- `v=1`. Significa un movimiento hacia la parte positiva del eje vertical ("arriba").
- `v=0`. No hay desplazamiento en el eje vertical.
- `v=-1`. Hay un desplazamiento hacia la parte negativa del eje vertical ("abajo").
Con estos dos números, se hacen una serie de casos de las posibles combinaciones de valores de `h` y `v`, por ejemplo, si ambos valen 1, significa que habrá un desplazamiento tanto en el eje vertical como en el horizontal, esto se interpreta como un desplazamiento en un ángulo de 45° (o π/4 en radianes), por otro lado, si `h=1` y `v=0`, se toma un desplazamiento sólo horizontal y solo hacia la derecha. Con la combinación de valores de `h` y `v`, se eligen valores de una variable llamada `theta`, que nos indica el ángulo que tomará el desplazamiento del individuo. Una vez teniendo el valor de `theta` y del desplazamiento que hará, se hace la conversión de regreso a coordenadas cartesianas, y se obtiene la nueva posición del individuo haciendo una suma de vectores, el de posición con el de movimiento. Ahora, sigue el otro caso.
##### Contador con valor distinto de cero.
Para este caso, se interpreta que el individuo está realizando su ciclo de movimiento, pero aún no lo ha terminado, por lo cual, para este tipo de desplazamientos se usará un modelo de desplazamiento cíclico simplificado, se asume que las posiciones y distancias viajadas en los días que dura el ciclo de movimiento se pueden aproximar con poligonos regulares, se busca que, dado un `tiempo` de ciclo, este nos dirá el número de vértices que hay en el polígono formado por las posiciones que ocupa el individuo durante todo su ciclo de movimiento, a su vez, se usa un teorema, el cual nos dice que la suma de los ángulos externos a un polígono es 360° (o 2π radianes), por lo cual, si estamos en un cierto momento del ciclo, para determinar el ángulo del movimiento siguiente, se puede visualizar como está a continuación
![Movimiento](https://github.com/user-attachments/assets/2071141e-1252-4c52-b4dc-f5aa2c6d5f66)
Ya que requerimos saber el ángulo con la horizontal, y sabemos que 2π/`tiempo` es  

