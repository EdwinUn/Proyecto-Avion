# INICIAR RAPIDO - Sistema de Gestion de Vuelos v2.0

## En 30 segundos...

### Opcion 1: Interfaz Grafica (Recomendado)
```bash
python "EJER1 - Colas, Bicolas.py"
```
- Boton "Simulacion Automatica" para demo completa
- Muestra pistas, lista de espera, tiempos en tiempo real
- Interfaz visual con colores

### Opcion 2: Simulacion en Consola
```bash
python simulacion_consola.py
```
- Demo automatica: registra 15 vuelos, ejecuta ciclos
- Muestra estado en cada ciclo
- Prensa ENTER en pasos

### Opcion 3: Ejemplos de Codigo
```bash
python ejemplos_uso.py
```
- 4 ejemplos diferentes: basico, ciclos, limites, estadisticas
- Muestra como usar el sistema en codigo


## Archivos Principales

| Archivo | Descripcion |
|---------|------------|
| `backend.py` | Logica: clases Vuelo, ColaCircular, AeropuertoManager |
| `EJER1 - Colas, Bicolas.py` | Interfaz grafica con Tkinter |
| `simulacion_consola.py` | Demo en consola sin GUI |
| `ejemplos_uso.py` | 4 ejemplos de como usar |
| `README.md` | Documentacion completa |
| `DECISIONES_DISEÑO.md` | Explicacion tecnica detallada |
| `CAMBIOS_IMPLEMENTADOS.md` | Resumen de cambios (este archivo) |


## Lo Que Se Implemento

✓ Limite configurable en lista de espera
✓ Tiempo de despegue para cada vuelo (reducido cada ciclo)
✓ Tiempo de espera en lista general
✓ Sistema de ciclos que simula paso del tiempo
✓ Clases bien organizadas (Vuelo, ColaCircular, Manager)
✓ Estadisticas (despegues, rechazos)
✓ Muestra clara de estado del sistema


## Parametros Configurables

```python
from backend import AeropuertoManager

manager = AeropuertoManager(
    num_pistas=3,           # Cuantas pistas
    capacidad_pista=5,      # Vuelos max por pista
    max_lista_espera=10,    # Vuelos max esperando
    tiempo_despegue=3       # Ciclos para preparacion
)
```


## Ejemplo Basico en 5 Lineas

```python
from backend import AeropuertoManager

manager = AeropuertoManager()
for i in range(15):
    manager.registrar_vuelo()
for _ in range(20):
    manager.simular_ciclo()
print(f"Despegues: {manager.total_despegues}, Rechazos: {manager.total_rechazos}")
```


## Interpretacion de Salida

```
[+] AM001 -> Pista 1          = Vuelo asignado a pista
[!] VB002 -> Lista de Espera  = Vuelo esperando (pistas llenas)
[X] LA003 -> RECHAZADO        = Vuelo rechazado (lista llena)

Pista 1: 2/5 vuelos           = 2 vuelos, capacidad 5
(Prox: MX001, 2s)             = Siguiente vuelo, 2 ciclos para despegar

[DESPEGUE] MX001 despego      = Vuelo salio exitosamente
[MOVIMIENTO] VB002 paso ...   = Vuelo paso de espera a pista

Eficiencia: 13/15 (86.7%)     = Porcentaje de vuelos despegados
```


## Preguntas Frecuentes

### P: Como veo el estado completo?
```python
estado = manager.get_estado_completo()
print(estado)  # Dict con todo: pistas, espera, ciclos, despegues
```

### P: Como limpio para nueva simulacion?
```python
# Crear nuevo manager
manager = AeropuertoManager()
```

### P: Puedo cambiar nombres de vuelos?
```python
# Ahora usa prefix automatico (MX, AM, VB, LA, AV)
# Los numeros se incrementan automaticamente
```

### P: Que pasa si la lista de espera se llena?
```
total_rechazos incrementa y el vuelo no se registra
```

### P: Como se que un vuelo esta listo?
```
tiempo_despegue llega a 0 (mostrado como "LISTO" en celda)
```


## Estructura de Clases (Resumen)

```
Vuelo
  - nombre: string
  - tiempo_despegue: int
  - tiempo_espera: int
  + reducir_tiempo_despegue()
  + incrementar_tiempo_espera()

ColaCircular  
  - datos: array [Vuelo]
  - frente, final: punteros
  + encolar(vuelo)
  + desencolar()
  + actualizar_tiempos()

AeropuertoManager
  - pistas: [ColaCircular]
  - lista_espera: [Vuelo]
  - total_despegues: int
  - total_rechazos: int
  + registrar_vuelo()
  + despegar_vuelo()
  + simular_ciclo()
```


## Reportes Finales de Sistema

Despues de simulacion, puedes ver:
- `manager.total_despegues`: Cuantos despegaron
- `manager.total_rechazos`: Cuantos rechazados
- `manager.ciclo_actual`: En que ciclo termino
- `manager.contador_vuelo`: Total generados
- `manager.get_lista_espera()`: Quien sigue esperando


---

**Versión:** 2.0
**Estado:** Completado y testeado
**Fecha:** Marzo 2026
