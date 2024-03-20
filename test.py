from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time  # Import time module for sleep

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_input():
    app.logger.debug("Received validation request")
    if not request.is_json:
        return jsonify({'status': 'fail', 'message': 'Request must be in JSON format'}), 400
    
    data = request.get_json()
    user_input = data.get('user_input')
    app.logger.debug(f"User input: {user_input}")
    
    if not user_input:
        return jsonify({'status': 'fail', 'message': 'No user input provided'}), 400
    
    url_to_check = f"https://brokercheck.finra.org/individual/summary/{user_input}"
    app.logger.debug(f"URL to check: {url_to_check}")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = ChromeService(executable_path=ChromeDriverManager().install())

    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get(url_to_check)
        time.sleep(3)  # Wait for 3 seconds to ensure the page has loaded and any redirects have occurred
        final_url = driver.current_url
        app.logger.debug(f"Final URL after 3 seconds: {final_url}")  # Print the final URL
        
        # Here, replace 'https://brokercheck.finra.org/' with the specific URL you're checking against
        if final_url == 'https://brokercheck.finra.org/':
            return jsonify({'status': 'fail', 'message': 'Invalid input, please try again.'})
        else:
            return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
