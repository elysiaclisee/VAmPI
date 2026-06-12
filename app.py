from config import vuln_app, vuln, alive
import os
from flask import jsonify

'''
 Decide if you want to server a vulnerable version or not!
 DO NOTE: some functionalities will still be vulnerable even if the value is set to 0
          as it is a matter of bad practice. Such an example is the debug endpoint.
'''
app = vuln_app.app

@app.after_request
def add_security_headers(response):
    #error 10021: X-Content-Type-Options Header Missing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    #error 90004: Cross-Origin-Resource-Policy Header Missing
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin' 
    return response

@app.errorhandler(404)
def not_found_error(error):
    response = jsonify({"message": "Resource not found"})
    response.status_code = 404
    return add_security_headers(response)
 
@app.errorhandler(500)
def handle_500(e):
    response = jsonify({"message": "Internal Server Error"})
    response.status_code = 500
    return add_security_headers(response)

if __name__ == '__main__':
    #turn off debug mode to prevent Modern Web Application (10109)
    debug_option = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    vuln_app.run(host='0.0.0.0', port=5000, debug=debug_option)
