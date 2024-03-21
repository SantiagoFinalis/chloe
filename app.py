from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_input():
    app.logger.debug("Received validation request")
    if not request.is_json:
        return jsonify({'status': 'fail', 'message': 'Request must be in JSON format'}), 400

    data = request.get_json()
    # Fetch data using the unique name 'crd'
    user_input = data.get('crd')
    app.logger.debug(f"User input from crd: {user_input}")

    if not user_input:
        return jsonify({'status': 'fail', 'message': 'No user input provided for crd'}), 400

    url_to_check = f"https://brokercheck.finra.org/individual/summary/{user_input}"
    app.logger.debug(f"URL to check: {url_to_check}")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = ChromeService(executable_path=ChromeDriverManager().install())

    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get(url_to_check)
        time.sleep(3)  # Allow time for any redirects and full page load
        final_url = driver.current_url
        app.logger.debug(f"Final URL after 3 seconds: {final_url}")
        
        if final_url == 'https://brokercheck.finra.org/':  # Or other logic based on your needs
            return jsonify({'status': 'fail', 'message': 'Invalid input for crd, please try again.'})
        else:
            return jsonify({'status': 'success', 'message': 'The input for crd is valid.'})

if __name__ == '__main__':
    app.run(debug=True)
