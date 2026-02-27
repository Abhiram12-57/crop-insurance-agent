import pandas as pd
import uuid

class PayoutEngine:
    def __init__(self):
        # In a real scenario, this would be a database table
        self.payout_ledger = pd.DataFrame(columns=['Transaction ID', 'Date', 'Farmer ID', 'Amount (INR)', 'Reason'])

    def trigger_payout(self, farmer_id, reason, amount=5000):
        """
        Generate unique transaction ID, add timestamp, log payout, prevent duplicates
        """
        # Basic fraud logic / duplicate prevention
        # Check if farmer already received a payout this year/season
        if not self.payout_ledger.empty:
            recent_payouts = self.payout_ledger[
                (self.payout_ledger['Farmer ID'] == farmer_id)
            ]
            if not recent_payouts.empty:
                return False, "Payout already processed for this farmer recently."
                
        tx_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_record = pd.DataFrame([{
            'Transaction ID': tx_id,
            'Date': timestamp,
            'Farmer ID': farmer_id,
            'Amount (INR)': amount,
            'Reason': reason
        }])
        
        self.payout_ledger = pd.concat([self.payout_ledger, new_record], ignore_index=True)
        return True, tx_id
        
    def get_ledger(self):
        return self.payout_ledger
