"""
Test diagnostico: Verificar por qué los vuelos en espera no se mueven
"""

from backend import Aeropuerto

print("\n==== DIAGNOSTICO: Movimiento Espera-Pista ====\n")

aeropuerto = Aeropuerto()

# Registrar exactamente 18 vuelos
print("Registrando 18 vuelos...")
for i in range(18):
    v, estado = aeropuerto.registrar_vuelo()
    if estado == "en_espera":
        print("  [{}] {} - ESPERA (prep={})".format(i+1, v.nombre, v.tiempo_preparacion))

print("\nEstado INICIAL:")
print("  Pistas: {} vuelos".format(sum(p.tamaño for p in aeropuerto.pistas)))
print("  Espera: {} vuelos".format(len(aeropuerto.lista_espera)))
for i, v in enumerate(aeropuerto.lista_espera):
    print("    - {} (prep en pista anterior: {})".format(v.nombre, v.tiempo_preparacion))

print("\n" + "-"*60)
print("Simulando 10 ciclos para despejar algunos vuelos...")
print("-"*60 + "\n")

for ciclo in range(10):
    print("CICLO {}:".format(ciclo))
    
    # Antes de simular
    print("  ANTES DE SIMULAR:")
    for pista in aeropuerto.pistas:
        if not pista.esta_vacia():
            frente = pista.siguiente()
            vuelos_str = " | ".join(["{}(T:{})".format(v.nombre, v.tiempo_preparacion) for v in pista.listar()])
            print("    {}: {}".format(pista.nombre, vuelos_str))
    
    # Simular
    aeropuerto.simular_ciclo()
    
    # Después de simular
    print("  DESPUES DE SIMULAR:")
    for pista in aeropuerto.pistas:
        if not pista.esta_vacia():
            vuelos_str = " | ".join(["{}(T:{})".format(v.nombre, v.tiempo_preparacion) for v in pista.listar()])
            print("    {}: {}".format(pista.nombre, vuelos_str))
    
    eventos = aeropuerto.get_eventos_ciclo()
    
    if eventos["despegues"]:
        print("  >>> [DESPEGUES] {}".format(", ".join([v.nombre for v in eventos['despegues']])))
    
    if eventos["movimientos_espera"]:
        print("  >>> [MOVIMIENTOS] {}".format(", ".join([v.nombre for v in eventos['movimientos_espera']])))
    
    if not eventos["despegues"] and not eventos["movimientos_espera"]:
        print("  (Sin eventos)")
    
    print()

print("="*60)
print("ESTADISTICAS FINALES:")
stats = aeropuerto.obtener_estadisticas()
print("  Despegues: {}".format(stats['total_despegues']))
print("  Vuelos en espera: {}".format(stats['lista_espera_ocupada']))
print("  Vuelos en sistema: {}".format(stats['vuelos_en_sistema']))
print("="*60)
