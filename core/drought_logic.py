def check_drought(df, farmer_id, rain_threshold, moisture_threshold, consecutive_days=5):
    """
    Drought if:
    - Rainfall below threshold for X consecutive days
    OR
    - Soil moisture below critical level
    Return boolean drought status, and the reason.
    """
    farmer_data = df[df['Farmer ID'] == farmer_id].sort_values('Date')
    if farmer_data.empty:
        return False, "No data"
        
    # Check soil moisture condition today (last day in data)
    latest_moisture = farmer_data.iloc[-1]['Soil Moisture (%)']
    if latest_moisture < moisture_threshold:
        return True, f"Soil moisture ({latest_moisture}%) below critical level ({moisture_threshold}%)"
        
    # Check consecutive dry days
    farmer_data['is_dry'] = farmer_data['Rainfall (mm)'] < rain_threshold
    
    # Calculate consecutive dry days
    dry_streak = 0
    for is_dry in farmer_data['is_dry'].tail(consecutive_days):
        if is_dry:
            dry_streak += 1
        else:
            dry_streak = 0
            
    if dry_streak >= consecutive_days:
        return True, f"Rainfall below threshold ({rain_threshold}mm) for {consecutive_days} consecutive days"
        
    return False, "Normal conditions"
