# 🎯 Sistema de Ticks — Arquitectura Senior Dev

## 📋 Resumen

Implementé un **sistema dual de ticks** que permite manejar la progresión de tiempo de forma manual (paso a paso) o automática (bucle continuo) con control de velocidad. El countdown se visualiza en tiempo real en las celdas de pistas y la lista de espera.

---

## 🏗️ Decisiones Arquitectónicas

### 1. **Evitar Threads → Usar `after()`**
- ❌ **Antes**: Threads daemon bloqueaban eventos entre ciclos
- ✅ **Ahora**: `after()` no bloquea la UI, más limpio
- **Beneficio**: No hay race conditions, UI responsiva siempre

### 2. **Separación de Responsabilidades**
- `_ejecutar_tick()` — Un ciclo único
- `_next_tick_manual()` — Dispara un tick manual
- `_toggle_auto_ticks()` — Inicia/pausa ticks automáticos
- `_programar_proximo_tick()` — Agenda el siguiente tick automático

### 3. **Control de Velocidad**
```
Fórmula: tiempo_ms = 1000 / velocidad_tick
- velocidad=0.5 → 500ms entre ticks (0.5 ticks/seg)
- velocidad=1.0 → 1000ms entre ticks (1 tick/seg) ← Default
- velocidad=2.0 → 500ms entre ticks (2 ticks/seg)
- velocidad=3.0 → 333ms entre ticks (3 ticks/seg)
```

### 4. **Detección Automática de Fin**
El sistema detiene automáticamente cuando:
- No hay vuelos en pistas
- No hay vuelos en lista de espera
Esto evita ticks inútiles y es más eficiente

---

## 🎮 Interfaz de Usuario

### Botones de Control

| Botón | Estado | Función |
|-------|--------|---------|
| **➡️ Next Tick** | Normal (verde) | Avanza **1 ciclo manual** |
| **▶️ Auto Tick** | Normal (verde) | Inicia ticks **automáticos** |
| **⏸️ Pausar** | Durante Auto | Pausa los ticks, vuelve a verde |

### Slider de Velocidad
- **Rango**: 0.5x a 3.0x
- **Incremento**: 0.5x por paso
- **Ajustable**: Mientras ticks automáticos corren (sin reiniciar)

### Indicador de Ciclo
```
┌─────────────────┐
│   Ciclo: 47     │  ← Actualiza en tiempo real
└─────────────────┘
```

---

## 📊 Visualización del Countdown

### En Pistas (Celdas)
```
┌────────────┐
│     ✈      │
│  Vuelo-001 │
│   ⏱️2      │  ← Tiempo de despegue contando hacia 0
└────────────┘
```

Cada tick:
- Tiempo **decrece** (2 → 1 → 0)
- Cuando llega a 0, el vuelo **despega**
- Celda queda **LIBRE**

### En Lista de Espera
```
⏳ Lista de Espera General
┌──────────────────────────────────────┐
│ 1. Vuelo-045   2. Vuelo-046         │
│ ⏳ 5s         ⏳ 10s                │
└──────────────────────────────────────┘
Total: 2 vuelo(s) | Espacio: 8 disponibles
```

Cada tick:
- Tiempo de **espera** se **incrementa**
- Cuando hay pista libre, vuelo **se mueve a pista**
- Recibe su nuevo `tiempo_despegue`

---

## 🔄 Flujo de Ejecución

### Escenario 1: Ticks Manuales (Next Tick)
```
Usuario presiona "➡️ Next Tick"
         ↓
   _next_tick_manual()
         ↓
   _ejecutar_tick()
         ↓
   manager.simular_ciclo()
         ↓
   Actualiza ciclo_actual
   Muestra eventos en log
   _refresh_all() actualiza UI
         ↓
   Espera siguiente click
```

### Escenario 2: Ticks Automáticos (Auto Tick)
```
Usuario presiona "▶️ Auto Tick"
         ↓
   _toggle_auto_ticks() inicia
         ↓
   Botones se deshabilitan (excepto "⏸️ Pausar")
   _programar_proximo_tick()
         ↓
   after(tiempo_ms) agenda siguiente
         ↓
   _ejecutar_tick()
         ↓
   Verifica hay_vuelos
         ├─ SÍ: Agenda nuevo after()
         └─ NO: Detiene automáticamente
         ↓
   Repite hasta que no haya vuelos
         ↓
   "⏸️ Pausar" para detener manualmente
```

### Escenario 3: Simulación Automática (15 Vuelos)
```
Usuario presiona "⚡ Simulación Automática (15 vuelos)"
         ↓
   Registra 15 vuelos con delays (300ms entre cada)
         ↓
   Habilita botones "➡️ Next Tick" y "▶️ Auto Tick"
         ↓
   Usuario elige:
   - Ticks manuales (paso a paso)
   - Ticks automáticos (fast-forward)
```

---

## 💾 Variables de Estado

```python
self.auto_ticks_activos = False    # Control de Auto Tick on/off
self.ciclo_actual = 0               # Número de ciclo visible
self.velocidad_tick = 1.0          # Multiplicador de velocidad (0.5-3.0)
self.after_id = None               # ID para cancelar after()
self.simulacion_activa = False      # Flag de simulación en progreso
```

---

## 🎬 Casos de Uso

### Caso 1: Observar paso a paso
```
1. Presiona "⚡ Simulación Automática (15 vuelos)"
2. Espera registro (5 segundos aprox)
3. Presiona "➡️ Next Tick" para cada ciclo
4. Observa cómo:
   - Tiempos descienden en pistas
   - Tiempos suben en espera
   - Vuelos despejan cuando tiempo = 0
```

### Caso 2: Ver simulación rápida
```
1. Presiona "⚡ Simulación Automática (15 vuelos)"
2. Espera registro
3. Mueve slider a 2.0x (velocidad máxima)
4. Presiona "▶️ Auto Tick"
5. Sistema completa en ~5 segundos
```

### Caso 3: Pausa y reanuda
```
1. Inicia "▶️ Auto Tick"
2. Después de varios ticks, presiona "⏸️ Pausar"
3. Usa "➡️ Next Tick" para avanzar controladamente
4. Vuelve a presionar "▶️ Auto Tick" para reanudar automático
```

### Caso 4: Manejo manual puro
```
1. Registra vuelos manualmente (botón "✚ Registrar Vuelo")
2. Usa "➡️ Next Tick" para procesar cada ciclo
3. Presiona "🛫 Despegar Vuelo" cuando lo necesites
4. Combina ticks con despegues manuales
```

---

## 📈 Mejoras vs Versión Anterior

| Aspecto | Antes | Ahora |
|--------|------|------|
| **Control** | Automático fijo | Manual + Automático dual |
| **Visualización** | Estática | Countdown en tiempo real |
| **Velocidad** | 1 ciclo/seg fijo | Ajustable 0.5x - 3.0x |
| **Threading** | Threads daemon | `after()` sin threads |
| **Responsividad** | Puede trabar | Siempre fluida |
| **Pausa** | No disponible | ⏸️ Pausa/Reanuda |
| **Fin automático** | No | Sí, cuando termina |

---

## 🐛 Manejo de Errores

### Error: "Ticks deshabilitados durante Auto Tick"
**Causa**: Intentas presionar "Next Tick" mientras "Auto Tick" está corriendo  
**Solución**: Presiona "⏸️ Pausar" primero

### Error: "Botones grises durante simulación"
**Causa**: Sistema registrando 15 vuelos  
**Solución**: Espera ~5 segundos, después se habilitan

### Error: "Auto Tick no responde"
**Causa**: `after_id` no fue cancelado correctamente  
**Solución**: Asegúrate de presionar "⏸️ Pausar" antes de salir

---

## 🔧 Configuración Avanzada

Si quieres ajustar parámetros, edita estas variables en `__init__`:

```python
# Velocidad inicial por defecto
self.velocidad_tick = 1.5  # En lugar de 1.0

# Delay entre registros de vuelos (ms)
self.after(300, lambda: self._registrar_vuelos_iterativamente(index + 1))
#         ↑
#         300ms = 0.3 segundos entre cada vuelo
```

---

## 📝 Log de Eventos

El panel derecho muestra eventos en tiempo real con colores:

```
── Simulación Automática iniciada ──
Fase 1: Registrando 15 vuelos...
[✚] Vuelo-001 → Pista 1 (despegue en 8s)
[✚] Vuelo-002 → Pista 2 (despegue en 6s)
...
Fase 2: Sistema listo para ticks. Usa 'Next Tick' o 'Auto Tick'

[⏱️ Ciclo 1]
  [→] Vuelo-005 pasó a Pista 3
  ⏳ Esperando: Vuelo-006(1s), Vuelo-007(2s), ...

[⏱️ Ciclo 2]
  [🛫] Vuelo-001 despegó
  [→] Vuelo-008 pasó a Pista 1
  ⏳ Esperando: Vuelo-006(0s), Vuelo-007(1s), ...
```

---

## ✨ Razones de Diseño

### ¿Por qué `after()` en lugar de threads?

1. **Simplicidad**: Una sola línea para programar siguiente
2. **Seguridad**: Sin race conditions en acceso a UI
3. **Control**: Fácil pausar/reanudar con `after_cancel()`
4. **Performance**: Menor overhead que threads

### ¿Por qué contador visual (`ciclo_actual`)?

1. **Debugging**: Sabes exactamente en qué ciclo estás
2. **Feedback**: Confirma que está progresando
3. **Correlación**: Puedes correlacionar con eventos en log

### ¿Por qué detección automática de fin?

1. **UX**: No desperdicies ciclos sin datos
2. **Eficiencia**: Menor CPU cuando termina
3. **Claridad**: Mensaje explícito cuando completa

