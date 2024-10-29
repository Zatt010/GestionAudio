from AgenteReinas import AgenteReinas
from Tablero import Tablero

if __name__=="__main__":
    juancito = AgenteReinas(12)
    t = Tablero(12)

    t.insertar(juancito)
    t.run()

