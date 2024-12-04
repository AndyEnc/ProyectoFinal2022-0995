import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class TestTranscriptor(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get('http://localhost:5000') 

    def tearDown(self):
        self.driver.quit()

    def test_audio_recording(self):
        """Prueba de grabación de audio."""
        driver = self.driver

        start_recording_btn = driver.find_element(By.ID, 'startRecording')

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'startRecording'))
        )
        actions = ActionChains(driver)
        actions.move_to_element(start_recording_btn).click().perform()

        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, 'recordingStatus').text == "Recording..."
        )

        stop_recording_btn = driver.find_element(By.ID, 'stopRecording')

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'stopRecording'))
        )
        actions.move_to_element(stop_recording_btn).click().perform()

        recording_status = driver.find_element(By.ID, 'recordingStatus')
        self.assertEqual(recording_status.text, "Recording Completed.", "El estado de grabación no se actualizó correctamente.")

if __name__ == "__main__":
    unittest.main()
