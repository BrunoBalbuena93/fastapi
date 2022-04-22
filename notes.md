# FastAPI 
Tiene su parecido con Flask.

Para instanciar una aplicación, simplemente se declara dentro de `main.py` de la siguiente manera.
```
from fastapi import FastAPI
my_app = FastAPI()
``` 

Y posteriormente, para ejecutarse:
```
uvicorn main:my_app --reload
```
donde `uvicorn` es el gestor de la ejecución (como lo es `gunicorn` en Django), `main` es el nombre donde buscará la aplicación y `my_app` la instancia de la aplicación
Al construir un API usando este Framework, por default se generan docs bajo el path `/docs` y `/redocs`

## Paths

Al declarar un path, se indica que aplicación está siendo seleccionada, con que *verb* y el path determinado en su argumento. todo esto como un decorador. Después, al declarar la función podemos incluir el tipo de dato que esperamos recibir, esto es para ingresar una validación previa a la ejecución del codigo (cortesía de `OpenAPI`). 
```
@my_app.get('/items/{items_id}')
async def read_item(item_id: str):
    return {'item_id': item_id}
```
En **FastAPI** solo es necesario regresar un diccionario. 

Así como cualquier aplicación web, el orden es importante, por lo que si quisieramos tener los endpoints `/users/me` y `/users/{user_id}`, deberíamos colocar primero `/me` para que no se confundiera tratando de castear `user_id = me`.

Los tipos de objetos que se pueden recoger dentro de un path son _int_, _str_, o custom generados mediante un Enum

#### Customizando los paths mediante Enum
Esto se puede interpretar también como **Valores Predefinidos**, y para ello se utiliza una clase que herede de `Enum` como se muestra en el ejemplo
``` 
from enum import Enum

class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'

app = FastAPI()

@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {'model_name': model_name, 'message': 'Deep learning FTW!'}
    
    elif model_name.value == 'lenet':
        return {'model_name': model_name, 'message': 'LeCNN all the Images'}
    return {'model_name': model_name, 'message': 'Have some residuals'}
```
Se desprenden 3 puntos en el codigo mostrado
- **Exclusividad**: Al definirse solo los 3 tipos de campos, la api rechazará automáticamente todos los que sean distintos a los indicados
- **Comparatividad**: Para castear que opción se ha escogido se puede hacer valer como `ModelName.class` o bien, como `model_name.value`, es decir, atributo de la clase o valor de la instancia
- **Documentación**: Dentro de la documentación, por defecto se generará como lista al probarse.

## Query params

Todo lo que no esté mapeado dentro de un `path` y posterior al _?_ es considerado un query param. 

Los query params pueden ser opcionales u obligatorios, dependiendo de la forma en la que son casteados.

```
@app.get('/query')
async def read_query_params(limit:int, index: Optional[int] = None, offset: bool=False):
    item = {'limit': limit}
    if index:
        item.update({'index': index})
    if offset:
        item.update({'offset': 'active'})
    return item
```
En el ejemplo, `index` es un parametro obligatorio, `index` es opcional marcado como *None* por default, y `offset` se considera *false* a menos que explicitamente se diga que no lo es.

#### Validación Adicional 
Además de la validación por tipado, se le puede indicar a FastAPI que debe cumplir con otros parámetros mediante el uso de `Query()`. 
```
@app.get('advanced-query')
async def read_advance_query_params(
    p: Optional[str] = Query(None,min_length=2, max_length=50), 
    q: str = Query('default', regex='^def'),
    r: str = Query(..., title='Mandatory', description='You can define a description here', alias='alias-name')):
    return {'p': p, 'q': q, 'r': r}
```
Donde regex representa una expresión regular, title, description son datos informativos y alias mapea el parámetro.


## Request Body
Como cualquier aplicación, no solo se requieren métodos `GET`. Dentro de FastAPI se necesita un modelo del body que se va a recibir, muy similar a las interfases de Typescript, para ello se utiliza la biblioteca `pydantic`

### Pydantic Models
Creando los modelos heredando de `BaseModel`, se definen los atributos con su tipado, valores opcionales y default para posteriormente ser utilizados como un tipo de dato.
```
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post('/items/{item_id}')
async def create_item(item_id:str, item: Item):
    return item
```
Observando la ruta especificada en la función observamos que hay un parámetro de `item_id`, FastAPI reconoce que este parametro junto con su tipado en la definición de la función corresponde al pathname, posteriormente *algo* llamado `item`, tipado con el modelo construido lo asociará con el `request.body`, y finalmente si otro parámetro es definido pero no incluido en el path, es considerado `query_param`.

Existen otros métodos para leer el body de una request, en caso que no se quiera utilizar `BaseModel` para generar interfaces.

### Especificando modelos
Similar a `Query` y `Path`, se utiliza la función `Field`, que tiene las mismas propiedades que las otras dos (todas ellas heredan de un mismo padre).
```
class User(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    email: str = Field(None, description='Este campo no es mandatorio')
```
También es posible utilizar sets y listas dentro de los modelos así como anidar otros modelos, simplemente se agrega el campo, se indica el tipo y sus posibles condiciones, y funciona como un objeto anidado dentro del modelo padre.

### Mezclando modelos
Supongamos que dentro del body del request quisieramos incluir más de un modelo, o bien, agregar parámetros independientes, siendo así FastAPI nos permite hacer esto mediante la separación de los componentes en la estructura de los modelos, es decir:
```
{
    "modelo_1": {
        "atributos": "del",
        "modelo": 1
    },
    "modelo_2": {
        "atributos": "del",
        "modelo": 2
    },
    "parametro": "independiente"
}
```
La definición de la función quedaría de la siguiente manera:
```
@app.post('/advanced-items/{item_id}')
async def create_advanced_items(
    item_id: int,
    item: Item,
    user: User,
    additional: int= Body(...,gt=0)
    ):
    return {'item_id': item_id, 'item': item, 'user': user, 'add': additional}
```
Notese que `Item` y `User` deben estar definidos en algun lugar.

### Casteos distintos a los elementales
El casteo de variables también es válido para:
- `UUID` representado como `str` → `item_id: UUID`
- `datetime` represantado como `str` en formato `YYYY-mm-ddTHH:MM:SS<tz>` → `start_date: datetime`
- `date` represantado como `str` en formato `YYYY-mm-dd` → `start_date: date`
- `time` represantado como `str` en formato `HH:MM:SS.ZZZ` → `start_date: time`
- `bytes` represantado como `str` en formato binario 
- `Decimal` representado como `float`

### Modelos de respuesta
Al definir una vista se puede definir un modelo de respuesta, el cual indica que datos se enviarán en la response así como validación previa al contestar apegado a las reglas del modelo en cuestión.

Un ejemplo de esta situación sería al hacer un SignUp de un usuario, ya que no deberíamos regresar el valor del password dentro del response. En el codigo se utiliza password como plain string, obviamente esto es algo que NO se debe implementar en una aplicación de producción.
```
class User(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    password: str = Field(min_length=6)
    email: str = Field(None, description='Este campo no es mandatorio')
 
class UserOut(BaseModel):
    username : str = Field(..., title='Identificación', max_length=50)
    email: str = Field(None, description='Este campo no es mandatorio')

@app.post('/user/', response_model=UserOut)
async def create_user(user: User):
    return user
```
Adicionalmente está el campo `response_model_exclude_unset` que remueve los campos no definidos, `response_model_exclude_defaults` para remover los defaults, y `response_model_exclude_none` para remover los campos vacios.

Nota: Si queremos agregar `status` a las responses, éstos se colocan en el decorador como `status_code`
```
from fastapi import status

@app.post('the/route', status_code=status.HTTP_201_CREATED)
async def my_fn(data: str):
    return {'name': data}
```

## Usando form-data
> Debes tener instalado `python-multipart`
Simplemente se importa `Form` de fastapi y al definirse los campos en la view, las identificas como *Form*
```
@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```
## Files
Para recibir archivos se utiliza `FileUpload` desde _fastapi_, y si se desea hacer validaciones, la clase `File` que funciona igual que `Field` y `Query`.

#### ¿Por qué usar `UploadFile` en lugar de `bytes`?
Primeramente por un tema de memoria, al ser leido como *bytes*, se almacenará en memoria todo el contenido, lo cual funcionará bien para elementos pequeños pero traerá problemas para elementos de mayor tamaño.

Al trabajar con *UploadFile*, FastAPI decidirá en donde almacenarlo (ya sea en disco o en memoria) dependiendo de su tamaño. El tipo de objeto es un *file-like*, es decir, se puede pasar a otras dependencias de python como un *TemporaryFile*.

## Manejando Errores
Por defecto FastAPI atiende los errores básicos, como verbos de request no permitidos, requerimientos no cumplidos dentro de modelos y cosas así, para agregar errores customizados se utiliza la excepción `HTTPException`, la cual se declara como `raise HTTPException(status_code=404, detail="Detalles del error")` y FastAPI hará su magia. 
> En `detail` puede ir cualquier estructura JSONizable, no solo un `str`

Hay formas para hacer override de los handlers que se pueden leer en [la documentación](https://fastapi.tiangolo.com/tutorial/handling-errors/), no se mencionarán aquí ya que son casos muy especificos y personalmente, me da pereza.

### Json Encoder
FastAPI tiene un encoder para convertir modelos a *json*, te preguntarás ¿Qué diferencia hay con usar `.dict()`; pues esto es para todas las variables no *jsonizables* como datetimes o decimales. `from fastapi.encoder import jsonable_encoder`

## Dependencias
¿Qué es una *inyección de dependencias*?

Supongamos que necesitas una cierta lógica para un grupo de requests, ya que todas ellas tendrían una conexión a DB, necesitan los mismos parámetros, o bien, autenticaciones. Entonces se pueden definir lineas de código como *dependencias* que pueden ser heredadas (en el sentido que FastAPI hará todo lo necesario para que puedas leerlas).

Esto es util para minimizar el codigo, o al menos evitar duplicación del mismo.

Para utlizar dependencias, se utiliza `Depends`, que aunque pinta como `Body` o `Query`, tiene un funcionamiento distinto; este recibe una función la cual *mapea* e inyecta como variable dentro de la función donde está siendo inyectado

### Path Dependencies

En este primer ejemplo se utiliza este feature para capturar parámetros dentro de una función.

Ejemplo de dependencia como función en [dependencies](app/dependencies.py)
```
async def common_parrameters(q: Optional[str] = None, skip: int = 0, limit: int = 10):
    return {'q': q, 'skip': skip, 'limit': limit}
```
Dependencia siendo usada en [items](app/routers/items.py)
```
@router.get('/')
async def read_items(commons: dict = Depends(common_parrameters)):
    return commons
```
Dependencia siendo usada en [users](app/routers/users.py)
```
@router.get('/users/')
async def read_users(commons: dict = Depends(common_parrameters)):
    return commons
```

Y así como pueden funciones, también pueden ser clases. El funcionamiento es el mismo, solamente al instanciarse se cambia un poco la estructura
```
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@router.get('/users/')
async def read_users(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return commons
```
> **Subdependencias** Dado que su programación es inyectable, se pueden anidar dependencias entre si, es decir, una dependencia puede tener a su vez una dependencia interna y así tantas veces sean necesarias.

### Dependencias como middlewares
Quizá no sea la mejor forma de definirlo, pero pareciese que funciona como tal.

Supongamos que no queremos obtener información sobre los datos que recoge, sino que queremos validar cierta información (por ejemplo, que un usuario esté autenticado). Entonces hacemos uso de un `raise HTTPException`, el cual hará que la solicitud no llegue a donde está queriendo llegar, y obteniendo un mensaje determinado. Tal como un *middleware*

```
from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]

```

## Dependencia Global

Como se mencionó arriba, las dependencias pueden ser incluidas en cualquier router o función, en caso que deseemos incluirlas de manera global en la aplicación al denotarlas en el constructor de la aplicación
```
app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
```

## Dependencias con Yield
Dependencias que queremos que hagan algunas cosas después de retornar un valor, en estos casos usamos `yield`, que permite regresar el valor y seguir la ejecución del código, como por ejemplo, para la conexión de una base de datos, se esperaría obtener la conexión y al concluir lo que se debe hacer, cerrarla.

Un ejemplo de esto
```
async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
```
En el ejemplo se ve un try → finally, esto se debe a que si en la ejecución del código intermedio, ya sea otra dependencia o la función como tal se presenta una excepción, estemos seguros de "cerrar" el hilo respecto a la dependencia aquí mencionada, la conexión a base de datos.
> Después de un yield no se puede levantar un `HTTPException`, ya que se ejecuta una vez enviada la respuesta

## Seguridad
FastAPI tiene soporte para varios tipos de autenticaciones. Se mencionarán los principales y se incluyen en [`app/authentication.py`](app/authentication.py)
### Oauth2
Es ampliamente usado por *third party packages* como *facebook* o *github* (o bien, una forma de la misma). Está incluida en la parte de de `fastapi.security`.

#### Flujo de contraseña
Dado que en este punto todavía no hay una base de datos conectada, vamos a *mockear* el sistema para ver funcionar el flujo de las contraseñas.

Siguiendo el ejemplo dispuesto en la documentación, se utilizan las siguientes funciones:

```
def get_user(db, username: str) -> UserInDB:
    if username in db:
        userdict = db.get(username)
        return UserInDB(**userdict)

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
```

Y la lógica es la siguiente:
1. Al consumir `/token` primero se obtiene el objeto del usuario que está tratando de loggearse, en el ejemplo se usa data mockeada, en una aplicación se haría la consulta a base de datos para obtener esta información. En caso de no existir, se regresa una excepción con error 400
2. Paralelamente, se hace una instancia del modelo `UserInDB` con la forma que se envía.
3. Se hace la validación de contraseña, en este caso con `fake_hash_password` para comparar con la almacenada en la base de datos.
4. En caso de que las contraseñas sean las mismas, lo loggea

### Dejando la implementación rudimentaria
Se puede (y sugiere) usar las bibliotecas existentes para encriptado de contraseñas, tales como `bcrypt`, con la que podemos reproducir una encriptación practicamente igual a la de Django o Flask.

También podemos configurar el uso de tokens del tipo _JWT_ para la autenticación utilizando una llave (que puedes generar usando `openssl rand -hex 32`), un algoritmo de encriptación (usualmente el `HS256`) y un tiempo de vida definido como `timedelta`

## Dependencias para JWT
```
pip install "python-jose[cryptography]"
pip install "passlib[bcrypt]"
```

Utilizando `CryptoContext` generas el esquema de encriptación para las contraseñas, el cual se encarga de la validación 

> Se usa el argumento `sub` al crear el access_token para identificar ese _algo_ que lo hace distinto, como el nombre de usuario

## Middlewares

#### Repasando un poco
Un _middleware_ es una función (o conjuto de ellas) que se ejecutan para cada request antes de ser procesada por algun _path_, ejecutar el proceso del _path_ y retomarla para ejecutar otra función antes de enviar la respuesta.

## Bases de datos

### Relacionales
Inicialmente se describirá el flujo con SQLAlchemy, pero cabe destacar la existencia de [SQLModel](https://sqlmodel.tiangolo.com/), que es un ORM sobre `SQLAlchemy` y `Pydantic`

> Uno de los ORM utilizados por FastAPI es `SQLAlchemy`, sin embargo hay otros ORM como `SQLModel` o `Peewee`

### SQLAlchemy

Inicialmente hay que crear el _engine_ de sqlalchemy con el que se comunicará con la base de datos, así como un generador de `SessionLocal`, donde cada instancia es una sesión, i.e., _SessionLocal_ generará las sesiones de la aplicación, y por ultimo un modelo Base, el cual será el objeto del cual heredarán los modelos de la base de datos.

> Para este ejemplo, conectaremos con una base _SQLite_ para fines prácticos

#### Generando modelos
Todo modelo debe heredar del modelo `Base` que se define en las configuraciones de [database](/app/orm/database.py). En ese archivo también se incluye el generador de sesiones y la conexión a la base.

Para crear los modelos, se identifican las columnas, el tipo de datos que contendrán y las relaciones que hay entre ellas.

- Los **Pydantic Models** son representaciones de estos modelos, podría decirse que son los esquemas, y pueden  tener los mismos campos que el modelo en cuestión, sin embargo puedes tener más de un schema por tabla. 
- Estos modelos tienen una clase `Config` (algo así como `Meta` en Django) donde se define `orm_mode=True`, esto le indica al ORM que debe leerlo como objeto y no como diccionario. Esto es importante porque SQLAlchemy carga solo la información requerida en el momento, i.e., lazy loading, a menos que se le pidan los elementos relacionados con este objeto, este no los cargará.
- 

## Routing
A diferencia de *django*, no hay como tal una estructura de como se debe de organizar FastAPI, sin embargo la documentación recomienda una estructura como en el ejemplo 

```
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   └── routers
│   │   ├── __init__.py
│   │   ├── items.py
│   │   └── users.py
│   └── internal
│       ├── __init__.py
│       └── admin.py
```
Para este proyecto ejemplo se sigue algo similar.

### Definiendo rutas
Similar a como se haría en un mismo archivo, se definen con un decorador sobre la función a ejecutar, la diferencia es que ahora no se usa `@app` sino `@router` con un router previamente definido.

Para el ejemplo usaremos el [routers/items.py](app/routers/items.py). 
```
router = APIRouter(
    prefix='/items',
    responses={404: {'description': 'Not Found'}}
)


@router.post('/')
async def create_item(item: Item):
    return item
```
Donde se define el prefijo que tendrán todas las rutas de este path, también es posible denotar los tipos de responses que pueda tener (como un 404 en el ejemplo), tags y dependencias al igual que se haría con `@app`.

Y para poder ser utilizado en la aplicación, solo hace falta agregar en [app/main.py](app/main.py)
```
from .routers import items
app = FastAPI()
app.include_router(items.router)
```

Con esto se cubre lo básico de routing, si quieres saber más, la documentación está [aqui](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-the-same-router-multiple-times-with-different-prefix)

## Background Tasks
Se pueden definir tareas en segundo plano para ejecutarse una vez que se ha mandado la respuesta, lo cual es útil para notificaciones por e-mail, procesamiento de datos (carga de archivos grandes) entre otros.

Primero se debe importar `BackgroundTasks` de `fastapi` e incluirla como parámetro de las funciones, de esta manera _fastapi_ generará la instancia para ejecutar.

Una vez que se decida solicitar la función, simplemente hay mandarla llamar dentro de la path function donde hay que agregar la función a ejecutar y los argumentos que recibirá.
```
backgroud_instance.add_task(function, *args)
```
