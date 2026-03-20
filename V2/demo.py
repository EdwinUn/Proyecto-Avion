"""
Demostración: Sistema de Gestión de Vuelos en Aeropuerto
Muestra un ejemplo práctico completo de la simulación
"""

from backend import Aeropuerto


def demostración():
    print("\n" + "="*80)
    print("  SISTEMA DE GESTION DE VUELOS EN AEROPUERTO - DEMO")
    print("="*80 + "\n")
    
    # Crear aeropuerto
    aeropuerto = Aeropuerto()
    print("[INIT] Aeropuerto creado con {} pistas, capacidad {} vuelos/pista".format(
        aeropuerto.NUM_PISTAS, aeropuerto.CAPACIDAD_PISTA))
    print("[INFO] Limite lista espera: {} vuelos".format(aeropuerto.MAX_CAPACIDAD_ESPERA))
    print("[INFO] Tiempo preparacion: {}-{} ciclos".format(
        aeropuerto.TIEMPO_PREPARACION_MIN, aeropuerto.TIEMPO_PREPARACION_MAX))
    
    # Fase 1: Registrar vuelos
    print("\n" + "-"*80)
    print("FASE 1: Registrando 20 vuelos...")
    print("-"*80 + "\n")
    
    for i in range(20):
        vuelo, estado = aeropuerto.registrar_vuelo()
        if vuelo:
            print("[{:2d}] {} registrado - Estado: {}".format(i+1, vuelo.nombre, estado))
        else:
            print("[{:2d}] RECHAZADO - lista espera llena".format(i+1))
    
    # Fase 2: Estado inicial
    print("\n" + "-"*80)
    print("ESTADO DEL SISTEMA (Ciclo 0):")
    print("-"*80)
    
    print("\nDETALLE DE PISTAS:")
    for pista in aeropuerto.pistas:
        vuelos = pista.listar()
        if vuelos:
            print("  {}: {}".format(
                pista.nombre,
                " | ".join(["{} (T:{})".format(v.nombre, v.tiempo_preparacion) for v in vuelos])
            ))
        else:
            print("  {}: [vacia]".format(pista.nombre))
    
    if aeropuerto.lista_espera:
        print("\nVUELOS EN ESPERA (Ciclo 0):")
        for v in aeropuerto.lista_espera:
            print("  {}".format(v.nombre))
    
    # Fase 3: Simulación
    print("\n" + "-"*80)
    print("FASE 2: Simulación (30 ciclos)...")
    print("-"*80 + "\n")
    
    despegues_totales = []
    movimientos_totales = []
    
    for ciclo in range(30):
        aeropuerto.simular_ciclo()
        eventos = aeropuerto.get_eventos_ciclo()
        
        if eventos["despegues"] or eventos["movimientos_espera"]:
            print("CICLO {}: ".format(ciclo), end="")
            
            if eventos["despegues"]:
                print("[DESPEGUES: {}] ".format(
                    ", ".join([v.nombre for v in eventos['despegues']])), end="")
                despegues_totales.extend(eventos["despegues"])
            
            if eventos["movimientos_espera"]:
                print("[ASIGNADOS: {}]".format(
                    ", ".join([v.nombre for v in eventos['movimientos_espera']])), end="")
                movimientos_totales.extend(eventos["movimientos_espera"])
            
            print()
    
    # Fase 4: Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL DE SIMULACION")
    print("="*80)
    
    stats = aeropuerto.obtener_estadisticas()
    
    print("\nESTADISTICAS:")
    print("  Ciclos simulados: {}".format(stats['ciclos_simulados']))
    print("  Total vuelos procesados: {}".format(stats['total_procesados']))
    print("  Total vuelos asignados: {}".format(stats['total_asignados']))
    print("  Total vuelos despegados: {}".format(stats['total_despegues']))
    print("  Total vuelos rechazados: {}".format(stats['total_rechazos']))
    print("  Tasa rechazo: {:.1f}%".format(stats['tasa_rechazo_pct']))
    
    print("\nESTADO ACTUAL DEL SISTEMA:")
    print("  Vuelos en pistas: {}".format(stats['vuelos_en_sistema']))
    print("  Pistas ocupadas: {}/{}".format(stats['pistas_ocupadas'], aeropuerto.NUM_PISTAS))
    print("  Vuelos en lista espera: {}/{}".format(
        stats['lista_espera_ocupada'], aeropuerto.MAX_CAPACIDAD_ESPERA))
    
    print("\nDETALLE FINAL DE PISTAS:")
    for pista in aeropuerto.pistas:
        vuelos = pista.listar()
        if vuelos:
            print("  {}: {}".format(
                pista.nombre,
                " -> ".join(["{} (T:{})".format(v.nombre, v.tiempo_preparacion) for v in vuelos])
            ))
        else:
            print("  {}: [vacia]".format(pista.nombre))
    
    if aeropuerto.lista_espera:
        print("\nVUELOS AUN EN ESPERA:")
        for v in aeropuerto.lista_espera:
            print("  {} (esperando {} ciclos)".format(v.nombre, v.tiempo_espera_acumulado))
    
    print("\n" + "="*80)
    print("FIN DE LA DEMOSTRACION")
    print("="*80 + "\n")


if __name__ == "__main__":
    demostración()
