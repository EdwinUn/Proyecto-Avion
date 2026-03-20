"""
DOCUMENTACIÓN DE MEJORAS - SISTEMA DE GESTIÓN DE VUELOS

Este documento describe los cambios implementados y las decisiones de diseño.
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  1. DECISIONES DE DISEÑO
# ═══════════════════════════════════════════════════════════════════════════════

"""
DECISIÓN 1: Crear Clase Vuelo (Encapsulación)
───────────────────────────────────────────────
PROBLEMA: El sistema anterior usaba strings para representar vuelos, lo que no
permitía controlar tiempos de despegue ni de espera.

SOLUCIÓN: Crear clase Vuelo con:
  • ID único (contador global)
  • Nombre (MX001, AM002, etc.)
  • tiempo_despegue: ciclos hasta poder despegar
  • tiempo_espera: tiempo acumulado en lista general
  • Métodos para reducir tiempos e incrementar espera

VENTAJAS:
  ✓ Encapsulación: cada vuelo mantiene su propio estado
  ✓ Extensibilidad: fácil agregar más propiedades (destino, pasajeros, etc.)
  ✓ Trazabilidad: cada vuelo tiene un ID único
  ✓ Control de tiempo: ahora podemos manejar tiempos internamente

CÓDIGO CLAVE:
```python
class Vuelo:
    def __init__(self, nombre: str, tiempo_despegue: int = 3):
        self.nombre = nombre
        self.tiempo_despegue = tiempo_despegue
        self.tiempo_espera = 0
    
    def reducir_tiempo_despegue(self) -> bool:
        """Retorna True si está listo para despegar"""
        if self.tiempo_despegue > 0:
            self.tiempo_despegue -= 1
        return self.tiempo_despegue <= 0
```


DECISIÓN 2: ColaCircular Mejorada (Control de Tiempos)
────────────────────────────────────────────────────────
PROBLEMA: La cola circular original no tenía forma de actualizar tiempos de
despegue de los vuelos en las pistas.

SOLUCIÓN: Agregar método actualizar_tiempos() que:
  • Itera sobre todos los vuelos en la cola
  • Reduce su tiempo_despegue
  • Retorna lista de vuelos listos para despegar

VENTAJAS:
  ✓ Separación de responsabilidades: la cola maneja estructura, tiempos se
    actualizan en ella
  ✓ Mejor performance: una sola pasada por la cola por ciclo
  ✓ Información clara: retorna los vuelos listos inmediatamente

CÓDIGO CLAVE:
```python
def actualizar_tiempos(self) -> list['Vuelo']:
    listos = []
    for vuelo in self.datos:
        if vuelo is not None:
            if vuelo.reducir_tiempo_despegue():
                listos.append(vuelo)
    return listos
```


DECISIÓN 3: Sistema de Ciclos de Simulación
──────────────────────────────────────────────
PROBLEMA: El sistema anterior no tenía un concepto de "tiempo" real. Los
despegues eran instantáneos sin período de preparación.

SOLUCIÓN: Implementar método simular_ciclo() que en cada iteración:
  1. Reduce tiempos de despegue en todas las pistas
  2. Despega vuelos listos (tiempo_despegue = 0)
  3. Mueve vuelos de espera a pistas disponibles (FIFO)
  4. Incrementa tiempos de espera en lista general

VENTAJAS:
  ✓ Realismo: los vuelos tienen tiempo de preparación
  ✓ Control: el sistema avanza de forma controlada
  ✓ Observabilidad: eventos claros en cada ciclo
  ✓ Escalabilidad: fácil de extender con más lógica

CICLO TÍPICO:
  Ciclo 0: Registrar vuelos
  Ciclo 1: tiempo_despegue 3 → 2 para todos
  Ciclo 2: tiempo_despegue 2 → 1 para todos
  Ciclo 3: tiempo_despegue 1 → 0 → DESPEGUES, movimientos de espera
  Ciclo 4: nuevos vuelos llegan a pistas vacías


DECISIÓN 4: Límite Configurable en Lista de Espera
────────────────────────────────────────────────────
PROBLEMA: La lista de espera original no tenía límite, causando potencial
acumulación infinita.

SOLUCIÓN: Agregar parámetro max_lista_espera en Aeropuerto:
  • Límite por defecto: 10 vuelos
  • Configurable en construcción: AeropuertoManager(..., max_lista_espera=15)
  • Vuelos rechazados si lista llena: total_rechazos incrementa

VENTAJAS:
  ✓ Control de recursos: evita acumulación infinita
  ✓ Realismo: los aeropuertos reales tienen límites
  ✓ Configurabilidad: cada simulación puede tener sus propios límites
  ✓ Rastreabilidad: contamos rechazos

CÓDIGO CLAVE:
```python
def registrar_vuelo(self):
    if pista:
        pista.encolar(vuelo)
    elif len(self.lista_espera) < self.max_lista_espera:
        self.lista_espera.append(vuelo)
    else:
        self.total_rechazos += 1  # Vuelo rechazado
```


DECISIÓN 5: Clase Aeropuerto como Orquestador
───────────────────────────────────────────────
PROBLEMA: AeropuertoManager era un manager básico sin concepto de simulación
global.

SOLUCIÓN: Mejorar a clase Aeropuerto que:
  • Gestiona ciclos de simulación
  • Coordina todas las pistas
  • Maneja lista de espera
  • Rastrean estadísticas globales

RESPONSABILIDADES:
  1. Creación y mantenimiento de pistas
  2. Generación de vuelos
  3. Asignación a pista menos ocupada
  4. Gestión de lista de espera
  5. Ejecución de ciclos de simulación
  6. Rastreo de estadísticas

VENTAJAS:
  ✓ Single responsibility: cada método tiene función clara
  ✓ Testeable: fácil de probar cada operación
  ✓ Estadísticas: tenemos visibilidad de lo que ocurre


DECISIÓN 6: Frontend Actualizado (Mínimos Cambios)
───────────────────────────────────────────────────
PROBLEMA: El frontend usaba strings, necesitaba adaptación.

SOLUCIÓN: Cambios mínimos en frontend:
  • Mostrar vuelo.nombre en lugar de vuelo
  • Mostrar vuelo.tiempo_despegue en celdas
  • Mostrar vuelo.tiempo_espera en lista de espera
  • Agregar método _ejecutar_ciclo_simulacion() para nueva simulación

VENTAJAS:
  ✓ Mantenimiento: cambios mínimos, menos chances de bugs
  ✓ Compatibilidad: interfaz gráfica sigue funcionando
  ✓ UI mejorada: ahora muestra tiempos

"""


# ═══════════════════════════════════════════════════════════════════════════════
#  2. FLUJO DE CONTROL DEL SISTEMA
# ═══════════════════════════════════════════════════════════════════════════════

"""
FLUJO NORMAL (Simulación Manual):
──────────────────────────────────
1. Usuario hace click en "Registrar Vuelo"
   → manager.registrar_vuelo()
   → Vuelo se asigna a pista menos ocupada O va a espera
   → Frontend muestra asignación

2. Usuario hace click en "Despegar Vuelo"
   → manager.despegar_vuelo()
   → Vuelo frente de pista sale
   → Si hay en espera, sube a la pista
   → Frontend actualiza

3. Repetir hasta simular todo manualmente


FLUJO SIMULACIÓN AUTOMÁTICA CON CICLOS:
─────────────────────────────────────────
1. Usuario hace click en "Simulación Automática"
2. FASE 1 (0.5s por vuelo):
   → Registra 15 vuelos distribuidamente
   → Algunos en pistas, otros en espera
   
3. FASE 2 (1s por ciclo):
   → Para cada ciclo:
      a) manager.simular_ciclo()
         - Reduce tiempos en pistas
         - Despega vuelos listos
         - Mueve de espera a pistas
         - Incrementa tiempos de espera
      b) Frontend muestra eventos
      c) Esperar 1 segundo

4. FASE 3:
   → Mostrar resumen: despegues, rechazos, eficiencia


DIAGRAMA DE FLUJO DE CICLO:
───────────────────────────

    ┌─────────────────────────────┐
    │    INICIO DE CICLO          │
    └──────────────┬──────────────┘
                   │
         ┌─────────▼──────────┐
         │ Actualizar tiempos │
         │ en todas pistas    │
         └─────────┬──────────┘
                   │
    ┌──────────────▼───────────────┐
    │ Identificar vuelos listos    │
    │ (tiempo_despegue <= 0)       │
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │ Despejar vuelos listos      │
    │ Actualizar estadísticas      │
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │ Para cada pista disponible:  │
    │ Mover vuelo de espera (FIFO) │
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │ Incrementar tiempo_espera    │
    │ de vuelos en lista general   │
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │ Incrementar ciclo_actual     │
    │ Retornar eventos             │
    └──────────────┬───────────────┘
                   │
         ┌─────────▼──────────┐
         │    FIN DE CICLO    │
         └────────────────────┘

"""


# ═══════════════════════════════════════════════════════════════════════════════
#  3. IMPLEMENTACIÓN TÉCNICA
# ═══════════════════════════════════════════════════════════════════════════════

"""
ESTRUCTURA DE CLASES:
─────────────────────

┌─────────────────────────────────────────────────────────────┐
│                     Vuelo (Entidad)                         │
├─────────────────────────────────────────────────────────────┤
│ • id_unico: int (contador global)                          │
│ • nombre: str (MX001, AM002, etc.)                         │
│ • tiempo_despegue: int (ciclos restantes)                  │
│ • tiempo_espera: int (ciclos en espera)                    │
├─────────────────────────────────────────────────────────────┤
│ + reducir_tiempo_despegue() -> bool                         │
│ + incrementar_tiempo_espera() -> None                       │
│ + get_info() -> str                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│           ColaCircular (Estructura de Datos)                │
├─────────────────────────────────────────────────────────────┤
│ • capacidad: int                                            │
│ • nombre: str                                               │
│ • datos: list[Vuelo | None] (array circular)               │
│ • frente: int (índice)                                      │
│ • final: int (índice)                                       │
│ • tamaño: int                                               │
├─────────────────────────────────────────────────────────────┤
│ + encolar(vuelo: Vuelo) -> bool                             │
│ + desencolar() -> Vuelo | None                              │
│ + siguiente() -> Vuelo | None                               │
│ + actualizar_tiempos() -> list[Vuelo]  ← NUEVO             │
│ + esta_llena() -> bool                                      │
│ + esta_vacia() -> bool                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         AeropuertoManager (Orquestador)                     │
├─────────────────────────────────────────────────────────────┤
│ • pistas: list[ColaCircular]                                │
│ • lista_espera: list[Vuelo]                                 │
│ • max_lista_espera: int (límite nuevo)                      │
│ • ciclo_actual: int (contador nuevo)                        │
│ • total_despegues: int (estadística)                        │
│ • total_rechazos: int (estadística)                         │
├─────────────────────────────────────────────────────────────┤
│ + registrar_vuelo() -> (Vuelo, ColaCircular | None)         │
│ + despegar_vuelo(pista_idx) -> (Vuelo | None, Vuelo | None)│
│ + simular_ciclo() -> dict  ← NUEVO                          │
│ + ejecutar_simulacion_completa(num_ciclos) -> list ← NUEVO  │
│ + get_estado_completo() -> dict  ← NUEVO                    │
└─────────────────────────────────────────────────────────────┘

"""


# ═══════════════════════════════════════════════════════════════════════════════
#  4. EJEMPLOS DE USO
# ═══════════════════════════════════════════════════════════════════════════════

"""
EJEMPLO 1: Simulación Básica
──────────────────────────────

from backend import AeropuertoManager

# Crear aeropuerto con parámetros personalizados
manager = AeropuertoManager(
    num_pistas=3,
    capacidad_pista=5,
    max_lista_espera=10,
    tiempo_despegue=3
)

# Registrar algunos vuelos
for i in range(5):
    vuelo, pista = manager.registrar_vuelo()
    if pista:
        print(f"{vuelo.nombre} asignado a {pista.nombre}")
    else:
        print(f"{vuelo.nombre} en lista de espera")

# Ejecutar un ciclo
evento = manager.simular_ciclo()
print(f"Despegues en ciclo {evento['ciclo']}: {len(evento['despegues'])}")


EJEMPLO 2: Simulación Completa de 20 Ciclos
──────────────────────────────────────────────

eventos = manager.ejecutar_simulacion_completa(20)

for evento in eventos:
    ciclo = evento['ciclo']
    despegues = len(evento['despegues'])
    movimientos = len(evento['movimientos_espera'])
    print(f"Ciclo {ciclo}: {despegues} despegues, {movimientos} movimientos")


EJEMPLO 3: Visualización de Estado Completo
──────────────────────────────────────────────

estado = manager.get_estado_completo()
print(f"Ciclo actual: {estado['ciclo']}")
print(f"Material despegado: {estado['total_despegues']} vuelos")
print(f"Vuelos rechazados: {estado['total_rechazos']}")

for pista_info in estado['pistas']:
    print(f"{pista_info['nombre']}: {pista_info['vuelos']}/{pista_info['capacidad']}")

print(f"En espera: {len(estado['lista_espera'])} vuelos")
print(f"Espacios disponibles: {estado['espacio_espera']}")

"""


# ═══════════════════════════════════════════════════════════════════════════════
#  5. RESPUESTA A REQUERIMIENTOS
# ═══════════════════════════════════════════════════════════════════════════════

"""
REQUERIMIENTO 1: Límite en Lista de Espera
───────────────────────────────────────────
✓ IMPLEMENTADO en AeropuertoManager.__init__(max_lista_espera=10)
✓ Los nuevos vuelos son rechazados si lista_espera está llena
✓ Se rastrean en total_rechazos
✓ Frontend muestra espacios disponibles


REQUERIMIENTO 2: Tiempo de Espera en Pistas
────────────────────────────────────────────
✓ IMPLEMENTADO: cada Vuelo tiene tiempo_despegue (default 3 ciclos)
✓ Se reduce en cada ciclo: vuelo.reducir_tiempo_despegue()
✓ Se muestra en la celda de la pista: "MX001\n(2s)"
✓ Solo despega cuando llega a 0


REQUERIMIENTO 3: Tiempo de Espera en Lista General
───────────────────────────────────────────────────
✓ IMPLEMENTADO: cada Vuelo tiene tiempo_espera
✓ Se incrementa cada ciclo: vuelo.incrementar_tiempo_espera()
✓ Se muestra en lista de espera: "AM002\n(5s)"
✓ Los vuelos más antiguos (FIFO) suben primero


REQUERIMIENTO 4: Simulación Realista con Ciclos
────────────────────────────────────────────────
✓ IMPLEMENTADO: simular_ciclo() ejecuta un ciclo completo
✓ Ciclo 1: reduce tiempos en pistas
✓ Ciclo 2: despega listos, mueve de espera
✓ Ciclo 3: incrementa tiempos de espera
✓ ejecutar_simulacion_completa() para múltiples ciclos


REQUERIMIENTO 5: Buenas Prácticas
──────────────────────────────────
✓ Clases bien definidas: Vuelo, ColaCircular, AeropuertoManager
✓ Métodos con responsabilidades claras
✓ Documentación extensiva en docstrings
✓ Nombres descriptivos para métodos y variables
✓ Separación de responsabilidades: vista/lógica


REQUERIMIENTO 6: Salida Esperada Clara
───────────────────────────────────────
✓ Frontend muestra: asignación, despegues, movimientos, rechazos
✓ Simulación en consola (simulacion_consola.py) muestra:
  - Asignación de vuelos a pistas
  - Despegues en cada ciclo
  - Movimientos desde lista de espera
  - Rechazos cuando lista está llena
  - Estado de pistas y espera cada ciclo

"""
