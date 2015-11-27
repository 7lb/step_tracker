# Create
### Aggiunta passi per la data corrente
POST /v1/days  
POST /v2/users/[user]/days
##### Body richiesta:
```json
{
    "steps": "100"
}
```

##### Ritorna:
201 Created:
```json
{
    "message": "Created",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            },
    "uri": "http://localhost:5000/v1/days/2010-10-20"
}
```

400 Bad Request:
```json
{
    "message": "Bad Request: item already present"
}
```
se esistono già dei dati riferiti alla data corrente

```json
{
    "message": "Bad Request: missing step number"
}
```
se non è presente "steps" nel body della richiesta


# Retrieve
### Recupero passi per una data arbitraria
GET /v1/days/[data ISO 8601]  
GET /v2/users/[user]/days/[data ISO 8601]

##### Ritorna:
200 OK:
```json
{
    "message": "OK",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            }
}
```

404 Not Found:
```json
{
    "message": "Not Found"
}
```
se non esistono dati per la data richiesta

# Update
### Modifica passi per la data corrente
PUT /v1/days  
PUT /v2/users/[user]/days
##### Body richiesta:
```json
{
    "steps": "100"
}
```

##### Ritorna:
200 OK:
```json
{
    "message": "OK",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            },
    "uri": "http://localhost:5000/v1/days/2010-10-20"
}
```

400 Bad Request:
```json
{
    "message": "Bad Request: missing step number"
}
```
se non è presente "steps" nel body della richiesta

404 Not Found:
```json
{
    "message": "Not Found"
}
```
se non esistono dati per la data corrente

# Delete
### Eliminazione passi per una data arbitraria
DELETE /v1/days/[data ISO 8601]  
DELETE /v2/users/[user]/days/[data ISO 8601]

##### Ritorna:
200 OK:
```json
{
    "message": "OK",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            }
}
```

404 Not Found:
```json
{
    "message": "Not Found"
}
```
se non esistono dati per la data richiesta
