import argparse
import numpy as np
import random
from collections import defaultdict
from func_timeout import func_timeout, FunctionTimedOut

class GRASP_:
    def __init__(self, instancia, tiempo_limite, lambda_, alfa, estrategia_bl):
        self.instancia = instancia
        self.tiempo_limite = tiempo_limite
        self.lambda_ = lambda_
        self.alfa = alfa
        self.estrategia_bl = estrategia_bl
        self.Mejor_Solucion = None
    
    def Leer_Instancia(self):
        with open(self.instancia, "r") as archivo:
            lineas = archivo.readlines()
            self.tamano_aula = int(lineas[0].split()[1])
            self.tamano_equipos = int(lineas[1].split()[1])
            self.generos_alumnos = {}
            self.puntuaciones_belbin_alumnos = {}
            for i in range(3, len(lineas)):
                linea = lineas[i].split()
                id_alumno = int(linea[0]) - 1
                genero = linea[1]
                puntuaciones = np.array(linea[2:], dtype=float)
                self.generos_alumnos[id_alumno] = genero
                self.puntuaciones_belbin_alumnos[id_alumno] = puntuaciones
            aux = list(self.generos_alumnos.values())
            self.proporcion_mujeres_aula = aux.count("F") / len(aux)
    
    def f(self, Solucion):
        eficacia_equipos = []
        cobertura_roles_equipos = []
        balance_generos_equipos = []
        equipos = defaultdict(list)
        for id_alumno, id_equipo in enumerate(Solucion):
            equipos[id_equipo].append(id_alumno)
        umbrales_roles_belbin = np.array([12, 11, 14, 9, 10, 10, 13, 7])
        for id_equipo, id_alumnos in equipos.items():
            generos_equipo = []
            puntuaciones_equipo = np.empty((0, 8))
            for i in id_alumnos:
                generos_equipo.append(self.generos_alumnos[i])
                puntuaciones_equipo = np.vstack((puntuaciones_equipo, self.puntuaciones_belbin_alumnos[i]))
            maximas_puntuaciones = np.max(puntuaciones_equipo, axis=0)
            cobertura_roles = np.sum((maximas_puntuaciones >= umbrales_roles_belbin).astype(int)) / 8
            cobertura_roles_equipos.append(cobertura_roles)
            proporcion_mujeres_equipo = generos_equipo.count("F") / len(generos_equipo)
            balance_generos = 1 - abs(proporcion_mujeres_equipo - self.proporcion_mujeres_aula)
            balance_generos_equipos.append(balance_generos)
            eficacia = self.lambda_ * cobertura_roles + (1 - self.lambda_) * balance_generos
            eficacia_equipos.append(eficacia)
        
        valor_funcion_objetivo = np.mean(eficacia_equipos)

        return valor_funcion_objetivo, np.mean(cobertura_roles_equipos), np.mean(balance_generos_equipos)
    
    def c(self, puntuaciones_alumno_candidato, genero_alumno_candidato, puntuaciones_equipo, generos_equipo):
        umbrales_roles_belbin = np.array([12, 11, 14, 9, 10, 10, 13, 7])

        if puntuaciones_equipo.shape[0] == 0:
            puntuaciones_equipo = puntuaciones_equipo.reshape(0, 8)
            eficacia = 0
        else:
            maximas_puntuaciones = np.max(puntuaciones_equipo, axis=0)
            cobertura_roles = np.sum((maximas_puntuaciones >= umbrales_roles_belbin).astype(int)) / 8
            proporcion_mujeres = generos_equipo.count("F") / len(generos_equipo)
            balance_generos = 1 - abs(proporcion_mujeres - self.proporcion_mujeres_aula)
            eficacia = self.lambda_ * cobertura_roles + (1 - self.lambda_) * balance_generos
        
        puntuaciones_equipo_actualizadas = np.vstack([puntuaciones_equipo, puntuaciones_alumno_candidato])
        generos_equipo_actualizados = generos_equipo + [genero_alumno_candidato]
        maximas_puntuaciones_actualizadas = np.max(puntuaciones_equipo_actualizadas, axis=0)
        cobertura_roles_actualizada = np.sum((maximas_puntuaciones_actualizadas >= umbrales_roles_belbin).astype(int)) / 8
        proporcion_mujeres_actualizada = generos_equipo_actualizados.count("F") / len(generos_equipo_actualizados)
        balance_generos_actualizado = 1 - abs(proporcion_mujeres_actualizada - self.proporcion_mujeres_aula)
        eficacia_actualizada = self.lambda_ * cobertura_roles_actualizada + (1 - self.lambda_) * balance_generos_actualizado

        coste_incremental = eficacia_actualizada - eficacia

        return coste_incremental
    
    def Greedy_Randomized_Construction(self):
        Solucion = [0] * self.tamano_aula
        num_equipos_creados = self.tamano_aula / self.tamano_equipos
        num_equipos_creados = (lambda num_equipos_creados: int(num_equipos_creados) + 1 if num_equipos_creados - int(num_equipos_creados) >= 0.5 else int(num_equipos_creados))(num_equipos_creados)
        puntuaciones_equipos = defaultdict(list)
        generos_equipos = defaultdict(list)
        C = [i for i in range(self.tamano_aula)]
        while len(C) != 0:
            for id_equipo in range(1, num_equipos_creados + 1):
                puntuaciones_equipo = np.array(puntuaciones_equipos[id_equipo])
                generos_equipo = generos_equipos[id_equipo]
                costes_incrementales = {}
                for id_alumno_candidato in C:
                    puntuaciones_alumno_candidato = self.puntuaciones_belbin_alumnos[id_alumno_candidato]
                    genero_alumno_candidato = self.generos_alumnos[id_alumno_candidato]
                    costes_incrementales[id_alumno_candidato] = self.c(puntuaciones_alumno_candidato, genero_alumno_candidato, puntuaciones_equipo, generos_equipo)
                c_min = min(costes_incrementales.values())
                c_max = max(costes_incrementales.values())
                umbral = c_max + self.alfa * (c_min - c_max)
                RCL = []
                for id_alumno_candidato, coste_incremental in costes_incrementales.items():
                    if coste_incremental >= umbral:
                        RCL.append(id_alumno_candidato)
                id_alumno_candidato_aleatorio = random.choice(RCL)
                Solucion[id_alumno_candidato_aleatorio] = id_equipo
                puntuaciones_equipos[id_equipo].append(self.puntuaciones_belbin_alumnos[id_alumno_candidato_aleatorio])
                generos_equipos[id_equipo].append(self.generos_alumnos[id_alumno_candidato_aleatorio])
                C.remove(id_alumno_candidato_aleatorio)
                if len(C) == 0:
                    break
        
        return Solucion
    
    def Generar_Vecindario(self, Solucion):
        Vecindario = []
        for id_alumno_1, id_equipo_1 in enumerate(Solucion):
            for id_alumno_2, id_equipo_2 in enumerate(Solucion):
                if id_equipo_1 != id_equipo_2:
                    solucion_vecina = Solucion.copy()
                    solucion_vecina[id_alumno_1] = id_equipo_2
                    solucion_vecina[id_alumno_2] = id_equipo_1
                    if solucion_vecina not in Vecindario:
                        Vecindario.append(solucion_vecina)
        random.shuffle(Vecindario)

        return Vecindario
    
    def Busqueda_Local(self, Solucion):
        f_ = self.f(Solucion)[0]
        while True:
            optimo_local = 1
            N = self.Generar_Vecindario(Solucion)
            for solucion_vecina in N:
                f_solucion_vecina = self.f(solucion_vecina)[0]
                if f_solucion_vecina > f_:
                    optimo_local = 0
                    Solucion = solucion_vecina
                    f_ = f_solucion_vecina
                    if self.estrategia_bl == "first-improving":
                        break
            if optimo_local == 1:
                break
        
        return Solucion
    
    def GRASP_esquema(self):
        self.Leer_Instancia()
        f_Mejor_Solucion = float("-inf")
        while True:
            Solucion = self.Greedy_Randomized_Construction()
            Solucion = self.Busqueda_Local(Solucion)
            f_Solucion = self.f(Solucion)[0]
            if f_Solucion > f_Mejor_Solucion:
                self.Mejor_Solucion = Solucion
                f_Mejor_Solucion = f_Solucion
    
    def ejecutar(self):
        try:
            func_timeout(self.tiempo_limite, self.GRASP_esquema)
        except FunctionTimedOut:
            pass

    def mejor_solucion(self):
        return self.Mejor_Solucion, self.f(self.Mejor_Solucion)
    
    def equipos_formados(self):
        equipos = defaultdict(list)
        for id_alumno, id_equipo in enumerate(self.Mejor_Solucion):
            equipos[id_equipo].append(id_alumno + 1)
        equipos = dict(sorted(equipos.items()))
        for id_equipo, id_alumnos in equipos.items():
            print("Equipo {}: Alumnos {}".format(id_equipo, ", ".join(map(str, id_alumnos))))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--instancia", type=str, required=True)
    parser.add_argument("--tiempo_limite", type=int, required=True)
    parser.add_argument("--lambda_", type=float, required=True)
    parser.add_argument("--alfa", type=float, required=True)
    parser.add_argument("--estrategia_bl", type=str, required=True)
    args = parser.parse_args()
    mi_algoritmo = GRASP_(args.instancia, args.tiempo_limite, args.lambda_, args.alfa, args.estrategia_bl)
    mi_algoritmo.ejecutar()
    mejor_solucion = mi_algoritmo.mejor_solucion()
    print()
    if mejor_solucion == None:
        print("El tiempo limite especificado es insuficiente. No se ha podido generar ninguna solucion.")
    else:
        print("La mejor solucion es:\n")
        print(mejor_solucion)
        print()
        print("Los equipos que se han formado son:\n")
        mi_algoritmo.equipos_formados()
        print()