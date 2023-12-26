import re
import nltk
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
from collections import Counter


class ProcesadorDeTweets:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.stop_words = set()
        self.stop_words.update(set(stopwords.words('english')))
        self.stop_words.update(set(stopwords.words('spanish')))        
        # Utiliza Latin-1 como codificacion al leer el archivo CSV
        ruta = r"data/Tweets.csv"
        self.df_tweets = pd.read_csv(ruta, delimiter=";", encoding='latin-1')



    def elim_2vocales(self, tweet):
        patron = r'\b[a-zA-Z]{2}\b'
        return re.sub(patron, '', tweet)

    def elim_urls(self, tweet):
        # Eliminar las urls de un tweet
        res = re.sub(r'http\S+', '', tweet)

        # Eliminar los caracteres especiales
        res = re.sub(r'[^\w\s]', '', res)

        # Eliminar los numeros
        res = re.sub(r'\d+', '', res)

        # Eliminar las menciones
        res = re.sub(r'@\w+', '', res)

        # Eliminar los espacios en blanco
        res = res.strip()

        return res

    def elim_hash_emojis(self, tweet):
        # Eliminar hashtags
        res = re.sub(r'#\w+', '', tweet)
        # Eliminar emojis
        res = res.encode('ascii', 'ignore').decode('ascii')

        return res

    def elim_punct(self, tweet):
        return re.sub(r'[^\w\s]', '', tweet)

    def normalize(self, tweet):
        return tweet.lower()

    def tokenize(self, tweet):
        return nltk.word_tokenize(tweet)

    def elim_stopwords(self, tokens):
        return [i for i in tokens if not i in self.stop_words]

    def lematize(self, tokens):
        return [self.lemmatizer.lemmatize(word) for word in tokens]
    
    def singular(self,tokens):
        terminaciones = ['ies', 'es', 's']
        for i in range(len(tokens)):
            for a in terminaciones:
                if tokens[i].endswith(a):
                    tokens[i] = tokens[i][:-len(a)]
                    break
        return tokens

    def preprocesar(self, tweet):
        tweet = self.elim_urls(tweet)
        tweet = self.elim_hash_emojis(tweet)
        tweet = self.elim_2vocales(tweet)
        tweet = self.elim_punct(tweet)
        tweet = self.normalize(tweet)
        tokens = self.tokenize(tweet)
        tokens = self.elim_stopwords(tokens)
        tokens = self.lematize(tokens)
        tokens = self.singular(tokens)

        return tokens
    
    def preprocesar_listado_tweets(self):
        bolsa_oraciones = []
        for tweet in self.df_tweets['Tweets']:
            bolsa_palabras = self.preprocesar(tweet)
            oracion = ' '.join(bolsa_palabras)
            bolsa_oraciones.append(oracion)


        # Convertir la lista en un DataFrame
        return pd.DataFrame({'Tweets': bolsa_oraciones})
        

    def palabras50(self):
        # Lista de tweets
        tweets = []

        # Agregar los tweets del DataFrame a la lista tweets
        for indice, fila in self.preprocesar_listado_tweets().iterrows():
            tweet = fila['Tweets']
            tweets.append(tweet)

        # Unimos todos los tweets en un solo texto
        texto_completo = ' '.join(tweets)

        # Tokenizamos el texto
        palabras = re.findall(r'\w+', texto_completo.lower())
        # Contamos la frecuencia de cada palabra
        frecuencia_palabras = Counter(palabras)

        # Las 50 palabras mas comunes
        palabras_comunes = frecuencia_palabras.most_common(50)

        palabras = palabras_comunes

        # Obtener los valores de la columna 0 y colocarlos en una lista
        columna_0_lista = arreglo_np[:, 0].tolist()
        # Conversion a arreglo numpy
        palabras = columna_0_lista
        arreglo_np = np.array(palabras)
        return palabras
    
    def contar_palabra_en_oracion(self , oracion, palabra_buscada):
        # Convierte la oracion a minusculas para hacer la busqueda insensible a mayusculas/minusculas
        oracion = oracion.lower()
        # Divide la oracion en palabras usando espacios como separadores
        palabras = self.preprocesar(oracion)
        # Inicializa un contador para llevar un registro de las repeticiones
        contador = 0
        # Itera a traves de las palabras y cuenta cuantas veces aparece la palabra buscada
        for palabra in palabras:
            if palabra == palabra_buscada.lower():
                contador += 1
        return contador

    def generacion_de_palabras_claves_ordenadas(self):
        #Score
        datos = [
            ("covid", 0.898129811),
            ("pandemia", 0.879092244),
            ("coronavirus", 0.866448177),
            ("vacuna", 0.897141422),
            ("cuarentena", 0.705230229),
            ("contagio", 0.760679509),
            ("vacunacion", 0.929045321),
            ("mascarilla", 0.640068648),
            ("distanciamiento", 0.999250856),
            ("muerte", 0.660330467),
            ("variante", 0.875497264),
            ("pcr", 0.922868046),
            ("inmunizacion", 0.880282973),
            ("sintoma", 0.657348412),
            ("hospitalizacion", 0.6733829882),
            ("aislamiento", 0.507508488),
            ("oms", 0.997729725),
            ("emergencia", 0.451805309),
            ("protocolo", 0.994527605),
            ("tratamiento", 0.543998753),
            ("riesgo", 0.576211098),
            ("virus", 0.713434091),
            ("asintomatico", 0.795920826),
            ("minsa", 0.981348133),
            ("resiliencia", 0.747445449),
            ("transmision", 0.881276136),
            ("tasa", 0.979623615),
            ("mortalidad", 0.9041266678),
            ("incidencia", 0.8084302981),
            ("sistema", 0.902776234),
            ("salud", 0.872353904),
            ("crisis", 0.909035916),
            ("desinfectante", 0.987561629),
            ("rastreo", 0.871339403),
            ("ventilador", 0.649354958),
            ("inmunidad", 0.869176727),
            ("cierre", 0.772089406),
            ("prueba", 0.876430908),
            ("desescalada", 0.78452895),
            ("inoculacion", 0.986740817),
            ("critico", 0.984331997),
            ("alarma", 0.836429715),
            ("teletrabajo", 0.518196581),
            ("masa", 0.623441622),
            ("telemedicina", 0.580048225),
            ("uci", 0.927946863),
            ("frontera", 0.95432517),
            ("desinfeccion", 0.717965775),
            ("mensajero", 0.577157196),
            ("experimental", 0.817530041),
            ("reglamento", 0.87569138)
        ]
        # Crear la matriz numpy de tuplas
        matriz_tuplas = np.array(datos, dtype=[('palabra', 'U20'), ('frecuencia', float)])

        # Ordena la lista de mayor a menor segun la tercera columna (indice 2)
        keys_L = sorted(matriz_tuplas, key=lambda x: x[1], reverse=True)

        return keys_L