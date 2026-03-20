"""
Frontend - Sistema de Gestión de Vuelos en Aeropuerto
Interfaz gráfica con tkinter que consume backend.AeropuertoManager
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

from backend import AeropuertoManager


# ─────────────────────────────────────────────
#  APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────

class VentanaAeropuerto(tk.Tk):
    COLORES = {
        "bg":           "#0D1117",
        "panel":        "#161B22",
        "borde":        "#30363D",
        "vacio":        "#21262D",
        "ocupado":      "#DA3633",
        "frente":       "#F78166",
        "texto":        "#E6EDF3",
        "subtexto":     "#8B949E",
        "acento":       "#388BFD",
        "verde":        "#3FB950",
        "espera":       "#D29922",
        "btn_reg":      "#238636",
        "btn_dep":      "#DA3633",
        "btn_sim":      "#388BFD",
        "btn_hover":    "#2EA043",
    }

    def __init__(self):
        super().__init__()
        self.title("✈  Sistema de Gestión de Vuelos — Cola Circular")
        self.configure(bg=self.COLORES["bg"])
        self.resizable(False, False)

        # Backend
        self.manager = AeropuertoManager()
        self.simulacion_activa = False

        self._build_ui()
        self._refresh_all()

    # ── Construcción de UI ──────────────────────

    def _build_ui(self):
        # Título
        hdr = tk.Frame(self, bg=self.COLORES["bg"])
        hdr.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(
            hdr, text="✈  AEROPUERTO — GESTIÓN DE VUELOS",
            font=("Courier New", 16, "bold"),
            bg=self.COLORES["bg"], fg=self.COLORES["acento"]
        ).pack(side="left")

        tk.Label(
            hdr, text="Cola Circular · Punteros frente/final",
            font=("Courier New", 9),
            bg=self.COLORES["bg"], fg=self.COLORES["subtexto"]
        ).pack(side="left", padx=14, pady=(4, 0))

        sep = tk.Frame(self, bg=self.COLORES["borde"], height=1)
        sep.pack(fill="x", padx=20, pady=10)

        # Cuerpo
        body = tk.Frame(self, bg=self.COLORES["bg"])
        body.pack(padx=20, pady=0)

        # Columna izquierda: pistas + espera
        left = tk.Frame(body, bg=self.COLORES["bg"])
        left.pack(side="left", fill="both")

        self.frames_pistas = []
        self.celdas_pistas = []      # lista de listas de Labels
        self.lbl_info_pistas = []

        pistas = self.manager.get_pistas()
        for i, pista in enumerate(pistas):
            frame = tk.LabelFrame(
                left,
                text=f"  {pista.nombre}  ",
                font=("Courier New", 10, "bold"),
                bg=self.COLORES["panel"],
                fg=self.COLORES["acento"],
                bd=1, relief="solid",
                labelanchor="nw"
            )
            frame.pack(fill="x", padx=0, pady=(0, 10))

            celdas = []
            fila_celdas = tk.Frame(frame, bg=self.COLORES["panel"])
            fila_celdas.pack(padx=10, pady=(4, 2))

            for j in range(pista.capacidad):
                celda = tk.Label(
                    fila_celdas,
                    text="", width=7, height=3,
                    font=("Courier New", 8, "bold"),
                    bg=self.COLORES["vacio"],
                    fg=self.COLORES["texto"],
                    relief="flat", bd=0
                )
                celda.grid(row=0, column=j, padx=3, pady=3)
                celdas.append(celda)

            lbl_info = tk.Label(
                frame,
                text="",
                font=("Courier New", 8),
                bg=self.COLORES["panel"],
                fg=self.COLORES["subtexto"],
                anchor="w"
            )
            lbl_info.pack(fill="x", padx=10, pady=(0, 6))

            self.frames_pistas.append(frame)
            self.celdas_pistas.append(celdas)
            self.lbl_info_pistas.append(lbl_info)

        # Lista de espera
        espera_frame = tk.LabelFrame(
            left,
            text="  ⏳  Lista de Espera General  ",
            font=("Courier New", 10, "bold"),
            bg=self.COLORES["panel"],
            fg=self.COLORES["espera"],
            bd=1, relief="solid",
            labelanchor="nw"
        )
        espera_frame.pack(fill="x", padx=0, pady=(0, 10))

        self.espera_canvas = tk.Frame(espera_frame, bg=self.COLORES["panel"])
        self.espera_canvas.pack(padx=10, pady=8, fill="x")

        self.lbl_espera_info = tk.Label(
            espera_frame, text="Sin vuelos en espera.",
            font=("Courier New", 8),
            bg=self.COLORES["panel"], fg=self.COLORES["subtexto"],
            anchor="w"
        )
        self.lbl_espera_info.pack(fill="x", padx=10, pady=(0, 6))

        # Columna derecha: controles + log
        right = tk.Frame(body, bg=self.COLORES["bg"])
        right.pack(side="left", fill="both", padx=(18, 0))

        # Controles
        ctrl = tk.LabelFrame(
            right,
            text="  Controles  ",
            font=("Courier New", 10, "bold"),
            bg=self.COLORES["panel"],
            fg=self.COLORES["texto"],
            bd=1, relief="solid",
            labelanchor="nw"
        )
        ctrl.pack(fill="x", pady=(0, 10))

        btn_style = dict(
            font=("Courier New", 10, "bold"),
            relief="flat", bd=0,
            cursor="hand2", pady=8
        )

        self.btn_reg = tk.Button(
            ctrl, text="✚  Registrar Vuelo",
            bg=self.COLORES["btn_reg"], fg="white",
            command=self.registrar_vuelo, **btn_style
        )
        self.btn_reg.pack(fill="x", padx=10, pady=(10, 4))

        # Selector de pista para despegar
        sel_frame = tk.Frame(ctrl, bg=self.COLORES["panel"])
        sel_frame.pack(fill="x", padx=10, pady=2)

        tk.Label(
            sel_frame, text="Pista a despegar:",
            font=("Courier New", 9),
            bg=self.COLORES["panel"], fg=self.COLORES["subtexto"]
        ).pack(side="left")

        self.pista_sel = tk.IntVar(value=0)
        opciones = ["Auto (Round-Robin)"] + [f"Pista {i+1}" for i in range(len(pistas))]
        self.combo_pista = ttk.Combobox(
            sel_frame, textvariable=self.pista_sel,
            values=opciones, state="readonly", width=18,
            font=("Courier New", 9)
        )
        self.combo_pista.current(0)
        self.combo_pista.pack(side="left", padx=6)

        self.btn_dep = tk.Button(
            ctrl, text="🛫  Despegar Vuelo",
            bg=self.COLORES["btn_dep"], fg="white",
            command=self.despegar_vuelo, **btn_style
        )
        self.btn_dep.pack(fill="x", padx=10, pady=4)

        self.btn_sim = tk.Button(
            ctrl, text="⚡  Simulación Automática (15 vuelos)",
            bg=self.COLORES["btn_sim"], fg="white",
            command=self.iniciar_simulacion, **btn_style
        )
        self.btn_sim.pack(fill="x", padx=10, pady=(4, 10))

        # Punteros info
        ptr_frame = tk.LabelFrame(
            right,
            text="  Punteros de Cola  ",
            font=("Courier New", 10, "bold"),
            bg=self.COLORES["panel"],
            fg=self.COLORES["texto"],
            bd=1, relief="solid",
            labelanchor="nw"
        )
        ptr_frame.pack(fill="x", pady=(0, 10))

        self.lbl_punteros = tk.Label(
            ptr_frame, text="",
            font=("Courier New", 8),
            bg=self.COLORES["panel"],
            fg=self.COLORES["texto"],
            justify="left", anchor="w"
        )
        self.lbl_punteros.pack(fill="x", padx=10, pady=8)

        # Log
        log_frame = tk.LabelFrame(
            right,
            text="  Log de Eventos  ",
            font=("Courier New", 10, "bold"),
            bg=self.COLORES["panel"],
            fg=self.COLORES["texto"],
            bd=1, relief="solid",
            labelanchor="nw"
        )
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            log_frame,
            font=("Courier New", 8),
            bg=self.COLORES["vacio"],
            fg=self.COLORES["texto"],
            relief="flat", bd=0,
            width=38, height=14,
            state="disabled",
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)

        scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text["yscrollcommand"] = scroll.set

        # Tags de color para el log
        self.log_text.tag_config("reg",  foreground=self.COLORES["verde"])
        self.log_text.tag_config("dep",  foreground=self.COLORES["frente"])
        self.log_text.tag_config("esp",  foreground=self.COLORES["espera"])
        self.log_text.tag_config("err",  foreground=self.COLORES["ocupado"])
        self.log_text.tag_config("sim",  foreground=self.COLORES["acento"])
        self.log_text.tag_config("info", foreground=self.COLORES["subtexto"])

    # ── Métodos de Negocio (ahora usan Backend) ────────

    def registrar_vuelo(self):
        """Registra un nuevo vuelo a través del backend"""
        vuelo, pista_asignada = self.manager.registrar_vuelo()
        
        # Verificar si fue rechazado (lista espera llena)
        estado_espera = len(self.manager.get_lista_espera())
        max_espera = self.manager.max_lista_espera
        
        if pista_asignada:
            self._log(f"[✚] {vuelo.nombre} → {pista_asignada.nombre} (despegue en {vuelo.tiempo_despegue}s)", "reg")
        elif estado_espera < max_espera:
            self._log(f"[⏳] {vuelo.nombre} → Lista de Espera (pistas llenas)", "esp")
        else:
            self._log(f"[✗] {vuelo.nombre} → RECHAZADO (lista de espera llena)", "err")
        
        self._refresh_all()

    def despegar_vuelo(self):
        """Despega un vuelo a través del backend"""
        sel = self.combo_pista.get()
        
        if sel == "Auto (Round-Robin)" or sel == "":
            pista_idx = None
        else:
            pista_idx = int(sel.split(" ")[1]) - 1

        vuelo_despegado, vuelo_de_espera = self.manager.despegar_vuelo(pista_idx)

        if vuelo_despegado is None:
            self._log("[!] No hay vuelos en la pista seleccionada.", "err")
            return

        self._log(f"[🛫] {vuelo_despegado.nombre} despegó", "dep")

        if vuelo_de_espera:
            pistas = self.manager.get_pistas()
            pista_destino = None
            for p in pistas:
                if vuelo_de_espera in p.get_slots():
                    pista_destino = p
                    break
            if pista_destino:
                self._log(f"[→] {vuelo_de_espera.nombre} pasó de Espera → {pista_destino.nombre}", "esp")

        self._refresh_all()

    def iniciar_simulacion(self):
        """Inicia simulación automática en thread separado"""
        if self.simulacion_activa:
            return
        self.simulacion_activa = True
        self.btn_sim.config(state="disabled", text="⚡ Simulando...")
        self._log("── Simulación Automática iniciada ──", "sim")
        self._log("Fase 1: Registrando 15 vuelos...", "info")
        t = threading.Thread(target=self._run_simulacion, daemon=True)
        t.start()

    def _run_simulacion(self):
        """
        Ejecuta la simulación: 
        1. Registra 15 vuelos (distribuidos en varios ciclos)
        2. Ejecuta ciclos de simulación para procesar despegues
        """
        # Fase 1: Registrar 15 vuelos distribuidamente
        for i in range(15):
            self.after(0, self.registrar_vuelo)
            time.sleep(0.5)
        
        # Esperar a que se registren todos
        time.sleep(1)
        self.after(0, lambda: self._log("Fase 2: Ejecutando ciclos de simulación...", "info"))
        time.sleep(0.5)
        
        # Fase 2: Ejecutar ciclos de simulación (máximo 20 ciclos)
        for ciclo in range(20):
            self.after(0, self._ejecutar_ciclo_simulacion)
            time.sleep(1)  # 1 segundo por ciclo
            
            # Si no hay vuelos ni en pistas ni en espera, terminar
            pistas = self.manager.get_pistas()
            espera = self.manager.get_lista_espera()
            hay_vuelos = any(not p.esta_vacia() for p in pistas) or len(espera) > 0
            if not hay_vuelos:
                break
        
        self.after(0, self._fin_simulacion)

    def _ejecutar_ciclo_simulacion(self):
        """Ejecuta un ciclo de simulación y muestra eventos"""
        evento = self.manager.simular_ciclo()
        ciclo = evento["ciclo"]
        
        self._log(f"\n[⏱ Ciclo {ciclo}]", "sim")
        
        # Mostrar despegues
        for vuelo in evento["despegues"]:
            self._log(f"  [🛫] {vuelo.nombre} despegó", "dep")
        
        # Mostrar movimientos de espera
        for vuelo, pista in evento["movimientos_espera"]:
            self._log(f"  [→] {vuelo.nombre} pasó a {pista.nombre}", "esp")
        
        # Mostrar estado generalde espera
        espera = self.manager.get_lista_espera()
        if espera:
            vuelos_espera = ", ".join([f"{v.nombre}({v.tiempo_espera}s)" for v in espera])
            self._log(f"  ⏳ Esperando: {vuelos_espera}", "info")
        
        self._refresh_all()

    def _fin_simulacion(self):
        """Limpia estado de simulación y muestra resumen"""
        self.simulacion_activa = False
        self.btn_sim.config(state="normal", text="⚡  Simulación Automática (15 vuelos)")
        
        # Resumen final
        self._log("", "info")
        self._log("── Simulación Automática finalizada ──", "sim")
        self._log(f"Total despegues: {self.manager.total_despegues}", "info")
        self._log(f"Total rechazos: {self.manager.total_rechazos}", "info")

    # ── Refresco de UI ─────────────────────────

    def _refresh_all(self):
        """Refresca toda la interfaz"""
        self._refresh_pistas()
        self._refresh_espera()
        self._refresh_punteros()

    def _refresh_pistas(self):
        """Actualiza visualización de pistas con celdas y punteros"""
        pistas = self.manager.get_pistas()
        for i, pista in enumerate(pistas):
            slots = pista.get_slots()
            frente_idx = pista.frente
            celdas = self.celdas_pistas[i]

            for j, celda in enumerate(celdas):
                vuelo = slots[j]
                if vuelo is None:
                    celda.config(
                        text="LIBRE",
                        bg=self.COLORES["vacio"],
                        fg=self.COLORES["subtexto"]
                    )
                else:
                    es_frente = (j == frente_idx and not pista.esta_vacia())
                    color_bg = self.COLORES["frente"] if es_frente else self.COLORES["ocupado"]
                    # Mostrar nombre y tiempo de despegue
                    info_vuelo = vuelo.get_info()
                    celda.config(
                        text=f"✈\n{info_vuelo}",
                        bg=color_bg,
                        fg="white"
                    )

            sig = pista.siguiente()
            sig_texto = f"{sig.nombre} ({sig.tiempo_despegue}s)" if sig else "—"
            info = (
                f"Vuelos: {pista.tamaño}/{pista.capacidad}  |  "
                f"frente={pista.frente}  final={pista.final}  |  "
                f"Siguiente: {sig_texto}"
            )
            self.lbl_info_pistas[i].config(text=info)

    def _refresh_espera(self):
        """Actualiza visualización de lista de espera con tiempos"""
        # Limpiar widgets anteriores
        for w in self.espera_canvas.winfo_children():
            w.destroy()

        lista_espera = self.manager.get_lista_espera()
        if not lista_espera:
            tk.Label(
                self.espera_canvas, text="— Sin vuelos en espera —",
                font=("Courier New", 8),
                bg=self.COLORES["panel"], fg=self.COLORES["subtexto"]
            ).pack()
            espacio = self.manager.max_lista_espera
            self.lbl_espera_info.config(text=f"Cola de espera vacía ({espacio}/{self.manager.max_lista_espera} espacios disponibles).")
        else:
            fila = tk.Frame(self.espera_canvas, bg=self.COLORES["panel"])
            fila.pack(fill="x")
            for vuelo in lista_espera:
                tk.Label(
                    fila, text=f"✈ {vuelo.nombre}\n({vuelo.tiempo_espera}s)",
                    font=("Courier New", 8, "bold"),
                    bg=self.COLORES["espera"], fg="white",
                    padx=6, pady=4, relief="flat"
                ).pack(side="left", padx=3, pady=2)
            espacio = self.manager.max_lista_espera - len(lista_espera)
            self.lbl_espera_info.config(
                text=f"Total en espera: {len(lista_espera)} vuelo(s) ({espacio} espacios disponibles)"
            )

    def _refresh_punteros(self):
        """Actualiza información de punteros de cola"""
        pistas = self.manager.get_pistas()
        lineas = []
        for pista in pistas:
            sig = pista.siguiente()
            sig_texto = f"{sig.nombre} ({sig.tiempo_despegue}s)" if sig else "—"
            lineas.append(
                f"{pista.nombre:<8}  frente={pista.frente}  "
                f"final={pista.final}  "
                f"siguiente={sig_texto}"
            )
        self.lbl_punteros.config(text="\n".join(lineas))

    def _log(self, msg: str, tag: str = "info"):
        """Agrega mensaje al log con formato de color"""
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")


# ─────────────────────────────────────────────
#  ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = VentanaAeropuerto()
    app.mainloop()