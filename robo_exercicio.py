import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import json
import time

# =====================================================================
# PARTE 1: ESTRUTURA DA SIMULAÇÃO (NÃO MODIFICAR)
# Esta parte contém a estrutura básica da simulação, incluindo o ambiente,
# o robô e a visualização. Não é recomendado modificar esta parte.
# =====================================================================

class Ambiente:
    def __init__(self, largura=800, altura=600, num_obstaculos=5, num_recursos=5):
        self.largura = largura
        self.altura = altura
        self.obstaculos = self.gerar_obstaculos(num_obstaculos)
        self.recursos = self.gerar_recursos(num_recursos)
        self.tempo = 0
        self.max_tempo = 1000  # Tempo máximo de simulação
        self.meta = self.gerar_meta()  # Adicionando a meta
        self.meta_atingida = False  # Flag para controlar se a meta foi atingida
    
    def gerar_obstaculos(self, num_obstaculos):
        obstaculos = []
        for _ in range(num_obstaculos):
            x = random.randint(50, self.largura - 50)
            y = random.randint(50, self.altura - 50)
            largura = random.randint(20, 100)
            altura = random.randint(20, 100)
            obstaculos.append({
                'x': x,
                'y': y,
                'largura': largura,
                'altura': altura
            })
        return obstaculos
    
    def gerar_recursos(self, num_recursos):
        recursos = []
        for _ in range(num_recursos):
            x = random.randint(20, self.largura - 20)
            y = random.randint(20, self.altura - 20)
            recursos.append({
                'x': x,
                'y': y,
                'coletado': False
            })
        return recursos
    
    def gerar_meta(self):
        # Gerar a meta em uma posição segura, longe dos obstáculos
        max_tentativas = 100
        margem = 50  # Margem das bordas
        
        for _ in range(max_tentativas):
            x = random.randint(margem, self.largura - margem)
            y = random.randint(margem, self.altura - margem)
            
            # Verificar se a posição está longe o suficiente dos obstáculos
            posicao_segura = True
            for obstaculo in self.obstaculos:
                # Calcular a distância até o obstáculo mais próximo
                dist_x = max(obstaculo['x'] - x, 0, x - (obstaculo['x'] + obstaculo['largura']))
                dist_y = max(obstaculo['y'] - y, 0, y - (obstaculo['y'] + obstaculo['altura']))
                dist = np.sqrt(dist_x**2 + dist_y**2)
                
                if dist < 50:  # 50 pixels de margem extra
                    posicao_segura = False
                    break
            
            if posicao_segura:
                return {
                    'x': x,
                    'y': y,
                    'raio': 30  # Raio da meta
                }
        
        # Se não encontrar uma posição segura, retorna o centro
        return {
            'x': self.largura // 2,
            'y': self.altura // 2,
            'raio': 30
        }
    
    def verificar_colisao(self, x, y, raio):
        # Verificar colisão com as bordas
        if x - raio < 0 or x + raio > self.largura or y - raio < 0 or y + raio > self.altura:
            return True
        
        # Verificar colisão com obstáculos
        for obstaculo in self.obstaculos:
            if (x + raio > obstaculo['x'] and 
                x - raio < obstaculo['x'] + obstaculo['largura'] and
                y + raio > obstaculo['y'] and 
                y - raio < obstaculo['y'] + obstaculo['altura']):
                return True
        
        return False
    
    def verificar_coleta_recursos(self, x, y, raio):
        recursos_coletados = 0
        for recurso in self.recursos:
            if not recurso['coletado']:
                # Usando uma abordagem mais segura para cálculo de distância
                dx = float(x - recurso['x'])
                dy = float(y - recurso['y'])
                # Usando hypot para cálculo mais seguro de distância
                distancia = np.hypot(dx, dy)
                if distancia < raio + 10:  # 10 é o raio do recurso
                    recurso['coletado'] = True
                    recursos_coletados += 1
        return recursos_coletados
    
    def verificar_atingir_meta(self, x, y, raio):
        if not self.meta_atingida:
            # Usando uma abordagem mais segura para cálculo de distância
            dx = float(x - self.meta['x'])
            dy = float(y - self.meta['y'])
            # Usando hypot para cálculo mais seguro de distância
            distancia = np.hypot(dx, dy)
            if distancia < raio + self.meta['raio']:
                self.meta_atingida = True
                return True
        return False
    
    def reset(self):
        self.tempo = 0
        for recurso in self.recursos:
            recurso['coletado'] = False
        self.meta_atingida = False
        return self.get_estado()
    
    def get_estado(self):
        return {
            'tempo': self.tempo,
            'recursos_coletados': sum(1 for r in self.recursos if r['coletado']),
            'recursos_restantes': sum(1 for r in self.recursos if not r['coletado']),
            'meta_atingida': self.meta_atingida
        }
    
    def passo(self):
        self.tempo += 1
        return self.tempo >= self.max_tempo
    
    def posicao_segura(self, raio_robo=15):
        """Encontra uma posição segura para o robô, longe dos obstáculos"""
        max_tentativas = 100
        margem = 50  # Margem das bordas
        
        for _ in range(max_tentativas):
            x = random.randint(margem, self.largura - margem)
            y = random.randint(margem, self.altura - margem)
            
            # Verificar se a posição está longe o suficiente dos obstáculos
            posicao_segura = True
            for obstaculo in self.obstaculos:
                # Calcular a distância até o obstáculo mais próximo
                dist_x = max(obstaculo['x'] - x, 0, x - (obstaculo['x'] + obstaculo['largura']))
                dist_y = max(obstaculo['y'] - y, 0, y - (obstaculo['y'] + obstaculo['altura']))
                dist = np.sqrt(dist_x**2 + dist_y**2)
                
                if dist < raio_robo + 20:  # 20 pixels de margem extra
                    posicao_segura = False
                    break
            
            if posicao_segura:
                return x, y
        
        # Se não encontrar uma posição segura, retorna o centro
        return self.largura // 2, self.altura // 2

class Robo:
    def __init__(self, x, y, raio=15):
        self.x = x
        self.y = y
        self.raio = raio
        self.angulo = 0  # em radianos
        self.velocidade = 0
        self.energia = 100
        self.recursos_coletados = 0
        self.colisoes = 0
        self.distancia_percorrida = 0
        self.tempo_parado = 0  # Novo: contador de tempo parado
        self.ultima_posicao = (x, y)  # Novo: última posição conhecida
        self.meta_atingida = False  # Novo: flag para controlar se a meta foi atingida
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.energia = 100
        self.recursos_coletados = 0
        self.colisoes = 0
        self.distancia_percorrida = 0
        self.tempo_parado = 0
        self.ultima_posicao = (x, y)
        self.meta_atingida = False
    
    def mover(self, aceleracao, rotacao, ambiente):
        # Atualizar ângulo
        self.angulo += rotacao
        
        # Verificar se o robô está parado
        distancia_movimento = np.sqrt((self.x - self.ultima_posicao[0])**2 + (self.y - self.ultima_posicao[1])**2)
        if distancia_movimento < 0.1:  # Se moveu menos de 0.1 unidades
            self.tempo_parado += 1
            # Forçar movimento após ficar parado por muito tempo
            if self.tempo_parado > 5:  # Após 5 passos parado
                aceleracao = max(0.2, aceleracao)  # Força aceleração mínima
                rotacao = random.uniform(-0.2, 0.2)  # Pequena rotação aleatória
        else:
            self.tempo_parado = 0
        
        # Atualizar velocidade
        self.velocidade += aceleracao
        self.velocidade = max(0.1, min(5, self.velocidade))  # Velocidade mínima de 0.1
        
        # Calcular nova posição
        novo_x = self.x + self.velocidade * np.cos(self.angulo)
        novo_y = self.y + self.velocidade * np.sin(self.angulo)
        
        # Verificar colisão
        if ambiente.verificar_colisao(novo_x, novo_y, self.raio):
            self.colisoes += 1
            self.velocidade = 0.1  # Mantém velocidade mínima mesmo após colisão
            # Tenta uma direção diferente após colisão
            self.angulo += random.uniform(-np.pi/4, np.pi/4)
        else:
            # Atualizar posição
            self.distancia_percorrida += np.sqrt((novo_x - self.x)**2 + (novo_y - self.y)**2)
            self.x = novo_x
            self.y = novo_y
        
        # Atualizar última posição conhecida
        self.ultima_posicao = (self.x, self.y)
        
        # Verificar coleta de recursos
        recursos_coletados = ambiente.verificar_coleta_recursos(self.x, self.y, self.raio)
        self.recursos_coletados += recursos_coletados
        
        # Verificar se atingiu a meta
        if not self.meta_atingida and ambiente.verificar_atingir_meta(self.x, self.y, self.raio):
            self.meta_atingida = True
            # Recuperar energia ao atingir a meta
            self.energia = min(100, self.energia + 50)
        
        # Consumir energia
        self.energia -= 0.1 + 0.05 * self.velocidade + 0.1 * abs(rotacao)
        self.energia = max(0, self.energia)
        
        # Recuperar energia ao coletar recursos
        if recursos_coletados > 0:
            self.energia = min(100, self.energia + 20 * recursos_coletados)
        
        return self.energia <= 0
    
    def get_sensores(self, ambiente):
        # Distância até o recurso mais próximo
        dist_recurso = float('inf')
        for recurso in ambiente.recursos:
            if not recurso['coletado']:
                # Usando uma abordagem mais segura para cálculo de distância
                dx = float(self.x - recurso['x'])
                dy = float(self.y - recurso['y'])
                # Usando hypot para cálculo mais seguro de distância
                dist = np.hypot(dx, dy)
                dist_recurso = min(dist_recurso, dist)
        
        # Distância até o obstáculo mais próximo
        dist_obstaculo = float('inf')
        for obstaculo in ambiente.obstaculos:
            # Simplificação: considerar apenas a distância até o centro do obstáculo
            centro_x = float(obstaculo['x'] + obstaculo['largura'] / 2)
            centro_y = float(obstaculo['y'] + obstaculo['altura'] / 2)
            # Usando uma abordagem mais segura para cálculo de distância
            dx = float(self.x - centro_x)
            dy = float(self.y - centro_y)
            # Usando hypot para cálculo mais seguro de distância
            dist = np.hypot(dx, dy)
            dist_obstaculo = min(dist_obstaculo, dist)
        
        # Distância até a meta
        # Usando uma abordagem mais segura para cálculo de distância
        dx_meta = float(self.x - ambiente.meta['x'])
        dy_meta = float(self.y - ambiente.meta['y'])
        # Usando hypot para cálculo mais seguro de distância
        dist_meta = np.hypot(dx_meta, dy_meta)
        
        # Ângulo até o recurso mais próximo
        angulo_recurso = 0
        if dist_recurso < float('inf'):
            for recurso in ambiente.recursos:
                if not recurso['coletado']:
                    dx = float(recurso['x'] - self.x)
                    dy = float(recurso['y'] - self.y)
                    angulo = np.arctan2(dy, dx)
                    angulo_recurso = angulo - self.angulo
                    # Normalizar para [-pi, pi]
                    while angulo_recurso > np.pi:
                        angulo_recurso -= 2 * np.pi
                    while angulo_recurso < -np.pi:
                        angulo_recurso += 2 * np.pi
                    break
        
        # Ângulo até a meta
        dx_meta = float(ambiente.meta['x'] - self.x)
        dy_meta = float(ambiente.meta['y'] - self.y)
        angulo_meta = np.arctan2(dy_meta, dx_meta) - self.angulo
        # Normalizar para [-pi, pi]
        while angulo_meta > np.pi:
            angulo_meta -= 2 * np.pi
        while angulo_meta < -np.pi:
            angulo_meta += 2 * np.pi
        
        return {
            'dist_recurso': dist_recurso,
            'dist_obstaculo': dist_obstaculo,
            'dist_meta': dist_meta,
            'angulo_recurso': angulo_recurso,
            'angulo_meta': angulo_meta,
            'energia': self.energia,
            'velocidade': self.velocidade,
            'meta_atingida': self.meta_atingida
        }

class Simulador:
    def __init__(self, ambiente, robo, individuo):
        self.ambiente = ambiente
        self.robo = robo
        self.individuo = individuo
        self.frames = []
        
        # Configurar matplotlib para melhor visualização
        plt.style.use('default')  # Usar estilo padrão
        plt.ion()  # Modo interativo
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_xlim(0, ambiente.largura)
        self.ax.set_ylim(0, ambiente.altura)
        self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
    
    def simular(self):
        self.ambiente.reset()
        # Encontrar uma posição segura para o robô
        x_inicial, y_inicial = self.ambiente.posicao_segura(self.robo.raio)
        self.robo.reset(x_inicial, y_inicial)
        self.frames = []
        
        # Limpar a figura atual
        self.ax.clear()
        self.ax.set_xlim(0, self.ambiente.largura)
        self.ax.set_ylim(0, self.ambiente.altura)
        self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Desenhar obstáculos (estáticos)
        for obstaculo in self.ambiente.obstaculos:
            rect = patches.Rectangle(
                (obstaculo['x'], obstaculo['y']),
                obstaculo['largura'],
                obstaculo['altura'],
                linewidth=1,
                edgecolor='black',
                facecolor='#FF9999',  # Vermelho claro
                alpha=0.7
            )
            self.ax.add_patch(rect)
        
        # Desenhar recursos (estáticos)
        for recurso in self.ambiente.recursos:
            if not recurso['coletado']:
                circ = patches.Circle(
                    (recurso['x'], recurso['y']),
                    10,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#99FF99',  # Verde claro
                    alpha=0.8
                )
                self.ax.add_patch(circ)
        
        # Desenhar a meta
        meta_circ = patches.Circle(
            (self.ambiente.meta['x'], self.ambiente.meta['y']),
            self.ambiente.meta['raio'],
            linewidth=2,
            edgecolor='black',
            facecolor='#FFFF00',  # Amarelo
            alpha=0.8
        )
        self.ax.add_patch(meta_circ)
        
        # Criar objetos para o robô e direção (serão atualizados)
        robo_circ = patches.Circle(
            (self.robo.x, self.robo.y),
            self.robo.raio,
            linewidth=1,
            edgecolor='black',
            facecolor='#9999FF',  # Azul claro
            alpha=0.8
        )
        self.ax.add_patch(robo_circ)
        
        # Criar texto para informações
        info_text = self.ax.text(
            10, self.ambiente.altura - 50,  # Alterado de 10 para 50 para descer a legenda
            "",
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
        )
        
        # Atualizar a figura
        plt.draw()
        plt.pause(0.01)
        
        try:
            while True:
                # Obter sensores
                sensores = self.robo.get_sensores(self.ambiente)
                
                # Avaliar árvores de decisão
                aceleracao = self.individuo.avaliar(sensores, 'aceleracao')
                rotacao = self.individuo.avaliar(sensores, 'rotacao')
                
                # Limitar valores
                aceleracao = max(-1, min(1, aceleracao))
                rotacao = max(-0.5, min(0.5, rotacao))
                
                # Mover robô
                sem_energia = self.robo.mover(aceleracao, rotacao, self.ambiente)
                
                # Atualizar visualização em tempo real
                self.ax.clear()
                self.ax.set_xlim(0, self.ambiente.largura)
                self.ax.set_ylim(0, self.ambiente.altura)
                self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
                self.ax.set_xlabel("X", fontsize=12)
                self.ax.set_ylabel("Y", fontsize=12)
                self.ax.grid(True, linestyle='--', alpha=0.7)
                
                # Desenhar obstáculos
                for obstaculo in self.ambiente.obstaculos:
                    rect = patches.Rectangle(
                        (obstaculo['x'], obstaculo['y']),
                        obstaculo['largura'],
                        obstaculo['altura'],
                        linewidth=1,
                        edgecolor='black',
                        facecolor='#FF9999',
                        alpha=0.7
                    )
                    self.ax.add_patch(rect)
                
                # Desenhar recursos
                for recurso in self.ambiente.recursos:
                    if not recurso['coletado']:
                        circ = patches.Circle(
                            (recurso['x'], recurso['y']),
                            10,
                            linewidth=1,
                            edgecolor='black',
                            facecolor='#99FF99',
                            alpha=0.8
                        )
                        self.ax.add_patch(circ)
                
                # Desenhar a meta
                meta_circ = patches.Circle(
                    (self.ambiente.meta['x'], self.ambiente.meta['y']),
                    self.ambiente.meta['raio'],
                    linewidth=2,
                    edgecolor='black',
                    facecolor='#FFFF00',  # Amarelo
                    alpha=0.8
                )
                self.ax.add_patch(meta_circ)
                
                # Desenhar robô
                robo_circ = patches.Circle(
                    (self.robo.x, self.robo.y),
                    self.robo.raio,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#9999FF',
                    alpha=0.8
                )
                self.ax.add_patch(robo_circ)
                
                # Desenhar direção do robô
                direcao_x = self.robo.x + self.robo.raio * np.cos(self.robo.angulo)
                direcao_y = self.robo.y + self.robo.raio * np.sin(self.robo.angulo)
                self.ax.plot([self.robo.x, direcao_x], [self.robo.y, direcao_y], 'r-', linewidth=2)
                
                # Adicionar informações
                info_text = self.ax.text(
                    10, self.ambiente.altura - 50,  # Alterado de 10 para 50 para descer a legenda
                    f"Tempo: {self.ambiente.tempo}\n"
                    f"Recursos: {self.robo.recursos_coletados}\n"
                    f"Energia: {self.robo.energia:.1f}\n"
                    f"Colisões: {self.robo.colisoes}\n"
                    f"Distância: {self.robo.distancia_percorrida:.1f}\n"
                    f"Meta atingida: {'Sim' if self.robo.meta_atingida else 'Não'}",
                    fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
                )
                
                # Atualizar a figura
                plt.draw()
                plt.pause(0.05)
                
                # Verificar fim da simulação
                if sem_energia or self.ambiente.passo():
                    break
            
            # Manter a figura aberta até que o usuário a feche
            plt.ioff()
            plt.show()
            
        except KeyboardInterrupt:
            plt.close('all')
        
        return self.frames
    
    def animar(self):
        # Desativar o modo interativo antes de criar a animação
        plt.ioff()
        
        # Criar a animação
        anim = animation.FuncAnimation(
            self.fig, self.atualizar_frame,
            frames=len(self.frames),
            interval=50,
            blit=True,
            repeat=True  # Permitir que a animação repita
        )
        
        # Mostrar a animação e manter a janela aberta
        plt.show(block=True)
    
    def atualizar_frame(self, frame_idx):
        return self.frames[frame_idx]

# =====================================================================
# PARTE 2: ALGORITMO GENÉTICO (PARA O VOCÊ MODIFICAR)
# Esta parte contém a implementação do algoritmo genético.
# Deve modificar os parâmetros e a lógica para melhorar o desempenho.
# =====================================================================

class IndividuoPG:
    def __init__(self, profundidade=3):
        self.profundidade = profundidade
        self.arvore_aceleracao = self.criar_arvore_aleatoria()
        self.arvore_rotacao = self.criar_arvore_aleatoria()
        self.fitness = 0

    def criar_arvore_aleatoria(self):
        if self.profundidade == 0:
            return self.criar_folha()

        # Aumentando a probabilidade de operadores relacionados à meta
        operadores = [
            '+', '-', '*', '/', 'max', 'min', 'abs', 
            'if_positivo', 'if_negativo', 'if_then_else',
            'sin', 'cos', 'media', 'prioridade',
            'if_recurso_proximo',
            'if_todos_coletados',
            'if_energia_baixa',
            'if_meta_proxima',
            'if_meta_proxima',
            'if_meta_proxima',  # Triplicando a chance deste operador
            'ir_para_meta'  # Novo operador específico
        ]
        
        operador = random.choice(operadores)

        if operador in ['+', '-', '*', '/', 'max', 'min', 'prioridade', 'media']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'direita': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria()
            }
        elif operador in ['abs', 'sin', 'cos']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'direita': None
            }
        elif operador == 'if_then_else':
            return {
                'tipo': 'operador',
                'operador': operador,
                'condicao': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'entao': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'senao': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria()
            }
        else:
            return self.criar_folha()

    def criar_folha(self):
        tipo = random.choice([
            'constante', 'dist_recurso', 'dist_obstaculo', 'dist_meta',
            'angulo_recurso', 'angulo_meta', 'energia', 'velocidade', 
            'meta_atingida',
            'recursos_restantes',  # Novo sensor
            'distancia_ultima_posicao',  # Novo sensor
            'tempo_restante'  # Novo sensor
        ])
        if tipo == 'constante':
            return {'tipo': 'folha', 'valor': random.uniform(-10, 10)}
        else:
            return {'tipo': 'folha', 'variavel': tipo}

    def avaliar(self, sensores, tipo='aceleracao'):
        arvore = self.arvore_aceleracao if tipo == 'aceleracao' else self.arvore_rotacao
        return self.avaliar_no(arvore, sensores)

    def avaliar_no(self, no, sensores):
        if no is None:
            return 0

        if no['tipo'] == 'folha':
            if 'valor' in no:
                return no['valor']
            elif 'variavel' in no:
                valor = sensores.get(no['variavel'], 0)
                # Normalização de valores para melhor controle
                if no['variavel'] in ['dist_recurso', 'dist_obstaculo', 'dist_meta']:
                    return min(valor / 1000, 1.0)  # Limita a distância normalizada
                elif no['variavel'] in ['angulo_recurso', 'angulo_meta']:
                    return valor / np.pi  # Normaliza ângulos
                return valor

        op = no.get('operador')

        if op == 'abs':
            return abs(self.avaliar_no(no.get('esquerda'), sensores))
        elif op == 'sin':
            valor = self.avaliar_no(no.get('esquerda'), sensores)
            return np.sin(min(max(valor, -np.pi), np.pi))  # Limita o valor do seno
        elif op == 'cos':
            valor = self.avaliar_no(no.get('esquerda'), sensores)
            return np.cos(min(max(valor, -np.pi), np.pi))  # Limita o valor do cosseno
        elif op == 'media':
            return (self.avaliar_no(no.get('esquerda'), sensores) + self.avaliar_no(no.get('direita'), sensores)) / 2
        elif op == 'prioridade':
            # Nova lógica de priorização mais forte
            recursos_coletados = sensores.get('recursos_coletados', 0)
            total_recursos = sensores.get('total_recursos', 5)
            
            if recursos_coletados == total_recursos:
                # Se todos os recursos foram coletados, força prioridade para meta
                return self.avaliar_no(no.get('direita'), sensores) * 2  # Multiplicador para forçar direção à meta
            else:
                # Se ainda há recursos, prioriza o recurso mais próximo
                return self.avaliar_no(no.get('esquerda'), sensores)
        elif op == 'if_then_else':
            cond = self.avaliar_no(no.get('condicao'), sensores)
            return self.avaliar_no(no.get('entao'), sensores) if cond > 0 else self.avaliar_no(no.get('senao'), sensores)
        elif op == 'if_recurso_proximo':
            dist_recurso = sensores.get('dist_recurso', float('inf'))
            return 1 if dist_recurso < 200 else -1
        elif op == 'if_todos_coletados':
            recursos_coletados = sensores.get('recursos_coletados', 0)
            total_recursos = sensores.get('total_recursos', 5)
            return 1 if recursos_coletados == total_recursos else -1
        elif op == 'if_energia_baixa':
            energia = sensores.get('energia', 100)
            return 1 if energia < 30 else -1
        elif op == 'if_meta_proxima':
            dist_meta = sensores.get('dist_meta', float('inf'))
            return 1 if dist_meta < 300 else -1
        elif op == 'ir_para_meta':
            # Novo operador que força movimento em direção à meta
            recursos_coletados = sensores.get('recursos_coletados', 0)
            total_recursos = sensores.get('total_recursos', 5)
            angulo_meta = sensores.get('angulo_meta', 0)
            
            if recursos_coletados == total_recursos:
                # Se todos os recursos foram coletados, retorna o ângulo para a meta
                return angulo_meta
            else:
                # Caso contrário, retorna 0 (sem influência)
                return 0

        esquerda = self.avaliar_no(no.get('esquerda'), sensores)
        direita = self.avaliar_no(no.get('direita'), sensores) if no.get('direita') is not None else 0

        # Limita os valores para evitar overflow
        esquerda = min(max(esquerda, -1000), 1000)
        direita = min(max(direita, -1000), 1000)

        if op == '+': return esquerda + direita
        elif op == '-': return esquerda - direita
        elif op == '*': return esquerda * direita
        elif op == '/': return esquerda / direita if direita != 0 else 0
        elif op == 'max': return max(esquerda, direita)
        elif op == 'min': return min(esquerda, direita)

        return 0

    def mutacao(self, probabilidade=0.4):
        self.mutacao_no(self.arvore_aceleracao, probabilidade)
        self.mutacao_no(self.arvore_rotacao, probabilidade)

    def mutacao_no(self, no, probabilidade):
        if random.random() < probabilidade:
            if no['tipo'] == 'folha':
                if 'valor' in no:
                    no['valor'] = random.uniform(-5, 5)
                elif 'variavel' in no:
                    no['variavel'] = random.choice([
                        'dist_recurso', 'dist_obstaculo', 'dist_meta',
                        'angulo_recurso', 'angulo_meta', 'energia', 
                        'velocidade', 'meta_atingida'
                    ])
            else:
                no['operador'] = random.choice([
                    '+', '-', '*', '/', 'max', 'min', 'abs', 'sin', 'cos',
                    'media', 'prioridade', 'if_then_else'
                ])

        if no['tipo'] == 'operador':
            if 'condicao' in no:
                self.mutacao_no(no['condicao'], probabilidade)
                self.mutacao_no(no['entao'], probabilidade)
                self.mutacao_no(no['senao'], probabilidade)
            else:
                self.mutacao_no(no['esquerda'], probabilidade)
                if no['direita'] is not None:
                    self.mutacao_no(no['direita'], probabilidade)

    def crossover(self, outro):
        novo = IndividuoPG(self.profundidade)
        novo.arvore_aceleracao = self.crossover_no(self.arvore_aceleracao, outro.arvore_aceleracao)
        novo.arvore_rotacao = self.crossover_no(self.arvore_rotacao, outro.arvore_rotacao)
        return novo

    def crossover_no(self, no1, no2):
        return json.loads(json.dumps(no1 if random.random() < 0.5 else no2))

    def salvar(self, arquivo):
        with open(arquivo, 'w') as f:
            json.dump({
                'arvore_aceleracao': self.arvore_aceleracao,
                'arvore_rotacao': self.arvore_rotacao
            }, f)

    @classmethod
    def carregar(cls, arquivo):
        with open(arquivo, 'r') as f:
            dados = json.load(f)
            individuo = cls()
            individuo.arvore_aceleracao = dados['arvore_aceleracao']
            individuo.arvore_rotacao = dados['arvore_rotacao']
            return individuo

class ProgramacaoGenetica:
    def __init__(self, tamanho_populacao=50, profundidade=3):
        self.tamanho_populacao = tamanho_populacao
        self.profundidade = profundidade
        self.populacao = [IndividuoPG(profundidade) for _ in range(tamanho_populacao)]
        self.melhor_individuo = None
        self.melhor_fitness = float('-inf')
        self.historico_fitness = []
    
    def avaliar_populacao(self):
        ambiente = Ambiente()
        robo = Robo(ambiente.largura // 2, ambiente.altura // 2)
        
        for individuo in self.populacao:
            fitness = 0
            
            # Simular 5 tentativas
            for _ in range(5):
                ambiente.reset()
                robo.reset(ambiente.largura // 2, ambiente.altura // 2)
                ultima_distancia_recurso = float('inf')
                ultima_distancia_meta = float('inf')
                tempo_sem_progresso = 0
                recursos_coletados_anterior = 0
                tempo_apos_coleta = 0
                
                while True:
                    # Obter sensores
                    sensores = robo.get_sensores(ambiente)
                    sensores['total_recursos'] = len(ambiente.recursos)
                    
                    # Avaliar árvores de decisão
                    aceleracao = individuo.avaliar(sensores, 'aceleracao')
                    rotacao = individuo.avaliar(sensores, 'rotacao')
                    
                    # Limitar valores
                    aceleracao = max(-1, min(1, aceleracao))
                    rotacao = max(-0.5, min(0.5, rotacao))
                    
                    # Mover robô
                    sem_energia = robo.mover(aceleracao, rotacao, ambiente)
                    
                    # Verificar progresso
                    nova_distancia_recurso = sensores.get('dist_recurso', float('inf'))
                    nova_distancia_meta = sensores.get('dist_meta', float('inf'))
                    
                    # Verificar progresso na coleta
                    if robo.recursos_coletados > recursos_coletados_anterior:
                        recursos_coletados_anterior = robo.recursos_coletados
                        tempo_sem_progresso = 0
                        tempo_apos_coleta = 0
                    # Verificar progresso em direção à meta após coleta completa
                    elif robo.recursos_coletados == len(ambiente.recursos):
                        tempo_apos_coleta += 1
                        if nova_distancia_meta < ultima_distancia_meta:
                            tempo_sem_progresso = 0
                        else:
                            tempo_sem_progresso += 1
                    # Verificar progresso em direção ao recurso
                    elif nova_distancia_recurso < ultima_distancia_recurso:
                        tempo_sem_progresso = 0
                    else:
                        tempo_sem_progresso += 1
                    
                    ultima_distancia_recurso = nova_distancia_recurso
                    ultima_distancia_meta = nova_distancia_meta
                    
                    # Verificar fim da simulação
                    if sem_energia or ambiente.passo() or tempo_sem_progresso > 50 or (tempo_apos_coleta > 100 and robo.recursos_coletados == len(ambiente.recursos)):
                        break
                
                # Calcular fitness 
                fitness_tentativa = (
                    robo.recursos_coletados * 300 +  # Aumentado de 100 para 300
                    robo.distancia_percorrida * 0.2 +  # Aumentado de 0.1 para 0.2
                    (1000 - robo.tempo_parado) * 0.5 +  # Novo: penalidade por ficar parado
                    robo.energia * 0.3 +  # Novo: bônus por manter energia
                    (1000 - robo.colisoes * 30) +  # Reduzido de 50 para 30
                    (5000 if robo.meta_atingida else 0)  # Aumentado de 500 para 5000
                )
                
                # Penalidades adicionais
                if robo.recursos_coletados == 0:
                    fitness_tentativa *= 0.3  # Penalidade maior por não coletar recursos
                elif robo.recursos_coletados < len(ambiente.recursos) and robo.meta_atingida:
                    fitness_tentativa *= 0.5  # Penalidade por ir para meta sem coletar tudo
                elif robo.recursos_coletados == len(ambiente.recursos) and not robo.meta_atingida:
                    fitness_tentativa *= 0.5  # Penalidade maior por não ir para meta após coletar tudo
                    # Penalidade adicional baseada no tempo após coleta
                    fitness_tentativa *= max(0.5, 1 - (tempo_apos_coleta / 100))
                
                fitness += max(0, fitness_tentativa)
            
            individuo.fitness = fitness / 5  # Média das 5 tentativas
            
            # Atualizar melhor indivíduo
            if individuo.fitness > self.melhor_fitness:
                self.melhor_fitness = individuo.fitness
                self.melhor_individuo = individuo
    
    def selecionar(self):
        # Seleção por torneio com tamanho variável
        tamanho_torneio = 5
        selecionados = []
        
        # Manter os 15% melhores indivíduos
        n_elite = max(1, int(self.tamanho_populacao * 0.15))
        elite = sorted(self.populacao, key=lambda x: x.fitness, reverse=True)[:n_elite]
        selecionados.extend(elite)
        
        # Selecionar o resto por torneio
        while len(selecionados) < self.tamanho_populacao:
            torneio = random.sample(self.populacao, tamanho_torneio)
            vencedor = max(torneio, key=lambda x: x.fitness)
            selecionados.append(vencedor)
        
        return selecionados
    
    def evoluir(self, n_geracoes=50):
        for geracao in range(n_geracoes):
            print(f"Geração {geracao + 1}/{n_geracoes}")
            
            # Avaliar população
            self.avaliar_populacao()
            
            # Registrar melhor fitness
            self.historico_fitness.append(self.melhor_fitness)
            print(f"Melhor fitness: {self.melhor_fitness:.2f}")
            
            # Selecionar indivíduos
            selecionados = self.selecionar()
            
            # Criar nova população
            nova_populacao = []
            
            # Elitismo - manter o melhor indivíduo
            nova_populacao.append(self.melhor_individuo)
            
            # Preencher o resto da população
            while len(nova_populacao) < self.tamanho_populacao:
                pai1, pai2 = random.sample(selecionados, 2)
                filho = pai1.crossover(pai2)
                filho.mutacao(probabilidade=0.2)  # Aumentada probabilidade de mutação
                nova_populacao.append(filho)
            
            self.populacao = nova_populacao
        
        return self.melhor_individuo, self.historico_fitness

# =====================================================================
# PARTE 3: EXECUÇÃO DO PROGRAMA (PARA O ALUNO MODIFICAR)
# Esta parte contém a execução do programa e os parâmetros finais.
# =====================================================================

# Executando o algoritmo
if __name__ == "__main__":
    print("Iniciando simulação de robô com programação genética...")
    
    # Criar e treinar o algoritmo genético
    print("Treinando o algoritmo genético...")
    # PARÂMETROS PARA O ALUNO MODIFICAR
    pg = ProgramacaoGenetica(tamanho_populacao=400, profundidade=5)
    melhor_individuo, historico = pg.evoluir(n_geracoes=15)
    
    # Salvar o melhor indivíduo
    print("Salvando o melhor indivíduo...")
    melhor_individuo.salvar('melhor_robo.json')
    
    # Plotar evolução do fitness
    print("Plotando evolução do fitness...")
    plt.figure(figsize=(10, 5))
    plt.plot(historico)
    plt.title('Evolução do Fitness')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.savefig('evolucao_fitness_robo.png')
    plt.close()
    
    # Simular o melhor indivíduo
    print("Simulando o melhor indivíduo...")
    ambiente = Ambiente()
    robo = Robo(ambiente.largura // 2, ambiente.altura // 2)
    simulador = Simulador(ambiente, robo, melhor_individuo)
    
    print("Executando simulação em tempo real...")
    print("A simulação será exibida em uma janela separada.")
    print("Pressione Ctrl+C para fechar a janela quando desejar.")
    simulador.simular() 
