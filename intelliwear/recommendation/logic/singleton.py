from recommendation.logic.recommendation import CBModel
from recommendation.logic.CF import CFModel
from recommendation.logic.ImgSearch import SearchModel
from recommendation.logic.NLP import NLP

_cb_instance = None
_cf_instance = None 
_img_instance = None 
_nlp_instance = None



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
        path = 'recommendation/data2/'
        _cf_instance = CFModel(directory=path)
        print(_cf_instance)
        #print("hellog")
    return _cf_instance



def get_image_search_model():
    global _img_instance
    if _img_instance is None:
        path = 'recommendation/imageSearchData'
        _img_instance = SearchModel(directory=path)

    return _img_instance


def get_nlp_model():
    global _nlp_instance
    if _nlp_instance is None:
        path = 'recommendation/nlpData'  
        _nlp_instance = NLP(directory=path)
    return _nlp_instance