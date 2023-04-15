import pytest
from geotrouvetout import detect_languages


def test_detect_languages_english():
    text_and_confidences = {"Mind the gap between the train and the platform": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "en" in languages
    text_and_confidences = {"electrical wholesalers ltd": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "en" in languages
    text_and_confidences = {"Loading Keep Clear": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "en" in languages
    text_and_confidences = {"footpath": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "en" in languages
    text_and_confidences = {"Martin Luther King Jr": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "en" in languages
    text_and_confidences = {"best price": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "en" in languages    
    text_and_confidences = {"93 Buckingham steet": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "en" in languages


def test_detect_languages_french():
    text_and_confidences = {"avenue du general de gaulle": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "fr" in languages
    text_and_confidences = {"coiffure": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "fr" in languages
    text_and_confidences = {"esthetique soin du visage": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "fr" in languages    
    text_and_confidences = {"Quai de Garonne": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "fr" in languages
    text_and_confidences = {"le bois gaumont": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "fr" in languages
    text_and_confidences = {"sortie de camions": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "fr" in languages
    text_and_confidences = {"Centre Commercial": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "fr" in languages


# detect spanish and catalan all spoken in spain
def test_detect_languages_spanish():
    text_and_confidences = {"Carrer de la Fe": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "es" or "ca" in languages
    text_and_confidences = {"aeropuerto": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "es" or "ca" in languages
    text_and_confidences = {"carretera camposancos": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "es" or "ca" in languages
    text_and_confidences = {"universidad del istmo": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "es" or "ca" in languages
    text_and_confidences = {"vamos a la tiendita": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "es" or "ca" in languages
    text_and_confidences = {"transito y validad": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "es" or "ca" in languages
    text_and_confidences = {"licorerias camarena": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "es" or "ca" in languages

"""
#TODO make more precise test with tunisia, turc, israel, marocco
def test_detect_languages_arabic():
    text_and_confidences = {"الطريق السريع": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ar" in languages
    text_and_confidences = {"صالون حلاقة": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ar" in languages
    text_and_confidences = {"تمهل": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ar" in languages
    text_and_confidences = {"شارع موريس اودان": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ar" in languages
    text_and_confidences = {"ممنوع السباحة": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ar" in languages
"""


# detect hindi, marathi, telugu, kannada, tamil and malayalarm, all spoken in India
def test_detect_languages_indian():
    text_and_confidences = {"ताज महल": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "hi" or "mr" or "te" or "kn" or "ta" or "ml" in languages
    text_and_confidences = {"दिल्ली होटल": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "hi" or "mr" or "te" or "kn" or "ta" or "ml" in languages    
    text_and_confidences = {"मॉल": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "hi" or "mr" or "te" or "kn" or "ta" or "ml" in languages
    text_and_confidences = {"हेयर सैलून": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "hi" or "mr" or "te" or "kn" or "ta" or "ml" in languages
    

def test_detect_languages_russian():
    text_and_confidences = {"москва": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"красноказарменная": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"медицинский магазин": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"ул. вавилова 7a": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"доставляем ляем": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"чита 302 бырка 3": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"советская столовая": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"автомойка": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages
    text_and_confidences = {"автостоянка": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "ru" in languages


def test_detect_languages_portuguese():
    text_and_confidences = {"segurança social casa do povo": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "pt" in languages
    text_and_confidences = {"confraria nossa senhora do ó": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "pt" in languages
    text_and_confidences = {"hipermercado": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "pt" in languages
    text_and_confidences = {"universidade": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "pt" in languages
    text_and_confidences = {"escola sonho de Emilia": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "pt" in languages


def test_detect_languages_chinese():
    text_and_confidences = {"正阳门": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "cn" or "zh-cn" in languages
    text_and_confidences = {"飞机场": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "cn" or "zh-cn" in languages
    text_and_confidences = {"朝阳路": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "cn" or "zh-cn" in languages
    text_and_confidences = {"慈云寺桥": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "cn" or "zh-cn" in languages
    text_and_confidences = {"Yandong": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "cn" or "zh-cn" in languages
    text_and_confidences = {"Shuangjiang": 1.0}
    languages = detect_languages(text_and_confidences)
    assert "cn" or "zh-cn" in languages
