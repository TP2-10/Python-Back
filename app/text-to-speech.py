from gtts import gTTS

text = "Esta es la historia que deseas narrar en audio."
tts = gTTS(text, lang='es')  # 'es' representa el idioma (español)
tts.save('story.mp3')  # Guarda el audio en un archivo MP3