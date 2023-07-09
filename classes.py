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
import sys

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size



def get_dict_size(d):
    size = sys.getsizeof(d)
    if isinstance(d, dict):
        for value in d.values():
            size += get_dict_size(value)
    elif isinstance(d, (list, tuple)):
        for item in d:
            size += get_dict_size(item)
    elif isinstance(d, set):
        for item in d:
            size += sys.getsizeof(item)
    return size

# Example nested dictionary
# nested_dict = {
#     'a': 1,
#     'b': {
#         'c': [2, 3, 4],
#         'd': {'e': 5, 'f': 6}

#from sys import getsizeof
p=[]
payload = {'deviceId': 'SN002', 'deviceType': 'standalone', 'timeStamp': '04-07-2023T10-40-51', 'recTimeStamp': '04-07-2023T10-40-37.wav', 'recFileName': 'rec_04-07-2023T10-40-37.wav', 'gpsLat': 44.568, 'gpsLong': 18.333, 'recDuration': 20, 'recSamplingRate': 48000, 'recFormat': 'wav', 'detectionCount': 43, 'onsetThreshold': 0.01, 'classThreshold': 0.5, 'classType': 'all','peakClass': [{'Chainsaw': '0.923'}, {'Chainsaw': '0.923'}, {'Chainsaw': '0.923'}, {'Chainsaw': '0.923'}, {'Chainsaw': '0.845'}, {'Chainsaw': '0.904'}, {'Vehicle': '0.156'}, {'Engine': '0.319'}, {'Fart': '0.257'}, {'Chainsaw': '0.587'}, {'Chainsaw': '0.896'}, {'Chainsaw': '0.675'}, {'Chainsaw': '0.622'}, {'Tools': '0.736'}, {'Chainsaw': '0.970'}, {'Chainsaw': '0.942'}, {'Chainsaw': '0.775'}, {'Chainsaw': '0.892'}, {'Chainsaw': '0.953'}, {'Chainsaw': '0.965'}, {'Chainsaw': '0.856'}, {'Chainsaw': '0.837'}, {'Chainsaw': '0.953'}, {'Light engine (high frequency)': '0.987'}, {'Light engine (high frequency)': '0.981'}, {'Light engine (high frequency)': '0.983'}, {'Chainsaw': '0.868'}, {'Tools': '0.719'}, {'Chainsaw': '0.781'}, {'Jackhammer': '0.641'}, {'Jackhammer': '0.225'}, {'Tools': '0.159'}, {'Speech': '0.154'}, {'Speech': '0.222'}, {'Speech': '0.505'}, {'Tools': '0.301'}, {'Chainsaw': '0.850'}, {'Jackhammer': '0.686'}, {'Jackhammer': '0.748'}, {'Chainsaw': '0.542'}, {'Tools': '0.462'}, {'Tools': '0.654'}, {'Tools': '0.774'}]}
size=get_dict_size(payload)
print(size)
print(len(p))