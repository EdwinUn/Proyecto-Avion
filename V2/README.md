# Sistema de Gestión de Vuelos - Aeropuerto

Simulador de despegues en un aeropuerto usando **colas circulares** como estructura de datos principal, con control de tiempos y sistema de ciclos de simulación.

## 🎯 Características Principales

### ✅ Implementado en v2.0

1. **Colas Circulares para Pistas**
   - 3 pistas de despegue (configurable)
   - Capacidad máxima de 5 vuelos por pista (configurable)
   - Punteros frente/final con operaciones de encolación/desencolación

2. **Control de Tiempos**
   - Cada vuelo tiene tiempo de preparación (3 ciclos por defecto)
   - Cada vuelo cuenta tiempo acumulado en lista de espera
   - Sistema de ciclos que simula paso del tiempo

3. **Lista de Espera Mejorada**
   - Límite máximo configurable (10 vuelos por defecto)
   - Vuelos rechazados si lista está llena
   - Movimiento FIFO a pistas cuando hay espacio
   - Rastreo de tiempo de espera por vuelo

4. **Simulación Realista**
   - Ciclos de simulación que avanzan el "reloj"
   - En cada ciclo:
     - Se reducen tiempos de despegue
     - Se despejan vuelos listos
     - Se mueven vuelos de espera
     - Se incrementan tiempos en espera

5. **Buenas Prácticas**
   - Clases bien definidas: `Vuelo`, `ColaCircular`, `AeropuertoManager`
   - Código modular y documentado
   - Interfaces gráfica y consola
   - Estadísticas y rastreo completo

## 📦 Archivos

### Backend
- **`backend.py`** - Lógica principal
  - `Vuelo`: Representa un vuelo con tiempos
  - `ColaCircular`: Cola circular mejorada
  - `AeropuertoManager`: Orquestador de simulación

### Frontend
- **`EJER1 - Colas, Bicolas.py`** - Interfaz gráfica (tkinter)
  - Visualización de pistas en tiempo real
  - Lista de espera con tiempos
  - Log de eventos
  - Simulación automática

- **`simulacion_consola.py`** - Simulación sin GUI
  - Muestra estado en consola
  - Pasos por demanda
  - Ideal para testing

### Documentación
- **`DECISIONES_DISEÑO.md`** - Explicación técnica detallada
- **`README.md`** - Este archivo

## 🚀 Uso

### Interfaz Gráfica

```bash
python "EJER1 - Colas, Bicolas.py"
```

**Controles:**
- **Registrar Vuelo**: Agrega nuevo vuelo a pista o espera
- **Despegar Vuelo**: Saca vuelo de frente de pista
- **Simulación Automática**: Registra 15 vuelos y ejecuta ciclos

### Simulación en Consola

```bash
python simulacion_consola.py
```

**Flujo:**
1. FASE 1: Registra 15 vuelos
2. FASE 2: Ejecuta ciclos de simulación automática
3. FASE 3: Muestra resumen con estadísticas

### Uso desde Código Python

```python
from backend import AeropuertoManager

# Crear aeropuerto
manager = AeropuertoManager(
    num_pistas=3,
    capacidad_pista=5,
    max_lista_espera=10,
    tiempo_despegue=3
)

# Registrar vuemlos
for i in range(15):
    vuelo, pista = manager.registrar_vuelo()
    print(f"{vuelo.nombre} → {pista.nombre if pista else 'Espera'}")

# Ejecutar ciclos
while True:
    evento = manager.simular_ciclo()
    if evento["despegues"]:
        print(f"Ciclo {evento['ciclo']}: {len(evento['despegues'])} despegues")
    
    # Verificar si terminar
    pistas = manager.get_pistas()
    espera = manager.get_lista_espera()
    if all(p.esta_vacia() for p in pistas) and not espera:
        break
```

## 🔧 Configuración

### Parámetros del AeropuertoManager

```python
manager = AeropuertoManager(
    num_pistas=3,              # Número de pistas
    capacidad_pista=5,         # Vuelos máx por pista
    max_lista_espera=10,       # Vuelos máx en espera
    tiempo_despegue=3          # Ciclos para preparación
)
```

## 📊 Salida Esperada

### Simulación Automática (GUI)

```
[✚] MX001 → Pista 1 (despegue en 3s)
[✚] AM002 → Pista 2 (despegue en 3s)
[⏳] VB003 → Lista de Espera (pistas llenas)
...
[⏱ Ciclo 1]
  ... (tiempos se reducen)

[⏱ Ciclo 3]
  [🛫] MX001 despegó
  [→] VB003 pasó a Pista 1

...

Total despegues: 15
Total rechazos: 0
```

### Simulación Consola

```
════════════════════════════════════════════════════════════════════════════════
  ESTADO DE PISTAS  
════════════════════════════════════════════════════════════════════════════════

Pista 1         Vuelos: 2/5  │ [→MX001→ ][AM002] [...] [...] [...] │ (Prox: MX001, 1s)
Pista 2         Vuelos: 1/5  │ [→VB003→ ] [...] [...] [...] [...] │ (Prox: VB003, 2s)
Pista 3         Vuelos: 0/5  │ [...] [...] [...] [...] [...] │ (vacía)

════════════════════════════════════════════════════════════════════════════════
  LISTA DE ESPERA (2/10)  
════════════════════════════════════════════════════════════════════════════════

  1. LA004      Tiempo en espera: 5s
  2. AV005      Tiempo en espera: 3s

  Espacios disponibles: 8/10

════════════════════════════════════════════════════════════════════════════════
  ESTADÍSTICAS  
════════════════════════════════════════════════════════════════════════════════

  Ciclo actual: 12
  Total despegues: 7
  Total rechazos: 0
  Vuelos generados: 15
```

## 📈 Datos Estadísticos

La simulación rastrea:

- **`total_despegues`**: Vuelos que salieron exitosamente
- **`total_rechazos`**: Vuelos rechazados (lista espera llena)
- **`ciclo_actual`**: Número de ciclo actual
- **`contador_vuelo`**: Total de vuelos generados

## 🔄 Flujo de un Ciclo de Simulación

```
INICIO DE CICLO
    ↓
Reducir tiempo_despegue en pistas
    ↓
Identificar vuelos listos (tiempo = 0)
    ↓
Despejar vuelos listos
    ↓
Mover vuelos de espera a pistas (FIFO)
    ↓
Incrementar tiempo_espera en lista general
    ↓
Incrementar ciclo_actual
    ↓
FIN DE CICLO → Retornar eventos
```

## 🎓 Conceptos

### Cola Circular
- Estructura de datos que usa arreglo circular
- Punteros `frente` y `final` que avanzan
- Evita desperdicio de espacio (diferente a cola simple)

### Tiempo de Despegue
- Ciclos que debe esperar un vuelo antes de poder salir
- Se reduce en cada ciclo: `tiempo_despegue -= 1`
- Cuando llega a 0, el vuelo puede despegar

### Tiempo de Espera
- Ciclos que un vuelo ha estado en lista de espera
- Se incrementa cada ciclo que no puede subir a pista
- Útil para análisis de QoS (calidad de servicio)

### FIFO en Lista de Espera
- Vuelo más antiguo (First In) sube primero (First Out)
- Implementado con `pop(0)` en Python

## 📝 Ejemplos de Ejecución

### Ejemplo 1: 15 Vuelos, 3 Pistas

```
Pista 1: [MX001(3s)] [AM002(3s)] [VB003(3s)] [...] [...]
Pista 2: [LA004(3s)] [AV005(3s)] [...] [...] [...]
Pista 3: [MX006(3s)] [...] [...] [...] [...]
Espera: [AM007(0s)] [VB008(0s)] [LA009(0s)]

Ciclo 1:
  tiempo_despegue: 3 → 2

Ciclo 3:
  MX001, AM002, VB003, LA004, AV005, MX006 despelan
  AM007, VB008, LA009 suben a pistas

...

Eficiencia: 15/15 = 100%
```

## ⚠️ Notas

- Los cambios mantienen compatibilidad con código anterior
- El frontend requiere tkinter: `pip install tkinter` (incluido en Python)
- La simulación es determinística (mismos vuelos cada vez)
- Tiempo en simulación es "simbólico", cada ciclo ≈ 1 segundo en ejecución

## 📄 Licencia

Proyecto educativo - Sistema de Gestión de Vuelos
