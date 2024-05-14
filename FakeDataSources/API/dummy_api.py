from flask import Flask, jsonify, request

# initializes flask
app = Flask(__name__)

# A simple route that returns a welcome message
@app.route('/')
def hello_world():
    return 'Hello, World!'

# A route that echoes back the data sent in a POST request
@app.route('/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify(data)

# A route that calculates the sum of two numbers provided as query parameters
@app.route('/add')
def add():
    a = request.args.get('a', type=int)
    b = request.args.get('b', type=int)
    if a is None or b is None:
        return jsonify({"error": "Please provide both 'a' and 'b' query parameters."}), 400
    return jsonify({"result": a + b})

if __name__ == '__main__':
    app.run(debug=True)
