from AgenteIA.AgentePSR import AgentePSR

class AgenteReinas(AgentePSR):

    def __init__(self, n):
        AgentePSR.__init__(self)
        self.reinasEnFila = [0] * n
        self.reinasEnDiagIzq = [0] * (2 * n - 1)
        self.reinasEnDiagDer = [0] * (2 * n - 1)

    def getConflictos(self, vari, valor, asignacion):
        n = len(self.get_variables())
        c = self.reinasEnFila[valor] + self.reinasEnDiagDer[vari + valor] + self.reinasEnDiagIzq[vari - valor + n - 1]
        if asignacion.get(vari) == valor:
            c -= 3
        return c

    def asignar(self, variable, val, asignacion):
        anterior = asignacion.get(variable, None)
        if val != anterior:
            if anterior is not None:
                self.registrarConflictos(asignacion, variable, anterior, -1)
            self.registrarConflictos(asignacion, variable, val, +1)
            asignacion[variable] = val

    def desasignar(self, variable, asignacion):
        if variable in asignacion:
            self.registrarConflictos(asignacion, variable, asignacion[variable], -1)
            del asignacion[variable]

    def esCompleto(self,asignacion):
        return len(asignacion) == len(self.get_variables())

    def registrarConflictos(self, asignacion, var, val, delta):
        n = len(self.get_variables())
        self.reinasEnFila[val] += delta
        self.reinasEnDiagDer[var + val] += delta
        self.reinasEnDiagIzq[var - val + n - 1] += delta


