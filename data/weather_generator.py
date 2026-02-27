import pandas as pd
import numpy as np
import datetime

def generate_mock_weather_data(days=60, num_farmers=10):
    """
    Generates synthetic weather data.
    Fields: Date, Rainfall (mm), Temperature (°C), Soil Moisture (%), District, Farmer ID
    Range:
        Rainfall: 0 - 100 mm (mostly lower with occasional spikes)
        Temperature: 20 - 45 °C
        Soil Moisture: 10 - 80 %
    """
    np.random.seed(42)
    
    start_date = datetime.date.today() - datetime.timedelta(days=days)
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]
    
    districts = ['Pune', 'Nashik', 'Aurangabad', 'Nagpur', 'Solapur']
    
    data = []
    
    for farmer_id in range(1, num_farmers + 1):
        district = np.random.choice(districts)
        
        base_rain = np.random.exponential(scale=5, size=days) 
        base_rain = np.clip(base_rain, 0, 100)
        
        # Introduce a dry spell
        dry_start = np.random.randint(10, days - 20)
        dry_end = dry_start + np.random.randint(10, 20)
        base_rain[dry_start:dry_end] = np.random.uniform(0, 2, size=(dry_end - dry_start))
        
        temperatures = np.random.uniform(20, 35, size=days)
        # Higher temp during dry spell
        temperatures[dry_start:dry_end] += np.random.uniform(5, 10, size=(dry_end - dry_start))
        temperatures = np.clip(temperatures, 20, 45)
        
        soil_moisture = np.zeros(days)
        current_moisture = np.random.uniform(40, 60)
        
        for i in range(days):
            # Moisture increases with rain, decreases with high temp
            current_moisture += base_rain[i] * 0.5 - (temperatures[i] - 25) * 0.5
            current_moisture = np.clip(current_moisture, 10, 80)
            soil_moisture[i] = current_moisture
            
        for i, date in enumerate(dates):
            data.append({
                'Date': date,
                'Farmer ID': f'FMD-{farmer_id:04d}',
                'District': district,
                'Rainfall (mm)': round(base_rain[i], 2),
                'Temperature (°C)': round(temperatures[i], 2),
                'Soil Moisture (%)': round(soil_moisture[i], 2)
            })
            
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df
