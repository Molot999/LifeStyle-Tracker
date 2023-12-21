def onerm_langer_formula(weight_lifted, repetitions):
    return round((weight_lifted * repetitions) / 30 + weight_lifted, 2)

def onerm_mayhew_watanabe_formula(weight_lifted, repetitions):
    return round(weight_lifted * (1 + 0.0333 * repetitions), 2)

def onerm_repsch_formula(weight_lifted, repetitions):
    return round(weight_lifted * (1 + 0.0333 * repetitions + 0.0000067 * repetitions ** 2), 2)

def maxhr( age):
    return 220 - int(age)