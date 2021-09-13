from flask import Flask, redirect, url_for, render_template, request, session, Response
import pickle
import pandas as pd
import json
from logger import Logger
log = Logger()

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
    try:
        log.write_log('Single Sale API called')
        if request.method == "POST":
            request_data = request.get_json()   
            log.write_log('Receiving data from API ')
            outlet_type = request_data['outlet_type']
            outlet_year = request_data['outlet_year']
            item_type = request_data['item_type']
            item_mrp = request_data['item_mrp']
            item_weight = request_data['item_weight']
            item_visibility = request_data['item_visibility']
            selected_model = request_data['selected_model']

            sales = SingleSales(outlet_type, outlet_year, item_type, item_mrp, item_weight, item_visibility)
            log.write_log('Sales object created successfully')
            log.write_log('Prediction Process start')
            result = predict_single(sales, get_model(selected_model))
            log.write_log('API response sent')
        else:
            return None
    except Exception as e:
        log.write_log('Error -', str(e))
    return json.dumps(result[0])

# Prediction API for Bulk Sales Data
@app.route("/bulk_sales", methods=['GET', 'POST'])
def bulk_sales():
    try:
        log.write_log('Bulk Sales API called')
        if request.method == "POST":
            log.write_log('Receiving data from API ')
            selected_model = request.form['selected_model']
            file = request.files['file']
            log.write_log('File received')
            df = pd.read_csv(file)
            log.write_log('File loaded as dataframe')
            log.write_log('Prediction Process start')
            result = predict_bulk(df, get_model(selected_model))
            log.write_log('Formulating API response')
            output = merge(df, result)
            log.write_log('API response sent')
        else:
            return None
    except Exception as e:
        log.write_log('Error -', str(e))
    return Response(output.to_csv(), mimetype="text/csv", headers={"Content-disposition":"attachment; filename=filename.csv"})

# Get and load saved model
def get_model(selected_model):
    log.write_log('Loading model')
    switcher =  {
                    'Linear' : 'model\Linear_Regressor.pkl',
                    'RandomForest' : 'model\RandomForest_Regressor.pkl',
                }
    model_filename = switcher.get(selected_model)
    file = open(model_filename, 'rb')
    log.write_log('Model loaded successfully')
    return pickle.load(file) 

# Predict result for Single sale
def predict_single(sale, model):
    return model.predict([[sale.outlet_type, sale.outlet_year, sale.item_type, sale.item_mrp, sale.item_weight, sale.item_visibility]])

# Predict result for bulk
def predict_bulk(df, model):
    log.write_log('Processing model prediction')
    return model.predict(df)

#Merge input file with output (bulk prediction only)
def merge(df, result):
    return pd.concat([df, pd.DataFrame(result, columns=['Predicted_Sales'])], axis=1)

if __name__ == "__main__":
    app.run(debug=True)