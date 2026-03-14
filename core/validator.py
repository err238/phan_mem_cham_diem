def validate_score(value):

    try:

        v = float(value)

        return 0 <= v <= 10

    except:
        return False
    
def validate_weight(value):

    try:
        v = float(value)
        return 0 <= v <= 1
    except:
        return False
