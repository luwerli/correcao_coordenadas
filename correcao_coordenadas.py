# Programa que recebe um arquivo txt com coordenadas geográficas e aplica correções. 
# As correções disponíveis são: 1(uniforme), 2(proporcional) e 3(ambas)
# As correções são aplicadas a todos os pontos do arquivo exceto o primeiro.
# As informações que o usuário deve alterar para sua área de estudo estão marcadas na chamada principal com: ---------

import os
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyproj import Proj


def ler_coordenadas(arquivo):
    """Lê as coordenadas do arquivo e salva em listas"""
    list_lon = []
    list_lat = []
    delimitadores = [';', ',', ' '] # as coordenadas x e y podem estar separadas por ; , ou espaço
    for delimitador in delimitadores:
        try:
            with open(arquivo, 'r') as f:
                linhas = f.readlines()
                for i, linha in enumerate(linhas):
                    if i == 0:  # Ignora a primeira linha que contém o cabeçalho
                        continue
                    componentes = linha.strip().split(delimitador)
                    try:
                        list_lon.append(float(componentes[2])) 
                        list_lat.append(float(componentes[1]))  # latitudes estão na segunda coluna
                    except ValueError:
                        print("Erro na linha:{}".format(linha.strip()))
            break  # Se conseguir ler com o delimitador atual, sai do loop
        except IndexError:
            # Se não conseguir ler, Limpa as listas e tenta com o próximo delimitador
            list_lon.clear()
            list_lat.clear()
            continue
    return list_lon, list_lat


def conversao_utm(list_lon, list_lat, zona, hemisferio):
    """Converte coordenadas geográficas para UTM."""
    proj_utm = Proj(proj="utm", zone=zona, north=(hemisferio == "N"))
    list_x, list_y = [], []

    for lon, lat in zip(list_lon, list_lat):
        x, y = proj_utm(lon, lat)
        list_x.append(x)
        list_y.append(y)

    return list_x, list_y


def correcao_uniforme(list_x, list_y):
    """Aplica a correção uniforme."""
    n = len(list_x)
    delta_x = (list_x[0] - list_x[-1]) / (n - 1)
    delta_y = (list_y[0] - list_y[-1]) / (n - 1)

    x_corrigidos = [list_x[i] + i * delta_x for i in range(n)]
    y_corrigidos = [list_y[i] + i * delta_y for i in range(n)]
    
    return x_corrigidos, y_corrigidos


def correcao_proporcional(list_x, list_y):
    """Aplica a correção proporcional."""
    n = len(list_x)
    distancias = [np.sqrt((list_x[i] - list_x[i-1])**2 + (list_y[i] - list_y[i-1])**2) for i in range(1, n)]
    soma_distancias = sum(distancias)

    x_corrigidos = [list_x[0]] # as coordenadas do primeiro ponto permanecem as mesmas
    y_corrigidos = [list_y[0]]

    for i in range(1, n):
        fator = sum(distancias[:i]) / soma_distancias
        delta_x = (list_x[0] - list_x[-1]) * fator
        delta_y = (list_y[0] - list_y[-1]) * fator

        x_corrigidos.append(list_x[i] + delta_x)
        y_corrigidos.append(list_y[i] + delta_y)
    
    return x_corrigidos, y_corrigidos


def conversao_geograficas(x_corrigidos, y_corrigidos, zona, hemisferio):
    """Converte coordenadas corrigidas de UTM para geográficas"""
    proj_utm = Proj(proj="utm", zone=zona, north=(hemisferio == "N")) # zona de hemisferio definidos pelo usuário
    lon_corrigidos, lat_corrigidos = [], []

    for x, y in zip(x_corrigidos, y_corrigidos):
        lon, lat = proj_utm(x, y, inverse=True)
        lon_corrigidos.append(lon)
        lat_corrigidos.append(lat)

    return lon_corrigidos, lat_corrigidos


def salvar_txt_corrigido(arquivo, lon_corrigidos, lat_corrigidos):
    """Salva as coordenadas corrigidas em um arquivo de texto separado por ;"""
    with open(arquivo, 'w') as f:
        f.write("Longitude;Latitude\n")
        for i in range(len(lon_corrigidos)):
            f.write(f"{lon_corrigidos[i]};{lat_corrigidos[i]}\n")


def salvar_shapefile(shape_pontos, shape_poligono, lon_corrigidos, lat_corrigidos, crs):
    """Salva as coordenadas corrigidas e um polígono que conecta essas coordenadas em um shapefile"""

    # Definir CRS (Sistema de Referência de Coordenadas)
    crs = crs  # crs definido pelo usuário

    # salvar as coordenadas corrigidas
    pontos = [Point(x, y) for x, y in zip(lon_corrigidos, lat_corrigidos)]
    gdf_pontos = gpd.GeoDataFrame(geometry = pontos, crs = crs) #geodataframe é o nome convencional usado no geopandas
    gdf_pontos.to_file(shape_pontos, driver='ESRI Shapefile')

    #salvar o polígono no shapefile
    poligono = Polygon([(x, y) for x, y in zip(lon_corrigidos, lat_corrigidos)])
    gdf_poligono = gpd.GeoDataFrame(geometry=[poligono], crs = crs)
    gdf_poligono.to_file(shape_poligono, driver='ESRI Shapefile', mode='a')
    
    print("Arquivos shapefiles salvos no diretório: {}".format(os.path.abspath(shape_pontos)))


def plotar_grafico(list_lon, list_lat, lon_corrigidos, lat_corrigidos):
    """Plota as coordenadas originais e corrigidas em um gráfico,
    assim como gera a poligonal das coordenadas originais e corrigidas"""
    plt.figure()
    
    # Plotar pontos
    plt.scatter(list_lon, list_lat, color='blue')
    plt.scatter(lon_corrigidos, lat_corrigidos, color='red')

    # Plotar polígonos
    plt.plot(list_lon + [list_lon[0]], list_lat + [list_lat[0]], label='Polígono Original', color='blue')  # Fechar o polígono original
    plt.plot(lon_corrigidos + [lon_corrigidos[0]], lat_corrigidos + [lat_corrigidos[0]], label='Polígono Corrigido', color='red')

    # Plotar rótulos e título
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')
    plt.legend()
    plt.title(f'Correção de coordenadas {correcao}')
    plt.show()


if __name__ == "__main__":
    """chamada principal"""
    # Diretório dos arquivos de entrada e saída
    # -------- Altere os diretórios de entrada e saída para o diretório no seu computador ---------
    arquivo_entrada = r'arquivo.txt'
    arquivo_saida = r'arquivo.txt'
    shape_pontos = r'arquivo.shp'
    shape_poligono = r'arquivo.shp'

    if arquivo_entrada is None:
        print("Falha ao carregar as coordenadas. Fechando programa.")

    # Definição da zona e hemisferio para as coordenadas na projeção UTM
    list_lon, list_lat = ler_coordenadas(arquivo_entrada) # x e y recebem os valores do arquivo de entrada
    zona = '29' # --------  Altere a zona e o hemisferio de acordo com a regiao estudo --------------------
    hemisferio = 'N'
    list_x, list_y = conversao_utm(list_lon, list_lat, zona, hemisferio)

    # Escolha do método de correção
    print("\nEscolha o método de correção:")
    print("1. Correção uniforme")
    print("2. Correção proporcional")
    print("3. Ambas correções")
    opcao = input("Escolha entre os métodos 1, 2 ou 3: ")

    if opcao == '1':
        x_corrigidos, y_corrigidos = correcao_uniforme(list_x, list_y)
        correcao = "Uniforme"
    elif opcao == '2':
        x_corrigidos, y_corrigidos = correcao_proporcional(list_x, list_y)
        correcao = "Proporcional"
    elif opcao == '3':
        x_corrigidos, y_corrigidos = correcao_uniforme(list_x, list_y)
        x_corrigidos, y_corrigidos = correcao_proporcional(x_corrigidos,y_corrigidos)
        correcao = "Uniforme e Proporcional"
    else:
        print("Opção inválida. Fechando programa")

    crs = "32629" # ------------ Altere o crs de acordo com a zona UTM previamente selecionada -------
    lon_corrigidos, lat_corrigidos = conversao_geograficas(x_corrigidos, y_corrigidos, zona, hemisferio)
    plotar_grafico(list_x, list_y, x_corrigidos, y_corrigidos) #  plotagem do gráfico em coordenadas planas

    # Opções de arquivo para salvar as coordenadas corrigidas
    salvar = input("Deseja salvar em coordenadas planas (1) ou geográficas(2)?")
    if salvar == '1':
        salvar_txt_corrigido(arquivo_saida, list_x, list_y)
        salvar_shapefile(shape_pontos, shape_poligono, list_x, list_y, crs)
    elif salvar == '2':
        salvar_txt_corrigido(arquivo_saida, lon_corrigidos, lat_corrigidos)
        salvar_shapefile(shape_pontos, shape_poligono, lon_corrigidos, lat_corrigidos, crs)
    else:
        print("Opção inválida. Fechando programa")