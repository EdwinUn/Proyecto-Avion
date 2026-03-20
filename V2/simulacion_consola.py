"""
Simulacion en Consola - Sistema de Gestion de Vuelos
Demuestra el funcionamiento completo del sistema sin interfaz grafica.

Características:
- Simulacion automatica con 15 vuelos
- Ciclos de tiempo donde se procesan despegues y movimientos de espera
- Visualizacion clara del estado del sistema en cada ciclo
"""

from backend import Vuelo, ColaCircular, AeropuertoManager
import time


def limpiar_pantalla():
    """Limpia la pantalla de consola"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_estado_pistas(manager):
    """Muestra el estado visual de todas las pistas"""
    print("\n" + "="*80)
    print("|  ESTADO DE PISTAS  |")
    print("="*80)
    
    for pista in manager.get_pistas():
        print(f"\n{pista.nombre:<15} Vuelos: {pista.tamaño}/{pista.capacidad}", end="")
        
        # Visualizacion grafica
        slots = pista.get_slots()
        print(f"  | ", end="")
        
        for i, vuelo in enumerate(slots):
            if vuelo is None:
                print(f"[    ]", end=" ")
            else:
                # Mostrar diferente si es frente
                es_frente = (i == pista.frente and not pista.esta_vacia())
                marcador = ">" if es_frente else " "
                print(f"[{marcador}{vuelo.nombre}{marcador}]", end=" ")
        
        # Info de punteros
        siguiente = pista.siguiente()
        sig_info = f"(Prox: {siguiente.nombre}, {siguiente.tiempo_despegue}s)" if siguiente else "(vacia)"
        print(f"| {sig_info}")
        print(f"  Punteros: frente={pista.frente}  final={pista.final}")


def mostrar_lista_espera(manager):
    """Muestra la lista de espera con tiempos"""
    lista = manager.get_lista_espera()
    espacio = manager.max_lista_espera - len(lista)
    
    print(f"\n{'='*80}")
    print(f"|  LISTA DE ESPERA ({len(lista)}/{manager.max_lista_espera})  |")
    print(f"{'='*80}")
    
    if not lista:
        print("  [VACIA]")
    else:
        for i, vuelo in enumerate(lista, 1):
            print(f"  {i:2}. {vuelo.nombre:<10} Tiempo en espera: {vuelo.tiempo_espera}s")
    
    print(f"\n  Espacios disponibles: {espacio}/{manager.max_lista_espera}")


def mostrar_estadisticas(manager):
    """Muestra estadisticas de la simulacion"""
    print(f"\n{'='*80}")
    print(f"|  ESTADISTICAS  |")
    print(f"{'='*80}")
    print(f"  Ciclo actual: {manager.ciclo_actual}")
    print(f"  Total despegues: {manager.total_despegues}")
    print(f"  Total rechazos: {manager.total_rechazos}")
    print(f"  Vuelos generados: {manager.contador_vuelo - 1}")


def simular():
    """Ejecuta la simulacion completa"""
    print("\n")
    print("+" + "="*78 + "+")
    print("|" + " "*78 + "|")
    print("|" + "  SISTEMA DE GESTION DE VUELOS - SIMULACION EN CONSOLA".center(78) + "|")
    print("|" + " "*78 + "|")
    print("+" + "="*78 + "+")
    
    # Inicializar manager
    print("\n[INICIALIZANDO SISTEMA]")
    print("  * 3 pistas de despegue (capacidad 5 cada una)")
    print("  * Lista de espera: maximo 10 vuelos")
    print("  * Tiempo de despegue por defecto: 3 ciclos")
    
    manager = AeropuertoManager(
        num_pistas=3,
        capacidad_pista=5,
        max_lista_espera=10,
        tiempo_despegue=3
    )
    
    input("\nPresiona ENTER para comenzar...")
    
    # FASE 1: Registrar 15 vuelos
    print("\n" + "*"*80)
    print("FASE 1: REGISTRANDO 15 VUELOS")
    print("*"*80)
    
    # Crear manager
    manager = AeropuertoManager(
        num_pistas=3,
        capacidad_pista=5,
        max_lista_espera=10,
        tiempo_despegue=3
    )
    
    for i in range(15):
        vuelo, pista = manager.registrar_vuelo()
        
        if pista:
            estado = f"[+] {vuelo.nombre:8} -> {pista.nombre}"
        elif len(manager.get_lista_espera()) < manager.max_lista_espera:
            estado = f"[!] {vuelo.nombre:8} -> Lista de Espera"
        else:
            estado = f"[X] {vuelo.nombre:8} -> RECHAZADO (lista llena)"
        
        print(f"  Vuelo {i+1:2}: {estado}")
        time.sleep(0.3)
    
    mostrar_estado_pistas(manager)
    mostrar_lista_espera(manager)
    mostrar_estadisticas(manager)
    
    input("\nPresiona ENTER para iniciar ciclos de simulación...")
    
    # FASE 2: Ejecutar ciclos de simulación
    print("\n" + "*"*80)
    print("FASE 2: SIMULACIÓN POR CICLOS")
    print("*"*80)
    
    ciclo_count = 0
    max_ciclos = 25
    
    while ciclo_count < max_ciclos:
        # Verificar si hay vuelos pendientes
        pistas = manager.get_pistas()
        espera = manager.get_lista_espera()
        hay_vuelos = any(not p.esta_vacia() for p in pistas) or len(espera) > 0
        
        if not hay_vuelos:
            print("\n✓ Todos los vuelos han despegado o salido del sistema")
            break
        
        # Ejecutar ciclo
        evento = manager.simular_ciclo()
        ciclo_count += 1
        
        print(f"\n{'─'*80}")
        print(f"[CICLO {evento['ciclo']}]")
        print(f"{'─'*80}")
        
        # Mostrar despegues
        if evento["despegues"]:
            for vuelo in evento["despegues"]:
                print(f"  [DESPEGUE] {vuelo.nombre} despego")
        
        # Mostrar movimientos de espera
        if evento["movimientos_espera"]:
            for vuelo, pista in evento["movimientos_espera"]:
                print(f"  [MOVIMIENTO] {vuelo.nombre} paso a {pista.nombre} (desde lista de espera)")
        
        # Mostrar estado
        print(f"\n  Estado actual:")
        for pista in pistas:
            print(f"    {pista.nombre}: {pista.tamaño}/{pista.capacidad} vuelos", end="")
            if not pista.esta_vacia():
                siguiente = pista.siguiente()
                print(f"  (Prox: {siguiente.nombre}, {siguiente.tiempo_despegue}s)")
            else:
                print(" (vacia)")
        
        if espera:
            vuelos_espera_str = ", ".join([f"{v.nombre}({v.tiempo_espera}s)" for v in espera])
            print(f"    Espera: {vuelos_espera_str}")
        else:
            print(f"    Espera: vacia")
        
        time.sleep(1)  # Pausa de 1 segundo entre ciclos
    
    # FASE 3: Resumen final
    print("\n" + "*"*80)
    print("SIMULACION FINALIZADA")
    print("*"*80)
    
    mostrar_estadisticas(manager)
    
    print(f"\n{'='*80}")
    print(f"|  RESUMEN FINAL  |")
    print(f"{'='*80}")
    print(f"  * Ciclos ejecutados: {ciclo_count}")
    print(f"  * Vuelos despegados exitosamente: {manager.total_despegues}")
    print(f"  * Vuelos rechazados: {manager.total_rechazos}")
    print(f"  * Eficiencia: {(manager.total_despegues / 15) * 100:.1f}%")
    
    # Verificar si quedan vuelos
    if len(manager.get_lista_espera()) > 0:
        print(f"\n  [ADVERTENCIA] {len(manager.get_lista_espera())} vuelo(s) aun en espera")
    
    print(f"\n")


if __name__ == "__main__":
    try:
        simular()
    except KeyboardInterrupt:
        print("\n\n[SIMULACION INTERRUMPIDA POR USUARIO]")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
