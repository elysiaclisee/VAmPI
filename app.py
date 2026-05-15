from config import vuln_app, vuln, alive
import os

'''
 Decide if you want to server a vulnerable version or not!
 DO NOTE: some functionalities will still be vulnerable even if the value is set to 0
          as it is a matter of bad practice. Such an example is the debug endpoint.
'''

app = vuln_app.app

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Server'] = 'Web-Server'  
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin' 
    return response

@app.errorhandler(404)
def not_found_error(error):
    response = jsonify({"error": "Not Found"})
    response.status_code = 404
    return add_security_headers(response)

if __name__ == '__main__':
    vuln_app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    vuln_app.run(host='0.0.0.0', port=5000, debug=True)
