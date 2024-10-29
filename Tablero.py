from AgenteIA.Entorno import Entorno
import pygame
from pygame.locals import *
import sys


class Tablero(Entorno):

    def __init__(self, n):
        Entorno.__init__(self)
        self.tam = n

    def get_percepciones(self, agente):
        agente.setVariables(list(range(self.tam)))
        agente.setDominio(list(range(self.tam)))
        agente.setVecinos(list(range(self.tam)))
        agente.programa()
        agente.inhabilitar()
    def ejecutar(self, agente):
        n = len(agente.get_variables())
        print (agente.get_acciones())
        pygame.init()
        ventana = pygame.display.set_mode((600, 600))
        dim = 400 / 8
        pygame.display.set_caption('Problema de las N-Reinas!!')
        # Dibuja el cuadrado que sera de la medida de la pantalla creada
        fondoGris = pygame.Surface(ventana.get_size())
        # Le pone el color de fondo gris
        fondoGris.fill((200, 200, 200))
        # Dibuja el cuadrado negro a partir de la posicion (0, 0)
        ventana.blit(fondoGris, (0, 0))
        # Actualiza el contenido de la pantalla
        pygame.display.flip()
        # Colores utilizados
        negro = (0, 0, 0)
        blanco = (255, 255, 255)
        reina = pygame.image.load("reina.png")
        while True:
            impar = 1
            for i in range(n):
                for j in range(n):
                    # dependiendo de la paridad de la variable odd el cuadrado sera blanco o negro
                    if (impar % 2) == 0:
                        color = negro
                    else:
                        color = blanco
                    pygame.draw.rect(ventana, color, (i * dim, j * dim, dim, dim))
                    if i == agente.get_acciones()[j]:
                        ventana.blit(reina, (i * dim, j * dim))
                    impar += 1
                impar += 1
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    sys.exit()
