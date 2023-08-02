import simpy
import random
import numpy as np

# Tiempo de inicio y fin de la simulación
TIEMPO_INICIO = 17 * 60  # 17:00 en minutos
TIEMPO_FIN = 20 * 60  # 20:00 en minutos

# Tiempo que tarda una persona en escoger una máquina
TIEMPO_ESCOGER_MAQUINA = 2

# Tiempos de uso de cada máquina (en segundos)
PROBABILIDAD_USO_MAQUINA = {
	1: 120 / 41,
	2: 120 / 34,
	3: 120 / 19,
	4: 120 / 26
}

TIEMPO_MEDIO_USO_MAQUINA = {
	1: 55,
	2: 25,
	3: 30,
	4: 25,
}

VARIANZA_POR_MAQUINA = {  # la varianza real de las maquinas
	1: 10,
	2: 8,
	3: 7,
	4: 6,
}

def formato_tiempo(minutos):
	horas = minutos // 60
	minutos = minutos % 60
	return f'{int(horas):02d}:{int(minutos):02d}'

class Persona:
	def __init__(self, env, nombre):
		self.env = env
		self.nombre = nombre
		self.maquinas_utilizadas = []

	def escoger_maquina(self, maquinas):
		# La persona escoge una máquina aleatoria de las disponibles y no utilizadas
		maquinas_disponibles_no_utilizadas = [
			maquina for maquina in maquinas if maquina not in self.maquinas_utilizadas]
		maquina_escogida = random.choice(maquinas_disponibles_no_utilizadas)
		self.maquinas_utilizadas.append(maquina_escogida)
		print(f'Tiempo {formato_tiempo(env.now)}: {self.nombre} escoge la maquina {maquina_escogida}. Personas en el gimnasio: {self.gimnasio.personas_en_gimnasio}')

		# Esperar el tiempo de uso de la máquina
		# tiempo_uso = TIEMPO_USO_MAQUINA[maquina_escogida]
		tiempo_uso = max(0, random.normalvariate(
			TIEMPO_MEDIO_USO_MAQUINA[maquina_escogida], VARIANZA_POR_MAQUINA[maquina_escogida]))
		yield env.timeout(tiempo_uso)

		# si utilizo todas las maquinas del gimnasio la persona se va (editar para que use todas las que eligio en base a las "rutinas mas elegidas")
		if len(self.maquinas_utilizadas) == self.gimnasio.NUM_MAQUINAS:
			self.maquinas_utilizadas = []
			self.gimnasio.personas_en_gimnasio -= 1
			print(
				f'Tiempo {formato_tiempo(env.now)}: {self.nombre} deja el gimnasio ->. Personas en el gimnasio: {gimnasio.personas_en_gimnasio}')
		else:
			print(f'Tiempo {formato_tiempo(env.now)}: {self.nombre} deja la maquina {maquina_escogida}. Personas en el gimnasio: {gimnasio.personas_en_gimnasio}')
			# Esperar 2 segundos antes de escoger la siguiente máquina
			espera = max(0, random.normalvariate(TIEMPO_ESCOGER_MAQUINA, 0.5))
			yield env.timeout(espera)
			if len(self.maquinas_utilizadas) < self.gimnasio.NUM_MAQUINAS:
				env.process(self.escoger_maquina())


class Gimnasio:
	def __init__(self):
		self.personas = []
		self.personas_en_gimnasio = 80  # horario pick
		self.limite_personas = 120
		self.NUM_MAQUINAS = 4
		self.maquinas_disponibles = self.maquinas()
	
	def maquinas(self):
		maquinas = []
		# aqui se genera la probabilidad de uso de cada maquina, probabilidad para usar la 1, 2, 3 y 4 por separado (no son una rutina)
		for i in range(4):
			if random.random() < PROBABILIDAD_USO_MAQUINA[i+1]:
				maquinas.append(i+1)
		return maquinas
	
	
	def simular(self):
		for persona in personas:
			# Generar un tiempo de llegada aleatorio siguiendo una distribución exponencial
			tiempo_llegada += random.expovariate(1)
			env.process(llegada_persona(env, persona))
			env.run(until=TIEMPO_INICIO + tiempo_llegada)
			
	def setPersonas(self, lista_personas):
		self.personas = lista_personas
	
	

def retirar_personas(env, gimnasio):
	while True:
		# Esperar 30 minutos
		yield env.timeout(20)
		# determinar el número de personas a retirar (entre 1 y 3)
		num_personas_retirar = random.randint(1, 3)
		# verificar que haya suficientes personas en el gimnasio para retirar
		if gimnasio.personas_en_gimnasio >= num_personas_retirar:
			personas_retirar = random.sample(
				range(1, 60), num_personas_retirar)
			gimnasio.personas_en_gimnasio -= num_personas_retirar

			personas_retiradas = ', '.join(
				[f'Persona {i}' for i in personas_retirar])
			print(f'Tiempo {formato_tiempo(env.now)}: Se retiran {num_personas_retirar} personas del gimnasio: {personas_retiradas}. Personas en el gimnasio: {gimnasio.personas_en_gimnasio}')


def llegada_persona(env, persona, gimnasio):
	# llega al gimnasio y espera antes de escoger la primera máquina
	tiempo_llegada = env.now
	if (gimnasio.personas_en_gimnasio + 1 > 120):
		print(f'Tiempo {formato_tiempo(tiempo_llegada)}: {persona.nombre} llega al gimnasio pero se va. Personas en el gimnasio: {gimnasio.personas_en_gimnasio} ')
	else:
		print(f'Tiempo {formato_tiempo(tiempo_llegada)}: {persona.nombre} llega al gimnasio <-. Personas en el gimnasio: {gimnasio.personas_en_gimnasio} ')
		gimnasio.personas_en_gimnasio += 1

	espera = max(0, random.normalvariate(TIEMPO_ESCOGER_MAQUINA, 0.5))
	yield env.timeout(espera)

	# la persona escoge su primera máquina
	env.process(persona.escoger_maquina())


env = simpy.Environment(initial_time=TIEMPO_INICIO)
gimnasio = Gimnasio()
personas = [Persona(env, f'Persona {i+1}', gimnasio)
			for i in range(80, gimnasio.limite_personas + 40)]

gimnasio.setPersonas(personas)
tiempo_llegada = 0



# Ejecutar la simulación
# retirar personas cada tanto tiempo
env.process(retirar_personas(env, gimnasio))
env.run(until=TIEMPO_FIN)
