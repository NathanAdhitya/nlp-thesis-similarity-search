from flask import Flask, jsonify, request
from flask_cors import CORS
import script
app = Flask(__name__)
CORS(app)
@app.route('/search/<string:query>', methods=['GET'])
def search(query):
    try:
        result = script.search(query)
        result = script.convert_to_json_serializable(result)
        print(result)
        print(type(result))

        return jsonify({
            "message": "Data retrieved successfully",
            "data": {
                "topPapers": result
            }
        }), 200

    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
