from flask import Flask, request, jsonify, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_input():
    app.logger.debug("Received validation request")
    if not request.is_json:
        return redirect(url_for('thank_you', valid="false"))

    data = request.get_json()
    user_input = data.get('crd')  # Fetch data using the unique name 'crd'
    app.logger.debug(f"User input from crd: {user_input}")

    if not user_input:
        return redirect(url_for('thank_you', valid="false"))

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

        if final_url == 'https://brokercheck.finra.org/':
            return redirect(url_for('thank_you', valid="false"))
        else:
            return redirect(url_for('thank_you', valid="true"))

@app.route('/thank_you')
def thank_you():
    validation_result = request.args.get('valid', default="false", type=str)
    
    if validation_result == "true":
        return render_template('valid_crd.html')  # Assuming you have a template for valid CRD
    else:
        return render_template('invalid_crd.html')  # Assuming you have a template for invalid CRD

if __name__ == '__main__':
    app.run(debug=True)