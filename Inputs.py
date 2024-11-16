import numpy as np
import random as r
import plotly.express as px 
import pandas as pd
import math as m 


class presa:
    def __init__(self, pos_x, pos_y, state, prob, species_id):
        self.sp = species_id
        self.p = prob
        self.x = pos_x
        self.y = pos_y
        self.state = state



class Individuals:
    def __init__(self, pos_x, pos_y, state, species_id, desplazamiento, cond, var, prob):
        self.sp = species_id
        self.x = pos_x
        self.y = pos_y
        self.state = state
        self.desp = desplazamiento
        self.co = cond
        self.v = var
        self.p = prob

class Aleatorio(Individuals):
    def __init__(self, pos_x, pos_y, state, species_id, desplazamiento, point_x, point_y,cond, var, prob):
        super().__init__(pos_x, pos_y, state, species_id, desplazamiento,cond, var, prob)
        self.px = point_x
        self.py = point_y
class Ciclico(Individuals):
    def __init__(self, pos_x, pos_y, state, species_id, desplazamiento, point_x, point_y, tiempo, cont, cond, var, prob):
        super().__init__(pos_x, pos_y, state, species_id, desplazamiento,cond, var, prob)
        self.px = point_x
        self.py = point_y
        self.t = tiempo
        self.c = cont

def mov_ciclico( x, y, c, tiempo, centro, desv):
    ra = np.random.normal( centro, desv )
    if c == 0:
        C = tiempo-1
        h = r.randint(-1,1)
        v = r.randint(-1,1)
        
        if h == 1:
            if v==1:
                theta = np.pi / 4
            elif v==-1:
                theta = (7/4)*np.pi
            else:
                theta = np.pi / 2
        elif h == -1:
            if v==1:
                theta = 3*np.pi / 4
            elif v==-1:
                theta = 5* np.pi / 4
            else:
                theta = 3*np.pi / 2
        else:
            if v==1:
                theta = np.pi / 2
            elif v==-1:
                theta = 3 *np.pi / 2
            else:
                theta = 0
        X = x+ ra *np.cos(theta)
        Y =y+ ra *np.sin(theta) 
    else:
        theta = (2* np.pi / tiempo)* (tiempo- c)
        C = c - 1
        X=x + ra *np.cos(theta)
        Y=y + ra *np.sin(theta)
    return X,Y,C

def dist(x1, y1, x2, y2):
    return m.sqrt((x2 - x1)**2 + (y2 - y1)**2  )


dep_d = dict()
dep_n = dict()
pr_d = dict()
pr_n = dict()

pr_M = dict()


data = pd.read_excel('Datos.xlsx')


n = 35
tiempo = int( input("Tiempo de la simulacion: ") )
ex = np.zeros((n,n))
simul = np.zeros((tiempo,n,n))

graf = {
    "x":[],
    "y":[],
    "t":[],
    "species":[]

}


number_species = len(data['Id'])

for i in range(number_species):
    ind = data.loc[i,"Individuos"]
    hr = data.loc[i, "Horario"] # (0-Diurno, 1-Nocturno)
    tp = data.loc[i, "Tipo"] #  (0-Depredador, 1-Presa)
    DN = len(dep_n)
    DD = len(dep_d)
    PN = len(pr_n)
    PD = len(pr_d)

    if hr == 0 and tp == 0: # Depredadores nocturnos
        cond = data.loc[i, "Conducta"] # 0 - Aleatoria, 1 - Ciclica
        if cond == 0:
            for j in range(ind):
                u = r.randint(0,n-1)
                v = r.randint(0,n-1)
                dep_n[DN + j] = Aleatorio(u, v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v, cond, data.loc[i,"Varianza"], data.loc[i,"Probabilidad"])
        else: 
            for j in range(ind):
                u = r.randint(0,n-1)
                v = r.randint(0,n-1)
                dep_n[DN + j] = Ciclico(u,v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v, data.loc[i,"Tiempo"], 0, cond, data.loc[i,"Varianza"], data.loc[i,"Probabilidad"])
    if hr == 1 and tp == 0: # Depredadores diurnos
        cond = data.loc[i, "Conducta"]
        if cond == 0:

            for j in range(ind):
                u = r.randint(0,n-1)
                v = r.randint(0,n-1)
                dep_d[DD + j] = Aleatorio(u,v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v,cond, data.loc[i, "Varianza"],  data.loc[i,"Probabilidad"] )
        else:
            for j in range(ind):
                u = r.randint(0,n-1)
                v = r.randint(0,n-1)
                dep_d[DD + j] = Ciclico(u,v, 1, data.loc[i, "Id"], data.loc[i, "Desplazamiento"], u,v, data.loc[i,"Desplazamiento"],0,cond, data.loc[i,"Varianza"],  data.loc[i,"Probabilidad"] )
    if hr == 0 and tp == 1: #Presas nocturnas
        for j in range(ind):
            pr_n[PN + j] = presa(r.randint(0,n-1), r.randint(0,n-1), 1, data.loc[i, "Probabilidad"], data.loc[i,"Id"])
    elif hr==1 and tp == 1: #Presas diurnas
        for j in range(ind):
            pr_d[PD + j] = presa(r.randint(0,n-1), r.randint(0,n-1), 1, data.loc[i, "Probabilidad"], data.loc[i,"Id"])


for t in range(tiempo):
    if t%2==0: #Noche
        for i in list(dep_n):
            if dep_n[i].co == 0:
                ra = np.random.normal( dep_n[i].desp, dep_n[i].v )
                theta = 2*np.pi * np.random.rand()
                dep_n[i].x += ra* np.cos(theta)
                dep_n[i].y += ra* np.sin(theta)

                    
            else:
                X, Y, C = mov_ciclico( dep_n[i].x, dep_n[i].y, dep_n[i].c, dep_n[i].t, dep_n[i].desp, dep_n[i].v )
                dep_n[i].x = X
                dep_n[i].y = Y
                dep_n[i].c = C
            for k in list(pr_n):
                    if dist(dep_n[i].x, dep_n[i].y, pr_n[k].x, pr_n[k].y) > 1:
                        pass
                    else:
                        Prob = (dep_n[i].p*(1- pr_n[k].p))
                        p1 = np.random.rand() #Numero aleatorio entre 0 y 1
                        if p1 < Prob:
                            L1 = len(pr_M)
                            if L1 ==0:
                                pr_n[k].state = t
                                pr_M[0] = pr_n[k]
                    
                            else:
                                pr_n[k].state = t
                                pr_M[L1+1] = pr_n[k]
                            del pr_n[k]
                            pr_n = {i: pr_n[key] for i, key in enumerate(pr_n)}
                        else:
                            pass 
    
    else: #Dia
        for i in list(dep_d):
            if dep_d[i].co == 0:
                    ra = np.random.normal( dep_d[i].desp, dep_d[i].v )
                    theta = 2*np.pi * np.random.rand()
                    dep_d[i].x += ra* np.cos(theta)
                    dep_d[i].y += ra* np.sin(theta)
            else:
                    X, Y, C = mov_ciclico( dep_d[i].x, dep_d[i].y, dep_d[i].c, dep_d[i].t, dep_d[i].desp, dep_d[i].v )
                    dep_d[i].x = X
                    dep_d[i].y = Y
                    dep_d[i].c = C
            for k in list(pr_d):
                    if dist(dep_d[i].x, dep_d[i].y, pr_d[k].x, pr_d[k].y) > 1:
                        pass
                    else:
                        Prob = (dep_d[i].p*(1- pr_d[k].p))
                        p1 = np.random.rand() #Numero aleatorio entre 0 y 1
                        if p1 < Prob:
                            L1 = len(pr_M)
                            if L1 ==0:
                                pr_d[k].state = t
                                pr_M[0] = pr_d[k]
                    
                            else:
                                pr_d[k].state = t
                                pr_M[L1+1] = pr_d[k]
                            del pr_d[k]
                            pr_d = {i: pr_d[key] for i, key in enumerate(pr_d)}
                        else:
                            pass 

        
    for j in dep_n:
        graf["x"].append(dep_n[j].x)
        graf["y"].append(dep_n[j].y)
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
    xaxis=dict(range=[-15, 45]),  
    yaxis=dict(range=[-15, 45]),
)

fig.show()




