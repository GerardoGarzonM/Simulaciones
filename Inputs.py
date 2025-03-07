import numpy as np
import random as r
import plotly.express as px 
import pandas as pd
import math as m 
from perlin_noise import PerlinNoise

import tkinter as tk
from tkinter import simpledialog


class presa: #Declaración de la clase presa, definiendo sus atributos
    def __init__(self, pos_x, pos_y, state, prob, species_id, desplazamiento, desviacion):
        self.sp = species_id 
        self.p = prob #Probabilidad de escape de la presa
        self.x = pos_x #Posicion horizontal de la presa
        self.y = pos_y  #Posicion vertical de la presa
        self.state = state #Estado (1-Viva, 0-Muerta)
        self.desp = desplazamiento #Desplazamiento promedio (km/dia)
        self.desv = desviacion # Desviacion estandar del desplazamiento promedio



class Individuals: #Se inicia la clase depredadores, con datos generales.
    def __init__(self, pos_x, pos_y, state, species_id, desplazamiento, cond, desv, prob, hambre, rango):
        self.sp = species_id
        self.x = pos_x  #Posicion horizontal del depredador
        self.y = pos_y  #Posicion vertical del depredador
        self.state = state #Estado (1-Vivo, 0-Muerto)
        self.desp = desplazamiento  #Desplazamiento promedio (km/dia)
        self.co = cond #Conducta (0-Aleatoria, 1-Ciclica)
        self.desv = desv # Desviacion estandar del desplazamiento promedio
        self.p = prob #Probabilidad de caza exitosa
        self.hambre = hambre #Dias que lleva el depredador sin comer
        self.rango = rango #Rango de detección promedio del depredador

class Aleatorio(Individuals): #Subclase de depredadores con movimiento aleatorio.
    def __init__(self, pos_x, pos_y, state, species_id, desplazamiento, point_x, point_y,cond, desv, prob, hambre, rango):
        super().__init__(pos_x, pos_y, state, species_id, desplazamiento,cond, desv, prob, hambre, rango)
        self.px = point_x #Punto inicial
        self.py = point_y 


class Ciclico(Individuals): #Subclase de depredaores con movimiento en ciclos.
    def __init__(self, pos_x, pos_y, state, species_id, desplazamiento, point_x, point_y, tiempo, cont, cond, desv, prob, hambre, rango):
        super().__init__(pos_x, pos_y, state, species_id, desplazamiento,cond, desv, prob, hambre, rango)
        self.px = point_x #Punto inicial
        self.py = point_y
        self.t = tiempo #Tiempo que tarda en terminar un ciclo de movimiento
        self.c = cont #Contador de cuantos dias lleva en su ciclo de movimiento

def mov_ciclico( x, y, c, tiempo, centro, desv): #Funcion para el movimiento ciclico.
    ra = np.random.normal( centro, desv ) #Distancia a recorrer.
    if c == 0: #Se checa el valor del contador, si es cero, entonces se va a iniciar un nuevo ciclo.
        C = tiempo #Se actualiza el contador.
        theta = np.pi*(r.randint(0,7)) #Angulo de direccion aleatorio (8 posibles).
        X = x+ ra *np.cos(theta) #Obtencion de coordenadas cartesianas.
        Y =y+ ra *np.sin(theta) 
    else: #Contador diferente de cero, entonces ya hay un ciclo en curso.
        theta = (2* np.pi / tiempo)* (tiempo- c) #Angulo de direccion.
        C = c - 1 #Se actualiza el contador.
        X=x + ra *np.cos(theta) #Se obtienen coordenadas cartesianas.
        Y=y + ra *np.sin(theta)
    return X,Y,C #Se regresan las coordenadas actualizadas y el contador actualizado.




def dist(x1, y1, x2, y2): #Funcion para hallar la distancia entre dos puntos.
    return m.sqrt((x2 - x1)**2 + (y2 - y1)**2  )

def sigmoide(t, inflexion): #Funcion que añade mas o menos rango de percepcion dependiendo del tiempo que lleva sin comer
    return 0.5- (1/(1+m.exp(-t+inflexion)))



#Ahora se pasa a la creacion de los diferentes diccionarios para el almacenamiento de datos de los diferentes individuos

dep_d = dict() #Diccionario de depredadores diurnos
dep_n = dict() #Diccionario de depredadores nocturnos
pr_d = dict()  #Diccionario de presas diurnas
pr_n = dict()  #Diccionario de presas nocturnas

pr_M = dict()  #Diccionario de presas muertas


data = pd.read_excel('Datos.xlsx') #Se leen los datos del excel




# Crear la ventana principal
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Pedir al usuario que introduzca el tiempo de la simulacion (cada unidad de tiempo corresponde a medio dia)
tiempo = simpledialog.askinteger("Entrada de Número", "Introduce un número:")

n = 40 #Tamaño de la simulacion (km)





# tiempo = int( input("Tiempo de la simulacion: ") )


graf = {
    "x":[],
    "y":[], #Arreglo para graficar el movimiento
    "t":[],
    "species":[]

}


noise = PerlinNoise(octaves=10, seed=13) #Creacion del mapa de ruido aleatorio que sirve como mapa de peligros
ruido = np.zeros((n,n))
for i in range(n):
    for j in range(n):
        ruido[i,j] = noise([i/n,j/n])

MIN = np.min(ruido) #Se buscan los valores minimo y maximo para el reescalamiento
MAX = np.max(ruido)

MIN2 = -0.5 #Se introducen los nuevos valores minimo y maximo
MAX2 = 0.5


ruido = MIN2 + ((ruido - MIN) * (MAX2 - MIN2)) / (MAX - MIN) #Se reescala la matriz



number_species = len(data['Id']) #Se obtiene el numero de especies que hay

for i in range(number_species): #Comienza ciclo sobre 
    ind = data.loc[i,"Individuos"] #Numero de individuos de la especie numero i
    hr = data.loc[i, "Horario"] # Su horario (0-Diurno, 1-Nocturno)
    tp = data.loc[i, "Tipo"] # Tipo de especie (0-Depredador, 1-Presa)
    DN = len(dep_n)
    DD = len(dep_d) #Constantes auxiliares
    PN = len(pr_n)  #Que son la cantidad de elementos
    PD = len(pr_d)  #En cada diccionario
    umbral_p = 0 #Se introduce el parametro de umbral de peligro

    if hr == 0 and tp == 0: # Depredadores nocturnos
        cond = data.loc[i, "Conducta"] #Conducta de movimiento  (0 - Aleatoria, 1 - Ciclica)
        if cond == 0: #Conducta aleatoria
            for j in range(ind):
                u = r.randint(0,n-1) #Se usan numeros aleatorios para  designar las posiciones iniciales
                v = r.randint(0,n-1)
                dep_n[DN + j] = Aleatorio(u, v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v, 0, data.loc[i,"Desviación"], data.loc[i,"Probabilidad"], 0, data.loc[i,"Rango"])
                #Se llena el diccionario correspondiente con los elementos y las propiedades que se describen
        else: #Conducta ciclica
            for j in range(ind):
                u = r.randint(0,n-1)
                v = r.randint(0,n-1)
                dep_n[DN + j] = Ciclico(u,v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v, data.loc[i,"Tiempo"], 0, 1, data.loc[i,"Desviación"], data.loc[i,"Probabilidad"], 0, data.loc[i,"Rango"] )
    #Se repite el proceso para los demas casos


    if hr == 1 and tp == 0: # Depredadores diurnos
        #Se hace el mismo procedimiento que en el paso anterior
        cond = data.loc[i, "Conducta"]
        if cond == 0:

            for j in range(ind):
                u = r.randint(0,n-1)
                v = r.randint(0,n-1)
                dep_d[DD + j] = Aleatorio(u,v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v,cond, data.loc[i, "Desviación"],  data.loc[i,"Probabilidad"], 0)
        else:
            for j in range(ind):
                u = r.randint(0,n-1)
                v = r.randint(0,n-1)
                dep_d[DD + j] = Ciclico(u,v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v, data.loc[i,"Desplazamiento"],0,cond, data.loc[i,"Desviación"],  data.loc[i,"Probabilidad"], 0 )
    
    if hr == 0 and tp == 1: #Presas nocturnas
        for j in range(ind):
            while(True): #Se hace un ciclo while para determinar la posicion inicial de las presas
                    u = r.randint(0,n-1) #Se usan numeros aleatorios para  designar las posiciones iniciales
                    v = r.randint(0,n-1)
                    if (ruido[u,v] < umbral_p):  #Si el nivel de peligro es menor al umbral de peligro, significa  que la sona es segura
                                                 #por lo cual si podra haber presas en ese lugar, de lo contrario se sigue iterando
                        break
            pr_n[PN + j] = presa(r.randint(0,n-1), r.randint(0,n-1), 1, data.loc[i, "Probabilidad"], data.loc[i,"Id"], data.loc[i,"Desplazamiento"], data.loc[i,"Desplazamiento"])
            #Se terminan de llenar ños datos

    elif hr==1 and tp == 1: #Presas diurnas
        #El proceso es el mismo
        for j in range(ind):
            while(True):
                    u = r.randint(0,n-1) #Se usan numeros aleatorios para  designar las posiciones iniciales
                    v = r.randint(0,n-1)
                    if (ruido[u,v] < umbral_p):
                        break
            pr_d[PD + j] = presa(r.randint(0,n-1), r.randint(0,n-1), 1, data.loc[i, "Probabilidad"], data.loc[i,"Id"], data.loc[i,"Desplazamiento"], data.loc[i,"Desplazamiento"])




Contador_distancia =0 #Se añaden los dos valores que más se van a medir, que es la cantidad de veces que una presa estuvo a poca distancia de un depredador
Contador_interaccion =0 #Y la cantidad de veces que esta cercania dio como resultado una presa muerta y un depredador alimentado.

limite_hambre=21 #Este valor da el tiempo limite (en dias) que un depredador puede aguantar sin comer.

for t in range(tiempo): #Se inicia el ciclo de la simulacion, la unidad del tiempo es 12 hrs, por cada 2 tiempos pasa un dia.
    if t%2==0: #Se toma que en los tiempos pares sea de noche
        for i in list(pr_n): #Movimiento de presas nocturnas
            if pr_n[i].state == 0:
                pass
            else:
                ra = np.random.normal( pr_n[i].desp, pr_n[i].desv )
                theta = 2*np.pi * np.random.rand()
                pr_n[i].x += ra* np.cos(theta) #Se hace movimiento aleatorio de las presas
                pr_n[i].y += ra* np.sin(theta)
                


        for i in list(dep_n): #Se itera sobre los depredadores nocturnos
            if dep_n[i].hambre >limite_hambre: #Si sus dias sin comer son mayores que el limite designado, el depredador muere
                dep_n[i].state = 0
            else:
                pass #De no ser asi, sigue vivo

            if dep_n[i].state == 1: #Si el i-esimo depredador sigue vivo, entonces se hace su movimiento
                if dep_n[i].co == 0: #Movimiento aleatorio
                    ra = np.random.normal( dep_n[i].desp, dep_n[i].desv )
                    theta = 2*np.pi * np.random.rand() 
                    dep_n[i].x += ra* np.cos(theta) #Cambio de posicion
                    dep_n[i].y += ra* np.sin(theta)
       


                        
                else: #Comportamiento ciclico
                    #Se hace uso de la funcion de movimiento ciclico para hallar la nueva posicion del depredador
                    X, Y, C = mov_ciclico( dep_n[i].x, dep_n[i].y, dep_n[i].c, dep_n[i].t, dep_n[i].desp, dep_n[i].desv)
                    
                    dep_n[i].x = X #Se actualizan las posiciones
                    dep_n[i].y = Y
                    dep_n[i].c = C

                for k in list(pr_n): #Ahora se hace la busqueda de presas a corta distancia
                        if dist(dep_n[i].x, dep_n[i].y, pr_n[k].x, pr_n[k].y) > (dep_n[i].rango + sigmoide(dep_n[i].hambre, 11)):
                            #Si la distancia de la k-esima presa con el i-esimo depredador es mayor a su rango de deteccion 
                            #Mas la deteccion extra que gana o pierde dependiendo de su hambre, entonces el depredador no detecta a la presa
                            pass
                        else: #En caso contrario, el depredador detecta a la presa, y entonces se pasa a la parte de probabilidades
                            Contador_distancia +=1 #Se actualiza el contador respectivo
                            numero1 = np.random.rand() #Se obtiene un numero aleatorio de una distribucion uniforme de [0,1)
                            if numero1 < (pr_n[k].p +  ruido[round((pr_n[k].x)%(n-1)), round((pr_n[k].y)%(n-1))]): #Si el numero resulta ser menor que la probabilidad de escape, significa que la presa escapo
                                dep_n[i].hambre +=1 

                            else:
                                numero2 = np.random.rand()  #Numero aleatorio entre 0 y 1

                                if numero2 < (dep_n[i].p +  ruido[round((pr_n[k].x)%(n-1)), round((pr_n[k].y)%(n-1))]):
                                    #Se hace uso de otro numero aleatorio y si este es menor a la suma de "probabilidad de matar a la presa" mas
                                    # "el peligro del area donde se encuentra la presa", entonces el depredador habra comido a la presa
                                    Contador_interaccion +=1 #Se actualiza el contador respectivo
                                    dep_n[i].hambre=0 #Como la caza fue exitosa, se elimina el hambre que tenia el depredador
                                    L1 = len(pr_M) #Constante auxiliar del numero de elementos de presas muertas
                                    if L1 ==0:
                                        pr_n[k].state = 0
                                        pr_n[k].c = t
                                        pr_M[0] = pr_n[k] #En caso de que sea la primera presa muerta, se comienza a llenar el diccionario
                                        pr_n[k].x = -1000
                                        pr_n[k].y = -1000
                                    
                            
                                    else:
                                        pr_n[k].state = 0
                                        pr_n[k].c = t    
                                        pr_M[L1+1] = pr_n[k] #En otro caso se sigue llenando el diccionario
                                        pr_n[k].x = -1000
                                        pr_n[k].y = -1000
                                        
                                    
                                else: #Si el numero elegido es mayor a los parametros usados, entonces la caza del depredador fallo
                                    dep_n[i].hambre +=1 
        

    else: #Dia
        for i in list(pr_d): #Movimiento de presas nocturnas
            if pr_d[i].state == 0:
                pass
            else:
                ra = np.random.normal( pr_d[i].desp, pr_d[i].desv )
                theta = 2*np.pi * np.random.rand()
                pr_d[i].x += ra* np.cos(theta) #Movimiento aleatorio
                pr_d[i].y += ra* np.sin(theta)
        
        for i in list(dep_d): #Se itera sobre los depredadores nocturnos
            if dep_d[i].hambre >limite_hambre: #Se checa el valor de hambre
                dep_d[i].state = 0
            else:
                pass
        

        for i in list(dep_d):
            if dep_d[i].state == 1:
                if dep_d[i].co == 0:
                        ra = np.random.normal( dep_d[i].desp, dep_d[i].desv )
                        theta = 2*np.pi * np.random.rand()
                        dep_d[i].x += ra* np.cos(theta) #Movimiento aleatorio
                        dep_d[i].y += ra* np.sin(theta)
                else:
                        X, Y, C = mov_ciclico( dep_d[i].x, dep_d[i].y, dep_d[i].c, dep_d[i].t, dep_d[i].desp, dep_d[i].desv)
                        dep_d[i].x = X
                        dep_d[i].y = Y #Movimiento ciclico
                        dep_d[i].c = C
                for k in list(pr_d):
                        if dist(dep_d[i].x, dep_d[i].y, pr_d[k].x, pr_d[k].y) >  (dep_d[i].rango + sigmoide(dep_d[i].hambre, 11)):
                            pass
                        else:
                            Contador_distancia +=1  #Se actualiza el contador respectivo
                            numero3 = np.random.rand()
                            if  (pr_d[k].p +  ruido[round((pr_d[k].x)%(n-1)), round((pr_d[k].y)%(n-1))]):
                                dep_n[i].hambre +=1 
                            else:
                                numero4 = np.random.rand()
                                if numero4 <( dep_d[i].p + ruido[round((pr_d[k].x)%(n-1)), round((pr_d[k].y)%(n-1))]):
                                    Contador_interaccion += 1  #Se actualiza el contador respectivo
                                    dep_d[i].hambre =0
                                    L1 = len(pr_M)
                                    if L1 ==0:
                                        pr_d[k].state = 0
                                        pr_d[k].c = t
                                        pr_M[0] = pr_d[k]
                                        pr_d[k].x = -1000
                                        pr_d[k].y = -1000
                                    
                            
                                    else:
                                        pr_d[k].state = 0
                                        pr_d[k].c = t
                                        pr_M[L1+1] = pr_n[k]
                                        pr_d[k].x = -1000
                                        pr_d[k].y = -1000
                                        
                                else:
                                    dep_d[i].hambre +=1 
       

        
    for j in dep_n:
        graf["x"].append(dep_n[j].x)
        graf["y"].append(dep_n[j].y) #Se añaden los datos al arreglo de grafica
        graf["species"].append(dep_n[j].sp)

    for j in dep_d:
        graf["x"].append(dep_d[j].x)
        graf["y"].append(dep_d[j].y)
        graf["species"].append(dep_d[j].sp)

    for j in pr_n:
        graf["x"].append(pr_n[j].x)
        graf["y"].append(pr_n[j].y)
        graf["species"].append(pr_n[j].sp)

    for j in pr_d:
        graf["x"].append(pr_d[j].x)
        graf["y"].append(pr_d[j].y)
        graf["species"].append(pr_d[j].sp)

    graf["t"].extend([t] * (len(dep_n) + len(dep_d) + len(pr_n) + len(pr_d)))


print(Contador_interaccion)
print(Contador_distancia)

# Conversión a DataFrame para visualización
df_graf = pd.DataFrame(graf)
fig = px.scatter(
    df_graf,
    x='x',
    y='y',
    animation_frame='t',
    color="species",
    title='Animación de Movimiento de Individuos',
)

fig.update_layout(
    xaxis=dict(range=[-1, 40]),  
    yaxis=dict(range=[-1, 40]),
)

fig.show() #Se muestra la grafica final de la simulacion




