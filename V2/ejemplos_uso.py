"""
Ejemplo Simple - Sistema de Gestión de Vuelos

Demuestra cómo usar el sistema de forma básica.
"""

from backend import AeropuertoManager
import time


def ejemplo_basico():
    """Ejemplo 1: Operación manual básica"""
    print("\n" + "="*70)
    print("EJEMPLO 1: Operación Manual Básica")
    print("="*70 + "\n")
    
    # Crear aeropuerto personalizado
    manager = AeropuertoManager(
        num_pistas=2,           # Solo 2 pistas
        capacidad_pista=3,      # Capacidad menor para demostración
        max_lista_espera=5,     # Límite de espera pequeño
        tiempo_despegue=2       # Despegue más rápido (2 ciclos)
    )
    
    # Registrar algunos vuelos
    print("Registrando 8 vuelos... (con 2 pistas de capacidad 3)\n")
    for i in range(8):
        vuelo, pista = manager.registrar_vuelo()
        status = f"-> {pista.nombre}" if pista else "-> ESPERA"
        print(f"  {i+1}. {vuelo.nombre:<8} {status}")
    
    # Mostrar estado
    print("\nEstado después de registros:")
    for pista in manager.get_pistas():
        print(f"  {pista.nombre}: {[v.nombre for v in pista.get_slots() if v]}")
    
    espera = manager.get_lista_espera()
    print(f"  Lista espera: {[v.nombre for v in espera]}")


def ejemplo_ciclos():
    """Ejemplo 2: Simulación con ciclos"""
    print("\n" + "="*70)
    print("EJEMPLO 2: Simulación por Ciclos")
    print("="*70 + "\n")
    
    manager = AeropuertoManager(
        num_pistas=2,
        capacidad_pista=2,
        max_lista_espera=3,
        tiempo_despegue=2
    )
    
    # Registrar 7 vuelos rápidamente
    print("Registrando 7 vuelos...\n")
    for i in range(7):
        vuelo, pista = manager.registrar_vuelo()
    
    # Mostrar estado inicial
    print("Estado inicial:")
    print(f"  Pista 1: {manager.get_pistas()[0].tamaño} vuelos")
    print(f"  Pista 2: {manager.get_pistas()[1].tamaño} vuelos")
    print(f"  Espera: {len(manager.get_lista_espera())} vuelos\n")
    
    # Ejecutar ciclos
    ciclo_despegues = []
    for ciclo in range(5):
        evento = manager.simular_ciclo()
        num_despegues = len(evento["despegues"])
        num_movimientos = len(evento["movimientos_espera"])
        ciclo_despegues.append(num_despegues)
        
        print(f"Ciclo {evento['ciclo']}: {num_despegues} despegues, {num_movimientos} movimientos")
        for pista in manager.get_pistas():
            print(f"    {pista.nombre}: {pista.tamaño} vuelos", end="")
            if pista.tamaño > 0:
                sig = pista.siguiente()
                print(f" (próx: {sig.nombre}, {sig.tiempo_despegue}s)")
            else:
                print()
    
    # Resumen
    print(f"\nTotal despegues en 5 ciclos: {sum(ciclo_despegues)}")
    print(f"Total rechazos: {manager.total_rechazos}")


def ejemplo_stress():
    """Ejemplo 3: Prueba de límites"""
    print("\n" + "="*70)
    print("EJEMPLO 3: Prueba de Límites (lista espera llena)")
    print("="*70 + "\n")
    
    manager = AeropuertoManager(
        num_pistas=1,           # Solo 1 pista
        capacidad_pista=2,      # Muy pequeña
        max_lista_espera=3,     # Límite bajo
        tiempo_despegue=1
    )
    
    print("Intentando registrar 10 vuelos con límites bajos...\n")
    
    asignados = 0
    en_espera = 0
    rechazados = 0
    
    for i in range(10):
        vuelo, pista = manager.registrar_vuelo()
        
        if pista:
            asignados += 1
            resultado = "[OK] PISTA"
        else:
            lista_llena = len(manager.get_lista_espera()) >= manager.max_lista_espera
            if lista_llena:
                rechazados += 1
                resultado = "[NO] RECHAZADO"
            else:
                en_espera += 1
                resultado = "[!] ESPERA"
        
        print(f"  {vuelo.nombre:<8} {resultado}")
    
    # Estadísticas
    print(f"\nEstadísticas:")
    print(f"  • Asignados a pista: {asignados}")
    print(f"  • En lista espera: {en_espera}")
    print(f"  • Rechazados: {rechazados} [NO]")
    print(f"\n  Total rechazos registrados: {manager.total_rechazos}")


def ejemplo_estadisticas():
    """Ejemplo 4: Análisis de estadísticas"""
    print("\n" + "="*70)
    print("EJEMPLO 4: Análisis de Estadísticas")
    print("="*70 + "\n")
    
    manager = AeropuertoManager(
        num_pistas=3,
        capacidad_pista=4,
        max_lista_espera=8,
        tiempo_despegue=3
    )
    
    # Registrar 20 vuelos
    print("Simulando sistema con 20 vuelos durante 10 ciclos...\n")
    for i in range(20):
        manager.registrar_vuelo()
    
    print(f"Estado inicial:")
    print(f"  Vuelos registrados: {manager.contador_vuelo - 1}")
    print(f"  En pistas: {sum(p.tamaño for p in manager.get_pistas())}")
    print(f"  En espera: {len(manager.get_lista_espera())}\n")
    
    # Ejecutar ciclos
    for _ in range(10):
        manager.simular_ciclo()
    
    # Mostrar estado final
    estado = manager.get_estado_completo()
    print(f"Estado después de {estado['ciclo']} ciclos:")
    print(f"  Despegues completados: {estado['total_despegues']}")
    print(f"  Rechazo de vuelos: {estado['total_rechazos']}")
    print(f"  Vuelos aún en pistas: {sum(p['vuelos'] for p in estado['pistas'])}")
    print(f"  Vuelos en espera: {len(estado['lista_espera'])}")
    
    # Porcentaje
    total_procesados = estado['total_despegues'] + estado['total_rechazos']
    print(f"\n  Eficiencia: {estado['total_despegues']}/{manager.contador_vuelo - 1} " +
          f"({(estado['total_despegues']/(manager.contador_vuelo - 1))*100:.1f}%)")


if __name__ == "__main__":
    try:
        ejemplo_basico()
        input("\nPresiona ENTER para continuar...")
        
        ejemplo_ciclos()
        input("\nPresiona ENTER para continuar...")
        
        ejemplo_stress()
        input("\nPresiona ENTER para continuar...")
        
        ejemplo_estadisticas()
        
        print("\n" + "="*70)
        print("✓ TODOS LOS EJEMPLOS COMPLETADOS")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n[Interrumpido por usuario]")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
