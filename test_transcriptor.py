from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# Ruta del chromedriver en tu sistema
chrome_driver_path = "C:\\Seleniumdriver\\chromedriver.exe"

# Configuración de Selenium con la ruta personalizada para ChromeDriver
driver = webdriver.Chrome(service=Service(chrome_driver_path))

# Lista para registrar los resultados de las pruebas
test_results = []

def log_test_result(test_name, status):
    """Registra el resultado de una prueba."""
    result = f"Prueba: {test_name} - {'PASÓ' if status else 'FALLÓ'}"
    test_results.append(result)
    print(result)

try:
    # Abrir la página de tu aplicación Flask
    driver.get("http://127.0.0.1:5000")
    print("Página cargada con éxito.")
    time.sleep(5)

    # Captura inicial
    driver.save_screenshot("pagina_inicial.png")
    log_test_result("Carga de la página", True)

    ### PRUEBA DE SUBIR ARCHIVO ###
    try:
        print("Probando la funcionalidad de subir archivo...")
        audio_file_input = driver.find_element(By.ID, "audioFile")  # ID del input para archivos
        audio_file_input.send_keys("D:\\Portafolio\\ProyectoGp\\uploads\\AudioMuestra.wav")
        time.sleep(2)

        driver.save_screenshot("archivo_cargado.png")
        print("Archivo cargado correctamente.")
        
        submit_button = driver.find_element(By.XPATH, "//form[@id='audioForm']//button")
        submit_button.click()
        time.sleep(5)

        driver.save_screenshot("formulario_enviado.png")
        log_test_result("Subida de archivo", True)
    except Exception as e:
        log_test_result("Subida de archivo", False)
        print(f"Error en la prueba de subir archivo: {e}")

    ### PRUEBA DE GRABAR AUDIO ###
    try:
        print("Probando la funcionalidad de grabar audio...")
        start_recording_button = driver.find_element(By.ID, "startRecording")  # ID del botón para grabar
        start_recording_button.click()
        time.sleep(5)  # Simula tiempo para grabar

        stop_recording_button = driver.find_element(By.ID, "stopRecording")  # ID del botón para detener grabación
        stop_recording_button.click()
        time.sleep(2)

        driver.save_screenshot("grabacion_completada.png")
        log_test_result("Grabación de audio", True)
    except Exception as e:
        log_test_result("Grabación de audio", False)
        print(f"Error en la prueba de grabar audio: {e}")

    ### PRUEBA DE TRANSCRIPCIÓN ###
    try:
        print("Verificando la transcripción...")
        transcription_text = driver.find_element(By.ID, "result")  
        transcribed_text = transcription_text.text
        print("Texto transcrito:", transcribed_text)

        driver.save_screenshot("transcripcion_resultado.png")
        log_test_result("Transcripción de audio", True)
    except NoSuchElementException:
        log_test_result("Transcripción de audio", False)
        print("No se encontró el elemento de transcripción.")
    except Exception as e:
        log_test_result("Transcripción de audio", False)
        print(f"Error en la prueba de transcripción: {e}")

except Exception as e:
    print(f"Error general durante las pruebas: {e}")
    log_test_result("Carga de la página", False)

finally:
    print("\n--- Resumen de las pruebas ---")
    for result in test_results:
        print(result)

    driver.quit()
    print("Navegador cerrado.")
