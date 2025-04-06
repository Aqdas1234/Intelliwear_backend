from recommendation.logic.recommendation import CBModel

_cb_instance = None


def get_cb_model():
    global _cb_instance
    if _cb_instance is None:
        path = 'recommendation/data'
        _cb_instance = CBModel(path)  
    return _cb_instance