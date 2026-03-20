# V2 - Sistema de Gestión de Vuelos Refactorizado

## 📋 Descripción

Versión completamente refactorizada del Sistema de Gestión de Vuelos con:

- **Sistema de simulación basado en ticks** - Cada "ciclo" representa una unidad de tiempo
- **Colas circulares optimizadas** - Estructura de datos eficiente para pistas
- **Gestión de tiempos** - Preparación y espera configurables
- **Límites configurables** - Capacidad de pistas y lista de espera
- **Movimientos FIFO automáticos** - Vuelos en espera se asignan a pistas disponibles
- **Despegues automáticos** - Round-Robin para fairness entre pistas

## 🏗️ Estructura del Código

### Classes Principales

#### `Vuelo`
Representa un vuelo individual en el ciclo de vida del aeropuerto.

```python
vuelo = Vuelo(
    id_vuelo=1,
    nombre="MX001",
    ciclo_llegada=0,
    tiempo_preparacion=5  # ciclos necesarios antes de despegar
)
```

**Métodos:**
- `decrementar_preparacion()`: Reduce tiempo de preparación (llamado en cada ciclo)
- `incrementar_espera()`: Aumenta tiempo en espera
- `esta_listo()`: Retorna True si tiempo_preparacion == 0

#### `ColaCircular`
Implementación de cola circular para gestionar vuelos en pistas.

```python
pista = ColaCircular(capacidad=5, nombre="Pista 1")
pista.encolar(vuelo)           # Agregar vuelo
vuelo = pista.desencolar()     # Remover y retornar frente
vuelos_lista = pista.listar()  # Obtener todos los vuelos
```

**Métodos:**
- `encolar(vuelo)`: Agrega vuelo al final
- `desencolar()`: Removes y retorna vuelo del frente
- `siguiente()`: Retorna vuelo del frente sin remover
- `listar()`: Retorna lista de todos los vuelos en orden
- `esta_llena()`, `esta_vacia()`: Estados de la cola

#### `Aeropuerto`
Orquestador central del sistema de simulación.

```python
aeropuerto = Aeropuerto()
vuelo, estado = aeropuerto.registrar_vuelo()  # Registrar nuevo vuelo
aeropuerto.simular_ciclo()                    # Simular próximo ciclo
estado_actual = aeropuerto.obtener_estado_sistema()  # Ver estado
```

**Características:**
- 3 pistas con capacidad 5 vuelos cada una
- Lista de espera con límite de 10 vuelos
- Tiempos de preparación: 3-8 ciclos (aleatorio)
- Sistema automático de ciclos

## 🎯 Uso del Sistema

### Importar el módulo

```python
from backend import Aeropuerto
```

### Crear una instancia

```python
aeropuerto = Aeropuerto()
```

### Registrar vuelos

```python
# Registrar un vuelo nuevo
vuelo, estado = aeropuerto.registrar_vuelo()

if estado == "asignado_a_pista":
    print(f"{vuelo.nombre} asignado a una pista")
elif estado == "en_espera":
    print(f"{vuelo.nombre} en lista de espera")
elif estado == "rechazado":
    print(f"{vuelo.nombre} RECHAZADO - lista espera llena")
```

### Simular ciclos

```python
# Simular un ciclo único
aeropuerto.simular_ciclo()

# Simular múltiples ciclos
for ciclo in range(30):
    aeropuerto.simular_ciclo()
```

### Acceder a eventos del ciclo

```python
eventos = aeropuerto.get_eventos_ciclo()

despegues = eventos["despegues"]          # Vuelos que despegaron
asignados = eventos["movimientos_espera"]  # Vuelos asignados de espera
rechazos = eventos["rechazos"]            # Vuelos rechazados
```

### Consultar estado del sistema

```python
estado = aeropuerto.obtener_estado_sistema()
# Retorna dict con:
# - ciclo actual
# - detalles de pistas
# - lista de espera
# - eventos del ciclo
# - estadísticas

stats = aeropuerto.obtener_estadisticas()
# Retorna dict con:
# - ciclos simulados
# - total asignados/despegues/rechazos
# - tasas y promedios
```

## 📊 Flujo de Operación

```
Registrar vuelo
    ↓
¿Hay pista disponible?
    ├─ SÍ → Asignar a pista menos ocupada
    └─ NO → ¿Hay espacio en lista espera?
            ├─ SÍ → Agregar a lista espera
            └─ NO → Rechazar vuelo

Simular ciclo
    ├─ 1. Decrementar tiempos en pistas
    ├─ 2. Incrementar tiempos en espera
    ├─ 3. Procesar despegues (Round-Robin)
    │       └─ Vuelos con tiempo=0 salen de pistas
    ├─ 4. Mover vuelos de espera a pistas (FIFO)
    └─ 5. Incrementar contador de ciclos
```

## 🔧 Configuración

Las constantes en la clase `Aeropuerto` pueden modificarse:

```python
class Aeropuerto:
    NUM_PISTAS = 3                    # Número de pistas
    CAPACIDAD_PISTA = 5               # Vuelos máx por pista
    MAX_CAPACIDAD_ESPERA = 10         # Vuelos máx en espera
    TIEMPO_PREPARACION_MIN = 3        # Mínimo ciclos preparación
    TIEMPO_PREPARACION_MAX = 8        # Máximo ciclos preparación
```

## 📈 Ejemplo Completo

Ver `demo.py` para una demostración funcional completa del sistema.

## 🧪 Pruebas

### Ejecutar pruebas unitarias

```bash
python test_simulacion.py
```

Valida:
- Simulación básica
- Límites de capacidad
- Round-Robin en despegues
- FIFO en movimientos espera
- Integridad del sistema

### Ejecutar diagnóstico

```bash
python diagnostico.py
```

Muestra detalles de tiempos antes/después de ciclos.

### Ejecutar demostración

```bash
python demo.py
```

Simulación completa con 20 vuelos y 30 ciclos.

## ✨ Mejoras Principales (vs V1)

| Característica | V1 | V2 |
|---|---|---|
| Clases | ColaCircular, AeropuertoManager | Vuelo, ColaCircular, Aeropuerto |
| Tiempos | Sin control | Sistema de ticks con control |
| Preparación | Instantánea | 3-8 ciclos configurable |
| Espera | Sin límite | Hasta 10 vuelos (configurable) |
| Movimiento espera | Manual | Automático FIFO |
| Despegues | Manual | Automático Round-Robin |
| Integridad | No validada | Validaciones incluidas |
| Estadísticas | Básicas | Completas y detalladas |

## 🐛 Bugs Corregidos

- **ColaCircular.listar() wrap-around**: Ahora maneja correctamente colas llenas (frente == final)
- **Tiempos no se decrementaban**: Bug en obtención de vuelos desde cola
- **No había movimientos espera**: Método `_mover_vuelos_espera_a_pistas()` no se ejecutaba

## 📝 Changelog

### v2.0.0 (Marzo 2026)

**NUEVAS CARACTERÍSTICAS:**
- ✅ Sistema de simulación basado en ticks
- ✅ Clases Vuelo y Aeropuerto separadas
- ✅ Tiempos de preparación/espera configurables
- ✅ Despegues automáticos con Round-Robin
- ✅ Movimientos FIFO desde lista espera
- ✅ Límites configurables

**CORRECCIONES:**
- ✅ Bug grave en ColaCircular.listar()
- ✅ Decrementación de tiempos no funcionaba
- ✅ Validaciones de integridad agregadas

## 📌 Notas

- El sistema usa números aleatorios para tiempos de preparación (reproducible con seed si es necesario)
- Todos los valores de tiempo están en "ciclos" - unidad abstracta de tiempo simulado
- El Round-Robin en despegues asegura que ninguna pista monopolice las salidas
- FIFO garantiza fairness en la lista de espera

---

**Última actualización:** Marzo 20, 2026
