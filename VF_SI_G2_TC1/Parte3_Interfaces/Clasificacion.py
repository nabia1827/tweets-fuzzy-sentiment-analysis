import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

def clasificar(tweet_Final):
    tweet_length = ctrl.Antecedent(np.arange(0, 141, 1), 'M')
    tweet_weight = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'G')
    fuw_weight = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'E')

    # Variable Tweet Length
    tweet_length['Very Short'] = fuzz.trimf(tweet_length.universe, [0, 0, 18])
    tweet_length['Short'] = fuzz.trimf(tweet_length.universe, [12, 25, 40])
    tweet_length['Moderate'] = fuzz.trimf(tweet_length.universe, [30, 65, 100])
    tweet_length['Long'] = fuzz.trimf(tweet_length.universe, [80, 100, 120])
    tweet_length['Very Long'] = fuzz.trimf(tweet_length.universe, [110, 140, 140])

    # Variable Tweet Weight
    tweet_weight['Very Low'] = fuzz.trimf(tweet_weight.universe, [0,0, 0.2])
    tweet_weight['Low'] = fuzz.trimf(tweet_weight.universe, [0.1, 0.25, 0.4])
    tweet_weight['Moderate'] = fuzz.trimf(tweet_weight.universe, [0.3, 0.5, 0.7])
    tweet_weight['High'] = fuzz.trimf(tweet_weight.universe, [0.6, 0.75, 0.9])
    tweet_weight['Very High'] = fuzz.trimf(tweet_weight.universe, [0.8, 1, 1])

    # Variable Frequency of Use of Words Weight
    fuw_weight['Low'] = fuzz.trimf(fuw_weight.universe, [0, 0, 0.12])
    fuw_weight['Moderate'] = fuzz.trimf(fuw_weight.universe, [0.06, 0.145, 0.23])
    fuw_weight['High'] = fuzz.trimf(fuw_weight.universe, [0.16, 1, 1])

    

    relevance = ctrl.Consequent(np.arange(0, 100.1, 0.1), 'R')


    # Variable Relevance
    relevance['Irrelevance/DK'] = fuzz.trapmf(relevance.universe, [0, 0, 10,30])
    relevance['Low Relevance'] = fuzz.trapmf(relevance.universe, [20, 30, 40,50])
    relevance['Moderate Relevance'] = fuzz.trapmf(relevance.universe, [40, 50,60,70])
    relevance['High Relevance'] = fuzz.trapmf(relevance.universe, [60, 70, 80,90])
    relevance['Very High Relevance'] = fuzz.trapmf(relevance.universe, [80, 90,100,100])


    rule0 = ctrl.Rule(tweet_length['Very Short'], relevance['Irrelevance/DK'])
    rule1 = ctrl.Rule(tweet_weight['Very Low'], relevance['Irrelevance/DK'])
    rule2 = ctrl.Rule(tweet_weight['Low']&fuw_weight['Low'], relevance['Irrelevance/DK'])
    rule3 = ctrl.Rule(tweet_weight['Low']&(fuw_weight['Moderate']|fuw_weight['High']), relevance['Low Relevance'])
    rule4 = ctrl.Rule(tweet_weight['Moderate'] &fuw_weight['Low'], relevance['Low Relevance'])
    rule5 = ctrl.Rule(tweet_weight['Moderate'] &(fuw_weight['Moderate']|fuw_weight['High'])& (tweet_length['Short']|tweet_length['Moderate']|tweet_length['Long']|tweet_length['Very Long']), relevance['Moderate Relevance'])
    rule6 = ctrl.Rule(tweet_weight['High'] & fuw_weight['Low']& (tweet_length['Short']|tweet_length['Moderate']|tweet_length['Long']|tweet_length['Very Long']), relevance['Moderate Relevance'])
    rule7 = ctrl.Rule(tweet_weight['High'] &(fuw_weight['Moderate']|fuw_weight['High'])& (tweet_length['Short']|tweet_length['Moderate']|tweet_length['Long']|tweet_length['Very Long']), relevance['High Relevance'])
    rule8 = ctrl.Rule(tweet_weight['Very High'] & fuw_weight['Low']& (tweet_length['Short']|tweet_length['Moderate']|tweet_length['Long']|tweet_length['Very Long']), relevance['Moderate Relevance'])
    rule9 = ctrl.Rule(tweet_weight['Very High'] & fuw_weight['Moderate']& (tweet_length['Short']|tweet_length['Moderate']|tweet_length['Long']|tweet_length['Very Long']), relevance['High Relevance'])
    rule10 = ctrl.Rule(tweet_weight['Very High'] & fuw_weight['High'] & (tweet_length['Short']|tweet_length['Moderate']|tweet_length['Long']|tweet_length['Very Long']), relevance['Very High Relevance'])


    # Creación del sistema de control
    system = ctrl.ControlSystem([rule0, rule1, rule2, rule3, rule4, rule5,rule6, rule7, rule8, rule9,rule10])

    # Simulación del sistema de control
    simulation = ctrl.ControlSystemSimulation(system)

    # Asigna valores de entrada
    simulation.input['M'] = tweet_Final[0]
    simulation.input['G'] = tweet_Final[1]
    simulation.input['E'] = tweet_Final[2]
    
    # Ejecuta la simulación
    simulation.compute()

    # Obtiene el resultado
    resultado = simulation.output['R']

    # Grados de relevancia
    lista_final_ahora_si_final_diosss = []
    lista_final_ahora_si_final_diosss.append(fuzz.interp_membership(relevance.universe, relevance['Very High Relevance'].mf, resultado))
    lista_final_ahora_si_final_diosss.append(fuzz.interp_membership(relevance.universe, relevance['High Relevance'].mf, resultado))
    lista_final_ahora_si_final_diosss.append(fuzz.interp_membership(relevance.universe, relevance['Moderate Relevance'].mf, resultado))
    lista_final_ahora_si_final_diosss.append(fuzz.interp_membership(relevance.universe, relevance['Low Relevance'].mf, resultado))
    lista_final_ahora_si_final_diosss.append(fuzz.interp_membership(relevance.universe, relevance['Irrelevance/DK'].mf, resultado))
    
    return lista_final_ahora_si_final_diosss