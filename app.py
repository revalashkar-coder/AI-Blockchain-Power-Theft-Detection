from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os
from datetime import datetime

from blockchain import Blockchain


app = Flask(__name__)


# ============================================
# LOAD AI MODEL
# ============================================

model = joblib.load("model/theft_model.pkl")


# ============================================
# CREATE BLOCKCHAIN
# ============================================

blockchain = Blockchain()


# ============================================
# FEATURES
# ============================================

FEATURES = [
    "voltage",
    "current",
    "power_factor",
    "previous_consumption",
    "consumption",
    "tamper",
    "deviation"
]


# ============================================
# HISTORY FILE
# ============================================

HISTORY_FILE = "prediction_history.csv"


# ============================================
# CREATE HISTORY FILE IF NOT EXISTS
# ============================================

def create_history_file():

    if not os.path.exists(HISTORY_FILE):

        df = pd.DataFrame(
            columns=[
                "consumer_id",
                "prediction",
                "confidence",
                "block_index",
                "block_hash",
                "timestamp"
            ]
        )

        df.to_csv(
            HISTORY_FILE,
            index=False
        )


create_history_file()


# ============================================
# HOME
# ============================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================
# PREDICT
# ============================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        data = request.get_json()


        # ----------------------------------------
        # Consumer
        # ----------------------------------------

        consumer_id = data["consumer_id"]


        # ----------------------------------------
        # Meter data
        # ----------------------------------------

        voltage = float(
            data["voltage"]
        )

        current = float(
            data["current"]
        )

        power_factor = float(
            data["power_factor"]
        )

        previous_consumption = float(
            data["previous_consumption"]
        )

        consumption = float(
            data["consumption"]
        )

        tamper = int(
            data["tamper"]
        )


        # ----------------------------------------
        # Deviation
        # ----------------------------------------

        deviation = (

            consumption -
            previous_consumption

        ) / (

            previous_consumption + 0.001

        )


        # ----------------------------------------
        # AI input
        # ----------------------------------------

        input_data = pd.DataFrame(

            [[
                voltage,
                current,
                power_factor,
                previous_consumption,
                consumption,
                tamper,
                deviation
            ]],

            columns=FEATURES

        )


        # ----------------------------------------
        # Prediction
        # ----------------------------------------

        prediction = model.predict(
            input_data
        )[0]


        probability = model.predict_proba(
            input_data
        )[0][1]


        confidence = round(
            probability * 100,
            2
        )


        # ----------------------------------------
        # Result
        # ----------------------------------------

        if prediction == 1:

            result = (
                "POWER THEFT DETECTED"
            )

            status = "THEFT"

        else:

            result = (
                "NORMAL CONSUMPTION"
            )

            status = "NORMAL"


        # ----------------------------------------
        # Explainable AI
        # ----------------------------------------

        reasons = []


        if tamper == 1:

            reasons.append(
                "Meter tampering detected"
            )


        if power_factor < 0.70:

            reasons.append(
                "Abnormally low power factor"
            )


        if deviation < -0.20:

            reasons.append(
                "Large decrease in reported consumption"
            )


        if deviation > 0.30:

            reasons.append(
                "Unusual consumption variation detected"
            )


        if current > 15:

            reasons.append(
                "High current detected"
            )


        if len(reasons) == 0:

            reasons.append(
                "No major abnormal pattern detected"
            )


        # ----------------------------------------
        # Timestamp
        # ----------------------------------------

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        # ----------------------------------------
        # Blockchain data
        # ----------------------------------------

        blockchain_data = {

            "consumer_id":
                consumer_id,

            "timestamp":
                timestamp,

            "voltage":
                voltage,

            "current":
                current,

            "power_factor":
                power_factor,

            "previous_consumption":
                previous_consumption,

            "consumption":
                consumption,

            "tamper":
                tamper,

            "deviation":
                round(
                    deviation,
                    4
                ),

            "prediction":
                status,

            "confidence":
                confidence,

            "explanation":
                reasons

        }


        # ----------------------------------------
        # Add block
        # ----------------------------------------

        block = blockchain.add_block(
            blockchain_data
        )


        # ----------------------------------------
        # Blockchain validation
        # ----------------------------------------

        blockchain_valid = (
            blockchain.is_chain_valid()
        )


        # ----------------------------------------
        # SAVE HISTORY
        # ----------------------------------------

        history_row = pd.DataFrame([{

            "consumer_id":
                consumer_id,

            "prediction":
                status,

            "confidence":
                confidence,

            "block_index":
                block.index,

            "block_hash":
                block.hash,

            "timestamp":
                timestamp

        }])


        history_row.to_csv(

            HISTORY_FILE,

            mode="a",

            header=False,

            index=False

        )


        # ----------------------------------------
        # Return result
        # ----------------------------------------

        return jsonify({

            "success": True,

            "consumer_id":
                consumer_id,

            "prediction":
                result,

            "status":
                status,

            "confidence":
                confidence,

            "reasons":
                reasons,

            "block_index":
                block.index,

            "block_hash":
                block.hash,

            "blockchain_valid":
                blockchain_valid,

            "timestamp":
                timestamp

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 400


# ============================================
# GET PREDICTION HISTORY
# ============================================

@app.route(
    "/history"
)
def get_history():

    try:

        create_history_file()

        df = pd.read_csv(
            HISTORY_FILE
        )


        records = df.to_dict(
            orient="records"
        )


        return jsonify({
            "success": True,
            "history": records
        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# ============================================
# BLOCKCHAIN
# ============================================

@app.route(
    "/blockchain"
)
def get_blockchain():

    return jsonify({

        "chain":
            blockchain.get_chain(),

        "length":
            len(blockchain.chain),

        "valid":
            blockchain.is_chain_valid()

    })


# ============================================
# RUN
# ============================================

if __name__ == "__main__":

    app.run(
        debug=True
    ) 