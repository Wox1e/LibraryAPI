# **RU**
# Описание

RESTful API для управления библиотекой. Оно позволяет пользователям регистрироваться, авторизоваться, управлять книгами, авторами, выдачей книг и читателями.

# Стэк:

* Python
     - FastAPI
* Pydantic
* PostreSQL
* JWT
  
# Функциональность:

**Аутентификация и пользователи:**

*  Регистрация нового пользователя
*  Авторизация через JWT
*  Обновление и удаление токена
*  Редактирование профиля
  
**Управление книгами:**

* Создание, обновление и удаление книги
* Получение списка всех книг или поиск по ID
  
**Управление авторами:**

* Добавление нового автора
* Редактирование и удаление данных об авторе
* Получение списка авторов или поиск по ID
  
**Выдача книг:**

* Выдача книи
* Назначение даты возврата
*  Возврат книги
  
**Читатели:**
* Просмотр списка читателей
* Поиск читателя по ID

# Установка

1) Установка

```
git clone https://github.com/Wox1e/LibraryAPI
```
2) Измените данные в .env
```
   # DEFAULT VALUES. CHANGE ON DEPLOY

     DB_HOST = "db_host"
     DB_PORT = 5433
     DB_USER = "postgres"
     DB_PASS = "postgres_pass"
     DB_NAME = "library"
     
     SECRET_KEY = "somesecretkey_98754809Y&(*HUPOI(h))"
     REF_TOK_LIFETIME_DAYS = 60
     ACCS_TOK_LIFETIME_MIN = 10
     
     
     
     BOOKS_LIMIT_FOR_READER = 5
```
Укажите данные своей базы данных

3) Создание таблиц
```
   alembic revision --autogenerate
   alembic upgrade head
```

4) Запуск
```
cd LibraryAPI/src
python -m uvicorn main:app --reload 
```

# Полная документация находится [тут](https://wox1e.github.io/LibraryAPI/)

<br /><br />

# **ENG**

# **Description**

A RESTful API for library management. It allows users to register, authenticate, manage books, authors, book rentals, and readers.

# **Stack**

-   **Python**
    -   FastAPI
-   **Pydantic**
-   **PostgreSQL**
-   **JWT**

# **Features**

### **Authentication and Users:**

-   User registration
-   JWT-based authentication
-   Token refresh and deletion
-   Profile editing

### **Book Management:**

-   Create, update, and delete books
-   Retrieve a list of books or search by ID

### **Author Management:**

-   Add a new author
-   Edit and delete author information
-   Retrieve a list of authors or search by ID

### **Book Rentals:**

-   Rent a book
-   Set a return date
-   Return a book

### **Readers:**

-   View a list of readers
-   Search for a reader by ID

# **Installation**

1.  **Clone the repository**
```
git clone https://github.com/Wox1e/LibraryAPI
```
2. Change .env file
```
   # DEFAULT VALUES. CHANGE ON DEPLOY

     DB_HOST = "db_host"
     DB_PORT = 5433
     DB_USER = "postgres"
     DB_PASS = "postgres_pass"
     DB_NAME = "library"
     
     SECRET_KEY = "somesecretkey_98754809Y&(*HUPOI(h))"
     REF_TOK_LIFETIME_DAYS = 60
     ACCS_TOK_LIFETIME_MIN = 10
     
     
     
     BOOKS_LIMIT_FOR_READER = 5
```
Enter your creditials

3. Create tables
 ```
   alembic revision --autogenerate
   alembic upgrade head
 ```

4. **Run the application**
```
cd LibraryAPI/src
python -m uvicorn main:app --reload 
```


# Full documentation avaliable [here](https://wox1e.github.io/LibraryAPI/)

