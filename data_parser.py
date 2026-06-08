import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OBSERVATIONS_PATH = os.path.join(BASE_DIR, "data", "observations.csv")


METRICS = {
    "systolic_bp": "Systolic Blood Pressure",
    "diastolic_bp": "Diastolic Blood Pressure",
    "heart_rate": "Heart rate",
    "respiratory_rate": "Respiratory rate",
    "body_temperature": "Body temperature",
    "oxygen_saturation": "Oxygen saturation in Arterial blood",
    "bmi": "Body mass index (BMI) [Ratio]",
    "weight": "Body Weight",
    "height": "Body Height",
    "glucose": "Glucose [Mass/volume] in Blood",
    "hemoglobin": "Hemoglobin [Mass/volume] in Blood",
    "hematocrit": "Hematocrit [Volume Fraction] of Blood by Automated count",
    "platelets": "Platelets [#/volume] in Blood by Automated count",
    "leukocytes": "Leukocytes [#/volume] in Blood by Automated count",
    "creatinine": "Creatinine [Mass/volume] in Blood",
    "urea_nitrogen": "Urea Nitrogen [Mass/volume] in Blood",
    "sodium": "Sodium [Moles/volume] in Blood",
    "potassium": "Potassium [Moles/volume] in Blood",
    "cholesterol_total": "Total Cholesterol",
    "cholesterol_hdl": "Cholesterol in HDL [Mass/volume] in Serum or Plasma",
    "cholesterol_ldl": "Cholesterol in LDL [Mass/volume] in Serum or Plasma by calculation",
    "triglycerides": "Triglycerides",
}


def _load_observations():
    #Ładowanie observations.csv
    if not hasattr(_load_observations, "_df"):
        if not os.path.exists(OBSERVATIONS_PATH):
            raise FileNotFoundError(f"File not found {OBSERVATIONS_PATH}. ")

        df = pd.read_csv(OBSERVATIONS_PATH, usecols=["PATIENT", "DESCRIPTION", "VALUE", "TYPE"],
            dtype={"PATIENT": str, "DESCRIPTION": str, "VALUE": str, "TYPE": str},)
        df = df[df["TYPE"] == "numeric"]
        df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
        df = df.dropna(subset=["VALUE"])
        _load_observations._df = df
    return _load_observations._df


def list_metrics():
    #zwraca tylko te metryki, dla których są dane w observations.csv
    df = _load_observations()
    available_descriptions = set(df["DESCRIPTION"].unique())
    available = {}
    for short_name, description in METRICS.items():
        if description in available_descriptions:
            available[short_name] = description
    return available


def get_metric(name):
    #pobiera wartości dla metryki po nazwie
    metrics = list_metrics()
    if name not in metrics:
        raise ValueError(f"Unknown metric: {name}.")
    description = metrics[name]
    df = _load_observations()
    return df.loc[df["DESCRIPTION"] == description, "VALUE"].tolist()