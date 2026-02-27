def generate_sms(farmer_id, tx_id, amount):
    """Generates an automated notification message for the farmer."""
    message = f"✅ ALERT: ₹{amount} has been credited to {farmer_id} bank account due to verified drought conditions. Ref: {tx_id}"
    return message
