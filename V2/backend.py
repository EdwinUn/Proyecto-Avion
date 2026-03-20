"""
Backend - Sistema de Gestión de Vuelos en Aeropuerto
Lógica de negocio: Colas circulares con control de tiempo, gestión de pistas y simulación por ciclos.

Decisiones de diseño:
- Clase Vuelo: Encapsula ID, tiempo de despegue y de espera para mejor control
- ColaCircular: Trabaja con objetos Vuelo, permite actualización de tiempos
- Clase Aeropuerto: Orquesta la simulación por ciclos (ticks) y coordina movimientos
- Sistema de ciclos: En cada ciclo se reducen tiempos, se procesan despegues y se mueven vuelos de espera
"""

import random
from typing import Optional


# ─────────────────────────────────────────────
#  ENTIDAD: Vuelo
# ─────────────────────────────────────────────

class Vuelo:
    """
    Representa un vuelo en el sistema.
    Controla tiempos de preparación (en pista) y espera (lista general).
    """
    contador_global = 0
    
    def __init__(self, nombre: str, tiempo_despegue: int = 3):
        self.id_unico = Vuelo.contador_global
        Vuelo.contador_global += 1
        self.nombre = nombre
        self.tiempo_despegue = tiempo_despegue  # Ciclos hasta poder despegar
        self.tiempo_espera = 0  # Ciclos acumulados en lista de espera
    
    def __str__(self) -> str:
        return self.nombre
    
    def __repr__(self) -> str:
        return f"Vuelo({self.nombre})"
    
    def reducir_tiempo_despegue(self) -> bool:
        """Reduce el tiempo de despegue. Retorna True si está listo (tiempo <= 0)"""
        if self.tiempo_despegue > 0:
            self.tiempo_despegue -= 1
        return self.tiempo_despegue <= 0
    
    def incrementar_tiempo_espera(self) -> None:
        """Incrementa el tiempo que lleva en lista de espera"""
        self.tiempo_espera += 1
    
    def get_info(self) -> str:
        """Retorna información del vuelo para visualización"""
        if self.tiempo_despegue > 0:
            return f"{self.nombre}\n({self.tiempo_despegue}s)"
        else:
            return f"{self.nombre}\n(LISTO)"


# ─────────────────────────────────────────────
#  ESTRUCTURA: Cola Circular Mejorada
# ─────────────────────────────────────────────

class ColaCircular:
    """
    Cola circular para gestionar vuelos en una pista.
    - Encola/Desencola vuelos
    - Actualiza tiempos de despegue en cada ciclo
    - Identifica vuelos listos para despegar
    """
    
    def __init__(self, capacidad: int, nombre: str):
        self.capacidad = capacidad
        self.nombre = nombre
        self.datos = [None] * capacidad
        self.frente = 0
        self.final = 0
        self.tamaño = 0

    def esta_llena(self) -> bool:
        return self.tamaño == self.capacidad

    def esta_vacia(self) -> bool:
        return self.tamaño == 0

    def encolar(self, vuelo: 'Vuelo') -> bool:
        """Agrega un vuelo al final de la cola"""
        if self.esta_llena():
            return False
        self.datos[self.final] = vuelo
        self.final = (self.final + 1) % self.capacidad
        self.tamaño += 1
        return True

    def desencolar(self) -> Optional['Vuelo']:
        """Remueve y retorna el vuelo del frente de la cola"""
        if self.esta_vacia():
            return None
        vuelo = self.datos[self.frente]
        self.datos[self.frente] = None
        self.frente = (self.frente + 1) % self.capacidad
        self.tamaño -= 1
        return vuelo

    def siguiente(self) -> Optional['Vuelo']:
        """Retorna el siguiente vuelo sin removerlo"""
        if self.esta_vacia():
            return None
        return self.datos[self.frente]

    def get_slots(self) -> list:
        """Retorna lista con los vuelos actuales en la cola"""
        return list(self.datos)
    
    def actualizar_tiempos(self) -> list['Vuelo']:
        """
        Reduce tiempos de despegue de todos los vuelos.
        Retorna lista de vuelos listos para despegar (tiempo <= 0).
        """
        listos = []
        for vuelo in self.datos:
            if vuelo is not None:
                if vuelo.reducir_tiempo_despegue():
                    listos.append(vuelo)
        return listos


# ─────────────────────────────────────────────
#  MANAGER: Aeropuerto con Simulación por Ciclos
# ─────────────────────────────────────────────

class AeropuertoManager:
    """
    Gestor del aeropuerto mejorado: administra pistas y lista de espera con control de tiempos.
    
    Características:
    - N colas circulares (pistas) como estructuras de datos principales
    - Lista de espera con límite máximo configurable
    - Sistema de simulación por ciclos que representan paso del tiempo
    - Control de tiempos de despegue y espera
    
    En cada ciclo:
    1. Se reducen tiempos de despegue en todas las pistas
    2. Se despejan vuelos listos (tiempo = 0)
    3. Se mueven vuelos de espera a pistas disponibles (FIFO)
    4. Se incrementan tiempos de espera en lista general
    """

    # Configuración por defecto
    NUM_PISTAS = 3
    CAPACIDAD_PISTA = 5
    MAX_LISTA_ESPERA = 10
    TIEMPO_DESPEGUE_DEFAULT = 3

    def __init__(self, num_pistas: int = NUM_PISTAS, 
                 capacidad_pista: int = CAPACIDAD_PISTA,
                 max_lista_espera: int = MAX_LISTA_ESPERA,
                 tiempo_despegue: int = TIEMPO_DESPEGUE_DEFAULT):
        """
        Inicializa el aeropuerto con los parámetros especificados.
        
        Args:
            num_pistas: Número de pistas de despegue
            capacidad_pista: Capacidad máxima de cada pista
            max_lista_espera: Límite máximo de vuelos en lista de espera
            tiempo_despegue: Ciclos por defecto para preparación de despegue
        """
        self.pistas = [
            ColaCircular(capacidad_pista, f"Pista {i+1}")
            for i in range(num_pistas)
        ]
        self.lista_espera = []
        self.max_lista_espera = max_lista_espera
        self.tiempo_despegue_default = tiempo_despegue
        
        self.contador_vuelo = 1
        self.contador_pista_despegue = 0  # Para Round-Robin
        self.ciclo_actual = 0
        
        # Estadísticas
        self.total_despegues = 0
        self.total_rechazos = 0

    # ── Generación de datos ────────────────

    def generar_nombre_vuelo(self) -> str:
        """Genera el siguiente nombre de vuelo (ej: MX001, AM002, etc)"""
        prefijos = ["MX", "AM", "VB", "LA", "AV"]
        nombre = f"{random.choice(prefijos)}{self.contador_vuelo:03d}"
        self.contador_vuelo += 1
        return nombre

    # ── Búsqueda y selección ───────────────

    def obtener_pista_menos_ocupada(self) -> Optional['ColaCircular']:
        """Retorna la pista con menor cantidad de vuelos (que no esté llena)"""
        no_llenas = [p for p in self.pistas if not p.esta_llena()]
        if not no_llenas:
            return None
        return min(no_llenas, key=lambda p: p.tamaño)

    def obtener_primera_pista_con_vuelos(self) -> Optional['ColaCircular']:
        """Retorna la primera pista que tenga vuelos"""
        for p in self.pistas:
            if not p.esta_vacia():
                return p
        return None

    def obtener_siguiente_pista_roundrobin(self) -> Optional['ColaCircular']:
        """Retorna la siguiente pista en Round-Robin que tenga vuelos"""
        inicio = self.contador_pista_despegue
        for i in range(len(self.pistas)):
            idx = (inicio + i) % len(self.pistas)
            if not self.pistas[idx].esta_vacia():
                self.contador_pista_despegue = (idx + 1) % len(self.pistas)
                return self.pistas[idx]
        return None

    # ── Operaciones de vuelos ──────────────

    def registrar_vuelo(self) -> tuple['Vuelo', Optional['ColaCircular']]:
        """
        Genera y registra un nuevo vuelo.
        
        Retorna: (vuelo, pista_asignada)
        - Si hay pista disponible: (vuelo, pista)
        - Si no pero hay espacio en espera: (vuelo, None)
        - Si lista espera llena: (vuelo, None) con indicador de rechazo
        """
        vuelo = Vuelo(self.generar_nombre_vuelo(), self.tiempo_despegue_default)
        pista = self.obtener_pista_menos_ocupada()
        
        if pista:
            pista.encolar(vuelo)
            return (vuelo, pista)
        elif len(self.lista_espera) < self.max_lista_espera:
            self.lista_espera.append(vuelo)
            return (vuelo, None)
        else:
            # Lista espera llena - rechazar vuelo
            self.total_rechazos += 1
            return (vuelo, None)  # Será identificado como rechazo en frontend

    def despegar_vuelo(self, pista_idx: Optional[int] = None) -> tuple[Optional['Vuelo'], Optional['Vuelo']]:
        """
        Despega un vuelo de la pista indicada (o auto si pista_idx=None).
        
        Retorna: (vuelo_despegado, vuelo_que_entra_de_espera)
        - vuelo_despegado: nombre del vuelo que se fue
        - vuelo_que_entra_de_espera: nombre del vuelo que pasó de espera a pista (o None)
        """
        if pista_idx is None:
            # Auto: Round-Robin entre pistas
            pista = self.obtener_siguiente_pista_roundrobin()
        else:
            pista = self.pistas[pista_idx]

        if pista is None or pista.esta_vacia():
            return (None, None)

        # Despegar
        vuelo_despegado = pista.desencolar()
        if vuelo_despegado:
            self.total_despegues += 1

        # Intentar mover de espera a la pista
        vuelo_de_espera = None
        if self.lista_espera:
            vuelo_de_espera = self.lista_espera.pop(0)
            pista.encolar(vuelo_de_espera)

        return (vuelo_despegado, vuelo_de_espera)

    # ── SIMULACIÓN POR CICLOS ──────────────

    def simular_ciclo(self) -> dict:
        """
        Ejecuta un ciclo completo de simulación.
        
        En cada ciclo:
        1. Reduce tiempos de despegue en todas las pistas
        2. Identifica y despega vuelos listos
        3. Mueve vuelos de espera a pistas disponibles
        4. Incrementa tiempos de espera en lista general
        
        Retorna dict con eventos ocurridos en este ciclo
        """
        eventos = {
            "ciclo": self.ciclo_actual,
            "despegues": [],
            "movimientos_espera": [],
            "evento": "Ejecutando ciclo..."
        }
        
        # 1. Actualizar tiempos en pistas y obtener vuelos listos
        vuelos_listos = []
        for pista in self.pistas:
            listos = pista.actualizar_tiempos()
            vuelos_listos.extend([(v, pista) for v in listos])
        
        # 2. Despejar vuelos listos
        for vuelo, pista in vuelos_listos:
            pista.desencolar()
            eventos["despegues"].append(vuelo)
            self.total_despegues += 1
            
            # Intentar mover vuelo de espera a esta pista
            if self.lista_espera:
                vuelo_espera = self.lista_espera.pop(0)
                pista.encolar(vuelo_espera)
                eventos["movimientos_espera"].append((vuelo_espera, pista))
        
        # 3. Actualizar tiempos en lista de espera
        for vuelo in self.lista_espera:
            vuelo.incrementar_tiempo_espera()
        
        self.ciclo_actual += 1
        return eventos

    def ejecutar_simulacion_completa(self, num_ciclos: int = 20) -> list[dict]:
        """
        Ejecuta múltiples ciclos de simulación.
        Útil para simular el sistema automáticamente.
        
        Retorna lista de eventos de cada ciclo
        """
        eventos_totales = []
        for _ in range(num_ciclos):
            evento = self.simular_ciclo()
            eventos_totales.append(evento)
        return eventos_totales

    # ── Getters para Frontend ──────────────

    def get_pistas(self) -> list:
        """Retorna lista de pistas"""
        return self.pistas

    def get_lista_espera(self) -> list:
        """Retorna copia de lista de espera"""
        return list(self.lista_espera)

    def get_contador_vuelo(self) -> int:
        """Retorna el contador actual de vuelos"""
        return self.contador_vuelo
    
    def get_estado_completo(self) -> dict:
        """Retorna estado completo del sistema para visualización"""
        return {
            "ciclo": self.ciclo_actual,
            "pistas": [
                {
                    "nombre": p.nombre,
                    "vuelos": p.tamaño,
                    "capacidad": p.capacidad,
                    "slots": p.get_slots()
                }
                for p in self.pistas
            ],
            "lista_espera": self.lista_espera,
            "espacio_espera": self.max_lista_espera - len(self.lista_espera),
            "total_despegues": self.total_despegues,
            "total_rechazos": self.total_rechazos
        }