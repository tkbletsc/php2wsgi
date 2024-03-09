from bottle import Bottle, request, run, template

application = Bottle()

# Route for handling GET requests
@application.route('/')
def index():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Bottle Web App</title>
</head>
<body>

<h2>Simple Bottle Web App</h2>

Post form example:
<form action="/post_example" method="post">
    <label for="data">Enter data:</label>
    <input type="text" id="data" name="data">
    <input type="submit" value="Submit">
</form>

Get form example:
<form action="/get_example" method="get">
    <label for="data">Enter data:</label>
    <input type="text" id="data" name="data">
    <input type="submit" value="Submit">
</form>

</body>
</html>
"""

# Route for handling POST requests
@application.route('/post_example', method='POST')
def post_example():
    # Accessing data from the POST request
    data_from_post = request.forms.get('data')

    # Displaying the received data
    return template("Received data from POST: {{data}}", data=data_from_post)

# Route for handling POST requests
@application.route('/get_example', method='GET')
def get_example():
    # Accessing data from the POST request
    data_from_get = request.query.get('data')

    # Displaying the received data
    return template("Received data from GET: {{data}}", data=data_from_get)

if __name__ == '__main__':
    # Run the web application on localhost:8080
    run(application, host='localhost', port=8080)
