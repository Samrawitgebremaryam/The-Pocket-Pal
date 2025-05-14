from googletrans import Translator

translator = Translator()
result = translator.translate("hi my name is samri", dest="es")
print(f"Translated text: {result.text}")