# 🔄 Diagrama de Flujo — Sistema de Ticks

## Diagrama 1: Estados Principales

```
                        ┌────────────────────┐
                        │  SISTEMA INICIADO  │
                        └─────────┬──────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                  │
                ▼                 ▼                  ▼
        ┌────────────────┐ ┌──────────────┐ ┌─────────────────┐
        │ ESPERA (idle)  │ │ REGISTRANDO  │ │ TICKS ACTIVOS   │
        │ (Sin ticks)    │ │15 VUELOS    │ │ (manual/auto)   │
        │                │ │              │ │                 │
        │ Botones:       │ │ Botones:     │ │ Botones:        │
        │ ✚ Registrar   │ │ (todos       │ │ ➡️ Next Tick   │
        │ 🛫 Despegar   │ │  disabled)   │ │ ▶️ Auto/⏸️      │
        │ ⚡ Simulación │ │              │ │ (velocidad)     │
        └────────┬───────┘ └──────┬───────┘ └────────┬────────┘
                 │                │                   │
                 └────(click)──────┼──(fin registro)──┘
                 "⚡"              │
                                  └─(usuario elige)─┐
                                                     │
                        ┌────────────────┬───────────┘
                        │                │
                        ▼                ▼
                ┌──────────────┐  ┌──────────────┐
                │ MANUAL MODE  │  │ AUTO MODE    │
                │              │  │              │
                │ ➡️ Next Tick │  │ ▶️ Auto Tick │
                │ (1 por 1)    │  │ (automático) │
                │              │  │              │
                └──────┬───────┘  └──────┬───────┘
                       │                 │
                       └────(fin)────────┘
                           │
                           ▼
                   ┌────────────────┐
                   │ FIN (si ✅)    │
                   │ 0 vuelos      │
                   └────────────────┘
```

---

## Diagrama 2: Flujo de Ticks Automáticos

```
┌──────────────────────────────────────────────────────────────┐
│                   AUTO TICKS WORKFLOW                         │
└──────────────────────────────────────────────────────────────┘

Click "▶️ Auto Tick"
       │
       ▼
┌─────────────────────────────┐
│ _toggle_auto_ticks()        │
│ - auto_ticks_activos=True   │
│ - Deshabilita botones       │
│ - Llama _programar_proximo_tick()
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│ _programar_proximo_tick()   │ ◄────────────────────┐
│                             │                      │
│ 1. Verifica hay_vuelos      │ (RECURSIVO)          │
│ 2. Si SÍ:                   │                      │
│    - Ejecuta _ejecutar_tick()                      │
│    - Calcula delay = 1000/velocidad_tick           │
│    - Agenda: after(delay, _programar_proximo_tick) ─┘
│ 3. Si NO:                   │
│    - Llama _toggle_auto_ticks() (pausa)
│    - Muestra "✅ Completado"
└─────────────────────────────┘
             │
             ▼
         [BUCLE]
    Se ejecuta cada:
    - 1000ms (velocidad=1.0)
    - 500ms  (velocidad=2.0)
    - 1500ms (velocidad=0.5)
             │
       (hasta fin)
             │
             ▼
Click "⏸️ Pausar"
       │
       ▼
┌─────────────────────────────┐
│ _toggle_auto_ticks()        │
│ - auto_ticks_activos=False  │
│ - after_cancel(after_id)    │
│ - Habilita botones de nuevo │
└─────────────────────────────┘
```

---

## Diagrama 3: Ejecución de Un Tick (Ciclo)

```
┌──────────────────────────────────────────────────────┐
│            EJECUCIÓN DE UN TICK (_ejecutar_tick)    │
└──────────────────────────────────────────────────────┘

START
  │
  ├─→ manager.simular_ciclo()
  │   ▼
  │   ┌─────────────────────────────┐
  │   │ BACKEND PROCESA:            │
  │   │ - Decrementa tiempo_despegue│
  │   │ - Incrementa tiempo_espera  │
  │   │ - Retorna evento con:       │
  │   │   * ciclo: número           │
  │   │   * despegues: [vuelos]    │
  │   │   * movimientos_espera: [] │
  │   └─────────────────────────────┘
  │
  ├─→ self.ciclo_actual = evento["ciclo"]
  │   (ej: ciclo_actual = 47)
  │
  ├─→ self.lbl_ciclo.config(text="Ciclo: 47")
  │   ▼
  │   ┌─────────────────────────────┐
  │   │ UI ACTUALIZA                │
  │   │ "Ciclo: 47" visible en      │
  │   │ pantalla                    │
  │   └─────────────────────────────┘
  │
  ├─→ self._log(f"[⏱️ Ciclo 47]", "sim")
  │   (muestra en log)
  │
  ├─→ FOR cada vuelo EN despegues:
  │   │   self._log(f"[🛫] {vuelo} despegó")
  │   │   (ej: "[🛫] Vuelo-001 despegó")
  │
  ├─→ FOR cada (vuelo, pista) EN movimientos:
  │   │   self._log(f"[→] {vuelo} pasó a {pista}")
  │   │   (ej: "[→] Vuelo-045 pasó a Pista 2")
  │
  ├─→ espera = manager.get_lista_espera()
  │   ├─→ SI espera NO ESTÁ VACÍA:
  │   │   self._log(f"⏳ Esperando: Vuelo-006(4s), Vuelo-007(5s)")
  │
  ├─→ self._refresh_all()
  │   ▼
  │   ┌──────────────────────────────┐
  │   │ UI REFRESCA COMPLETAMENTE:   │
  │   │                              │
  │   │ _refresh_pistas():           │
  │   │ ├─ Actualiza cada celda      │
  │   │ ├─ Muestra ⏱️N (countdown)   │
  │   │ ├─ Marca frente/ocupado      │
  │   │                              │
  │   │ _refresh_espera():           │
  │   │ ├─ Actualiza lista espera    │
  │   │ ├─ Muestra ⏳Ns acumulados   │
  │   │ ├─ Cuenta orden vuelos       │
  │   │                              │
  │   │ _refresh_punteros():         │
  │   │ └─ Info de frente/final      │
  │   └──────────────────────────────┘
  │
  └─→ return (fin de tick)
```

---

## Diagrama 4: Progresión Visual de Un Vuelo

```
ESCENARIO: Vuelo-001 registrado con tiempo_despegue=3

┌──────────────────────────────────────────────────────────┐
│                 PISTA 1 - VISUALIZACIÓN                  │
└──────────────────────────────────────────────────────────┘

[CICLO 0 - Estado inicial]
    ┌────────────┐
    │     ✈      │
    │  Vuelo-001 │  ← Acaba de registrarse
    │   ⏱️3      │  ← Despegará en 3 ciclos
    └────────────┘

[CICLO 1 - Primer tick]
    backend.simular_ciclo():
      - Decrementa: tiempo_despegue = 3 - 1 = 2
    
    Visualización actualizada:
    ┌────────────┐
    │     ✈      │
    │  Vuelo-001 │
    │   ⏱️2      │  ← Ahora: 2 ciclos
    └────────────┘

[CICLO 2 - Segundo tick]
    backend.simular_ciclo():
      - Decrementa: tiempo_despegue = 2 - 1 = 1
    
    Visualización:
    ┌────────────┐
    │     ✈      │
    │  Vuelo-001 │
    │   ⏱️1      │  ← Ahora: 1 ciclo
    └────────────┘

[CICLO 3 - Tercer tick] ⭐ DESPEGUE
    backend.simular_ciclo():
      - Decrementa: tiempo_despegue = 1 - 1 = 0
      - Detecta tiempo_despegue <= 0
      - DESPEGA: Evento tiene [Vuelo-001] en despegues[]
      - Remueve de pista
    
    Log muestra: "[🛫] Vuelo-001 despegó"
    
    Visualización:
    ┌────────────┐
    │   LIBRE    │  ← Celda queda vacía
    └────────────┘
```

---

## Diagrama 5: Progresión de Vuelo en Espera

```
ESCENARIO: Vuelo-045 entra a espera (pistas llenas)

┌──────────────────────────────────────────────────────────┐
│         LISTA DE ESPERA - VISUALIZACIÓN                  │
└──────────────────────────────────────────────────────────┘

[CICLO 5 - Entra a espera]
    Acción: registrar_vuelo() pero pistas llenas
    
    Backend:
      - Agrega a lista_espera
      - tiempo_espera = 0 (acaba de llegar)
    
    Visualización:
    ► 1. Vuelo-045
      ⏳ 0s          ← Espera cero segundos al llegar

[CICLO 6 - Espera aumenta]
    backend.simular_ciclo():
      - Incrementa tiempo_espera de todos en espera: 0 + 1 = 1
    
    Visualización:
    ► 1. Vuelo-045
      ⏳ 1s          ← Lleva 1 segundo esperando

[CICLO 7]
    backend.simular_ciclo():
      - Un vuelo despegó en pista
      - Hay espacio libre
      - eventos["movimientos_espera"] contiene (Vuelo-045, Pista-1)
      - Vuelo-045 se mueve a Pista-1 con nuevo tiempo_despegue
    
    Log muestra: "[→] Vuelo-045 pasó a Pista-1"
    
    Visualización:
    ┌────────────┐
    │     ✈      │
    │  Vuelo-045 │  ← Se mueve a pista
    │   ⏱️4      │  ← Nuevo tiempo de despegue
    └────────────┘
```

---

## Diagrama 6: Control de Velocidad

```
VELOCIDAD = 0.5x
├─ delay = 1000 / 0.5 = 2000ms
├─ 1 tick cada 2 segundos
└─ LENTO ━━━━━░░

VELOCIDAD = 1.0x (DEFAULT)
├─ delay = 1000 / 1.0 = 1000ms
├─ 1 tick por segundo
└─ NORMAL ━━━┃━━━

VELOCIDAD = 2.0x
├─ delay = 1000 / 2.0 = 500ms
├─ 2 ticks por segundo
└─ RÁPIDO ━━┃┃┃━

VELOCIDAD = 3.0x
├─ delay = 1000 / 3.0 = 333ms
├─ 3 ticks por segundo
└─ MUY RÁPIDO ┃┃┃┃┃

Cambiar velocidad EN VIVO:
  [Slider: ═════════════════░═══ 1.5x]
                    ↑
                 Usuario mueve
                    │
                    ▼
         self.velocidad_tick = 1.5
                    │
                    ▼
        Próximo after() usa:
        delay = 1000 / 1.5 = 667ms
```

---

## Diagrama 7: Fin Automático

```
┌──────────────────────────────────────────────────────────┐
│            DETECCIÓN AUTOMÁTICA DE FIN                   │
└──────────────────────────────────────────────────────────┘

Auto Ticks corriendo...
            │
            ├─→ _programar_proximo_tick()
            │   │
            │   ├─→ pistas = manager.get_pistas()
            │   │
            │   ├─→ espera = manager.get_lista_espera()
            │   │
            │   ├─→ hay_vuelos = any(pista contiene vuelo) OR espera NO vacía
            │   │
            │   ├─→ IF hay_vuelos:
            │   │     - _ejecutar_tick()
            │   │     - Programa siguiente after()
            │   │
            │   └─→ ELSE:
            │         - self._toggle_auto_ticks()  ← PAUSA automática
            │         - self._log("✅ Completado")
            │         - Botón cambia: "⏸️" → "▶️"
            │         - Habilita otros botones
            │
            ▼
    Sistema DETIENE solo cuando:
    ✓ Todas las pistas están vacías AND
    ✓ Lista de espera está vacía
    
    = No hay más trabajo que hacer
```

---

## Diagrama 8: Estado de Botones Según Contexto

```
┌────────────────────────────────────────────────────────────┐
│              MATRIZ DE ESTADO DE BOTONES                   │
└────────────────────────────────────────────────────────────┘

ESTADO: ESPERA (Inicial)
┌─────────────────────────────┐
│ ✚ Registrar     ✓ Habilitado │
│ 🛫 Despegar     ✓ Habilitado │
│ ➡️ Next Tick     ✓ Habilitado │
│ ▶️ Auto Tick     ✓ Habilitado │
│ ⚡ Simulación   ✓ Habilitado │
└─────────────────────────────┘

ESTADO: REGISTRANDO 15 VUELOS
┌─────────────────────────────┐
│ ✚ Registrar     ✗ Deshabilitado │
│ 🛫 Despegar     ✗ Deshabilitado │
│ ➡️ Next Tick     ✗ Deshabilitado │
│ ▶️ Auto Tick     ✗ Deshabilitado │
│ ⚡ Simulación   ✗ Deshabilitado │
│ (espera 5s...)              │
└─────────────────────────────┘

ESTADO: TICKS MANUALES (Next Tick activo)
┌─────────────────────────────┐
│ ✚ Registrar     ✓ Habilitado │
│ 🛫 Despegar     ✓ Habilitado │
│ ➡️ Next Tick     ✓ Habilitado │
│ ▶️ Auto Tick     ✓ Habilitado │ ← Puedes iniciar Auto
│ ⚡ Simulación   ✓ Habilitado │
└─────────────────────────────┘

ESTADO: TICKS AUTOMÁTICOS (Auto Tick corriendo)
┌─────────────────────────────┐
│ ✚ Registrar     ✗ Deshabilitado │
│ 🛫 Despegar     ✗ Deshabilitado │
│ ➡️ Next Tick     ✗ Deshabilitado │
│ ▶️ Auto Tick → ⏸️ Pausar    │ ← Cambia a "Pausar"
│ ⚡ Simulación   ✗ Deshabilitado │
│ [Slider]        ✓ Habilitado │ ← Control de velocidad
└─────────────────────────────┘

ESTADO: AUTO PAUSADO (Durante Auto → Presionó Pausar)
┌─────────────────────────────┐
│ ✚ Registrar     ✓ Habilitado │
│ 🛫 Despegar     ✓ Habilitado │
│ ➡️ Next Tick     ✓ Habilitado │ ← Puedes avanzar manual
│ ⏸️ Pausar → ▶️ Auto Tick     │ ← Cambia a "Auto" de nuevo
│ ⚡ Simulación   ✓ Habilitado │
└─────────────────────────────┘
```

---

## Diagrama 9: Flujo de Usuarios (Casos de Uso)

```
┌────────────────────────────────────────────────────────┐
│           FLUJOS DE USUARIO TÍPICOS                    │
└────────────────────────────────────────────────────────┘

─── CASO 1: DEBUG PASO A PASO ───
1. Clic "⚡ Simulación (15 vuelos)"
   └─→ [Espera 5 segundos registro]
2. Clic "➡️ Next Tick" (5 veces)
   └─→ Observa 5 ciclos, uno por uno
3. Clic "➡️ Next Tick" (cuando quiera parar)
4. Usa manual "🛫 Despegar Vuelo" si lo necesita


─── CASO 2: SIMULACIÓN RÁPIDA ───
1. Clic "⚡ Simulación (15 vuelos)"
   └─→ [Espera 5 segundos]
2. Mueve slider a 3.0x (velocidad máxima)
3. Clic "▶️ Auto Tick"
   └─→ Sistema completa en ~5-10 segundos
4. Se detiene automáticamente


─── CASO 3: TICKS AUTOMÁTICOS CON PAUSA ───
1. Clic "⚡ Simulación"
2. Clic "▶️ Auto Tick"
3. Después 10 ciclos, clic "⏸️ Pausar"
4. Usa "➡️ Next Tick" para avanzar controladamente
5. Clic "▶️ Auto Tick" de nuevo para reanudar velocidad


─── CASO 4: MEZCLA MANUAL Y AUTOMÁTICO ───
1. Registra vuelos manualmente (✚ Registrar)
2. Algunos ticks manuales: "➡️ Next Tick"
3. Despega uno manualmente: "🛫 Despegar"
4. Inicia auto ticks: "▶️ Auto Tick"
5. Pausa y despega otro: "⏸️" → "🛫" → "▶️"
```

---

## Diagrama 10: Ciclo de Vida Completo

```
┌──────────────────────────────────────────────────────────┐
│              CICLO DE VIDA COMPLETO                      │
└──────────────────────────────────────────────────────────┘

 [APP INICIA]
     │
     ├─→ __init__()
     │   ├─ self.auto_ticks_activos = False
     │   ├─ self.ciclo_actual = 0
     │   ├─ self.velocidad_tick = 1.0
     │   └─ self.after_id = None
     │
     ├─→ _build_ui()
     │   ├─ Crea botones
     │   ├─ Crea slider
     │   └─ Inicializa labels
     │
     └─→ mainloop()
         │
         ├─→ Usuario hace clic en "⚡ Simulación"
         │   │
         │   └─→ iniciar_simulacion()
         │       └─→ _registrar_vuelos_iterativamente()
         │           └─→ (15 veces) after(300ms, ...)
         │               └─→ registrar_vuelo() + after()
         │
         ├─→ [5 segundos después] _habilitar_ticks_para_simulacion()
         │   └─→ Botones "➡️ Next Tick" y "▶️ Auto" habilitados
         │
         ├─→ Usuario elige: "➡️ Next Tick" O "▶️ Auto Tick"
         │   │
         │   ├─→ SI "➡️ Next Tick":
         │   │   └─→ _next_tick_manual()
         │   │       └─→ _ejecutar_tick()
         │   │           └─→ [vuelve a esperar click]
         │   │
         │   └─→ SI "▶️ Auto Tick":
         │       └─→ _toggle_auto_ticks() (inicia)
         │           └─→ _programar_proximo_tick() [recursivo]
         │               ├─→ _ejecutar_tick()
         │               ├─→ after(delay, _programar_proximo_tick)
         │               ├─→ [delay] ejecuta
         │               ├─→ recursión hasta fin
         │               └─→ _toggle_auto_ticks() (pausa) ✅
         │
         ├─→ [Cualquier momento] Usuario clic "⏸️ Pausar"
         │   └─→ _toggle_auto_ticks() (pausa)
         │       ├─ after_cancel(after_id)
         │       ├─ Botones se habilitan
         │       └─→ [vuelve a esperar]
         │
         └─→ [Fin proceso] Usuario close ventana
             └─→ mainloop() = exit()

```

---

## Conclusión

Este sistema de ticks permite **máximo control** sobre la simulación:
- ✅ Manual completo (step-by-step)
- ✅ Automático completo (fast-forward)
- ✅ Híbrido (mezcla)
- ✅ Pausable en cualquier momento
- ✅ Ajuste de velocidad en vivo
- ✅ Visualización de countdown
- ✅ Detención automática inteligente

