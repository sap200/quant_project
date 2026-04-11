import uuid

class Account:
    def __init__(self):
        self.id = str(uuid.uuid4())
        
    def __str__(self):
        return f"Account(id={self.id})"

    def __repr__(self):
        return f"Account(id={self.id})"