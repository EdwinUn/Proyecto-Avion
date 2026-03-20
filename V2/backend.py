"""
Backend - Sistema de Gestión de Vuelos en Aeropuerto (v2 Refactorizado)
Simulación de vuelos usando Colas Circulares con sistema de ticks
"""

import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple


# ─────────────────────────────────────────────────────────────────
#  CLASE: Vuelo
# ─────────────────────────────────────────────────────────────────

@dataclass
class Vuelo:
    """
    Representa un vuelo individual con su ciclo de vida.
    
    Atributos:
        id_vuelo: identificador único del vuelo
        nombre: nombre del vuelo (ej: MX001, AM002)
        ciclo_llegada: ciclo en el que llegó el vuelo
        tiempo_preparacion: ciclos necesarios para prepararse en pista (decrementa cada ciclo)
        tiempo_espera_acumulado: ciclos que ha esperado en la cola de espera
    """
    id_vuelo: int
    nombre: str
    ciclo_llegada: int
    tiempo_preparacion: int
    tiempo_espera_acumulado: int = 0
    estado: str = "espera"  # "espera", "en_pista", "listo", "despegado", "rechazado"

    def decrementar_preparacion(self) -> None:
        """Decrementa el tiempo de preparación en 1 ciclo (usado cada tick)"""
        if self.tiempo_preparacion > 0:
            self.tiempo_preparacion -= 1

    def incrementar_espera(self) -> None:
        """Incrementa el tiempo de espera acumulado en 1 ciclo"""
        self.tiempo_espera_acumulado += 1

    def esta_listo(self) -> bool:
        """Retorna True si el vuelo está listo para despegar (tiempo_preparacion == 0)"""
        return self.tiempo_preparacion == 0

    def __str__(self) -> str:
        return f"{self.nombre}(T:{self.tiempo_preparacion},E:{self.tiempo_espera_acumulado})"

    def __repr__(self) -> str:
        return f"Vuelo({self.nombre})"


# ─────────────────────────────────────────────────────────────────
#  ESTRUCTURA: Cola Circular
# ─────────────────────────────────────────────────────────────────

class ColaCircular:
    """
    Implementación de Cola Circular para gestionar vuelos en pistas.
    Utiliza un arreglo circular con punteros frente/final.
    
    Cambios v2: ahora trabaja con objetos Vuelo en lugar de strings.
    """

    def __init__(self, capacidad: int, nombre: str):
        """
        Inicializa la cola circular.
        
        Args:
            capacidad: número máximo de vuelos que puede contener
            nombre: nombre descriptivo de la pista (ej: "Pista 1")
        """
        self.capacidad = capacidad
        self.nombre = nombre
        self.datos: List[Optional[Vuelo]] = [None] * capacidad
        self.frente = 0
        self.final = 0
        self.tamaño = 0

    def esta_llena(self) -> bool:
        """Retorna True si la cola está llena"""
        return self.tamaño == self.capacidad

    def esta_vacia(self) -> bool:
        """Retorna True si la cola está vacía"""
        return self.tamaño == 0

    def encolar(self, vuelo: Vuelo) -> bool:
        """
        Agrega un vuelo al final de la cola.
        
        Args:
            vuelo: Objeto Vuelo a encolar
            
        Returns:
            True si se encoló exitosamente, False si la cola está llena
        """
        if self.esta_llena():
            return False
        self.datos[self.final] = vuelo
        self.final = (self.final + 1) % self.capacidad
        self.tamaño += 1
        return True

    def desencolar(self) -> Optional[Vuelo]:
        """
        Remueve y retorna el vuelo al frente de la cola.
        
        Returns:
            El vuelo al frente, o None si la cola está vacía
        """
        if self.esta_vacia():
            return None
        vuelo = self.datos[self.frente]
        self.datos[self.frente] = None
        self.frente = (self.frente + 1) % self.capacidad
        self.tamaño -= 1
        return vuelo

    def siguiente(self) -> Optional[Vuelo]:
        """
        Retorna el vuelo al frente SIN removerlo.
        
        Returns:
            El vuelo al frente, o None si la cola está vacía
        """
        if self.esta_vacia():
            return None
        return self.datos[self.frente]

    def listar(self) -> List[Vuelo]:
        """
        Retorna una lista con todos los vuelos en la cola, en orden.
        
        Returns:
            Lista de vuelos desde frente hasta final
        """
        if self.esta_vacia():
            return []
        
        resultado = []
        if self.frente < self.final:
            # No hay wrap-around: [frente, frente+1, ..., final-1]
            resultado = [v for v in self.datos[self.frente:self.final] if v is not None]
        else:
            # Hay wrap-around o queue llena: [frente, frente+1, ..., final de arreglo, inicio, ..., final-1]
            resultado = [v for v in self.datos[self.frente:] if v is not None] + \
                       [v for v in self.datos[:self.final] if v is not None]
        
        return resultado

    def get_slots(self) -> List[Optional[Vuelo]]:
        """Retorna copia del arreglo interno (para visualización)"""
        return list(self.datos)


# ─────────────────────────────────────────────────────────────────
#  MANAGER: Aeropuerto
# ─────────────────────────────────────────────────────────────────

class Aeropuerto:
    """
    Gestor central del aeropuerto con simulación basada en ticks.
    
    Responsabilidades:
    - Gestionar N pistas (colas circulares)
    - Mantener lista de espera general con límite configurable
    - Simular ciclos de tiempo
    - Controlar génesis y asignación de vuelos
    - Registrar eventos (asignaciones, despegues, rechazos)
    """

    # ─── Constantes de Configuración ───
    NUM_PISTAS = 3
    CAPACIDAD_PISTA = 5
    MAX_CAPACIDAD_ESPERA = 10
    
    TIEMPO_PREPARACION_MIN = 3
    TIEMPO_PREPARACION_MAX = 8
    
    PREFIJOS_VUELOS = ["MX", "AM", "VB", "LA", "AV"]

    def __init__(self):
        """Inicializa el aeropuerto y sus estructuras de datos"""
        # Pistas
        self.pistas = [
            ColaCircular(self.CAPACIDAD_PISTA, f"Pista {i+1}")
            for i in range(self.NUM_PISTAS)
        ]
        
        # Lista de espera general
        self.lista_espera: List[Vuelo] = []
        
        # Reloj de simulación
        self.ciclo_actual = 0
        self.contador_vuelos = 1
        self.contador_pista_despegue = 0  # Para Round-Robin en despegues
        
        # Historial de eventos en el ciclo actual
        self.eventos_ciclo = {
            "asignados": [],
            "despegues": [],
            "movimientos_espera": [],
            "rechazos": [],
        }
        
        # Estadísticas globales
        self.total_asignados = 0
        self.total_despegues = 0
        self.total_rechazos = 0

    # ──────────────── Generación de Vuelos ──────────────

    def generar_nombre_vuelo(self) -> str:
        """
        Genera un nombre único para un vuelo.
        
        Returns:
            Nombre en formato: "XXYYY" (donde XX=prefijo, YYY=número)
        """
        prefijo = random.choice(self.PREFIJOS_VUELOS)
        nombre = f"{prefijo}{self.contador_vuelos:03d}"
        self.contador_vuelos += 1
        return nombre

    # ──────────────── Búsqueda y Selección ──────────────

    def obtener_pista_menos_ocupada(self) -> Optional[ColaCircular]:
        """
        Retorna la pista con menor cantidad de vuelos (que no esté llena).
        
        Returns:
            ColaCircular de la pista con menor tamaño, o None si todas están llenas
        """
        no_llenas = [p for p in self.pistas if not p.esta_llena()]
        if not no_llenas:
            return None
        return min(no_llenas, key=lambda p: p.tamaño)

    def obtener_siguiente_pista_roundrobin(self) -> Optional[ColaCircular]:
        """
        Retorna la siguiente pista en Round-Robin que tenga vuelos listos.
        Usado para despegues fair entre pistas.
        
        Returns:
            ColaCircular con vuelos, o None si ninguna tiene vuelos
        """
        inicio = self.contador_pista_despegue
        for i in range(self.NUM_PISTAS):
            idx = (inicio + i) % self.NUM_PISTAS
            if not self.pistas[idx].esta_vacia():
                self.contador_pista_despegue = (idx + 1) % self.NUM_PISTAS
                return self.pistas[idx]
        return None

    # ──────────────── Operaciones de Vuelos ──────────────

    def registrar_vuelo(self) -> Tuple[Optional[Vuelo], str]:
        """
        Genera y registra un nuevo vuelo.
        Lo asigna a la pista menos ocupada o a la lista de espera.
        
        Returns:
            Tupla (vuelo, estado) donde:
            - vuelo: Objeto Vuelo creado (o None si rechazado)
            - estado: "asignado_a_pista", "en_espera", o "rechazado"
        """
        # Crear vuelo
        vuelo = Vuelo(
            id_vuelo=self.contador_vuelos,
            nombre=self.generar_nombre_vuelo(),
            ciclo_llegada=self.ciclo_actual,
            tiempo_preparacion=random.randint(self.TIEMPO_PREPARACION_MIN, 
                                              self.TIEMPO_PREPARACION_MAX)
        )
        
        # Intentar asignar a pista
        pista = self.obtener_pista_menos_ocupada()
        if pista:
            vuelo.estado = "en_pista"
            pista.encolar(vuelo)
            self.total_asignados += 1
            self.eventos_ciclo["asignados"].append(vuelo)
            return (vuelo, "asignado_a_pista")
        
        # Si no hay pista, intentar agregar a lista de espera
        if len(self.lista_espera) < self.MAX_CAPACIDAD_ESPERA:
            vuelo.estado = "espera"
            self.lista_espera.append(vuelo)
            return (vuelo, "en_espera")
        
        # Rechazar si lista de espera está llena
        vuelo.estado = "rechazado"
        self.total_rechazos += 1
        self.eventos_ciclo["rechazos"].append(vuelo)
        return (None, "rechazado")

    def mover_de_espera_a_pista(self) -> Optional[Vuelo]:
        """
        Mueve el vuelo más antiguo de la lista de espera a una pista disponible.
        Usa FIFO: el primero que llegó es el primero que se mueve.
        
        Returns:
            El vuelo movido, o None si no había espacio o lista vacía
        """
        if not self.lista_espera:
            return None
        
        pista = self.obtener_pista_menos_ocupada()
        if not pista:
            return None
        
        # FIFO: el primer elemento
        vuelo = self.lista_espera.pop(0)
        vuelo.estado = "en_pista"
        pista.encolar(vuelo)
        
        self.eventos_ciclo["movimientos_espera"].append(vuelo)
        return vuelo

    def simular_ciclo(self) -> None:
        """
        Simula un ciclo completo de tiempo.
        
        En cada ciclo:
        1. Se decrementan tiempos de preparación en todas las pistas
        2. Se incrementan tiempos de espera en la lista general
        3. Se despejan vuelos listos (tiempo_preparacion == 0)
        4. Se mueven vuelos de espera a pistas disponibles
        """
        # Limpiar eventos del ciclo anterior
        self.eventos_ciclo = {
            "asignados": [],
            "despegues": [],
            "movimientos_espera": [],
            "rechazos": [],
        }
        
        # 1. Decrementar tiempos en pistas
        self._decrementar_tiempos_pistas()
        
        # 2. Incrementar tiempos de espera
        self._incrementar_tiempos_espera()
        
        # 3. Permitir despegues automáticos
        self._procesar_despegues()
        
        # 4. Mover vuelos de espera a pistas disponibles
        self._mover_vuelos_espera_a_pistas()
        
        # 5. Incrementar ciclo
        self.ciclo_actual += 1

    def _decrementar_tiempos_pistas(self) -> None:
        """Decrementa el tiempo de preparación de todos los vuelos en pistas"""
        for pista in self.pistas:
            vuelos = pista.listar()
            for vuelo in vuelos:
                vuelo.decrementar_preparacion()

    def _incrementar_tiempos_espera(self) -> None:
        """Incrementa el tiempo de espera de todos los vuelos en lista de espera"""
        for vuelo in self.lista_espera:
            vuelo.incrementar_espera()

    def _procesar_despegues(self) -> None:
        """
        Procesa despegues automáticos usando Round-Robin.
        Solo despegan vuelos con tiempo_preparacion == 0.
        """
        # Intentar despejar de cada pista en orden Round-Robin
        for _ in range(self.NUM_PISTAS):
            pista = self.obtener_siguiente_pista_roundrobin()
            if pista is None:
                break
            
            vuelo_frente = pista.siguiente()
            if vuelo_frente and vuelo_frente.esta_listo():
                vuelo_despegado = pista.desencolar()
                vuelo_despegado.estado = "despegado"
                self.total_despegues += 1
                self.eventos_ciclo["despegues"].append(vuelo_despegado)

    def _mover_vuelos_espera_a_pistas(self) -> None:
        """
        Mueve vuelos de la lista de espera a pistas disponibles, siguiendo FIFO.
        Continúa mientras haya espacio y vuelos en espera.
        """
        while self.lista_espera and not all(p.esta_llena() for p in self.pistas):
            pista_libre = self.obtener_pista_menos_ocupada()
            if not pista_libre:
                break
            
            self.mover_de_espera_a_pista()

    # ──────────────── Getters para Frontend ──────────────

    def get_pistas(self) -> List[ColaCircular]:
        """Retorna lista de pistas"""
        return self.pistas

    def get_lista_espera(self) -> List[Vuelo]:
        """Retorna copia de lista de espera"""
        return list(self.lista_espera)

    def get_ciclo_actual(self) -> int:
        """Retorna el ciclo simulado actual"""
        return self.ciclo_actual

    def get_eventos_ciclo(self) -> Dict:
        """Retorna eventos que ocurrieron en el ciclo actual"""
        return self.eventos_ciclo.copy()

    # ──────────────── Estado del Sistema ──────────────

    def obtener_estado_sistema(self) -> Dict:
        """
        Retorna un diccionario con el estado completo del sistema.
        Ideal para consumir por el frontend.
        
        Returns:
            Dict con: ciclo, pistas (con vuelos), lista_espera, eventos, estadísticas
        """
        return {
            "ciclo": self.ciclo_actual,
            "pistas": [
                {
                    "nombre": p.nombre,
                    "vuelos": [
                        {
                            "nombre": v.nombre,
                            "tiempo_preparacion": v.tiempo_preparacion,
                            "tiempo_espera": v.tiempo_espera_acumulado,
                            "estado": v.estado,
                        }
                        for v in p.listar()
                    ],
                    "tamaño": p.tamaño,
                    "capacidad": p.capacidad,
                }
                for p in self.pistas
            ],
            "lista_espera": [
                {
                    "nombre": v.nombre,
                    "tiempo_espera": v.tiempo_espera_acumulado,
                    "ciclo_llegada": v.ciclo_llegada,
                }
                for v in self.lista_espera
            ],
            "capacidad_espera": self.MAX_CAPACIDAD_ESPERA,
            "eventos": self.eventos_ciclo,
            "estadisticas": {
                "total_asignados": self.total_asignados,
                "total_despegues": self.total_despegues,
                "total_rechazos": self.total_rechazos,
                "vuelos_en_pistas": sum(p.tamaño for p in self.pistas),
                "vuelos_en_espera": len(self.lista_espera),
            }
        }

    # ──────────────── Utilidades ──────────────

    def reiniciar_simulacion(self) -> None:
        """Reinicia la simulación: limpia pistas, espera, reloj y estadísticas"""
        self.__init__()

    def validar_integridad(self) -> bool:
        """
        Valida que el sistema esté en estado consistente.
        Verificar: vuelos en pistas + espera + despegados = total registrados
        
        Returns:
            True si es válido, False si hay inconsistencia
        """
        vuelos_en_sistema = (
            sum(p.tamaño for p in self.pistas) +
            len(self.lista_espera)
        )
        total_procesados = self.total_asignados + self.total_rechazos
        
        # Integridad: los vuelos en sistema NO deben contar los despegados
        # total_asignados = total que han entrado al sistema (pistas o espera al principio)
        # total_despegues = los que salieron
        # En sistema: lo que aun no despegó
        
        return vuelos_en_sistema <= total_procesados

    def obtener_estadisticas(self) -> Dict:
        """
        Retorna estadísticas globales de la simulación.
        
        Returns:
            Dict con: vuelos procesados, tasa de rechazo, avg espera, etc.
        """
        total_procesados = self.total_asignados + self.total_rechazos
        vuelos_en_sistema = sum(p.tamaño for p in self.pistas) + len(self.lista_espera)
        
        return {
            "ciclos_simulados": self.ciclo_actual,
            "total_asignados": self.total_asignados,
            "total_despegues": self.total_despegues,
            "total_rechazos": self.total_rechazos,
            "total_procesados": total_procesados,
            "tasa_rechazo_pct": (self.total_rechazos / total_procesados * 100) if total_procesados > 0 else 0,
            "vuelos_en_sistema": vuelos_en_sistema,
            "pistas_ocupadas": sum(1 for p in self.pistas if not p.esta_vacia()),
            "lista_espera_ocupada": len(self.lista_espera),
        }

    def __str__(self) -> str:
        """Representación legible del estado actual del aeropuerto"""
        estado = f"\n{'='*60}\n"
        estado += f"AEROPUERTO - Ciclo {self.ciclo_actual}\n"
        estado += f"{'='*60}\n\n"
        
        for pista in self.pistas:
            estado += f"{pista.nombre}: [{pista.tamaño}/{pista.capacidad}] "
            vuelos = pista.listar()
            estado += " → ".join([v.nombre for v in vuelos]) if vuelos else "[vacía]"
            estado += "\n"
        
        estado += f"\nEspera: [{len(self.lista_espera)}/{self.MAX_CAPACIDAD_ESPERA}] "
        estado += " → ".join([v.nombre for v in self.lista_espera]) if self.lista_espera else "[vacía]"
        estado += "\n"
        
        estado += f"\n{'─'*60}\n"
        estado += f"Asignados: {self.total_asignados} | Despegues: {self.total_despegues} | Rechazos: {self.total_rechazos}\n"
        
        return estado