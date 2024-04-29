from flask import Flask, request, jsonify, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_input():
    app.logger.debug("Received validation request")

    is_json = request.headers.get('Content-Type') == 'application/json'
    data = request.get_json() if is_json else request.form
    crd_number = data.get('crd')

    if not crd_number:
        return redirect(url_for('thank_you', valid="false"))

    url_to_check = f"https://brokercheck.finra.org/individual/summary/{crd_number}"
    app.logger.debug(f"URL to check: {url_to_check}")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = ChromeService(executable_path=ChromeDriverManager().install())

    valid_crd = False
    try:
        with webdriver.Chrome(service=service, options=options) as driver:
            driver.get(url_to_check)
            time.sleep(3)  # Allow time for any redirects and full page load
            final_url = driver.current_url
            app.logger.debug(f"Final URL after 3 seconds: {final_url}")

            if final_url != 'https://brokercheck.finra.org/':
                valid_crd = True
    except Exception as e:
        app.logger.error(f"Error checking CRD: {str(e)}")
        return redirect(url_for('thank_you', valid="false"))  # Redirect immediately if Selenium encounters an error

 if valid_crd:
        pardot_url = "http://go.finalis.com/l/1065672/2024-04-23/dc5mq4"
        payload = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'phoneNumber': data.get('phone_number'),
            'linkedin_url': data.get('linkedin_url'),
            'typeA': data.get('country_of_residence'),
            'typeA14': data.get('state'),
            'do_you_have_a_finra_crd': 'yes',  # Assume yes since a valid CRD number exists
            'crd': crd_number,
            'briefDescription': data.get('business_description'),
            'howDid': data.get('how_did_you_hear_about_us'),
            'other': data.get('other')
        }

        # Send a POST request to Pardot only if CRD is valid
        response = requests.post(pardot_url, data=payload)
        app.logger.debug(f"Pardot post response: {response.status_code}")

        return redirect(url_for('thank_you', valid="true"))
    else:
        return redirect(url_for('thank_you', valid="false"))

@app.route('/thank_you')
def thank_you():
    validation_result = request.args.get('valid', default="false", type=str)
    if validation_result == "true":
        return render_template('valid_crd.html')
    else:
        return render_template('invalid_crd.html')

if __name__ == '__main__':
    app.run(debug=True)
