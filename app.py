from flask import Flask, jsonify, request
from price_suggestion import PriceSuggestion

app = Flask(__name__)

@app.route('/price_suggestion', methods=['GET'])
def price_suggestion():
    product = request.args.get('product')
    if not product:
        return jsonify({'error': 'Missing product parameter'}), 400
    
    try:
        quest = PriceSuggestion()
        price_suggestion = quest.get_price_suggestion(product)
        return jsonify({'price_suggestion': price_suggestion})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)