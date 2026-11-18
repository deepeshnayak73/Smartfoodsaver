from datetime import date

SOON_DAYS = 3

def days_left(expiry_date, today=None):
    today = today or date.today()
    return (expiry_date - today).days

def classify(expiry_date, today=None):
    d = days_left(expiry_date, today)
    if d < 0:
        return "Expired"
    if d <= SOON_DAYS:
        return "Expiring Soon"
    return "Fresh"
