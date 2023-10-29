from httpx import AsyncClient
import pytest

@pytest.mark.parametrize("email, fio, password, status_code",[
    ("qwerty@mail.ru", "qwerty", "qwerty", 201),
    ("qwerty@mail.ru", "qwerty", "qw123erty", 409),
    ("123qew", "qwerty", "qwerty", 422),
])
async def test_register(email, fio, password, status_code, ac: AsyncClient):
    response = await ac.post("/auth/register/", json=
                             {"email": email,
                              "fio": fio,
                              "password": password},
    )

    assert response.status_code == status_code



@pytest.mark.parametrize("username, password, status_code",[
    ("test@test.com", "test", 200),
    ("qwerty@mail.ru", "123qwerty", 401),
])
async def test_login(username, password, status_code, ac: AsyncClient):
    response = await ac.post("/auth/login", data={"username": username,
                                                  "password": password,},
                              headers={"content-type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status_code
    if response.status_code == 200:
        response_data = response.json()
        assert "access_token" in response_data
        assert response_data["token_type"] == "bearer"