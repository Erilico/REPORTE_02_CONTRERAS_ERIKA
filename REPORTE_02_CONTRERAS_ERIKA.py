# -*- coding: utf-8 -*-
import pandas as pd

"""
Aqui leemos el archivo csv usando la funcion read_csv de pandas
la manera mas sencilla de usarla es sin parametros:
    pd.read_csv('synergy_logistics.csv')
Sin embargo, con el proposito de procesar adecuadamente cada tipo de dato de
cada columna indique:
    index_col=0         # para decir que el register_id es el indice.
    encoding='utf-8'    # para indicar que nuestro documento incluye caracteres
                        # de este tipo.
    parse_dates=[4, 5]  # le estamos especificando aqui que la columna 4 y 5
                        # contienen fechas y quiero que las procese como tal.
"""
synergy_dataframe = pd.read_csv('synergy_logistics_database.csv',
                                index_col=0, encoding='utf-8',
                                parse_dates=[4, 5])
#%%
#Vamos a sacar los países que generan el 80% del valor de las exportaciones 
#e importaciones
#agrupamos por país de origen y sacamos la sumatoria del valor total de cada uno
pais_total_value = synergy_dataframe.groupby("origin").sum()["total_value"].reset_index()
#calculamos la ganancia total para esa categoria (exports/imports)
total_value_for_percent = pais_total_value["total_value"].sum()
#utilizamos ese valor para calcular el porcentaje
pais_total_value["percent"] = 100 * pais_total_value["total_value"]/total_value_for_percent
#ordenamos de mayor a menor los porcentajes de los paises
pais_total_value.sort_values(by="percent",ascending=False, inplace=True)
#calculamos el porcentaje acumulado para ver hasta qué país los ingresos son 
#del 80%
pais_total_value["cumsum"] = pais_total_value["percent"].cumsum()
#recortamos la lista a solo los países arriba del porcentaje acumulado de 80%
lista_pequeña = pais_total_value[pais_total_value["cumsum"] < 80]
print(f"""\nLos países que representan el 80% de todas las ganancias son: 
{lista_pequeña["origin"]}""")
#%%
#Para analizar el top 3 de medios de transporte y el menos rentable primero 
#vamos a calcular el ingreso por cada transporte agrupando por medio de 
#transporte, sumando los total_value que les corresponden y generando dataframe
total_transport = synergy_dataframe.groupby("transport_mode").sum()["total_value"].reset_index()
#ordenamos los medios de transporte por ingresos de mayor a menor
total_transport.sort_values(by="total_value",ascending=False, inplace=True)
#extraemos las primeras 3 filas porque ahí están los 3 medios de transporte con
#más ingresos
top_3 = total_transport.head(3)
#buscamos al transporte que quedó en la última fila para saber qué medio de 
#transporte puede reducir Synergy Logistics
last_transport = total_transport.iloc[-1:]
print(f"""\nLos 3 medios transportes que generan más ganancias son: 
{top_3["transport_mode"]}""")
print(f"""\nEl medio de transporte con menores ganancias es: 
{last_transport["transport_mode"]}""")
#%%
#Las rutas están conformadas por país de origen, país de destino y medio de 
#transporte.
#Si la compañia quiere conocer las 10 rutas más demandadas debemos sacar 
#la cantidad veces que se repite cada ruta.
#para eso primero vamos a agrupar las columnas que conforman las rutas
rutas_database = synergy_dataframe.groupby(by=["origin","destination","transport_mode"])
#contamos las repeticiones de las rutas en un dataframe
demanda_rutas = rutas_database.count()['total_value'].reset_index()
#también vamos a sacar los ingresos de cada ruta para saber cuánto gana la 
#empresa con las rutas más demandadas y si conviene enfocarse en ellas
ganancias_rutas = rutas_database.sum()['total_value'].reset_index()
#unimos los dataframes anteriores para analizarlos juntos
rutas = pd.concat([demanda_rutas, ganancias_rutas], ignore_index=True, sort=False, axis=1)
#quitamos las columnas que se repiten
rutas.drop([4,5,6],axis=1,inplace=True)
#ordenamos de mayor a menor el conteo de las rutas
rutas.sort_values(by=3,ascending=False, inplace=True)
#extraemos las 10 primeras rutas (que son las rutas que más se usaron)
top10demandas = rutas.head(10)
#cambiamos el nombre de las columnas para que se entienda en la visualización
tops = top10demandas.rename(columns={0: "origin",1:"destination",2:"transport",3:"count",7:"ingresos"})

numero_de_rutas = len(demanda_rutas.index)
print(f"""\nSynergy Logistics maneja {numero_de_rutas} rutas de importación y exportación.
Las 10 rutas más demandas son
{tops}""")

#%%
#Vamos a hacer un analisis más para determinar qué opción le vamos a recomendar
#a la empresa.
#La estrategía será calcular el ingreso de cada estrategía y encontrar la que
#tenga los ingresos más altos.

#sumamos los ingresos de los 10 países que dejan el 80% de las ganancias
ingresos_1 = lista_pequeña.sum()["total_value"]
#sumamos el total de ingresos del top 3 de medios de transportes
ingresos_2 = top_3.sum()["total_value"]
#sumamos la columna de ingresos del top de rutas
ingresos_3 = tops.sum()["ingresos"]
#ahora vamos a crear un diccionario y a ordenarlo de mayo a menor para extraer
#cuál de las estrategías es la que deja más ganancia
dicdeingresos = {"opcion1":ingresos_1, "opcion2":ingresos_2, "opcion3":ingresos_3}
dicdeingresos = [[value, key] for key, value in dicdeingresos.items()]
dicdeingresos = sorted(dicdeingresos, reverse=True)
top1 = dicdeingresos[0]
dicdeingresos = dict(dicdeingresos)
print(f"\nLa mejor opción es: {dicdeingresos[top1[0]]}")
