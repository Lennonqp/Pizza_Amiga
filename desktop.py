import tkinter as tk        #tkinter é pra parte visual
from tkinter import ttk
from datetime import datetime
import csv                  #precisa pro csv funcionar
import os                   #precisa pra acessar arquivos
import tkintermapview

ARQUIVO_CSV = 'dados.csv'   #arquivo que o bot salva os dados
INTERVALO_MS = 5000  #atualiza a tela a cada 5 segundos

class LeitorPedidos:    #classe abstrata que define a base dos diferentes leitores
    def carregar(self):
        return []  # vazio, classe abstrata

class LeitorCSV(LeitorPedidos):     #leitor de arquivos csv
    def __init__(self, caminho_arquivo):
        self._caminho = caminho_arquivo  #guarda o endereço do arquivo

    def carregar(self):
        if not os.path.exists(self._caminho):   #se nao encontrar retorna lista vazia
            return []
        with open(self._caminho, encoding='utf-8') as f: #abre e lê o arquivo, retorna a lista com as informações organizadas
            return list(csv.DictReader(f))


class LeitorJSON(LeitorPedidos):    #leitor de arquivos json, não é utilizada mas pode ser no futuro
    def __init__(self, caminho_arquivo):
        self._caminho = caminho_arquivo     #mesma lógica anterior, guarda o endereço do arquivo
    def carregar(self):
        if not os.path.exists(self._caminho):   #mesma coisa do anterior, se não encontra retorna lista vazia
            return []
        import json                             #importa json caso for usar a classe
        with open(self._caminho, encoding='utf-8') as f:    #mesma coisa do anterior, retorna a lista organizada
            return json.load(f)

class AppDesktop(tk.Tk):  #definições da janela, tkinter serve pra isso
    def __init__(self):
        super().__init__()  #inicializao o tkinter
        self.title("Central de Atendimentos - Pizza Amiga") #titulo
        self.geometry("1200x700")   #tamanho da janela
        self.configure(bg="#FDFBF7")    #cor do fundo da janela
        self._marcadores = []       
        self._leitor = LeitorCSV(ARQUIVO_CSV)  #instancia o leitor csv
        self._configurar_estilos()  #executa esses 3 metodos internos da classe pra inicializar
        self._construir_interface()
        self._atualizar_dados()

    def _configurar_estilos(self): 
        style = ttk.Style()
        style.theme_use("clam")     #tema customizavel
        style.configure("Treeview.Heading",     #definições da customização do cabeçalho
                        background="#D32F2F",   #cor de novo, vai se repetir várias vezes
                        foreground="white",
                        font=("Helvetica", 11, "bold"),
                        padding=8,
                        borderwidth=0)
        style.map("Treeview.Heading",
                  background=[('active', '#B71C1C')]) #faz a cor mudar quando o mouse passa por cima (muito importante)
        style.configure("Treeview",         #customização das linhas da tabela
                        background="white",
                        foreground="#333333",
                        rowheight=30,
                        font=("Helvetica", 10),
                        fieldbackground="white",
                        borderwidth=0)
        style.map("Treeview",           #cor de destaque quando o usuário seleciona uma linha da tabela
                  background=[('selected', '#FFEBEE')],
                  foreground=[('selected', '#B71C1C')])

    def _construir_interface(self):     #monta o layout da janela, onde cada coisa aparece
        header_frame = tk.Frame(self, 
                                bg="#D32F2F",
                                height=70)
        header_frame.pack(fill=tk.X, 
                          side=tk.TOP)
        header_frame.pack_propagate(False)

        titulo = tk.Label(header_frame,
                          text="🍕 Central de Atendimentos — Pizza Amiga",
                          font=("Helvetica", 16, "bold"), 
                          fg="white", 
                          bg="#D32F2F")
        titulo.pack(side=tk.LEFT, 
                    padx=20, 
                    pady=15)

        self._label_status = tk.Label(header_frame, 
                                      text="Aguardando dados...",
                                      font=("Helvetica", 10, "italic"), 
                                      fg="#FFCDD2", 
                                      bg="#D32F2F")
        self._label_status.pack(side=tk.RIGHT, 
                                padx=20, 
                                pady=20)

        painel = tk.Frame(self, 
                          bg="#FDFBF7")
        painel.pack(fill=tk.BOTH, 
                    expand=True, 
                    padx=10, 
                    pady=10)

        #tabela onde fica nome,sobrenome, latitude, longitude e endereço
        frame_tabela = tk.Frame(painel, 
                                bg="#FDFBF7")
        frame_tabela.pack(side=tk.LEFT, 
                          fill=tk.BOTH, 
                          expand=True, 
                          padx=(0, 5))

        scrollbar = ttk.Scrollbar(frame_tabela)
        scrollbar.pack(side=tk.RIGHT, 
                       fill=tk.Y)

        colunas = ('Nome', 'Sobrenome', 'Latitude', 'Longitude', 'Endereço')
        self._tabela = ttk.Treeview(frame_tabela, 
                                    columns=colunas, 
                                    show='headings', 
                                    yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._tabela.yview)

        for col in colunas:
            self._tabela.heading(col, text=col)
            if col == 'Endereco':
                self._tabela.column(col, 
                                    width=280, 
                                    anchor=tk.W)
            elif col in ('Latitude', 'Longitude'):
                self._tabela.column(col, 
                                    width=100, 
                                    anchor=tk.CENTER)
            else:
                self._tabela.column(col, 
                                    width=90, 
                                    anchor=tk.CENTER)

        self._tabela.pack(fill=tk.BOTH, 
                          expand=True)
        self._tabela.tag_configure('par', 
                                   background='#F9F9F9')
        self._tabela.tag_configure('impar', 
                                   background='white')
        self._tabela.bind("<<TreeviewSelect>>", self.centralizar_no_pedido) #clicar na linha centraliza no pedido

        #botão pra remover o registro selecionado
        btn_remover = tk.Button(frame_tabela,
                                text="🗑️ Remover selecionado",
                                command=self._remover_selecionado,
                                bg="#D32F2F", fg="white",
                                font=("Helvetica", 10, "bold"),
                                relief=tk.FLAT, 
                                padx=10, 
                                pady=6, 
                                cursor="hand2")
        btn_remover.pack(pady=(6, 0))

        frame_mapa = tk.Frame(painel,           #definições do mapa
                              bg="#FDFBF7")
        frame_mapa.pack(side=tk.RIGHT, 
                        fill=tk.BOTH, 
                        expand=True, 
                        padx=(5, 0))

        tk.Label(frame_mapa, 
                 text="📍 Mapa de Pedidos", 
                 font=("Helvetica", 11, "bold"),
                 bg="#FDFBF7", 
                 fg="#D32F2F").pack(pady=(0, 5))

        self._mapa = tkintermapview.TkinterMapView(frame_mapa,      #mapa interativo usando OpenStreetMap (não precisa de key)
                                                   width=500, 
                                                   height=580, 
                                                   corner_radius=8)
        self._mapa.pack(fill=tk.BOTH, 
                        expand=True)
        self._mapa.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png") 
        self._mapa.set_position(-15.0, -52.0)   #posição inicial
        self._mapa.set_zoom(4)

    def centralizar_no_pedido(self, event):
        #centraliza o mapa na localização do pedido selecionado na tabela
        selecionado = self._tabela.focus()  #item selecionado
        if not selecionado:
            return
        valores = self._tabela.item(selecionado, "values")  #lê os valores da linha
        try:
            lat = float(valores[2]) #latitude
            lon = float(valores[3]) #longitude
            self._mapa.set_position(lat, lon)   #move o mapa baseado nas coordenadas anteriores
            self._mapa.set_zoom(15)             #zoom
        except (ValueError, IndexError):    #ignora se os valores forem inválidos
            pass

    def _remover_selecionado(self):     #remove o endereço selecionado na lista
        #pega a linha selecionada na tabela
        selecionado = self._tabela.focus()
        if not selecionado:
            return

        valores = self._tabela.item(selecionado, "values")
        nome, sobrenome, latitude, longitude = valores[0], valores[1], valores[2], valores[3]

        #lê todos os registros e reescreve o CSV sem o selecionado
        registros = self._leitor.carregar()
        novos_registros = [
            r for r in registros
            if not (r.get('Nome') == nome and
                    r.get('Sobrenome') == sobrenome and
                    r.get('Latitude') == latitude and
                    r.get('Longitude') == longitude)
        ]

        with open(ARQUIVO_CSV, 'w', newline='', encoding='utf-8') as f:
            if novos_registros:
                escritor = csv.DictWriter(f, fieldnames=novos_registros[0].keys())
                escritor.writeheader()
                escritor.writerows(novos_registros)

        self._atualizar_dados()  #recarrega a tela

    def _atualizar_dados(self):     #se atualiza sozinha pra ver se tem novas localizações e adiciona/remove
        #limpa tabela e marcadores antigos
        for item in self._tabela.get_children():
            self._tabela.delete(item)           #remove todas as linhas da tabela
        for marcador in self._marcadores:
            marcador.delete()                   #remove todos os pinos do mapa
        self._marcadores.clear()                #esvazia a lista de marcadores

        try:
            registros = self._leitor.carregar()

            if registros:
                for i, linha in enumerate(reversed(registros)):
                    tag = 'par' if i % 2 == 0 else 'impar'
                    self._tabela.insert('', tk.END, values=(
                        linha.get('Nome', ''),
                        linha.get('Sobrenome', ''),
                        linha.get('Latitude', ''),
                        linha.get('Longitude', ''),
                        linha.get('Endereco', 'N/A')
                    ), tags=(tag,))

                    #adiciona marcador no mapa para cada pedido registrado
                    try:
                        lat = float(linha.get('Latitude', 0))
                        lon = float(linha.get('Longitude', 0))
                        nome = linha.get('Nome', '')
                        marcador = self._mapa.set_marker(lat, lon, text=f"🍕 {nome}")
                        self._marcadores.append(marcador)
                    except (ValueError, TypeError):
                        pass

                #centraliza no último pedido recebido
                try:
                    ultimo = registros[-1]
                    lat = float(ultimo.get('Latitude', -15.0))  #se não encontrar valores esses vão pro centro do país
                    lon = float(ultimo.get('Longitude', -52.0))
                    self._mapa.set_position(lat, lon)
                    self._mapa.set_zoom(13)
                except (ValueError, TypeError):
                    pass

                agora = datetime.now().strftime('%H:%M:%S')
                self._label_status.config(text=f"🔄 {len(registros)} pedido(s) — Atualizado às {agora}")
            else:
                #mostra a mensagem enquanto não tiver nenhuma localização
                self._label_status.config(text="⏳ Aguardando a primeira localização do Telegram...")
        except Exception as e:
            self._label_status.config(text=f"❌ Erro ao ler arquivo: {e}")

        #chama a próxima atualização automática de 5 segundos
        self.after(INTERVALO_MS, self._atualizar_dados)

if __name__ == '__main__':
    app = AppDesktop()  #cria a janela
    app.mainloop()      #mantém a janela aberta até o usuário fechar

    #Fonte utilizada para criar a classe LeitorCSV
    #https://python-adv-web-apps.readthedocs.io/en/latest/csv.html

    #Fontes utilizadas para criar o AppDesktop
    # https://www.tutorialspoint.com/python/tk_button.htm
    # https://customtkinter.tomschimansky.com/documentation/widgets/button/

    #Utilizamos IA para organizar as configurações visuais do painel, como cores, fontes e tamanhos, para ter um visual mais agrádavel, o mais otimizado possível.
    #Prompt usado: Otimizar este arquivo e alterar cores e fontes para algo mais agradável e relacionado ao tema pizzaria utilizando a biblioteca tkinter ja presente no projeto
