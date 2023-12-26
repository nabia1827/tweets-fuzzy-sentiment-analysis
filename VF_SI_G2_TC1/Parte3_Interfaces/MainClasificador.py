from ProcesadorDeTweets import ProcesadorDeTweets
from ExtraccionDeCaracteristicas import ExtraccionDeCaracteristicas

from ProcesadorDeTweets import ProcesadorDeTweets
from ExtraccionDeCaracteristicas import ExtraccionDeCaracteristicas
from Clasificacion import clasificar

def procesar_tweet(tweet_input):
    ptweets = ProcesadorDeTweets()
    tweet = ptweets.preprocesar(tweet_input)


    ec = ExtraccionDeCaracteristicas()
    tweet_Final = ec.listar(tweet)
    return(clasificar(tweet_Final))

def etiqueta_mayor_valor(array_valores):
    etiqueta = ["Demasiado relevante", "Muy relevante", "Medianamente relevante","Poco relevante", "Irrelevante"]
    # Encontrar el valor máximo en la lista
    valor_maximo = max(array_valores)

    # Obtener el índice del valor máximo
    indice_maximo = array_valores.index(valor_maximo)
    
    return etiqueta[indice_maximo]