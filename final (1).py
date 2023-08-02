import random as rnd
import math
import time
import numpy as np
import matplotlib.pyplot as plt
from pulp import *
import itertools

pulp.LpSolverDefault.msg = False

def maximizacionPuntaje(x2, x3):
	# Crear el problema de maximización
	prob = LpProblem("MaximizarPuntaje", LpMaximize)
	# Variables de decisión
	x1 = LpVariable("x1", lowBound=0, upBound=15, cat="Integer")
	x2 = LpVariable("x2", lowBound=0, upBound=x2, cat="Integer")
	x3 = LpVariable("x3", lowBound=0, upBound=x3, cat="Integer")
	x4 = LpVariable("x4", lowBound=0, upBound=4, cat="Integer")
	x5 = LpVariable("x5", lowBound=0, upBound=30, cat="Integer")

	# Función objetivo
	prob += 65 * x1 + 90 * x2 + 40 * x3 + 60 * x4 + 20 * x5
	# Restricciones
	prob += 1000 * x1 + 2000 * x2 + 1500 * x3 + 2500 * x4 + 300 * x5 <= 50000
	prob += x1 + x2 <= 20
	prob += 150 * x1 + 300 * x2 <= 1800
	# Resolver el problema
	status = prob.solve()
	# Verificar el estado de la solución
	if status == LpStatusOptimal:
		# Obtener los valores de las variables de decisión
		valores_variables = {}
		valor_funcion_objetivo = pulp.value(prob.objective)
		for variable in prob.variables():
			valores_variables[variable.name] = variable.varValue
	return valor_funcion_objetivo, valores_variables

def maximizacionCosto(x2, x3):
	# Crear el problema de maximización
	prob = LpProblem("MaximizarCosto", LpMaximize)
	# Variables de decisión
	x1 = LpVariable("x1", lowBound=0, upBound=15, cat="Integer")
	x2 = LpVariable("x2", lowBound=0, upBound=x2, cat="Integer")
	x3 = LpVariable("x3", lowBound=0, upBound=x3, cat="Integer")
	x4 = LpVariable("x4", lowBound=0, upBound=4, cat="Integer")
	x5 = LpVariable("x5", lowBound=0, upBound=30, cat="Integer")
	# Función objetivo
	prob += 150*x1 +  300*x2  +  40*x3 +  100*x4  +  10*x5
	# Restricciones
	prob += 1000 * x1 + 2000 * x2 + 1500 * x3 + 2500 * x4 + 300 * x5 <= 50000
	prob += x1 + x2 <= 20
	prob += 150 * x1 + 300 * x2 <= 1800

	# Resolver el problema
	status = prob.solve()
	# Verificar el estado de la solución
	if status == LpStatusOptimal:
		# Obtener los valores de las variables de decisión
		valores_variables = {}
		valor_funcion_objetivo = pulp.value(prob.objective)
		for variable in prob.variables():
			valores_variables[variable.name] = variable.varValue
	return valor_funcion_objetivo, valores_variables

print("  -->  Encontrando las mejores soluciones para cada modelo  <--")
#Existen 2 casos, donde x2 es igual a 0 por y y donde x3 es igual a 0 por y
x2_0_f1 = maximizacionPuntaje(0, 25)
x3_0_f1 = maximizacionPuntaje(10, 0)

best_max_f1 = x2_0_f1 if x2_0_f1[0] > x3_0_f1[0] else x3_0
LIMITE_FUNCION1 = best_max_f1[0]


x2_0_f2 = maximizacionCosto(0, 25)
x3_0_f2 = maximizacionCosto(10, 0)

best_max_f2 = x2_0_f2 if x2_0_f2[0] > x3_0_f2[0] else x3_0
LIMITE_FUNCION2 = best_max_f2[0]

print("  Maximizacion de puntaje:", LIMITE_FUNCION1)
print("  Maximizacion de costos:",  LIMITE_FUNCION2)
print()


print("  -->  Aplicando Nodo y Arco consistencia  <--")
domains = {
    'x1':  [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    'x2':  [0,1,2,3,4,5,6,7,8,9,10],
    'x3':  [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25],
    'x4':  [0,1,2,3,4],
    'x5':  [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30],
    'y' :  [0,1],
}

constraints = {
    ('x1', 'x2'): lambda a, b: a <= 20 - b,
    ('x2', 'x1'): lambda b, a: 20 - b >= a,
    ('x1', 'x2'): lambda a, b: a * 150 <= 1800 - b * 300,
    ('x2', 'x1'): lambda b, a:  1800 - b * 300 >= a * 150
}

def revise(x, y):
    revised = False
    x_domain = domains[x]
    y_domain = domains[y]
    all_constraints = [
        constraint for constraint in constraints if constraint[0] == x and constraint[1] == y]
    for x_value in x_domain:
        satisfies = False
        for y_value in y_domain:
            for constraint in all_constraints:
                constraint_func = constraints[constraint]
                if constraint_func(x_value, y_value):
                    satisfies = True
        if not satisfies:
            x_domain.remove(x_value)
            revised = True
    return revised

def ac3(arcs):
    queue = arcs[:]
    while queue:
        (x, y) = queue.pop(0)
        revised = revise(x, y)
        if revised:
            neighbors = [neighbor for neighbor in arcs if neighbor[1] == x]
            queue = queue + neighbors

arcs = [
    ('x1', 'x2'), ('x2', 'x1')
]

ac3(arcs)
for key, values in domains.items():
    print(f"  Dominio de {key}: {values}")
  

DIM = 6
MAX_ITERS = 500
N_AGENTS = 10

progreso_max = []
progreso_min = []

class Agent():
	def __init__(self):
		self.x = []
		self.x.append(rnd.choice(domains['x1']))
		self.x.append(rnd.choice(domains['x2']))
		self.x.append(rnd.choice(domains['x3']))
		self.x.append(rnd.choice(domains['x4']))
		self.x.append(rnd.choice(domains['x5']))
		self.x.append(rnd.choice(domains['y']))


	def isBetterThan(self, g):
		return self.fit() > g.fit()

	def fit(self):
		return self.p.eval(self.x)

	def move(self, g):
		self.x[0] = (rnd.choice(domains['x1']))
		self.x[1] = (rnd.choice(domains['x2']))
		self.x[2] = (rnd.choice(domains['x3']))
		self.x[3] = (rnd.choice(domains['x4']))
		self.x[4] = (rnd.choice(domains['x5']))
		self.x[5] = self.toBinary(self.x[5] + rnd.uniform(domains['y']) * (g.x[5] - self.x[5]))
	
	def toBinary(self, x):
		return 1 if (1 / (1 + math.exp(-x))) > rnd.random() else 0

	def _str_(self) -> str:
		return f"  fit:{self.fit()} x:{self.x}"

	def copy(self, a):
		self.x = a.x.copy()
	
	def toString(self):
		return self.x

class Swarm:
	def __init__(self):
		self.swarm = []
		self.g = Agent()

	def solve(self):
		self.initRand()
		self.evolve()

	def initRand(self):
		print("\n  -->  Fase de inicialización  <-- ")
		for _ in range(N_AGENTS):
			while True:
				a = Agent()
				if self.isFeasible(a.toString()):
					break
			self.swarm.append(a)
		self.swarmToConsole()

	def checkConstraint(self, x):
		x1, x2, x3, x4, x5, y = x
		return (
				min(domains['x1']) <= x1 <= max(domains['x1'])
			and min(domains['x2']) <= x2 <= max(domains['x2'])*(1-y)
			and min(domains['x3']) <= x3 <= max(domains['x3'])*y
			and min(domains['x4']) <= x4 <= max(domains['x4'])
			and min(domains['x5']) <= x5 <= max(domains['x5'])
			and min(domains['y']) <= y <= max(domains['y'])
			
			and x1 * 1000 + x2*(1-y) * 2000 + x3 * y * 1500 + x4 * 2500 + x5 * 300 <= 50000 # x1 * 1000 <= 50000 - x2 * 2000
			and x1 + x2*(1-y) <= 20 # x1 <= 20 - x2
			and 150*x1 + 300 * x2*(1-y) <= 1800  #x1 * 150 <= 1800 - x2 * 300
		)
			
	def isFeasible(self, x):
			return self.checkConstraint(x)
			
	def ver(self, x):
		x1, x2, x3, x4, x5, y = x
		f_min = 150*x1 +  300*x2*(1-y)  +  40*x3*(y)  +  100*x4  +  10*x5  # Función de minimización
		f_max =  65*x1 +   90*x2*(1-y)  +  40*x3*(y)  +   60*x4  +  20*x5  # Función de maximización
		return f_max, f_min

	def mostrar(self, x):
		x1, x2, x3, x4, x5, y = x
		f_min = 150*x1 +  300*x2*(1-y)  +  40*x3*(y)  +  100*x4  +  10*x5  # Función de minimización
		f_max =  65*x1 +   90*x2*(1-y)  +  40*x3*(y)  +   60*x4  +  20*x5  # Función de maximización
		print("\n  f max: ", f_max)
		print("  f min: ", f_min)
		
	def F_obj(self, x):
		x1, x2, x3, x4, x5, y = x
		f_min = 150*x1 +  300*x2*(1-y)  +  40*x3*(y)  +  100*x4  +  10*x5  # Función de minimización
		f_max =  65*x1 +   90*x2*(1-y)  +  40*x3*(y)  +   60*x4  +  20*x5  # Función de maximización
		f_obj = (f_max / LIMITE_FUNCION1) * 0.5 + ((LIMITE_FUNCION2 - f_min) / LIMITE_FUNCION2 - 0) * 0.5
		return (f_obj)
		
	def evolve(self):
		
		UB = [max(domains['x1']), max(domains['x2']), max(domains['x3']), max(domains['x4']), max(domains['x5']), max(domains['y'])]  # Valor superior del límite
		LB = [min(domains['x1']), min(domains['x2']), min(domains['x3']), min(domains['x4']), min(domains['x5']), min(domains['y'])]  # Valor inferior del límite	
		
		print("\n  -->  Comienza RSA  <-- ")
		
		Best_P = [1 for i in range(N_AGENTS)]
		Best_F = - float('inf')
		X = np.empty((N_AGENTS, DIM), dtype=object)
		for i in range(N_AGENTS):
			X[i] = self.swarm[i].toString()	
		Xnew = np.zeros((N_AGENTS, DIM))
		Conv = np.zeros(MAX_ITERS)
		
		Alpha = 0.1
		Beta = 0.005
		Ffun = np.zeros(X.shape[0])
		Ffun_new = np.zeros(X.shape[0])
		
		for i in range(X.shape[0]):
			
			Ffun[i] = self.F_obj(X[i, :])# Calcular los valores de aptitud de las soluciones
			if Ffun[i] > Best_F:
				Best_F = Ffun[i]
				Best_P = X[i, :]

		# Imprimir el mejor valor de aptitud y la mejor solución
		print("  Mejor Fitnees:", Best_F)
		print("\n  Mejor solución hasta ahora:", Best_P)

		t = 0
		while t < MAX_ITERS:
			ES = 2 * np.random.randint(-1, 2) * (1 - (t / MAX_ITERS))  # Ratio de probabilidad
			for i in range(1, X.shape[0]):
				for j in range(X.shape[1]):
					R = (Best_P[j] - X[np.random.randint(0, X.shape[0]), j]) / (Best_P[j] + sys.float_info.epsilon)
					P = Alpha + (X[i, j] - np.mean(X[i, :])) / (Best_P[j] * (UB[j] - LB[j]) + sys.float_info.epsilon)
					Eta = Best_P[j] * P
					
					if t < MAX_ITERS / 4:
						Xnew[i, j] = Best_P[j] - Eta * Beta - R * np.random.rand()
					elif t < 2 * MAX_ITERS / 4 and t >= MAX_ITERS / 4:
						Xnew[i, j] = Best_P[j] * X[np.random.randint(0, X.shape[0]), j] * ES * np.random.rand()
					elif t < 3 * MAX_ITERS / 4 and t >= 2 * MAX_ITERS / 4:
						Xnew[i, j] = Best_P[j] * P * np.random.rand()
					else:
						Xnew[i, j] = Best_P[j] - Eta * sys.float_info.epsilon - R * np.random.rand()				
				Flag_UB = Xnew[i, :] >= UB # verificar >=
				Flag_LB = Xnew[i, :] <= LB # verificar <=
				Xnew[i, :] = np.where(~(Flag_UB + Flag_LB), Xnew[i, :], Xnew[i, :] * (~(Flag_UB + Flag_LB)) + UB * Flag_UB + LB * Flag_LB) #
				Xnew[i, :] = np.floor(Xnew[i, :])
				
				if(self.isFeasible(Xnew[i, :])):
					Ffun_new[i] = self.F_obj(Xnew[i, :])
					if Ffun_new[i] > Ffun[i]:
						X[i, :] = Xnew[i, :]
						Ffun[i] = Ffun_new[i]

					if Ffun[i] > Best_F:
						Best_F = Ffun[i]
						Best_P = X[i, :]
			
			#observar como se van modiviendo las funciones objetivo
			progreso_max.append(self.ver(Best_P)[0])
			progreso_min.append(self.ver(Best_P)[1])
				
			Conv[t] = Best_F
			if t % 50 == 0:
				print(f"  En la iteración {t}, la mejor aptitud de la solución es {Best_F}")
			t += 1
			
		self.mostrar(Best_P)
		print("\n  La mejor solución obtenida por RSA es:", ", ".join([("x" + str(i+1) if i!= 5 else "y") + "=" + str(int(Best_P[i])) for i in range(len(Best_P))]) )
		print("  El mejor valor óptimo de la función objetivo encontrado por RSA es:", Best_F)
				

	def swarmToConsole(self):
		print("\n -- inicialización --")
		for i in range(N_AGENTS):
			print(f"  {self.swarm[i].toString()}")

	def bestToConsole(self):
		print("\n -- Best --")
		print("X1  X2  X3  X4  X5 Y")
		print(f"{self.g.toString()}")

try:
	Swarm().solve()
except Exception as e:
	print(f"{e} \nCaused by {e._cause_}")


# FRONTERA DE PARETO
import itertools
import matplotlib.pyplot as plt

# Definir las funciones objetivo
def objetivo1(x1, x2, x3, x4, x5, y):
    if x1 * 1000 + x2 * 2000 + x3* 1500 + x4 * 2500 + x5 * 300 <= 50000 and x1 + x2 <= 20 and 150*x1 + 300 * x2 <= 1800:
        return 150*x1 +  300*x2*(1-y)  +  40*x3*y  +  100*x4  +  10*x5
    else:
        return "no"

def objetivo2(x1, x2, x3, x4, x5, y):
    if x1 * 1000 + x2 * 2000 + x3* 1500 + x4 * 2500 + x5 * 300 <= 50000 and x1 + x2 <= 20 and 150*x1 + 300 * x2 <= 1800:
        return 65*x1 +   90*x2*(1-y)  +  40*x3*y  +   60*x4  +  20*x5
    else:
        return "no"

# Definir los rangos de valores de las variables
x1_range = range(min(domains['x1']), max(domains['x1']))
x2_range = range(min(domains['x2']), max(domains['x2']))
x3_range = range(min(domains['x3']), max(domains['x3']))
x4_range = range(min(domains['x4']), max(domains['x4']))
x5_range = range(min(domains['x5']), max(domains['x5']))
y_range  = range(min(domains['y']) , max(domains['y']))

# Generar todas las posibles combinaciones de valores
combinations = itertools.product(x1_range, x2_range, x3_range, x4_range, x5_range, y_range)
# Calcular los valores de las funciones objetivo para cada combinación
solutions = []
for combination in combinations:
    x1, x2, x3, x4, x5, y = combination
    obj1_value = objetivo1(x1, x2, x3, x4, x5, y)
    obj2_value = objetivo2(x1, x2, x3, x4, x5, y)
    if obj1_value != "no":
        solutions.append((obj1_value, obj2_value))

x_vals = [coord[0] for coord in solutions]
y_vals = [coord[1] for coord in solutions]
# Crear el gráfico de dispersión
plt.scatter(x_vals, y_vals)
# Etiquetas de los ejes
maximo = 0
x,y = 0, 0
valores_x = []
valores_y = []

lista_x = []
for i in solutions:
	x = i[0]
	y = i[1]
	if(x not in valores_x):
		#es inicialemtne de pareteo
		valores_x.append(x)
		valores_y.append(y)
	else:
		if(y > valores_y[valores_x.index(x)]):
			valores_y[valores_x.index(x)] = y
			
frontera = []
for i in range(len(valores_x)):
	frontera.append((valores_x[i], valores_y[i]))

for punto in frontera:
    plt.scatter(punto[0], punto[1], color='red')

plt.xlabel('Max Z = 65x1 + 90x2 + 40x3 + 60x4+ 20x5')
plt.ylabel('Max(Min) Z = 150x1+ 300x2 + 40x3+ 100x4+ 10x5')
# Título del gráfico
plt.title('Frontera de pareto')
# Mostrar el gráfico
plt.show()


#GRAFICO DE CONVERGENCIA, RESULTADO DE LAS FUNCIONES A TRAVES DEL TIEMPO
iteraciones = range(1, MAX_ITERS + 1)

convergencia_x = []
convergencia_y = []

for i in iteraciones:
	convergencia_x.append(progreso_max[i-1])
	convergencia_y.append(progreso_min[i-1])

plt.plot(iteraciones, convergencia_x, label='Max Z = 65x1 + 90x2 + 40x3 + 60x4+ 20x5')
plt.plot(iteraciones, convergencia_y, label='Max(Min) Z = 150x1+ 300x2 + 40x3+ 100x4+ 10x5')
plt.xlabel('Iteraciones')
plt.ylabel('Valor')
plt.title('Convergencia de las soluciones a través de Iteraciones')
plt.legend()
plt.show()

