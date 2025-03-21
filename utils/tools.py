import uuid


def generate_uuid_str():
    return str(uuid.uuid4().hex)
