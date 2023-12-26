from ProcesadorDeTweets import ProcesadorDeTweets

class ExtraccionDeCaracteristicas:
    def __init__(self):
        self.keys_L = ProcesadorDeTweets().generacion_de_palabras_claves_ordenadas()

    def indice_key(self, palabra):
        i = 1
        for palabra_cmp, nivel in self.keys_L:
            if palabra == palabra_cmp:
                return i
            i += 1
        else:
            return 0

    def similitud(self, palabra1, palabra2):
        c_palabra1 = set(palabra1)
        c_palabra2 = set(palabra2)
        if palabra1 in palabra2 or palabra2 in palabra1:
            intersection = len(c_palabra1.intersection(c_palabra2))
            union = len(c_palabra1.union(c_palabra2))
        else:
            return 0.0
        return intersection / union
    
    def cant_simil(self,token_list):
        cont = 0
        for palabra in token_list:
            for key,_ in self.keys_L:
                tmp = self.similitud(palabra, key)
                if tmp != 0.0:
                    cont = cont + 1
                    break
        if (cont != 0 ):
            return cont
        else:
            return 1000

    def funcion_wk(self, palabra):
        peso_1 = 1
        peso_2 = 0.5
        peso_3 = 0.25

        i = self.indice_key(palabra)

        if i == 0:
            return 0
        elif 1 <= i < 16:
            return peso_1
        elif 16 <= i < 32:
            return peso_2
        else:
            return peso_3

    def funcion_S(self, palabra):
        max = -1
        for clave, _ in self.keys_L:
            nuevo = self.funcion_wk(clave) * self.similitud(clave, palabra)
            if max < nuevo:
                max = nuevo
        return max

    def funcion_F(self, tweet):
        suma = 0
        for palabra in tweet:
            suma = suma + self.funcion_S(palabra)
        return suma

    def funcion_M(self, tweet):
        return len(tweet)

    def funcion_G(self, tweet):
        valor_F = self.funcion_F(tweet)
        valor_M = self.cant_simil(tweet)
        return valor_F/valor_M

    def funcion_I(self, tweet):
        sum = 0
        for palabra in tweet:
            ind = self.indice_key(palabra)
            if ind != 0:
                sum = sum + 1
        return sum

    def funcion_E(self, tweet):
        valor_I=self.funcion_I(tweet)
        valor_M=self.cant_simil(tweet)
        return valor_I/valor_M

    def listar(self,tweetFinal):
        resultados = []
        resultados.append(self.funcion_M(tweetFinal)) 
        resultados.append(self.funcion_G(tweetFinal)) 
        resultados.append(self .funcion_E(tweetFinal))
        print(resultados)

        return resultados 

