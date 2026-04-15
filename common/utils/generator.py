from uuid import UUID, uuid4

def generate_uuid() -> UUID:
    result = uuid4()
    return result