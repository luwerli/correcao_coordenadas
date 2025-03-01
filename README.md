# Correção de cooordenadas de poligonais
Correção de coordenadas geográficas obtidas por topografia com medição de distâncias

Em campos de topografia realizados com estações total ou nível, é possivel que ocorram erros da medição das distâncias entre as estações. Considerando que o erro de medição de um ponto para outro irá acumular, é possível que, ao fechar a poligonal, a medição da coordenada da base esteja incorreta.

A solução encontrada, ao invés de os profissionais terem de retornar ao campo para corrigir as medições, é realizar essa correção através de um código em python que distribui uniformemente ou proporcionalmente a correção das coordenadas medidas.

# Condições para que o código seja executado de forma correta
1. As coordenadas de entrada devem são geográficas e em um arquivo de texto na estrutura: longitude, latitude
2. As coordenadas podem estar separadas por ; , ou espaço
3. O usuário deve buscar qual a zona UTM correspondente a área de estudo

# Configurações do código
1. Na chamada principal onde diz:
arquivo_entrada = r'arquivo.txt'
arquivo_saida = r'arquivo.txt'
shape_pontos = r'arquivo.shp'
shape_poligono = r'arquivo.shp'

alterar r'arquivo.txt' pelo diretório do arquivo de entrada. Assim como os arquivos seguintes.

2. Onde lê-se zona = '29' e hemisferio = 'N', altere a zona e o hemisfério de acordo com a região estudo
    
3. Onde lê-se crs = "32629", Altere o crs de acordo com a zona UTM previamente selecionada
