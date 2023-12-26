import re
import emoji
import spacy
import string
import numpy
import spacy
import nltk
import copy
import math
from nrclex import NRCLex
from googletrans import Translator
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

translator = None
nlp = None
nlp_en = None
emociones = None
opuestos = None
nums_emociones = None
negadores = None
delimitadores = None

conectores = None
opositores_changeable = None
opositores_unchangeable = None

opositores_neg = None
intensificadores_adjetivos = None
atenuadores_adjetivos = None
intensificadores_accion = None

atenuadores_accion = None
no_pert_stopwords = None

no_sw = None
dict_emojis = None
pronombres_ingles =None

def init_variables():
    global translator, nlp, emociones,opuestos,nums_emociones,negadores,delimitadores,conectores,opositores_changeable,opositores_unchangeable
    global opositores_neg, intensificadores_adjetivos, atenuadores_adjetivos, intensificadores_accion, atenuadores_accion, no_pert_stopwords, no_sw,dict_emojis

    global intensificadores_both, atenuadores_both, nlp_en,pronombres_ingles 
    translator = Translator()
    nlp = spacy.load("es_core_news_sm")
    nlp_en = spacy.load("en_core_web_sm")
    nltk.download('punkt')

    emociones = {
    "fear":         ["😨","miedo",0],
    "anger":        ["😡", "enojo",1],
    "anticipation": ["🧐", "Anticipacion",2],
    "anticip":      ["🧐", "Anticipacion",2],
    "trust":        ["😉", "Confianza",3],
    "surprise":     ["😮", "Sorpresa",4],
    "positive":     ["➕", "Positivo",5],
    "negative":     ["➖", "Negativo",6],
    "sadness":      ["🥺", "Tristeza",7],
    "disgust":      ["🤢", "Asco",8],
    "joy":          ["😁", "Alegria",9]
    }

    opuestos = {
        "fear" : "trust",
        "anger" : "joy",
        "anticipation": "surprise",
        "anticip": "surprise",
        "trust" : "fear",
        "surprise": "anticipation",
        "positive": "negative",
        "negative": "positive",
        "sadness" : "joy",
        "disgust" : "joy",
        "joy":"sadness"
    }
    pronombres_ingles = {'I', 'you', 'he', 'she', 'it', 'we', 'they', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves'}

    nums_emociones = [
        "fear",
        "anger",
        "anticipation",
        "trust",
        "surprise",
        "positive",
        "negative",
        "sadness",
        "disgust",
        "joy"
    ]

    negadores = {"no", "tampoco", "nunca", "jamas", "jamás", "nadie", "nada", "ningun", "ningún",
                "ninguno", "ninguna"}

    delimitadores = {",", ";", ":"}

    conectores = {" y ", " o ", " cuando ", " u "," aunque ", " a pesar de "}

    # Conectores de contraste con orden intercambiable
    opositores_changeable = {"aunque", "a pesar de"} 

    # Conectores de contraste no intercambiable
    opositores_unchangeable = {"pero", "sin embargo", "no obstante", "por el contrario", "en cambio"}

    # Conectores de contraste con negacion implicita
    opositores_neg ={"no porque"}


    # Intensificadores de adjetivos
    intensificadores_adjetivos = {"extremadamente", "bastante", "realmente", "muy","tan","tanto", "demasiado",
                                "increíblemente", "absolutamente", "sumamente", "completamente"}
    # Atenuadores de adjetivos
    atenuadores_adjetivos = {"poco"} # un poco

    # intensifiers --> raiz cuadrada
    intensificadores_accion = {"bien", "extremadamente bien", "bastante bien", "realmente bien",
                            "muy bien", "demasiado bien", "increíblemente bien", "absolutamente bien",
                            "sumamente bien", "completamente bien", 
                            "mucho", "muchisimo"
                            }

    # attenuators --> potencia 2
    atenuadores_accion = {"mal", "extremadamente mal", "bastante mal", "realmente mal", "muy mal",
                        "demasiado mal", "increíblemente mal", "absolutamente mal", "sumamente mal",
                        "completamente mal", "poco bien",
                        "poco" 
                        }
    intensificadores_both = {"mejor", "mas"}
    atenuadores_both = {"peor", "menos"}

    no_pert_stopwords = {"bien","buen","buena","buenas","bueno","buenos","cierto","mal","verdadero","verdadera" }

    no_sw = no_pert_stopwords | negadores| intensificadores_adjetivos | atenuadores_adjetivos | intensificadores_accion |atenuadores_accion |intensificadores_both|atenuadores_both

#Creación del diccionario
         # miedo enojo anti confia sopre  posi nega triste asco alegria
dict_emojis = {
    "😊": [0.00, 0.00, 0.10, 0.75, 0.20, 0.85, 0.05, 0.00, 0.00, 0.95],
    "😂": [0.00, 0.00, 0.12, 0.68, 0.10, 0.87, 0.22, 0.00, 0.00, 0.96],
    "😹": [0.00, 0.00, 0.11, 0.68, 0.14, 0.85, 0.23, 0.03, 0.00, 0.96],
    "🙂": [0.15, 0.15, 0.55, 0.40, 0.63, 0.53, 0.18, 0.09, 0.20, 0.55],
    "🤣": [0.00, 0.00, 0.14, 0.68, 0.12, 0.84, 0.19, 0.00, 0.00, 0.99],
    "😄": [0.00, 0.00, 0.13, 0.80, 0.11, 0.86, 0.21, 0.00, 0.00, 0.98],
    "😆": [0.00, 0.00, 0.12, 0.70, 0.10, 0.88, 0.24, 0.00, 0.00, 0.99],
    "😅": [0.20, 0.00, 0.16, 0.40, 0.46, 0.69, 0.16, 0.10, 0.20, 0.55],
    "😎": [0.00, 0.00, 0.22, 0.98, 0.18, 0.90, 0.30, 0.10, 0.00, 0.96],
    "😇": [0.10, 0.00, 0.13, 0.80, 0.17, 0.91, 0.31, 0.00, 0.00, 0.88],
    "🤗": [0.00, 0.00, 0.14, 0.85, 0.16, 0.82, 0.32, 0.00, 0.00, 0.88],
    "🙃": [0.35, 0.40, 0.40, 0.20, 0.59, 0.59, 0.28, 0.10, 0.20, 0.55],
    "😕": [0.20, 0.45, 0.48, 0.20, 0.54, 0.16, 0.36, 0.20, 0.40, 0.45],
    "😔": [0.60, 0.16, 0.26, 0.10, 0.52, 0.18, 0.38, 0.42, 0.10, 0.05],
    "😢": [0.77, 0.15, 0.25, 0.20, 0.31, 0.09, 0.39, 0.53, 0.20, 0.05],
    "😥": [0.78, 0.14, 0.24, 0.20, 0.40, 0.10, 0.40, 0.54, 0.20, 0.05],
    "😟": [0.76, 0.22, 0.22, 0.20, 0.68, 0.12, 0.42, 0.56, 0.20, 0.05],
    "🙁": [0.75, 0.23, 0.23, 0.20, 0.49, 0.11, 0.41, 0.57, 0.40, 0.05],
    "😮": [0.31, 0.10, 0.47, 0.15, 0.80, 0.32, 0.34, 0.56, 0.10, 0.15],
    "😯": [0.42, 0.10, 0.48, 0.15, 0.71, 0.33, 0.35, 0.27, 0.10, 0.15],
    "😲": [0.49, 0.10, 0.45, 0.13, 0.78, 0.36, 0.32, 0.24, 0.20, 0.15],
    "😳": [0.48, 0.10, 0.44, 0.12, 0.77, 0.37, 0.33, 0.23, 0.30, 0.15],
    "😦": [0.55, 0.17, 0.41, 0.19, 0.65, 0.10, 0.36, 0.40, 0.20, 0.15],
    "😧": [0.66, 0.18, 0.42, 0.20, 0.76, 0.10, 0.35, 0.41, 0.25, 0.15],
    "😨": [0.95, 0.10, 0.49, 0.17, 0.82, 0.01, 0.37, 0.47, 0.40, 0.05],
    "😰": [0.98, 0.10, 0.32, 0.20, 0.76, 0.08, 0.39, 0.40, 0.40, 0.05],
    "😱": [0.87, 0.19, 0.41, 0.09, 0.95, 0.01, 0.38, 0.39, 0.25, 0.08],
    "😠": [0.60, 0.81, 0.53, 0.15, 0.30, 0.00, 0.37, 0.31, 0.20, 0.00],
    "😡": [0.62, 0.98, 0.55, 0.10, 0.30, 0.00, 0.35, 0.33, 0.20, 0.00],
    "😤": [0.43, 0.90, 0.56, 0.10, 0.20, 0.00, 0.34, 0.34, 0.20, 0.00],
    "😖": [0.97, 0.88, 0.30, 0.12, 0.40, 0.00, 0.30, 0.48, 0.80, 0.00],
    "😣": [0.85, 0.86, 0.38, 0.16, 0.40, 0.00, 0.32, 0.56, 0.70, 0.00],
    "😞": [0.88, 0.69, 0.31, 0.09, 0.35, 0.00, 0.29, 0.69, 0.66, 0.00],
    "😒": [0.36, 0.67, 0.39, 0.17, 0.23, 0.10, 0.31, 0.17, 0.60, 0.00],
    "😏": [0.49, 0.20, 0.42, 0.50, 0.16, 0.20, 0.28, 0.10, 0.20, 0.15],
    "🙄": [0.30, 0.35, 0.43, 0.25, 0.27, 0.06, 0.27, 0.21, 0.61, 0.15],
    "😣": [0.45, 0.46, 0.38, 0.16, 0.20, 0.00, 0.32, 0.56, 0.70, 0.00],
    "😢": [0.69, 0.30, 0.42, 0.20, 0.30, 0.10, 0.28, 0.60, 0.20, 0.00],
    "😭": [0.81, 0.12, 0.44, 0.12, 0.30, 0.00, 0.26, 0.89, 0.20, 0.00],
    "😪": [0.73, 0.24, 0.46, 0.34, 0.10, 0.00, 0.24, 0.70, 0.20, 0.10],
    "😴": [0.10, 0.00, 0.48, 0.50, 0.00, 0.40, 0.22, 0.00, 0.20, 0.50],
    "🤤": [0.00, 0.00, 0.49, 0.60, 0.10, 0.80, 0.21, 0.47, 0.20, 0.95],
    "😷": [0.58, 0.28, 0.50, 0.30, 0.34, 0.29, 0.20, 0.10, 0.20, 0.15],
    "🤒": [0.79, 0.33, 0.51, 0.20, 0.45, 0.00, 0.19, 0.79, 0.30, 0.05],
    "🤕": [0.71, 0.45, 0.52, 0.10, 0.56, 0.01, 0.18, 0.80, 0.20, 0.05],
    "🤢": [0.72, 0.42, 0.53, 0.15, 0.57, 0.02, 0.17, 0.61, 0.90, 0.05],
    "🤮": [0.73, 0.43, 0.54, 0.12, 0.58, 0.03, 0.16, 0.62, 0.95, 0.05],
    "🥴": [0.45, 0.25, 0.55, 0.30, 0.49, 0.24, 0.15, 0.43, 0.00, 0.15],
    "🥺": [0.67, 0.27, 0.56, 0.24, 0.30, 0.05, 0.14, 0.84, 0.00, 0.05],
    "🥱": [0.10, 0.10, 0.10, 0.35, 0.11, 0.46, 0.13, 0.15, 0.00, 0.45],
    "🤧": [0.70, 0.35, 0.58, 0.16, 0.12, 0.00, 0.12, 0.66, 0.20, 0.05],
    "🥳": [0.05, 0.00, 0.30, 0.71, 0.17, 0.82, 0.07, 0.00, 0.00, 0.99],
    "🤨": [0.30, 0.30, 0.38, 0.26, 0.62, 0.23, 0.02, 0.66, 0.20, 0.25],
    "🤑": [0.10, 0.05, 0.43, 0.71, 0.07, 0.66, 0.03, 0.00, 0.00, 0.55],
    "😑": [0.10, 0.50, 0.48, 0.16, 0.42, 0.40, 0.08, 0.20, 0.20, 0.25],
    "😐": [0.22, 0.62, 0.80, 0.28, 0.54, 0.45, 0.10, 0.28, 0.20, 0.25],
    "😶": [0.14, 0.44, 0.82, 0.30, 0.46, 0.40, 0.12, 0.20, 0.20, 0.25],
    "🫠": [0.26, 0.26, 0.24, 0.12, 0.58, 0.45, 0.14, 0.22, 0.10, 0.55],
    "🤯": [0.38, 0.28, 0.56, 0.44, 0.50, 0.45, 0.16, 0.24, 0.10, 0.25],
    "😬": [1.00, 0.30, 0.58, 0.10, 0.52, 0.12, 0.68, 0.66, 0.20, 0.05],
    "🥵": [0.49, 0.40, 0.57, 0.15, 0.41, 0.23, 0.17, 0.65, 0.20, 0.05],
    "🥶": [0.97, 0.45, 0.25, 0.23, 0.49, 0.22, 0.15, 0.73, 0.20, 0.05],
    "🤭": [0.06, 0.00, 0.10, 0.24, 0.12, 0.78, 0.19, 0.00, 0.00, 0.85],
    "🫣": [0.25, 0.15, 0.73, 0.41, 0.47, 0.62, 0.11, 0.00, 0.20, 0.65],
    "😻": [0.00, 0.00, 0.10, 0.90, 0.20, 0.91, 0.10, 0.00, 0.00, 0.95],
    "🤩": [0.00, 0.00, 0.10, 0.89, 0.20, 0.90, 0.09, 0.00, 0.00, 0.95],
    "🥰": [0.00, 0.00, 0.10, 0.88, 0.20, 0.89, 0.08, 0.00, 0.00, 0.99],
    "😍": [0.00, 0.00, 0.10, 0.87, 0.20, 0.88, 0.07, 0.00, 0.00, 0.99],
    "❣️": [0.00, 0.00, 0.10, 0.87, 0.20, 0.88, 0.07, 0.00, 0.00, 0.99],
    "👍": [0.01, 0.10, 0.10, 0.60, 0.00, 0.65, 0.20, 0.00, 0.00, 0.75],
    "👏": [0.01, 0.10, 0.10, 0.71, 0.00, 0.73, 0.21, 0.00, 0.00, 0.65],
    "🌞": [0.00, 0.00, 0.10, 0.80, 0.00, 0.90, 0.00, 0.00, 0.00, 0.99],
    "❤️": [0.00, 0.00, 0.10, 0.97, 0.20, 0.98, 0.07, 0.00, 0.00, 0.99],
    "❤": [0.00, 0.00, 0.10, 0.77, 0.20, 0.78, 0.07, 0.00, 0.00, 0.89],
}




def modif_lista_stopwords(no_sw):
    for palabra in no_sw:   
        if palabra in nlp.Defaults.stop_words:        
            nlp.Defaults.stop_words.remove(palabra)





def dividir_tweet(texto):
    # Encuentra y separa los emojis
    emojis = ''.join(c for c in texto if c in emoji.UNICODE_EMOJI['en'])
    
    # Elimina los emojis del texto original
    texto_sn = ''.join(c for c in texto if c not in emoji.UNICODE_EMOJI['en'])
    
    # Encuentra y separa los hashtags
    hashtags = ' '.join(re.findall(r'#\w+', texto_sn))
    
    # Elimina los hashtags del texto original
    contenido = re.sub(r'#\w+', '', texto_sn).strip()
    
    return contenido, hashtags, emojis

def init_pesos_oraciones(contenido_array):
    pesos_oraciones = []
    for i in range(len(contenido_array)):
        pesos_oraciones.append(1)
    return pesos_oraciones.copy()

def imprimir(txt_array):
    for i in range(len(txt_array)):
        print(i,":", txt_array[i])

def eliminar_urls_menc(array_oraciones):
    contenido_array = copy.deepcopy(array_oraciones)
    
    for i in range(len(contenido_array)):
        # Elimina los URL's
        contenido_array[i] = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', contenido_array[i])

        # Elimina las menciones
        contenido_array[i] = re.sub('@[^\s]+','', contenido_array[i])

        # Elimina los caracteres especiales
        contenido_array[i] = re.sub('[\s]+', ' ', contenido_array[i])
    
    contenido_array = [sublista for sublista in contenido_array if sublista]
    return contenido_array


def to_lower(contenido_array):
    for i in range(len(contenido_array)):
        contenido_array[i] = contenido_array[i].lower()
    return contenido_array


def is_division_correcta(suboraciones):
    division_correcta = True
    
    for j in range(len(suboraciones)):
        
        # Contamos la cantidad de palabras
        palabras = suboraciones[j].split()
        
        if(len(palabras) < 3):
            division_correcta = False
            break
            
    return division_correcta

def get_suboraciones(oracion, delimitador):
    # Dividmos la oracion segun el limitador actual
    suboraciones = oracion.split(delimitador)

    # Hubo subdivision ?
    if len(suboraciones) > 1:
        # Si hubo subdivision
        division_correcta = is_division_correcta(copy.deepcopy(suboraciones))
    
        if(division_correcta):
            return suboraciones
        else:
            return [oracion]
    else:
        # No hubo subdivision
        return suboraciones
    
def modificar_pesos(suboraciones,pesos_suboraciones, d):
    # El delimitador es una coma ?
    if d==",":    
        for i in range(len(suboraciones)):
            for opositor in opositores_changeable:
                if suboraciones[i].startswith(opositor):
                    if i == 0:
                        pesos_suboraciones[i] = 0.3
                        pesos_suboraciones[i+1] = 1
                    else:
                        pesos_suboraciones[i] = 0.3
                        pesos_suboraciones[i-1] = 1
    
    # El delimitador es un conector de contraste intercambiable                    
    if d.strip() in opositores_changeable:
                    for i in range(len(suboraciones)):
                        if i == 0:
                            pesos_suboraciones[i] = 1
                        else: 
                            pesos_suboraciones[i] = 0.3
    return pesos_suboraciones

def subdividir(delimitadores, contenido_array,pesos_oraciones):
    nueva_lista = []
    nuevos_pesos_oraciones = []

    for delimitador in delimitadores:
        for i in range(len(contenido_array)):
            contenido_array[i] = contenido_array[i].strip()
            suboraciones = get_suboraciones(contenido_array[i], delimitador)

            for i in range(len(suboraciones)):
                suboraciones[i] = suboraciones[i].strip()

            nueva_lista.extend(suboraciones)


            if len(suboraciones) > 1:
                pesos_suboraciones = []

                for i in range(len(suboraciones)):
                        pesos_suboraciones.append(1)

                pesos_suboraciones = modificar_pesos(suboraciones,pesos_suboraciones, delimitador)

                nuevos_pesos_oraciones.extend(pesos_suboraciones)
            else:
                nuevos_pesos_oraciones.append(1)


        contenido_array = []
        contenido_array = nueva_lista.copy()
        nueva_lista = []

        pesos_oraciones = []
        pesos_oraciones = nuevos_pesos_oraciones.copy()
        nuevos_pesos_oraciones = []
    return contenido_array,pesos_oraciones


def eliminiar_punt(contenido_array):
    for i in range(len(contenido_array)):
    
        # Elimina los signos de puntuación
        signos_puntuacion =   string.punctuation+'¿¡'

        contenido_array[i] = [char for char in contenido_array[i] if char not in signos_puntuacion]

        contenido_array[i] = ''.join(contenido_array[i])

    return contenido_array


def procesar_opositores(contenido_array, pesos_oraciones):
    # opositores unchangeable
    for i in range(len(contenido_array)):
        for opositor in opositores_unchangeable:
            if opositor in contenido_array[i]:
                if i != 0:
                    pesos_oraciones[i-1] = 0.3

    # opositores negacion
    for i in range(len(contenido_array)-1):
        for opositor in opositores_neg:
            if opositor in contenido_array[i]:
                    pesos_oraciones[i] = 0.3
                    pesos_oraciones[i+1] = 1  # Insertar negaciooooooooooooooooooooooooon
                    
    return contenido_array, pesos_oraciones


def tokenizar_texto(texto):
    doc = nlp(texto)
    tokens = [token.text for token in doc]
    return tokens


def tokenizar_tweet(contenido_array):
    tokens_array = []
    for i in range(len(contenido_array)):

        tokens_contenido = tokenizar_texto(contenido_array[i])
        tokens_array.append(tokens_contenido)

    return tokens_array



def no_stopwords(tokens_list):
    hay_stopwords_izq = []
    hay_stopwords_der = []
    tokens_limpios = []
    
    cont = 0
    izq_pendiente = False
    for i in range(len(tokens_list)):
 
        if tokens_list[i] not in nlp.Defaults.stop_words:
            if(izq_pendiente):
                hay_stopwords_izq.append(1)
                izq_pendiente = False
            else:
                hay_stopwords_izq.append(0)
            hay_stopwords_der.append(0)
            tokens_limpios.append(tokens_list[i])
            cont = cont + 1
        else:
            if(cont!=0):
                hay_stopwords_der[cont - 1] = 1 
            izq_pendiente = True
        
    #tokens_limpios = [token for token in tokens_list if token not in nlp.Defaults.stop_words]
    
    return tokens_limpios,hay_stopwords_izq,hay_stopwords_der


def eliminar_stopwords(tokens_array):
    swd = []
    swi = []
    for i in range(len(tokens_array)):
        tokens_array[i],izq, der = no_stopwords(tokens_array[i])
        swi.append(izq.copy())
        swd.append(der.copy())
    
    return tokens_array,swi,swd



def to_english(tokens_array):
    tokens_array_en = copy.deepcopy(tokens_array)
    print(tokens_array)
    for i in range(len(tokens_array_en)):
        for j in range(len(tokens_array_en[i])):
            tmp = translator.translate(tokens_array_en[i][j], src='es', dest='en')
            tokens_array_en[i][j] = tmp.text
    
    return tokens_array_en

def lematizar_adverbios(oraciones):
    for k in range(len(oraciones)):
        for i in range(len(oraciones[k])):
            if  len(oraciones[k][i])>3 and oraciones[k][i].endswith("ly") and oraciones[k][i] not in intensificadores_adjetivos:
                oraciones[k][i] = oraciones[k][i][:-len("ly")]
    return oraciones



def lematizar_oracion(tokens_list):
    lema = [token.lemma_ for token in nlp_en(" ".join(tokens_list))]
    return lema

def lematizar(tokens_array_en):
    for i in range(len(tokens_array_en)):
        tokens_array_en[i] = lematizar_oracion(tokens_array_en[i])
    
    return tokens_array_en

def show_emociones(arrayt_nivel_emociones):
    txt = ""
    for tupla in arrayt_nivel_emociones:
        if(tupla[1]!=0.0):
            txt = txt + emociones[tupla[0]][0]+ "" + str(tupla[1]) + "," 
    return txt


def showall_emociones(tokens_array, niveles_emocion):
    
    for i in range(len(tokens_array)):
        for j in range(len(tokens_array[i])):
            print(tokens_array[i][j], ':', show_emociones(niveles_emocion[i][j]))

def corregir_niveles(array):
    for i in range(len(array)):
        array[i] = [array[i][0], pow(array[i][1],1/2.5)]
    return array

def get_niveles_emocion(tokens_array_en):
    niveles_emocion = copy.deepcopy(tokens_array_en)

    for i in range(len(tokens_array_en)):
        for j in range(len(tokens_array_en[i])):
            array_tuplas = NRCLex(tokens_array_en[i][j].lower()).top_emotions
            niveles_emocion[i][j] = [list(tupla) for tupla in array_tuplas]
            niveles_emocion[i][j] = corregir_niveles(niveles_emocion[i][j])
   
    return niveles_emocion

def actualizar_nivel_emociones(niveles_emocion,tipo_operacion): #Parametro es una lista de tuplas
    nuevos_niveles_emocion = []
    
    for i in range(len(niveles_emocion)):
        sub_lista = [niveles_emocion[i][0], 0.0]
        if(tipo_operacion == 0): # raiz cuadrada, intensificar
            sub_lista[1] = math.sqrt(niveles_emocion[i][1])
        else: # potencia 2, atenuar
            sub_lista[1] = niveles_emocion[i][1] ** 2
            
        nuevos_niveles_emocion.append(sub_lista)
    return nuevos_niveles_emocion

def procesar_adjetivos(tokens_array, niveles_emocion):
    
    # Intensificar y atenuar adjetivos
    for i in range(len(tokens_array)):
        for j in range(len(tokens_array[i]) - 1):
            if tokens_array[i][j] in intensificadores_adjetivos:
                niveles_emocion[i][j + 1] = actualizar_nivel_emociones(niveles_emocion[i][j + 1], 0)

            if tokens_array[i][j] in atenuadores_adjetivos:
                niveles_emocion[i][j + 1] = actualizar_nivel_emociones(niveles_emocion[i][j + 1], 1)
    return niveles_emocion


def procesar_acciones(tokens_array, niveles_emocion):
    
    # Intensificar y atenuar acciones
    for i in range(len(tokens_array)):
        for j in range(len(tokens_array[i]) - 1):
            if(j < len(tokens_array[i]) - 3):
                modif1 = tokens_array[i][j + 1] + " " + tokens_array[i][j + 2]
            else:
                modif1 = ""
            modif2 = tokens_array[i][j + 1]


            if modif1 in intensificadores_accion or modif2 in intensificadores_accion:
                niveles_emocion[i][j] = actualizar_nivel_emociones(niveles_emocion[i][j], 0)

            if modif1 in atenuadores_accion or modif2 in atenuadores_accion:
                niveles_emocion[i][j] = actualizar_nivel_emociones(niveles_emocion[i][j], 1)
    return niveles_emocion

def procesar_otros(tokens_array, tokens_array_en, niveles_emocion, swi, swd):
    # Intensificar y atenuar adjetivos o acciones
    for i in range(len(tokens_array)):
        for j in range(len(tokens_array[i])):
            
            if tokens_array[i][j] in intensificadores_both:
                
                if(swi[i][j] != 1):
                    if((j - 1) > 0):
                        tipo = nlp_en(tokens_array_en[i][j - 1])
                        if(tipo[0].pos_ == 'VERB'):
                            niveles_emocion[i][j - 1] = actualizar_nivel_emociones(niveles_emocion[i][j - 1], 0)

                if(swd[i][j] != 1):
                    if((j + 1)< len(tokens_array[i])):
                        print(tokens_array_en[i][j])
                        tipo = nlp_en(tokens_array_en[i][j + 1])
                        if(tipo[0].pos_ == 'NOUN'):
                            niveles_emocion[i][j + 1] = actualizar_nivel_emociones(niveles_emocion[i][j + 1], 0)

            if tokens_array[i][j] in atenuadores_both:
                if(swi[i][j] != 1):
                    if((j - 1) > 0):
                        tipo = nlp_en(tokens_array_en[i][j - 1])
                        if(tipo[0].pos_ == 'VERB'):
                            niveles_emocion[i][j - 1] = actualizar_nivel_emociones(niveles_emocion[i][j - 1], 1)

                if(swd[i][j] != 1):
                    if((j + 1)< len(tokens_array[i])):
                        tipo = nlp_en(tokens_array_en[i][j + 1])
                        if(tipo[0].pos_ == 'NOUN'):
                            niveles_emocion[i][j + 1] = actualizar_nivel_emociones(niveles_emocion[i][j + 1], 1)
    return niveles_emocion


def is_vacio(array_niveles_emociones):
    
    for emocion_subarray in array_niveles_emociones:
        if(emocion_subarray[1] != 0.0):
            return False
    return True

def negar(array_niveles_emociones):
    array_tmp = copy.deepcopy(array_niveles_emociones)
    
    for i in range(len(array_niveles_emociones)):
        if array_niveles_emociones[i][1] != 0.0:
            nomb_emocion_actual = array_niveles_emociones[i][0]
            array_tmp[i][0] = opuestos[nomb_emocion_actual]
    return array_tmp


def aplicar_negaciones(tokens_array, niveles_emocion):

    for i in range(len(tokens_array)):
        for negac in negadores:
            for j in range(len(tokens_array[i])):
                if tokens_array[i][j] == negac:
                    encontrado = False
                    k = j + 1
                    while not encontrado and k <len(tokens_array[i]):

                        if not is_vacio(niveles_emocion[i][k]):
                            encontrado = True
                        else:
                            k = k + 1
                    if encontrado:
                        niveles_emocion[i][k] = negar(niveles_emocion[i][k])
    return niveles_emocion

def to_array10(array_niveles_emociones):
    array10 = [0,0,0,0,0,0,0,0,0,0]
    for nivel in array_niveles_emociones:
        indice = emociones[nivel[0]][2]
        array10[indice] = nivel[1]
    return array10.copy()


def get_puntuaciones(tokens_array, niveles_emocion):
    puntuacion_oraciones = []
    for i in range(len(tokens_array)):
        puntuacion_oracion = []
        for j in range(len(tokens_array[i])):
            array_tmp = to_array10(niveles_emocion[i][j])
            puntuacion_oracion.append(array_tmp)
        puntuacion_oraciones.append(copy.deepcopy(puntuacion_oracion))
        
    return puntuacion_oraciones


def get_promedios(puntuacion_oraciones):
    proms_oraciones = []
    for i in range(len(puntuacion_oraciones)):
        prom_oracion = []
        for k in range(10):
            prom = 0.0
            for j in range(len(puntuacion_oraciones[i])):
                prom =max(prom,puntuacion_oraciones[i][j][k])
            prom_oracion.append(prom)
        proms_oraciones.append(prom_oracion)
        
    return proms_oraciones


def aplicar_pesos(proms_oraciones, pesos_oraciones):
    proms_oraciones_peso = copy.deepcopy(proms_oraciones)
    for i in range(len(proms_oraciones_peso)):
        for j in range(len(proms_oraciones_peso[i])):
            proms_oraciones_peso[i][j] = proms_oraciones_peso[i][j] * pesos_oraciones[i]
    return proms_oraciones_peso 


def get_puntuacion_tweet(proms_oraciones_peso):
    
    puntuacion_tweet = []
    i = 0
    for j in range(len(proms_oraciones_peso[i])):
        pnt_emocion = 0.0
        cont = 0.0
        prom = 0.0
        for i in range(len(proms_oraciones_peso)):
            if(proms_oraciones_peso[i][j] != 0.0):
                pnt_emocion = pnt_emocion + proms_oraciones_peso[i][j]
                cont = cont + 1
        if(cont != 0.0):
            prom = pnt_emocion/cont
        i = i + 1

        puntuacion_tweet.append(prom)
    return puntuacion_tweet


def imprimir_puntuacion(puntuaciones_tweet):
    for i in range(len(puntuaciones_tweet)):
        print(emociones[nums_emociones[i]]," : ",puntuaciones_tweet[i])


# FUNCIONES DE HASHTAGS

def separar_palabras_en_hashtag(hashtag):
    # Utilizar expresiones regulares para separar palabras por mayúsculas o caracteres especiales
    palabras = re.findall(r'[A-Z][a-z]*', hashtag)
    
    return palabras

def separar_palabras(hashtags):
    for i in range(len(hashtags)):
        hashtags[i] = separar_palabras_en_hashtag(hashtags[i])
    return hashtags

def hashtag_to_lower(hashtags):
    for i in range(len(hashtags)):
        for j in range(len(hashtags[i])):
            hashtags[i][j] = hashtags[i][j].lower()
    return hashtags

def hashtag_to_english(hashtags): 
    hashtags_en = copy.deepcopy(hashtags)
    
    for i in range(len(hashtags_en)):
        for j in range(len(hashtags_en[i])):
            tmp = translator.translate(hashtags_en[i][j], src='es', dest='en')
            hashtags_en[i][j] = tmp.text
    return hashtags_en

def lemmatize(tokens_list):
    lemma = [token.lemma_ for token in nlp_en(" ".join(tokens_list))]
    return lemma

def lemmatize_txt(tokens_array):
    for i in range(len(tokens_array)):
        tokens_array[i] = lemmatize(tokens_array[i])
    
    return tokens_array

# FUNCIONES DE EMOJIS

#Creación del diccionario
         # miedo enojo anti confia sopre  posi nega triste asco alegria


def obtener_grado(list_emoji):
    puntuacion_emojis = []
    for test_emoji in list_emoji:
        grados_emociones = dict_emojis.get(test_emoji, [0,0,0,0,0,0,0,0,0,0])
        puntuacion_emojis.append(grados_emociones.copy())
        
    return puntuacion_emojis


def imprimir_grado_emojis(list_emoji,puntuacion_emojis):
    for i in range(len(list_emoji)):
        print(list_emoji[i], ':', puntuacion_emojis[i])

def get_puntuacion_emojis_tweet(nivel_emocion_emojis):
    puntuacion_final_emojis= []
    i = 0
    for j in range(len(nivel_emocion_emojis[i])):
        pnt_emocion = 0.0
        cont = 0.0
        prom = 0.0
        for i in range(len(nivel_emocion_emojis)):
            if(nivel_emocion_emojis[i][j] != 0.0):
                pnt_emocion = pnt_emocion + nivel_emocion_emojis[i][j]
                cont = cont + 1
        if(cont != 0.0):
            prom = pnt_emocion/cont
        i = i + 1

        puntuacion_final_emojis.append(prom)
    return puntuacion_final_emojis

def preprocesar_contenido(contenido_tweet):
    
    contenido_arr = nltk.sent_tokenize(contenido_tweet)
    pesos_oraciones = init_pesos_oraciones(contenido_tweet)
    contenido_arr = eliminar_urls_menc(contenido_arr)
    contenido_arr= to_lower(contenido_arr)
    contenido_arr, pesos_oraciones = subdividir(delimitadores,contenido_arr,pesos_oraciones)
    contenido_arr, pesos_oraciones = subdividir(conectores,contenido_arr,pesos_oraciones)
    contenido_arr = eliminiar_punt(contenido_arr)
    contenido_arr, pesos_oraciones = procesar_opositores(contenido_arr, pesos_oraciones)
    tokens_arr = tokenizar_tweet(contenido_arr)
    tokens_arr, swi_arr,swd_arr = eliminar_stopwords(tokens_arr)
    tokens_arr_en = to_english(tokens_arr)
    tokens_arr_en= lematizar_adverbios(tokens_arr_en)
    tokens_arr_en = lematizar(tokens_arr_en)  
    tokens_arr_en = [[palabra for palabra in sublista if palabra not in pronombres_ingles] for sublista in tokens_arr_en]
    print(tokens_arr_en)
    niv_emocion = get_niveles_emocion(tokens_arr_en)
    niv_emocion = procesar_adjetivos(tokens_arr, niv_emocion)
    niv_emocion = procesar_acciones(tokens_arr, niv_emocion)
    niv_emocion = procesar_otros(tokens_arr, tokens_arr_en, niv_emocion, swi_arr, swd_arr)
    niv_emocion = aplicar_negaciones(tokens_arr, niv_emocion)
    puntuac_oraciones = get_puntuaciones(tokens_arr, niv_emocion)
    promes_oraciones = get_promedios(puntuac_oraciones)
    promes_oraciones_peso  = aplicar_pesos(promes_oraciones, pesos_oraciones)
    puntuac_tweet = get_puntuacion_tweet(promes_oraciones_peso)
    
    return puntuac_tweet

def preprocesar_hashtags(contenido_hashtags):
    puntuac_hashtags_tweet = [0,0,0,0,0,0,0,0,0,0]

    contenido_hashtags = re.sub(r'#([^\s]+)', r'\1', contenido_hashtags)
    contenido_hashtags = tokenizar_texto(contenido_hashtags)
    contenido_hashtags = separar_palabras(contenido_hashtags)
    contenido_hashtags = hashtag_to_lower(contenido_hashtags)
    hashtags_eng = hashtag_to_english(contenido_hashtags)
    hashtags_eng = lemmatize_txt(hashtags_eng)
    print(hashtags_eng)
    if(hashtags_eng != []):
        niv_emocion_hashtags = get_niveles_emocion(hashtags_eng)
        puntuac_hashtags = get_puntuaciones(contenido_hashtags, niv_emocion_hashtags)
        promes_hashtags = get_promedios(puntuac_hashtags)
        puntuac_hashtags_tweet = get_puntuacion_tweet(promes_hashtags)
    
    
    return puntuac_hashtags_tweet


def preprocesar_emojis(contenido_emojis):
    punt_emojis_tweet = [0,0,0,0,0,0,0,0,0,0]
    if(contenido_emojis != ''):
        niv_emocion_emojis = obtener_grado(contenido_emojis)
        punt_emojis_tweet = get_puntuacion_emojis_tweet(niv_emocion_emojis)
        
    return punt_emojis_tweet

def preprocesar_tweet(tweet_input):
    init_variables()
    modif_lista_stopwords(no_sw)
    
    content, contenido_hashtags, contenido_emojis = dividir_tweet(tweet_input)
    length = len(content)
    emociones_contenido = preprocesar_contenido(content)
    emociones_hashtags = preprocesar_hashtags(contenido_hashtags)
    emociones_emojis = preprocesar_emojis(contenido_emojis)
    
    matriz_emociones = []
    for i in range(len(emociones_contenido)):
        matriz_emociones.append([emociones_contenido[i],
                                 emociones_hashtags[i],
                                 emociones_emojis[i],
                                 length])
        
    
    return matriz_emociones


content_score = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'content score')
hashtag_score = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'hashtag score')
emoji_score = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'emoji score')
tweet_length = ctrl.Antecedent(np.arange(0, 141, 1), 'tweet length')


def get_rules(content_score,hashtag_score,emoji_score, tweet_length, emotion_level):
    # Definir las reglas difusas
    r1 =ctrl.Rule(content_score['low']  & hashtag_score['low'] & emoji_score['low'], emotion_level['very low'])
    r2 =ctrl.Rule(content_score['low']  & hashtag_score['low'] & (emoji_score['medium'] | emoji_score['high']), emotion_level['low'])
    r3 =ctrl.Rule(content_score['low']  & hashtag_score['medium'] & emoji_score['low']& tweet_length['short'], emotion_level['very low'])
    r4 =ctrl.Rule(content_score['low']  & hashtag_score['medium'] & emoji_score['low'] & (tweet_length['medium'] | tweet_length['long']), emotion_level['low'])
    r5 =ctrl.Rule(content_score['low']  & hashtag_score['medium'] & (emoji_score['medium'] | emoji_score['high']), emotion_level['medium'])
    r6 =ctrl.Rule(content_score['low']  & hashtag_score['high'] & emoji_score['low'], emotion_level['low'])
    r7 =ctrl.Rule(content_score['low']  & hashtag_score['high'] & emoji_score['medium'], emotion_level['medium'])
    r8 =ctrl.Rule(content_score['low']  & hashtag_score['high'] & emoji_score['high'], emotion_level['high'])
    r9 =ctrl.Rule(content_score['medium']  & hashtag_score['low'] & emoji_score['low'], emotion_level['low'])
    r10 =ctrl.Rule(content_score['medium']  & hashtag_score['low'] & emoji_score['medium'], emotion_level['medium'])
    r11 =ctrl.Rule(content_score['medium']  & hashtag_score['low'] & emoji_score['high'], emotion_level['high'])
    r12 =ctrl.Rule(content_score['medium']  & hashtag_score['medium'] & emoji_score['low'], emotion_level['medium'])
    r13 =ctrl.Rule(content_score['medium']  & hashtag_score['medium'] & (emoji_score['medium'] | emoji_score['high']), emotion_level['high'])
    r14 =ctrl.Rule(content_score['medium']  & hashtag_score['high'] & emoji_score['low'], emotion_level['medium'])
    r15 =ctrl.Rule(content_score['medium']  & hashtag_score['high'] & (emoji_score['medium'] | emoji_score['high']), emotion_level['high'])
    r16 =ctrl.Rule(content_score['high']  & hashtag_score['low'] & emoji_score['low'], emotion_level['medium'])
    r17 =ctrl.Rule(content_score['high']  & hashtag_score['low'] & (emoji_score['medium'] | emoji_score['high']), emotion_level['high'])
    r18 =ctrl.Rule(content_score['high']  & hashtag_score['medium'] & emoji_score['low'], emotion_level['medium'])
    r19 =ctrl.Rule(content_score['high']  & hashtag_score['medium'] & (emoji_score['medium'] | emoji_score['high']), emotion_level['very high'])
    r20 =ctrl.Rule(content_score['high']  & hashtag_score['high'] & emoji_score['low'] & tweet_length['short'], emotion_level['high'])
    r21 =ctrl.Rule(content_score['high']  & hashtag_score['high'] & emoji_score['low']&(tweet_length['medium'] | tweet_length['long']), emotion_level['very high'])
    r22 =ctrl.Rule(content_score['high']  & hashtag_score['high'] & (emoji_score['medium'] | emoji_score['high']), emotion_level['very high'])
    return [r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15,r16,r17,r18,r19,r20,r21,r22]

def get_emotion_machine(etiq, content_score, hashtag_score,emoji_score,tweet_length):
    
    # Variables de entrada
    labels = ['low', 'medium', 'high']
    for label in labels:
        
        content_score[label] = fuzz.trimf(content_score.universe, [(labels.index(label) - 1)/2 + 0.20, labels.index(label)/2, (labels.index(label) + 1)/2 - 0.20])
        hashtag_score[label] = fuzz.trimf(hashtag_score.universe, [(labels.index(label) - 1)/2 + 0.20, labels.index(label)/2, (labels.index(label) + 1)/2- 0.20])
        emoji_score[label] = fuzz.trimf(emoji_score.universe, [(labels.index(label) - 1)/2 + 0.20, labels.index(label)/2, (labels.index(label) + 1)/2- 0.20])
    
    labels = ['short', 'medium', 'long']
    for label in labels:
        tweet_length[label] = fuzz.trimf(tweet_length.universe, [(labels.index(label) - 1)*70, labels.index(label)*70, (labels.index(label) + 1)*70])
    
    # Variables de salida
    emotion_level = ctrl.Consequent(np.arange(0, 1.01, 0.01), etiq)
    
    labels = ['very low', 'low', 'medium', 'high', 'very high']
    for label in labels:
        emotion_level[label] = fuzz.trimf(emotion_level.universe, [(labels.index(label) - 1)/4, labels.index(label)/4, (labels.index(label) + 1)/4])

    # Sistema de control difuso
    emotion_control = ctrl.ControlSystem(get_rules(content_score,hashtag_score,emoji_score, tweet_length, emotion_level))
    emotion_machine = ctrl.ControlSystemSimulation(emotion_control)
    
    return emotion_machine, emotion_level

def compute_emotion(values, etiq, emotion_level,control_machine):
    # Establecer entradas
    control_machine.input['content score'] = values[0]
    control_machine.input['hashtag score'] = values[1]
    control_machine.input['emoji score'] = values[2]
    control_machine.input['tweet length'] = values[3]

    control_machine.compute()
    result = control_machine.output[etiq]
    
    return result


def get_result_levels(matriz_emociones,content_score, hashtag_score,emoji_score,tweet_length):
    results = []
    
    for i in range(len(matriz_emociones)):
        machine, emotion_level = get_emotion_machine(emociones[nums_emociones[i]][1],
                                            content_score, hashtag_score,emoji_score,tweet_length)
        result = compute_emotion(matriz_emociones[i],
                                 emociones[nums_emociones[i]][1],emotion_level, machine)
        results.append(result)
    return results

def procesar_fuzzy_tweet(matriz_emociones):
    content_score = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'content score')
    hashtag_score = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'hashtag score')
    emoji_score = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'emoji score')
    tweet_length = ctrl.Antecedent(np.arange(0, 141, 1), 'tweet length')
    
    results = get_result_levels(matriz_emociones,content_score, hashtag_score,emoji_score,tweet_length)

    return results


def procesar_tweet(tweet_input):
    matriz_emociones = preprocesar_tweet(tweet_input)
    print(matriz_emociones)
    results = procesar_fuzzy_tweet(matriz_emociones)

    return results


#tweet = "Me quedo con todo lo bonito, gracias por todo.❣️🙂 #Inspiracion #Recuerdos" #0
#tweet = "Disfrutando de un día muy soleado en la playa🌞. Ha sido una semana horrible, pero hoy toca disfrutar mucho. No pienso estresarme.🌞🏖️ #VeranoEnLaPlaya #Playa #Relax" #ejem
#tweet = "¡Felicidad pura! Hoy me enteré de que fui aceptado en mi universidad de ensueño. 🎓😄 #Logros #Emocionado" #1
#tweet = "No puedo dejar de sonreír. Mi equipo @lostiburones ganó el campeonato. ¡Somos los campeones! 🏆🙌 #Victoria #Exito #TiburonesElMejorEquipo" #2
#tweet = "¡Qué día tan maravilloso! El sol brilla, los pájaros cantan y todo parece perfecto.🌞🌸 #Feliz #DíaPerfecto"#3
#tweet = "Reunión sorpresa con mi mejor amigo @Raul después de años. La amistad verdadera perdura.👫❤️ #Amigos #ReunionEmocionante" #4
#tweet = "¡Nuevo miembro de la familia! Adoptamos a un perrito adorable hoy.🐶❤️ #Adopcion #FamiliaFeliz"
#tweet = "Escuché un ruido extraño en medio de la noche y no puedo dormir.😨🌙 #NocheEspeluznante #Miedo"
#tweet = "Vi una película de terror @LaPuertaRoja anoche y todavía tengo escalofríos. ¡Demasiado espeluznante!🎬👻😨 #Terror #Pesadillas"
#tweet = "Estoy a punto de dar una presentación para el curso de Algebra, pero el nerviosismo me está matando.😰📊 #Nervioso #Presentacion"
#tweet = "Entré a la casa y las luces se apagaron repentinamente. ¡Corrí más rápido de lo que nunca he corrido! 💡🏃‍♂️😬 #Susto #Oscuridad"
#tweet = "¡Que irrespetuoso fue ese conductor en el tráfico hoy!😡🚗 #Trafico #Enojado"
#tweet = "Discutí con mi colega en la oficina. La frustración está en su punto máximo.😤💼 #Conflictos #Pelea"
tweet = "La compañía telefónica @Movistar me cobró una tarifa incorrecta. ¡Esto es inaceptable! 💸📱😡 #TarifasDelAsco #TeOdioMuchoMovistar #Molesto"
#tweet = "El servicio al cliente de @Ripley es terrible. ¿Es tan difícil ser amable y eficiente?😠📞 #ServicioAlCliente #Insatisfecho https://t.co/HYRZD7k636"



final_result = procesar_tweet(tweet)
#print(final_result)


imprimir_puntuacion(final_result)
