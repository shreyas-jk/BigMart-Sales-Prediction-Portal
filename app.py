from flask import Flask, redirect, url_for, render_template, request, session, Response
import pickle
import pandas as pd
import json

class SingleSales:
    def __init__(self, outlet_type, outlet_year, item_type, item_mrp, item_weight, item_visibility):
        self.outlet_year = outlet_year
        self.item_type = item_type
        self.item_mrp = item_mrp
        self.item_weight = item_weight
        self.item_visibility = item_visibility
        self.outlet_type = outlet_type
        self.item_type = item_type

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# Prediction API for single sale
@app.route("/single_sales", methods=['POST'])
def single_sales():
    if request.method == "POST":
        request_data = request.get_json()   
        outlet_type = request_data['outlet_type']
        outlet_year = request_data['outlet_year']
        item_type = request_data['item_type']
        item_mrp = request_data['item_mrp']
        item_weight = request_data['item_weight']
        item_visibility = request_data['item_visibility']
        selected_model = request_data['selected_model']

        sales = SingleSales(outlet_type, outlet_year, item_type, item_mrp, item_weight, item_visibility)
        result = predict_single(sales, get_model(selected_model))
    else:
        return None
    return json.dumps(result[0])

# Prediction API for Bulk Sales Data
@app.route("/bulk_sales", methods=['GET', 'POST'])
def bulk_sales():
    if request.method == "POST":
        selected_model = request.form['selected_model']
        file = request.files['file']
        df = pd.read_csv(file)
        result = predict_bulk(df, get_model(selected_model))
        output = merge(df, result)
    else:
        return None
    return Response(output.to_csv(), mimetype="text/csv", headers={"Content-disposition":"attachment; filename=filename.csv"})

# Get and load saved model
def get_model(selected_model):
    switcher =  {
                    'Linear' : 'Linear_Regressor.pkl',
                    'RandomForest' : 'RandomForest_Regressor.pkl',
                }
    model_filename = switcher.get(selected_model)
    file = open(model_filename, 'rb')
    return pickle.load(file) 

# Predict result for Single sale
def predict_single(sale, model):
    return model.predict([[sale.outlet_type, sale.outlet_year, sale.item_type, sale.item_mrp, sale.item_weight, sale.item_visibility]])

# Predict result for bulk
def predict_bulk(df, model):
    return model.predict(df)

#Merge input file with output (bulk prediction only)
def merge(df, result):
    return pd.concat([df, pd.DataFrame(result, columns=['Predicted_Sales'])], axis=1)

if __name__ == "__main__":
    app.run(debug=True)