"""
Test micro: Verificar ColaCircular.listar()
"""

from backend import Vuelo, ColaCircular

print("\n==== TEST MICRO: ColaCircular.listar() ====\n")

# PRUEBA 1: Sin wrap-around
print("PRUEBA 1: Sin wrap-around")
cola = ColaCircular(5, "Test")
for i in range(3):
    v = Vuelo(id_vuelo=i, nombre="V{}".format(i), ciclo_llegada=0, tiempo_preparacion=5-i)
    cola.encolar(v)

print("  tamaño: {}, frente: {}, final: {}".format(cola.tamaño, cola.frente, cola.final))
print("  listar(): {} vuelos".format(len(cola.listar())))
print()

# PRUEBA 2: Con wrap-around (desencolar algunos y reencolade otros)
print("PRUEBA 2: Con wrap-around")
cola2 = ColaCircular(5, "Test2")

# Encolar 5 vuelos (llenar)
for i in range(5):
    v = Vuelo(id_vuelo=i, nombre="A{}".format(i), ciclo_llegada=0, tiempo_preparacion=5)
    cola2.encolar(v)

print("  Despues de encolar 5:")
print("    tamaño: {}, frente: {}, final: {}".format(cola2.tamaño, cola2.frente, cola2.final))
print("    listar(): {} vuelos".format(len(cola2.listar())))

# Desencolar 2
cola2.desencolar()
cola2.desencolar()
print("  Despues de desencolar 2:")
print("    tamaño: {}, frente: {}, final: {}".format(cola2.tamaño, cola2.frente, cola2.final))
print("    listar(): {} vuelos".format(len(cola2.listar())))

# Encolar 2 nuevos (wrap-around)
v = Vuelo(id_vuelo=100, nombre="B0", ciclo_llegada=0, tiempo_preparacion=5)
cola2.encolar(v)
v = Vuelo(id_vuelo=101, nombre="B1", ciclo_llegada=0, tiempo_preparacion=5)
cola2.encolar(v)

print("  Despues de encolar 2 nuevos (wrap-around):")
print("    tamaño: {}, frente: {}, final: {}".format(cola2.tamaño, cola2.frente, cola2.final))
print("    datos: {}".format([str(d) if d else "None" for d in cola2.datos]))
print("    listar(): {} vuelos".format(len(cola2.listar())))
for v in cola2.listar():
    print("      - {}".format(v.nombre))
print()

# PRUEBA 3: Decrementar times de vuelos en ciruclución
print("PRUEBA 3: Decrementar times en circular wrap-around")
for vuelo in cola2.listar():
    print("  Antes: {} (T:{})".format(vuelo.nombre, vuelo.tiempo_preparacion))
    vuelo.decrementar_preparacion()
    print("  Despues: {} (T:{})".format(vuelo.nombre, vuelo.tiempo_preparacion))
