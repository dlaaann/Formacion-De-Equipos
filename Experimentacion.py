from GRASP import *
from GA import *
import os
import json
import re
import ast
import time

class Experimentacion_(GRASP_, GA_):
    def __init__(self, algoritmo, repeticiones, instancias, tiempo_limite, lambdas_, alfas, estrategias_bl):
        self.algoritmo = algoritmo
        self.repeticiones = repeticiones
        self.instancias = instancias
        self.tiempo_limite = tiempo_limite
        self.lambdas_ = lambdas_
        self.alfas = alfas
        self.estrategias_bl = estrategias_bl

    def GRASP_esquema(self):
        GRASP_.Leer_Instancia(self)
        self.Mejor_Solucion = None
        self.f_Mejor_Solucion = float("-inf")
        self.cobertura_roles_Mejor_Solucion = None
        self.balance_generos_Mejor_Solucion = None
        self.tiempo_convergencia = None
        self.f_alfa = []
        self.f_busqueda_local = []
        t1 = time.time()
        while True:
            Solucion = GRASP_.Greedy_Randomized_Construction(self)
            self.f_alfa.append(GRASP_.f(self, Solucion))
            Solucion = GRASP_.Busqueda_Local(self, Solucion)
            f_Solucion, cobertura_roles_Solucion, balance_generos_Solucion = GRASP_.f(self, Solucion)
            self.f_busqueda_local.append(f_Solucion)
            if f_Solucion > self.f_Mejor_Solucion:
                self.Mejor_Solucion = Solucion
                self.f_Mejor_Solucion = f_Solucion
                self.cobertura_roles_Mejor_Solucion = cobertura_roles_Solucion
                self.balance_generos_Mejor_Solucion = balance_generos_Solucion
                t2 = time.time()
                self.tiempo_convergencia = t2 - t1

    def GA_esquema(self):
        GA_.Leer_Instancia(self)
        self.Mejor_Solucion = None
        self.fitness_Mejor_Solucion = float("-inf")
        self.cobertura_roles_Mejor_Solucion = None
        self.balance_generos_Mejor_Solucion = None
        self.tiempo_convergencia = None
        t1 = time.time()
        Poblacion = GA_.Construir_Poblacion_Inicial(self)
        while True:
            Progenitores = GA_.Roulette_Wheel_Selection(self, Poblacion)
            Hijos = []
            for i in range(len(Progenitores) - 1):
                Progenitor_1 = Progenitores[i]
                Progenitor_2 = Progenitores[i + 1]
                Hijo_1, Hijo_2 = GA_.Cut_and_Crossfill(self, Progenitor_1, Progenitor_2)
                Hijo_1 = GA_.Swap_Mutation(self, Hijo_1)
                Hijo_2 = GA_.Swap_Mutation(self, Hijo_2)
                Hijos.append(Hijo_1)
                Hijos.append(Hijo_2)
            Poblacion = GA_.Reemplazo_Elitista(self, Poblacion, Hijos)
            Mejor_Solucion_Poblacion = Poblacion[0]
            fitness_Mejor_Solucion_Poblacion, cobertura_roles_Mejor_Solucion_Poblacion, balance_generos_Mejor_Solucion_Poblacion = GA_.fitness(self, Mejor_Solucion_Poblacion)
            if fitness_Mejor_Solucion_Poblacion > self.fitness_Mejor_Solucion:
                self.Mejor_Solucion = Mejor_Solucion_Poblacion
                self.fitness_Mejor_Solucion = fitness_Mejor_Solucion_Poblacion
                self.cobertura_roles_Mejor_Solucion = cobertura_roles_Mejor_Solucion_Poblacion
                self.balance_generos_Mejor_Solucion = balance_generos_Mejor_Solucion_Poblacion
                t2 = time.time()
                self.tiempo_convergencia = t2 - t1

    def ejecutar(self):
        if self.algoritmo == "GRASP":
            try:
                func_timeout(self.tiempo_limite, self.GRASP_esquema)
            except FunctionTimedOut:
                pass
        elif self.algoritmo == "GA":
            try:
                func_timeout(self.tiempo_limite, self.GA_esquema)
            except FunctionTimedOut:
                pass
    
    def exportar_resultados_a_JSON(self, resultados, nombre_archivo_resultados):
        if self.algoritmo == "GRASP":
            directorio_guardado = "./archivos_resultados_experimentacion/GRASP"
        elif self.algoritmo == "GA":
            directorio_guardado = "./archivos_resultados_experimentacion/GA"
        os.makedirs(directorio_guardado, exist_ok=True)
        with open(os.path.join(directorio_guardado, nombre_archivo_resultados + ".json"), "w") as archivo:
            json.dump(resultados, archivo, indent=4)

    def iniciar(self):
        instancias = os.listdir(self.instancias)
        for instancia in instancias:
            nombre_instancia = re.findall(r'^(.*)\.txt$', instancia)[0]
            resultados_instancia = {}
            self.instancia = os.path.join(self.instancias, instancia)
            if self.algoritmo == "GRASP":
                resultados_instancia.setdefault(nombre_instancia, {})
                for alfa in self.alfas:
                    resultados_instancia[nombre_instancia].setdefault(alfa, {})
                    self.alfa = alfa
                    for estrategia in self.estrategias_bl:
                        resultados_instancia[nombre_instancia][alfa].setdefault(estrategia, {})
                        self.estrategia_bl = estrategia
                        for lambda_ in self.lambdas_:
                            resultados_instancia[nombre_instancia][alfa][estrategia].setdefault(lambda_, {"mejores_soluciones": [], "f_mejores_soluciones": [], "cobertura_roles_mejores_soluciones": [], "balance_generos_mejores_soluciones": [], "tiempos_convergencia": [], "f_alfa": [], "f_busqueda_local": []})
                            self.lambda_ = lambda_
                            for repeticion in range(self.repeticiones):
                                self.ejecutar()
                                resultados_instancia[nombre_instancia][alfa][estrategia][lambda_]["mejores_soluciones"].append(self.Mejor_Solucion)
                                resultados_instancia[nombre_instancia][alfa][estrategia][lambda_]["f_mejores_soluciones"].append(self.f_Mejor_Solucion)
                                resultados_instancia[nombre_instancia][alfa][estrategia][lambda_]["cobertura_roles_mejores_soluciones"].append(self.cobertura_roles_Mejor_Solucion)
                                resultados_instancia[nombre_instancia][alfa][estrategia][lambda_]["balance_generos_mejores_soluciones"].append(self.balance_generos_Mejor_Solucion)
                                resultados_instancia[nombre_instancia][alfa][estrategia][lambda_]["tiempos_convergencia"].append(self.tiempo_convergencia)
                                resultados_instancia[nombre_instancia][alfa][estrategia][lambda_]["f_alfa"].append(np.mean(self.f_alfa))
                                resultados_instancia[nombre_instancia][alfa][estrategia][lambda_]["f_busqueda_local"].append(np.mean(self.f_busqueda_local))
            elif self.algoritmo == "GA":
                resultados_instancia.setdefault(nombre_instancia, {})
                for lambda_ in self.lambdas_:
                    resultados_instancia[nombre_instancia].setdefault(lambda_, {"mejores_soluciones": [], "fitness_mejores_soluciones": [], "cobertura_roles_mejores_soluciones": [], "balance_generos_mejores_soluciones": [], "tiempos_convergencia": []})
                    self.lambda_ = lambda_
                    for repeticion in range(self.repeticiones):
                        self.ejecutar()
                        resultados_instancia[nombre_instancia][lambda_]["mejores_soluciones"].append(self.Mejor_Solucion)
                        resultados_instancia[nombre_instancia][lambda_]["fitness_mejores_soluciones"].append(self.fitness_Mejor_Solucion)
                        resultados_instancia[nombre_instancia][lambda_]["cobertura_roles_mejores_soluciones"].append(self.cobertura_roles_Mejor_Solucion)
                        resultados_instancia[nombre_instancia][lambda_]["balance_generos_mejores_soluciones"].append(self.balance_generos_Mejor_Solucion)
                        resultados_instancia[nombre_instancia][lambda_]["tiempos_convergencia"].append(self.tiempo_convergencia)
            self.exportar_resultados_a_JSON(resultados_instancia, "resultados {}".format(nombre_instancia))
            print()
            print("'{}' terminada".format(instancia))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--algoritmo", type=str, required=True)
    parser.add_argument("--repeticiones", type=int, required=True)
    parser.add_argument("--instancias", type=str, required=True)
    parser.add_argument("--tiempo_limite", type=int, required=True)
    parser.add_argument("--lambdas_", type=str, required=True)
    parser.add_argument("--alfas", type=str, required=False, default="[]")
    parser.add_argument("--estrategias_bl", type=str, required=False, default="[]")
    args = parser.parse_args()
    if args.alfas:
        alfas = ast.literal_eval(args.alfas)
    else:
        alfas = []
    if args.estrategias_bl:
        estrategias_bl = ast.literal_eval(args.estrategias_bl)
    else:
        estrategias_bl = []
    mi_experimentacion = Experimentacion_(args.algoritmo, args.repeticiones, args.instancias, args.tiempo_limite, ast.literal_eval(args.lambdas_), alfas, estrategias_bl)
    mi_experimentacion.iniciar()
    print()
    print("Experimentacion finalizada")
    print()