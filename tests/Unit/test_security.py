from app.core.security import hash_password,verify_password , create_access_tokens , verify_access_token , create_refresh_tokens,verify_refresh_token

def test_password_logic():
    password = "mypassword123"
    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password,hashed_password)
    assert not verify_password("12345" , hashed_password)

def test_create_access_tokens():
    token = create_access_tokens("user34521")
    assert isinstance(token,str)
    assert token.count(".") == 2

def test_verify_access_token():
    user_id = "user123"
    token = create_access_tokens(user_id)
    validate_token = verify_access_token(token)
    assert user_id == validate_token["sub"]

def test_create_refresh_tokens():
    token,_ = create_refresh_tokens("user34521")
    assert isinstance(token,str)
    assert token.count(".") == 2

def test_verify_refresh_token():
    user_id = "user123"
    token,_ = create_refresh_tokens(user_id)
    validate_token = verify_refresh_token(token)
    assert user_id == validate_token["sub"]


