from recommendation.logic.recommendation import CBModel

_cb_instance = None


def get_cb_model():
    global _cb_instance
    if _cb_instance is None:
        path = 'recommendation/data'
        _cb_instance = CBModel(path)  
    return _cb_instance

from recommendation.logic.CFModel import CFModel

_cf_instance = None  

def get_cf_model():
    global _cf_instance
    if _cf_instance is None:
        path = 'recommendation/data'  
        _cf_instance = CFModel(path)
    return _cf_instance
