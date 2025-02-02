
# `auth.py`
## Модуль аутентификации с использованием JWT-токенов
### Классы:
- **`JWTencoder`** – отвечает за кодирование JWT-токенов.
- **`JWTgenerator`** – генерирует пару токенов: access-токен и refresh-токен.
- **`JWTvalidator`** – выполняет проверку подписи токена.
- **`JWTdecoder`** – декодирует JWT-токены.
- **`TokenHandler`** – управляет токенами в cookies пользователя.
- **`Validation`** – выполняет проверку токена и предоставляет информацию о пользователе.

## Описание классов и методов

### **Класс `JWTencoder`**
>Отвечает за кодирование JWT-токенов.

#### Методы:
- `form_JWT_payload(body: dict, living_time_min: int | None = 10) -> dict`
    > Формирует payload для JWT-токена.
  - `body` – данные, которые будут записаны в payload.
  - `living_time_min` – время жизни токена в минутах.

- `form_JWT_header(algorightm: str) -> dict`
  > Формирует заголовок для JWT-токена.
  - `algorightm` – алгоритм, который будет использоваться.

- `encode(body: dict, living_time_min: int | None = 10, algorightm: str | None = "HS256") -> str`
  > Кодирует JWT-токен с заданным временем жизни и алгоритмом.
  - `body` – данные, которые будут записаны в payload.
  - `living_time_min` – время жизни токена в минутах.
  - `algorightm` – алгоритм, который будет использоваться.

---

### **Класс `JWTgenerator`**
>Генерирует JWT-токены.

#### Методы:
- `generate_access_token(body: dict, token_lifetime_min: int) -> str`
  > Генерирует access-токен.
  - `body` – данные, которые будут записаны в payload.
  - `living_time_min` – время жизни токена в минутах.
  
- `generate_refresh_token(body: dict, token_lifetime_days: int) -> str`
  > Генерирует refresh-токен с заданным временем жизни в днях.
  - `body` – данные, которые будут записаны в payload.
  - `token_lifetime_days` – время жизни токена в днях.

- `generate_tokens(body: dict) -> tuple[str, str]`
  > Генерирует пару токенов (access, refresh).
  - `body` – данные, которые будут записаны в payload.

---

### **Класс `JWTvalidator`**
> Проверяет подпись токена.

#### Методы:
- `check(token: str) -> bool`
    > Проверяет корректность подписи токена.
  - `token` - токен
---

### **Класс `JWTdecoder`**
> Декодирует JWT-токен.

#### Методы:
- `decode(token: str) -> dict`
  > Декодирует токен и возвращает его содержимое.
   - `token` - токен
---

### **Класс `TokenHandler`**
> Управляет токенами пользователей.

#### Методы:
- `remove_tokens(response: Response) -> None`
  > Удаляет токены из cookies пользователя.
  - `response` - объект класса `Response` из модуля FastAPI
    
- `set_tokens(user: User, response: Response) -> None`
  > Устанавливает access и refresh токены в cookies пользователя.
  - `response` - объект класса `Response` из модуля `FastAPI`
  - `user` - объект класса `User` из модуля `db.models`
- `get_user_bytoken(token: str) -> User | None`
  > Извлекает пользователя по токену.
  - `token` - токен
---

### **Класс `Validation`**
> Проверяет корректность токена и получает информацию о пользователе.

#### Атрибуты:
- `is_token_valid: bool` – флаг валидности токена.
- `user: User` – объект пользователя.
- `is_admin: bool` – флаг наличия админ-прав.

#### Методы:
- `get_user() -> User`
  > Возвращает объект класса `User` из модуля `db.models`.

- `__UserValidation(request: Request) -> None`
  > Проверяет токен, валидирует пользователя, определяет права администратора.
  - `request` - объект класса `Request` из модуля `FastAPI`

- `validate(request: Request, admin_validation: bool = False) -> RedirectResponse | None`
  > Проверяет токен и выполняет перенаправление при необходимости.
  > Если токен истек – перенаправляет на `/auth/refresh`.
  > Если у пользователя нет прав администратора – возвращает ошибку `403`.
  > В случае других ошибок возвращает `401`.

  - `request` - объект класса `Request` из модуля `FastAPI`
  - `admin_validation` - True - проверять админ-права, False - не проверять
---

Этот модуль реализует защиту API на основе JWT-аутентификации, управляет пользовательскими токенами и проверяет их валидность.

