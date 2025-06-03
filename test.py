from flask import Flask, jsonify, request
from script import search
app = Flask(__name__)

@app.route('/search/<string:query>', methods=['GET'])
def search(query):
    try:
        result = search(query)

        return jsonify({
            "message": "Data retrieved successfully",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
