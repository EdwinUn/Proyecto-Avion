PROMPT: 

Estoy desarrollando un programa en Python para simular la gestión de despegues en un aeropuerto utilizando estructuras de datos (colas circulares).

El sistema actual ya implementa:

- N pistas de despegue representadas como colas circulares con capacidad máxima.

- Asignación de vuelos a la pista con menor número de elementos.

- Una lista de espera general cuando todas las pistas están llenas.

- Simulación de llegada de 15 vuelos.

Sin embargo, el programa tiene varios problemas y carencias que necesito que corrijas y mejores:
    
1. Límite en la lista de espera:

   - Actualmente, la lista de espera general no tiene límite de capacidad.

   - Implementa un límite máximo configurable para la lista de espera.

   - Si la lista está llena, los nuevos vuelos deben ser rechazados o manejarse con un mensaje adecuado.

2. Tiempo de espera en pistas:

   - No existe un tiempo de espera para que un vuelo despegue.

   - Implementa un sistema donde cada vuelo tenga un tiempo de preparación/despegue (por ejemplo, en ciclos o segundos simulados).

   - Solo cuando ese tiempo se cumple, el vuelo puede salir de la cola (despegar).

3. Tiempo de espera en lista general:

   - Los vuelos en la lista de espera no tienen control de tiempo.

   - Agrega un tiempo de espera para cada vuelo en esta lista.

   - Cuando haya espacio en alguna pista, se debe mover el vuelo más antiguo (FIFO) respetando su tiempo acumulado.

4. Simulación más realista:

   - Usa ciclos de simulación (ticks) para representar el paso del tiempo.

   - En cada ciclo:

     - Reducir tiempos de espera de vuelos en pistas.

     - Permitir despegues cuando el tiempo llegue a cero.

     - Mover vuelos desde la lista de espera a pistas disponibles.

5. Buenas prácticas:

   - Usa clases para representar:

     - Vuelo

     - ColaCircular

     - Aeropuerto

   - Mantén el código limpio, modular y bien comentado.

   - Muestra en consola el estado del sistema en cada ciclo (pistas y lista de espera).

6. Salida esperada:

   - Mostrar claramente:

     - Asignación de vuelos a pistas

     - Despegues

     - Movimientos desde lista de espera

     - Rechazo de vuelos si la lista está llena

Por favor, reestructura el código completo tanto del backend y del frontend sin modificar el codigo original mas que solo las modificaciones si es necesario para cumplir con estos requerimientos y explica brevemente las decisiones de diseño.
