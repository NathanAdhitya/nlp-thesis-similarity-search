from flask import Flask, jsonify, request
from flask_cors import CORS
import script
app = Flask(__name__)
CORS(app)
@app.route('/search/<string:search_type>/<string:query>', methods=['GET'])
def search_route(search_type, query):
    try:
        # Determine if searching thesis (paper) or author based on path parameter
        thesis = search_type == 'paper'
        topK = request.args.get('topK', type=int)
        model = request.args.get('model', type=str)

        if not thesis:
            program_ids = request.args.getlist('program_ids')
            program_ids = [int(pid) for pid in program_ids] if program_ids else None
        else:
            program_ids = None

        # Perform search
        result = script.search(query, thesis, topK, model, program_ids)

        # Build dynamic response key
        key = "topPapers" if thesis else "topAuthors"

        return jsonify({
            "message": "Data retrieved successfully",
            "data": {
                key: result
            }
        }), 200

    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500

@app.route('/programs', methods=['GET'])
def get_programs_route():
    try:
        programs = script.get_all_programs()

        return jsonify({
            "message": "Programs retrieved successfully",
            "data": {
                "programs": programs
            }
        }), 200

    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
