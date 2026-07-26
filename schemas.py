from marshmallow import Schema, fields, post_load
from .models import User, Session

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class SessionSchema(Schema):
    token = fields.Str(required=True)
    user_id = fields.Int(dump_only=True)
    expires = fields.DateTime(load_only=True)

    @post_load
    def make_session(self, data, **kwargs):
        return Session(**data)

class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class RegisterSchema(Schema):
    email = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)

def validate_data_schema(schema, data):
    try:
        schema.load(data)
        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False

# test data validation
if __name__ == "__main__":
    data = {"email": "test@example.com", "username": "testuser", "password": "testpass"}
    schema = UserSchema()
    assert validate_data_schema(schema, data) == True

    data = {"email": "test@example.com", "username": "testuser"}
    schema = UserSchema()
    assert validate_data_schema(schema, data) == False