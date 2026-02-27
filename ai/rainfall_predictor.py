import numpy as np
from sklearn.linear_model import LinearRegression

class RainfallPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        
    def train(self, df):
        """
        Train a simple Linear Regression model on historical weather data.
        Features: Temperature, Soil Moisture. Target: Rainfall.
        Note: In real-world, rainfall prediction requires more complex time-series models (LSTM, XGBoost),
        but for this hackathon, Linear Regression gives a basic directional forecast.
        """
        X = df[['Temperature (°C)', 'Soil Moisture (%)']].values
        y = df['Rainfall (mm)'].values
        
        self.model.fit(X, y)
        self.is_trained = True
        
    def predict_next_days(self, current_temp, current_moisture, days=5):
        """
        Predict rainfall for the next `days` days based on current conditions.
        """
        if not self.is_trained:
            return []
            
        predictions = []
        temp = current_temp
        moist = current_moisture
        
        for _ in range(days):
            pred_rain = self.model.predict([[temp, moist]])[0]
            pred_rain = max(0, pred_rain) # Rainfall cannot be negative
            predictions.append(round(pred_rain, 2))
            
            # Simulate next day conditions
            temp += np.random.uniform(-1, 1)
            moist += pred_rain * 0.5 - (temp - 25) * 0.5
            moist = np.clip(moist, 10, 80)
            
        return predictions
        
    def calculate_drought_risk(self, predicted_rainfall, threshold):
        """
        Calculate probability of drought risk based on predicted rainfall vs threshold.
        """
        if not predicted_rainfall:
            return 0.0
            
        days_below_threshold = sum(1 for rain in predicted_rainfall if rain < threshold)
        risk_probability = (days_below_threshold / len(predicted_rainfall)) * 100
        return round(risk_probability, 2)
