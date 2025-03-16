from datetime import timedelta

def parse_duration(value):
    '''
    Convert minutes in strings to timedelta objects, ignore invalid values
    '''
    try:
        value = int(value)
        if value > 0:
            return timedelta(minutes=value)
        pass
    except:
        ValueError
    return None
