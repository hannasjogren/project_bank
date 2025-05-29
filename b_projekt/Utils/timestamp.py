from datetime import datetime

def get_timestamp():
    return datetime.now().isoformat()

if __name__ == "__main__":
    print(get_timestamp())