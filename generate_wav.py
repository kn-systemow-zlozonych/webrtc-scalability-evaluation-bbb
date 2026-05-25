import pyttsx3

def create_wav(text, filename="test_audio.wav"):
    engine = pyttsx3.init()
    # Możesz ustawić prędkość mowy
    engine.setProperty('rate', 150)
    print(f"Generowanie mowy: {text}")
    engine.save_to_file(text, filename)
    engine.runAndWait()

if __name__ == "__main__":
    text_to_say = "Welcome to the Big Blue Button stress test. This is bot number zero speaking to verify audio quality."
    create_wav(text_to_say)