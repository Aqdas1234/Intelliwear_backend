from recommendation.logic.recommendation import CBModel
from recommendation.logic.CF import CFModel
from recommendation.logic.ImgSearch import SearchModel

_cb_instance = None
_cf_instance = None 
_img_instance = None 


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
        #print(_cf_instance)
        #print("hellog")
    return _cf_instance



def get_image_search_model():
    global _img_instance
    if _img_instance is None:
        path = 'recommendation/imageSearchData'
        _img_instance = SearchModel(directory=path)

    return _img_instance