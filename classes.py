def detectAnamoly(onsetclass,onsetpred,classThreshold):
    ambient=["animal","bird"]
    anamoly=["glass","wood"]
    if onsetpred <= classThreshold:
        return 2
    for i in range(len(ambient)):
        if onsetclass == ambient[i]:
            return 0
    for i in range(len(anamoly)):
        if onsetclass == anamoly[i]:
            return 1
    return 2