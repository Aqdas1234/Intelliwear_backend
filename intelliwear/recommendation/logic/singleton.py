from recommendation.logic.recommendation import CBModel
from intelliwear.recommendation.logic.CF import CFModel

_cb_instance = None
_cf_instance = None  


def get_cb_model():
    global _cb_instance
    if _cb_instance is None:
        path = 'recommendation/data'
        _cb_instance = CBModel(path)  
        print(_cb_instance)
    return _cb_instance



def get_cf_model():
    global _cf_instance
    if _cf_instance is None:
        path = 'recommendation/data'
        _cf_instance = CFModel(directory=path)
        print(_cf_instance)
        print("hellog")
    return _cf_instance
