import tkinter as tk
from tkinter import ttk
import time
import winsound
import threading
import os

class PomodoroApp:
    def __init__(self, master):
        self.master = master
        master.title("Pomodoro Timer")

        self.tempo_foco = 25 * 60
        self.tempo_descanso_curto = 5 * 60
        self.tempo_descanso_longo = 15 * 60
        self.ciclos_foco = 0
        self.estado = "foco"
        self.tempo_restante = self.tempo_foco
        self.timer_ativo = False
        self.thread_timer = None
        self.parar_thread = False

        self.label_tempo = ttk.Label(master, text=self.formatar_tempo(self.tempo_restante), font=("Arial", 48))
        self.label_tempo.pack(pady=20)

        self.label_estado = ttk.Label(master, text=f"Estado: {self.estado.capitalize()}", font=("Arial", 16))
        self.label_estado.pack(pady=5)

        self.botao_iniciar = ttk.Button(master, text="Iniciar", command=self.iniciar_timer)
        self.botao_iniciar.pack(pady=5)

        self.botao_pausar = ttk.Button(master, text="Pausar", command=self.pausar_timer, state=tk.DISABLED)
        self.botao_pausar.pack(pady=5)

        self.botao_resetar = ttk.Button(master, text="Resetar", command=self.resetar_timer)
        self.botao_resetar.pack(pady=5)

        self.manter_no_topo = tk.BooleanVar()
        self.check_topo = ttk.Checkbutton(master, text="Manter no topo", variable=self.manter_no_topo, command=self.atualizar_topo)
        self.check_topo.pack(pady=5)

        self.minimizar_na_bandeja = tk.BooleanVar()
        self.check_bandeja = ttk.Checkbutton(master, text="Minimizar na bandeja", variable=self.minimizar_na_bandeja, command=self.atualizar_bandeja)
        self.check_bandeja.pack(pady=5)

        self.master.protocol("WM_DELETE_WINDOW", self.ao_fechar_janela)

        self.atualizar_timer()

    def formatar_tempo(self, segundos):
        minutos = segundos // 60
        segundos_restantes = segundos % 60
        return f"{minutos:02}:{segundos_restantes:02}"

    def iniciar_timer(self):
        if not self.timer_ativo:
            self.timer_ativo = True
            self.botao_iniciar.config(state=tk.DISABLED)
            self.botao_pausar.config(state=tk.NORMAL)
            self.parar_thread = False
            self.thread_timer = threading.Thread(target=self.contar_tempo)
            self.thread_timer.daemon = True
            self.thread_timer.start()

    def pausar_timer(self):
        if self.timer_ativo:
            self.timer_ativo = False
            self.botao_iniciar.config(state=tk.NORMAL)
            self.botao_pausar.config(state=tk.DISABLED)
            self.parar_thread = True

    def resetar_timer(self):
        self.pausar_timer()
        self.estado = "foco"
        self.ciclos_foco = 0
        self.tempo_restante = self.tempo_foco
        self.label_tempo.config(text=self.formatar_tempo(self.tempo_restante))
        self.label_estado.config(text=f"Estado: {self.estado.capitalize()}")

    def atualizar_timer(self):
        if not self.timer_ativo:
            self.master.after(1000, self.atualizar_timer)
            return

        if self.tempo_restante > 0:
            self.label_tempo.config(text=self.formatar_tempo(self.tempo_restante))
            self.master.after(1000, self.atualizar_timer)
        else:
            self.mudar_estado()

    def contar_tempo(self):
        while self.timer_ativo and self.tempo_restante > 0 and not self.parar_thread:
            time.sleep(1)
            self.tempo_restante -= 1
            self.master.after(0, self.atualizar_label_tempo)

        if self.timer_ativo:
            self.master.after(0, self.mudar_estado)

    def atualizar_label_tempo(self):
        self.label_tempo.config(text=self.formatar_tempo(self.tempo_restante))

    def mudar_estado(self):
        if self.estado == "foco":
            self.ciclos_foco += 1
            if self.ciclos_foco < 4:
                self.estado = "descanso_curto"
                self.tempo_restante = self.tempo_descanso_curto
            else:
                self.estado = "descanso_longo"
                self.tempo_restante = self.tempo_descanso_longo
                self.ciclos_foco = 0  # Reseta os ciclos após o descanso longo
        else:
            self.estado = "foco"
            self.tempo_restante = self.tempo_foco

        self.label_estado.config(text=f"Estado: {self.estado.capitalize()}")
        self.label_tempo.config(text=self.formatar_tempo(self.tempo_restante))
        self.tocar_som()
        self.timer_ativo = True
        self.parar_thread = False
        self.thread_timer = threading.Thread(target=self.contar_tempo)
        self.thread_timer.daemon = True
        self.thread_timer.start()

    def tocar_som(self):
        nome_do_som = "Alarm01.wav"
        caminho_do_som = os.path.join(os.environ['WINDIR'], 'Media', nome_do_som)

        try:
            winsound.PlaySound(caminho_do_som, winsound.SND_FILENAME)
            print(f"Tocando som: {caminho_do_som}")
        except Exception as e:
            print(f"Não foi possível tocar o som: {caminho_do_som}. Erro: {e}")
            print("Verifique se o arquivo de som existe no caminho especificado.")

    def atualizar_topo(self):
        self.master.wm_attributes("-topmost", self.manter_no_topo.get())

    def atualizar_bandeja(self):
        if self.minimizar_na_bandeja.get():
            self.master.iconify()
        else:
            self.master.deiconify()

    def ao_fechar_janela(self):
        if self.minimizar_na_bandeja.get():
            self.master.iconify()
        else:
            self.master.destroy()

root = tk.Tk()
app = PomodoroApp(root)
root.mainloop()
