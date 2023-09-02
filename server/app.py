from flask import Flask, request, jsonify
from flask_cors import CORS

# Import your SVG processing functions
from svg_processor import generate_ripped_svg_from_svg_data

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/process-svg', methods=['POST'])
def process_svg():
    try:
        svg_data = request.json.get('svg_data', '')
        jaggedness = request.json.get('jaggedness', 40)
        print("Received jaggedness in Flask:", jaggedness)
        ripped_svg = generate_ripped_svg_from_svg_data(svg_data, jaggedness)

        
        if ripped_svg:
            return jsonify({'status': 'success', 'svg': ripped_svg})
        else:
            raise ValueError("Failed to generate ripped SVG.")
            
    except Exception as e:
        app.logger.error(f"Error processing SVG: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
