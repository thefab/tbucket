# API

## Concepts

Please read the [README.md](README.md) first (specifically the concepts section).

## Store a new transient object

### Request

    Method: POST
    Body (raw): the content of the object
    URL: http://{hostname}:{port}/tbucket/objects

    Optional headers:

    X-Tbucket-Lifetime: 3600
    (overrides the default lifetime (in seconds) for this object)

    X-Tbucket-Header-Content-Type: image/png
    (when the object will be requested, insert "Content-Type: image/png" header
     in response)

    X-Tbucket-Header-X-YourApplicationLogic: foobar
    (when the object will be requested, insert "X-YourApplicationLogic: foobar"
     header in reponse, same than previous example, just to show that 
     you can set any header)

### Response

#### The request is correct

    StatusCode: 201 (Created)
    Header: Location: http://{hostname}:{port}/tbucket/objects/{object_uid}
        => (UNIQUE OBJECT URL)
    Body: empty

#### The request is not correct

    StatusCode: 400 (Bad Request)
    Body: empty

## Get a stored transient object

### Request

    Method: GET
    URL: http://{hostname}:{port}/tbucket/objects/{object_uid}[?autodelete=1]
        => UNIQUE OBJECT URL GOT IN THE LOCATION HEADER OF A SUCCESSFUL STORE REQUEST 

    The autodelete parameter in query string is optional.

    Valid urls are :

    http://{hostname}:{port}/tbucket/objects/{object_uid}
    (no autodelete, by default)

    http://{hostname}:{port}/tbucket/objects/{object_uid}?autodelete=1
    (autodelete is activated)

    http://{hostname}:{port}/tbucket/objects/{object_uid}?autodelete=0
    (no autodelete, same than firts url)

If autodelete is activated, the transient object will be deleted automatically
after the first GET request. So if you GET the same URL another time, you
will have a 404 error. 

Note that `autodelete=1` breaks REST philosophy because this GET request is not
idempotent anymore.

### Response

#### The object exist (good url and not expired)

    StatusCode: 200
    Body: the content of the object
    
    Note: if you have set specific headers during the store request using
    X-Tbucket-Header-{header_name}: {header_value} syntax, you will get
    
    {header_name}: {header_value} in this GET response

#### The object does not exist (or is expired)

    StatusCode: 404 (Not Found)

## Delete a stored transient object

### Request

    Method: DELETE
    URL: http://{hostname}:{port}/tbucket/objects/{object_uid}
        => UNIQUE OBJECT URL GOT IN THE LOCATION HEADER OF A SUCCESSFUL STORE REQUEST 

### Response

#### The object exist (good url and not expired)

    StatusCode: 204 (No Content)
    Body: empty
    
#### The object does not exist (or is expired)

    StatusCode: 404 (Not Found)
    Body: empty
