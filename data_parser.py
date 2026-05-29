import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OBSERVATIONS_PATH = os.path.join(BASE_DIR, "data", "observations.csv")



def _load_observations():
    #Ładowanie observations.csv
    if not hasattr(_load_observations, "_df"):
        if not os.path.exists(OBSERVATIONS_PATH):
            raise FileNotFoundError(f"File not found {OBSERVATIONS_PATH}. ")

        df = pd.read_csv(OBSERVATIONS_PATH, usecols=["PATIENT", "DESCRIPTION", "VALUE"],
            dtype={"PATIENT": str, "DESCRIPTION": str, "VALUE": str},)
        df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
        df = df.dropna(subset=["VALUE"])
        _load_observations._df = df
    return _load_observations._df


def _values_for_description(description):
    #Zwraca listę wartości dla danej DESCRIPTION, czyli dokładne dopasowanie
    df = _load_observations()
    return df.loc[df["DESCRIPTION"] == description, "VALUE"].tolist()



def get_glucose():
    #Wartości glukozy
    return _values_for_description("Glucose [Mass/volume] in Blood")


def get_bmi():
    #"Wartości BMI
    return _values_for_description("Body Mass Index")


def get_blood_pressure():
    #Ciśnienie skurczowe
    return _values_for_description("Systolic Blood Pressure")



def get_all_values():
    #Wszystkie wartości liczbowe
    return _load_observations()["VALUE"].tolist()