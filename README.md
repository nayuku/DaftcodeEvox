# API do dodawania, edycji, usuwania i wyświetlania krótkich tekstów
### instalacja wymaganych pluginów
`pip3 install -r requirements.txt`  
### uruchomienie aplikacji lokalnie:
`python -m uvicorn main:app`  
### uruchomienie testów lokalnie:
`pytest tests.py`  

### API dostępne jest pod adresem: https://daftcode-evox.herokuapp.com/
### Dokumentacja z użyciem FastAPI Swagger: https://daftcode-evox.herokuapp.com/docs#/
Zwracany format odpowiedzi to JSON. Użytkownik mogący się uwierzytelnić jak i wiadomości zapisane są w bazie danych Sqlite3,  
której schemat zamieszczono poniżej:  
![image](https://user-images.githubusercontent.com/42339386/119516441-0d7d3780-bd77-11eb-9d4e-8328aa5cb9a9.png)

# Endpointy:
## Uwierzytelnienie:
| adres       | metoda    |zwracane kody|
| ------------- | ----------|-----------|
| https://daftcode-evox.herokuapp.com/auth | POST |201, 401|
####
Uwierzytelnienie odbywa się poprzez BasicAuth. Dane do uwierzytelnienia to:  
`admin:hard_password `   
Przykładowe zapytanie uwierzytelniające:  
```
curl -X 'POST'   'https://daftcode-evox.herokuapp.com/auth'\  
     -H 'accept: application/json'\  
     -H 'Authorization: Basic YWRtaW46aGFyZF9wYXNzd29yZA=='  
```
Uwierzytelnienie wymagane jest do korzystania z endpointów używanych do:
- Dodania wiadomości (POST /add_msg)
- Usunięcia wiadomości (DELETE /delete_msg/{id})
- Edycji wiadomości (PUT /edit_msg/{id})
####  
Uwierzytelnienie nie jest wymagane do czytania wiadomości (GET /read_msg/{id})   
Po poprawnym uwierzytelnieniu zostanie zwrócony kod `201` oraz wiadomość w formacie json:  
`{"detail": "Authorized"}`

## Odczytanie wiadomości o zadanym id:
| adres       | metoda    |zwracane kody|
| ------------- | ----------|-----------|
| https://daftcode-evox.herokuapp.com/read_msg/{id} | GET |200, 404, 422|
###
gdzie `{id}` to numeryczny identyfikator wiadomości np. 1.  
Po pomyślnym wejściu na adres zwrócony zostanie kod `200` oraz wiadomość:  
```
{
  "text": "treść wiadomości",
  "counter": 1
}
```
gdzie `counter` to licznik wyświetleń wiadomości inkrementowany przy każdym wyświetleniu.   
Przykładowe zapytanie: 
```
curl -X 'GET' \
  'https://daftcode-evox.herokuapp.com/read_msg/1' \
  -H 'accept: application/json'
 ```
 
## Dodanie nowej wiadomości
| adres       | metoda    |zwracane kody|
| ------------- | ----------|-----------|
| https://daftcode-evox.herokuapp.com/add_msg | POST |201, 400, 401, 422|
###
Aby dodać wiadomość po uwierzytelnieniu należy wysłać zapytanie metodą POST  
z następującym ciałem zapytania:  
```
{
  "text": "treść wiadomośći"
}
```
Wiadomość nie może być pusta, zawierać samych znaków białych (spacje, entery...) i przekraczać długość 160 znaków.  
Po poprawnym dodaniu wiadomości zostanie zwrócony kod `201` oraz json:  
`{"detail": "Created message with {id}"}`,  
gdzie `{id}` to numer dodanej wiadomości.  
Przykładowe zapytanie: 
```
curl -X 'POST' \
  'https://daftcode-evox.herokuapp.com/add_msg' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "treść wiadomości"
}'
 ```
 
## Usunięcie wiadomości o zadanym id:
| adres       | metoda    |zwracane kody|
| ------------- | ----------|-----------|
| https://daftcode-evox.herokuapp.com/delete_msg/{id} | DELETE |200, 401, 404, 422|
###
Aby usunąć wiadomość, po uwierzytelnieniu należy wysłać zapytanie metodą DELETE  
na powyższy adres, gdzie `{id}` to numer wiadomości do usunięcia.  
Po poprawnym usunięciu wiadomości zostanie zwrócony kod `200` oraz json:  
`{"detail": "Message with {id} deleted"}`   
Przykładowe zapytanie: 
```
curl -X 'DELETE' \
  'https://daftcode-evox.herokuapp.com/delete_msg/1' \
  -H 'accept: application/json'
 ```
 
## Edycja wiadomości o zadanym id:
| adres       | metoda    |zwracane kody|
| ------------- | ----------|-----------|
| https://daftcode-evox.herokuapp.com/edit_msg/{id} | PUT |200, 400, 401, 404, 422|
###
Aby edytować wiadomość, po uwierzytelnieniu należy wysłać zapytanie metodą PUT  
na powyższy adres, gdzie `{id}` to numer wiadomości do edycji z następującym ciałem zapytania:
```
{
  "text": "nowa treść wiadomości"
}
```
Po poprawnej edycji wiadomości zostanie zwrócony kod `200` oraz json:  
`{"detail": "Message with {id} altered with new text"}`,  
gdzie `{id}` to numer edytowanej wiadomości. Edycja wiadomości resetuje jej licznik wyświetleń.
Przykładowe zapytanie: 
```
curl -X 'PUT' \
  'https://daftcode-evox.herokuapp.com/edit_msg/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "nowa treść wiadomości"
}'
 ```
#### W przypadku niepoprawnego użycia któregokolwiek z endpointów zostanie zwrócony kod błedu klienta zaczynający się od 4.. (numery kodów wymienione w tabelkach) wraz z krótkim opisem błędu w postaci JSON np. dla 401:
```
{
  "detail": "Unauthorized"
}
```
