from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask on Render!"

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "This is sample data from the API!"})

if __name__ == '__main__':
    app.run(debug=True)