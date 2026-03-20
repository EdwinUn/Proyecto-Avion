"""
Script de prueba para validar funcionamiento de Aeropuerto con sistema de ticks.
"""

from backend import Aeropuerto


def prueba_basica_simulacion():
    """Prueba basica: registrar vuelos y simular ciclos"""
    print("\n" + "="*70)
    print("PRUEBA 1: Simulacion Basica (10 ciclos)")
    print("="*70)
    
    aeropuerto = Aeropuerto()
    
    # Registrar 8 vuelos (6 en pistas, 2 en espera)
    for i in range(8):
        vuelo, estado = aeropuerto.registrar_vuelo()
        if vuelo:
            print("[OK] {}: {} (T_prep={})".format(vuelo.nombre, estado, vuelo.tiempo_preparacion))
        else:
            print("[X] Vuelo rechazado")
    
    print("\n" + "-"*70)
    print("SIMULACION: 10 ciclos")
    print("-"*70 + "\n")
    
    for ciclo in range(10):
        print(">> CICLO {}:".format(ciclo))
        
        # Simular
        aeropuerto.simular_ciclo()
        
        # Mostrar estado
        for pista in aeropuerto.pistas:
            vuelos_str = " -> ".join(["{}(T:{})".format(v.nombre, v.tiempo_preparacion) for v in pista.listar()]) or "[vacia]"
            print("  {}: [{}/{}] {}".format(pista.nombre, pista.tamaño, pista.capacidad, vuelos_str))
        
        espera_str = " -> ".join(["{}(E:{})".format(v.nombre, v.tiempo_espera_acumulado) for v in aeropuerto.lista_espera]) or "[vacia]"
        print("  Espera: [{}/{}] {}".format(len(aeropuerto.lista_espera), aeropuerto.MAX_CAPACIDAD_ESPERA, espera_str))
        
        # Eventos
        eventos = aeropuerto.get_eventos_ciclo()
        if eventos["despegues"]:
            print("  [DESPEGUES] {}".format(", ".join([v.nombre for v in eventos['despegues']])))
        if eventos["movimientos_espera"]:
            print("  [MOVIMIENTOS] {}".format(", ".join([v.nombre for v in eventos['movimientos_espera']])))
        
        print()
    
    # Estadísticas finales
    stats = aeropuerto.obtener_estadisticas()
    print("-"*70)
    print("ESTADISTICAS FINALES:")
    print("  Ciclos simulados: {}".format(stats['ciclos_simulados']))
    print("  Total asignados: {}".format(stats['total_asignados']))
    print("  Total despegues: {}".format(stats['total_despegues']))
    print("  Total rechazos: {}".format(stats['total_rechazos']))
    print("  Vuelos en sistema: {}".format(stats['vuelos_en_sistema']))
    print("  Tasa rechazo: {:.1f}%".format(stats['tasa_rechazo_pct']))
    print("-"*70)
    
    return aeropuerto


def prueba_limite_espera():
    """Prueba 2: Verificar limite de capacidad en lista de espera"""
    print("\n" + "="*70)
    print("PRUEBA 2: Limite de Capacidad en Lista de Espera")
    print("="*70)
    
    aeropuerto = Aeropuerto()
    
    for i in range(18):
        vuelo, estado = aeropuerto.registrar_vuelo()
        if vuelo:
            print("  {:2d}. {}: {}".format(i+1, vuelo.nombre, estado))
        else:
            print("  {:2d}. Vuelo RECHAZADO".format(i+1))
    
    print("\n" + "-"*70)
    print("Final: {} asignados, {} rechazos".format(aeropuerto.total_asignados, aeropuerto.total_rechazos))
    print("Vuelos en pistas: {}".format(sum(p.tamaño for p in aeropuerto.pistas)))
    print("Vuelos en espera: {}".format(len(aeropuerto.lista_espera)))
    print("-"*70)
    
    return aeropuerto


def prueba_round_robin_despegues():
    """Prueba 3: Verificar Round-Robin en despegues"""
    print("\n" + "="*70)
    print("PRUEBA 3: Round-Robin en Despegues (Fairness)")
    print("="*70)
    
    aeropuerto = Aeropuerto()
    
    # Registrar 15 vuelos (saturar sistema)
    for i in range(15):
        aeropuerto.registrar_vuelo()
    
    print("Sistema inicializado con 15 vuelos")
    print("Pistas: {}, Espera: {}\n".format(sum(p.tamaño for p in aeropuerto.pistas), len(aeropuerto.lista_espera)))
    
    # Simular y rastrear despegues
    for ciclo in range(20):
        aeropuerto.simular_ciclo()
        
        # Rastrear de cuál pista despegaron
        eventos = aeropuerto.get_eventos_ciclo()
        for vuelo in eventos["despegues"]:
            print("  Ciclo {}: {} despego".format(ciclo, vuelo.nombre))
    
    print("\n" + "-"*70)
    stats = aeropuerto.obtener_estadisticas()
    print("Total despegues: {}".format(stats['total_despegues']))
    print("Vuelos restantes en pistas: {}".format(stats['vuelos_en_sistema']))
    print("-"*70)
    
    return aeropuerto


def prueba_fifo_espera():
    """Prueba 4: Verificar que movimientos desde espera respetan FIFO"""
    print("\n" + "="*70)
    print("PRUEBA 4: FIFO en Movimientos desde Espera")
    print("="*70)
    
    aeropuerto = Aeropuerto()
    
    # Registrar 18 vuelos: 15 en pistas/espera, 3 adicionales
    nombres_espera = []
    for i in range(18):
        vuelo, estado = aeropuerto.registrar_vuelo()
        if estado == "en_espera":
            nombres_espera.append(vuelo.nombre)
            print("  {:2d}. {} -> ESPERA".format(i+1, vuelo.nombre))
        else:
            print("  {:2d}. {} -> {}".format(i+1, vuelo.nombre, estado))
    
    print("\nVuelos en espera (en orden FIFO): {}".format(nombres_espera))
    print("\n" + "-"*70)
    print("Simulando 15 ciclos...")
    print("-"*70 + "\n")
    
    orden_movimientos = []
    for ciclo in range(15):
        aeropuerto.simular_ciclo()
        eventos = aeropuerto.get_eventos_ciclo()
        
        for vuelo in eventos["movimientos_espera"]:
            orden_movimientos.append(vuelo.nombre)
            print("  Ciclo {}: {} movido de espera a pista".format(ciclo, vuelo.nombre))
    
    print("\n" + "-"*70)
    print("Verificacion FIFO:")
    print("  Orden esperado: {}".format(nombres_espera))
    print("  Orden real:     {}".format(orden_movimientos))
    
    if orden_movimientos == nombres_espera[:len(orden_movimientos)]:
        print("  [OK] FIFO CORRECTO")
    else:
        print("  [ERROR] FIFO INCORRECTO")
    print("-"*70)
    
    return aeropuerto


def prueba_integridad():
    """Prueba 5: Validar integridad del sistema"""
    print("\n" + "="*70)
    print("PRUEBA 5: Validacion de Integridad del Sistema")
    print("="*70)
    
    aeropuerto = Aeropuerto()
    
    # Registrar y simular
    for i in range(20):
        aeropuerto.registrar_vuelo()
    
    print("Ejecutando 25 ciclos...")
    for ciclo in range(25):
        aeropuerto.simular_ciclo()
    
    print("\n" + "-"*70)
    valido = aeropuerto.validar_integridad()
    print("Validacion de integridad: {}".format("[OK] VALIDO" if valido else "[ERROR] INVALIDO"))
    
    stats = aeropuerto.obtener_estadisticas()
    print("\nEstadisticas:")
    print("  Total procesados: {}".format(stats['total_procesados']))
    print("  Total despegues: {}".format(stats['total_despegues']))
    print("  Vuelos en sistema: {}".format(stats['vuelos_en_sistema']))
    print("  Total en pistas + espera: {}".format(sum(p.tamaño for p in aeropuerto.pistas) + len(aeropuerto.lista_espera)))
    print("-"*70)
    
    return aeropuerto


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("  PRUEBAS DEL SISTEMA DE GESTION DE VUELOS - AEROPUERTO")
    print("#"*70)
    
    try:
        prueba_basica_simulacion()
        prueba_limite_espera()
        prueba_round_robin_despegues()
        prueba_fifo_espera()
        prueba_integridad()
        
        print("\n" + "#"*70)
        print("  [OK] TODAS LAS PRUEBAS COMPLETADAS")
        print("#"*70 + "\n")
        
    except Exception as e:
        print("\n[ERROR] ERROR durante pruebas: {}".format(e))
        import traceback
        traceback.print_exc()
