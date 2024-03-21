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
        return redirect(url_for('thank_you', valid="false", message='Request must be in JSON format'))

    data = request.get_json()
    # Fetch data using the unique name 'crd'
    user_input = data.get('crd')
    app.logger.debug(f"User input from crd: {user_input}")

    if not user_input:
        return redirect(url_for('thank_you', valid="false", message='No user input provided for crd'))

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
            return redirect(url_for('thank_you', valid="false", message='Invalid input for crd, please try again.'))
        else:
            return redirect(url_for('thank_you', valid="true", message='The input for crd is valid.'))

@app.route('/thank_you')
def thank_you():
    validation_result = request.args.get('valid', default="false", type=str)
    message = request.args.get('message', default="There was a problem with your submission.", type=str)
    
    if validation_result == "true":
        return render_template('thank_you.html', message=message)
    else:
        # This is where you would redirect back to the form with an error message, but for now, we just render a page
        return render_template('thank_you.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
