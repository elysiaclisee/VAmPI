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
    #error 10021: X-Content-Type-Options Header Missing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    #error 10036: Server Leaks Version Information (Ghi đè Header Server)
    response.headers['Server'] = 'Web-Server'  
    #error 10049: Storable and Cacheable Content (Tắt cache cho API)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    #error 90004: Cross-Origin-Resource-Policy Header Missing
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin' 
    return response

if __name__ == '__main__':
    vuln_app.run(host='0.0.0.0', port=5000, debug=True)
