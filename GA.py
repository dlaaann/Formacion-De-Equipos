import argparse
import numpy as np
import random
from collections import defaultdict
from func_timeout import func_timeout, FunctionTimedOut

class GA_:
    def __init__(self, instancia, tiempo_limite, lambda_):
        self.instancia = instancia
        self.tiempo_limite = tiempo_limite
        self.lambda_ = lambda_
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
    
    def fitness(self, Solucion):
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
        
        valor_fitness = np.mean(eficacia_equipos)

        return valor_fitness, np.mean(cobertura_roles_equipos), np.mean(balance_generos_equipos)
    
    def Randomized_Construction(self):
        Solucion = [0] * self.tamano_aula
        C = [i for i in range(self.tamano_aula)]
        num_equipos_creados = self.tamano_aula / self.tamano_equipos
        num_equipos_creados = (lambda num_equipos_creados: int(num_equipos_creados) + 1 if num_equipos_creados - int(num_equipos_creados) >= 0.5 else int(num_equipos_creados))(num_equipos_creados)
        while len(C) != 0:
            for id_equipo in range(1, num_equipos_creados + 1):
                id_alumno_aleatorio = random.choice(C)
                Solucion[id_alumno_aleatorio] = id_equipo
                C.remove(id_alumno_aleatorio)
                if len(C) == 0:
                    break
        
        return Solucion
    
    def Construir_Poblacion_Inicial(self):
        Poblacion = []
        for i in range(100):
            Solucion = self.Randomized_Construction()
            Poblacion.append(Solucion)
        
        return Poblacion
    
    def Roulette_Wheel_Selection(self, Poblacion):
        fitness_total_Poblacion = 0
        aux = []
        for Solucion in Poblacion:
            fitness_Solucion = self.fitness(Solucion)[0]
            fitness_total_Poblacion += fitness_Solucion
            aux.append((fitness_Solucion, Solucion))
        aux = sorted(aux, reverse=False)
        Progenitores = []
        for i in range(50):
            probabilidad_aleatoria = random.random()
            probabilidad_acumulada = 0
            for fitness_Solucion, Solucion in aux:
                probabilidad = fitness_Solucion / fitness_total_Poblacion
                probabilidad_acumulada += probabilidad
                if probabilidad_acumulada >= probabilidad_aleatoria:
                    Progenitores.append(Solucion)
                    break
        
        return Progenitores
    
    def Cut_and_Crossfill(self, Progenitor_1, Progenitor_2):
        numero_total_genes = len(Progenitor_1)
        conteo_alelos = defaultdict(int)
        for i in Progenitor_1:
            conteo_alelos[i] += 1
        posicion_aleatoria = random.randrange(1, numero_total_genes - 1)
        Descendiente_1 = Progenitor_1[:posicion_aleatoria]
        Descendiente_2 = Progenitor_2[:posicion_aleatoria]
        for i in Progenitor_2[posicion_aleatoria:] + Progenitor_2[:posicion_aleatoria]:
            if Descendiente_1.count(i) != conteo_alelos[i]:
                Descendiente_1.append(i)
            if len(Descendiente_1) == numero_total_genes:
                break
        for i in Progenitor_1[posicion_aleatoria:] + Progenitor_1[:posicion_aleatoria]:
            if Descendiente_2.count(i) != conteo_alelos[i]:
                Descendiente_2.append(i)
            if len(Descendiente_2) == numero_total_genes:
                break
        
        return Descendiente_1, Descendiente_2
    
    def Swap_Mutation(self, Descendiente):
        numero_total_genes = len(Descendiente)
        posicion_aleatoria_1 = random.randint(0, numero_total_genes - 1)
        if posicion_aleatoria_1 == 0:
            intervalos = [(posicion_aleatoria_1 + 1, numero_total_genes - 1)]
        elif posicion_aleatoria_1 == numero_total_genes - 1:
            intervalos = [(0, posicion_aleatoria_1 - 1)]
        else:
            intervalos = [(0, posicion_aleatoria_1 - 1), (posicion_aleatoria_1 + 1, numero_total_genes - 1)]
        intervalo_elegido = random.choice(intervalos)
        posicion_aleatoria_2 = random.randint(intervalo_elegido[0], intervalo_elegido[1])
        alelo_1 = Descendiente[posicion_aleatoria_1]
        alelo_2 = Descendiente[posicion_aleatoria_2]
        probabilidad_aleatoria = random.random()
        if probabilidad_aleatoria > 0.5:
            Descendiente[posicion_aleatoria_1] = alelo_2
            Descendiente[posicion_aleatoria_2] = alelo_1

        return Descendiente

    def Reemplazo_Elitista(self, Poblacion, Descendientes):
        tamano_Poblacion = len(Poblacion)
        nueva_Poblacion = []
        for Solucion in Poblacion + Descendientes:
            nueva_Poblacion.append((self.fitness(Solucion)[0], Solucion))
        nueva_Poblacion = sorted(nueva_Poblacion, reverse=True)[:tamano_Poblacion]
        nueva_Poblacion = [Solucion for fitness_Solucion, Solucion in nueva_Poblacion]

        return nueva_Poblacion

    def GA_esquema(self):
        self.Leer_Instancia()
        fitness_Mejor_Solucion = float("-inf")
        Poblacion = self.Construir_Poblacion_Inicial()
        while True:
            Progenitores = self.Roulette_Wheel_Selection(Poblacion)
            Descendientes = []
            for i in range(len(Progenitores) - 1):
                Progenitor_1 = Progenitores[i]
                Progenitor_2 = Progenitores[i + 1]
                Descendiente_1, Descendiente_2 = self.Cut_and_Crossfill(Progenitor_1, Progenitor_2)
                Descendiente_1 = self.Swap_Mutation(Descendiente_1)
                Descendiente_2 = self.Swap_Mutation(Descendiente_2)
                Descendientes.append(Descendiente_1)
                Descendientes.append(Descendiente_2)
            Poblacion = self.Reemplazo_Elitista(Poblacion, Descendientes)
            Mejor_Solucion_Poblacion = Poblacion[0]
            fitness_Mejor_Solucion_Poblacion = self.fitness(Mejor_Solucion_Poblacion)[0]
            if fitness_Mejor_Solucion_Poblacion > fitness_Mejor_Solucion:
                self.Mejor_Solucion = Mejor_Solucion_Poblacion
                fitness_Mejor_Solucion = fitness_Mejor_Solucion_Poblacion

    def ejecutar(self):
        try:
            func_timeout(self.tiempo_limite, self.GA_esquema)
        except FunctionTimedOut:
            pass

    def mejor_solucion(self):
        return self.Mejor_Solucion, self.fitness(self.Mejor_Solucion)
    
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
    args = parser.parse_args()
    mi_algoritmo = GA_(args.instancia, args.tiempo_limite, args.lambda_)
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