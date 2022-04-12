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

```
async def common_parrameters(q: Optional[str] = None, skip: int = 0, limit: int = 10):
    return {'q': q, 'skip': skip, 'limit': limit}

@app.get('/dependency/items/')
async def read_items(commons: dict = Depends(common_parrameters)):
    return commons

@app.get('/dependency/users/')
async def read_users(commons: dict = Depends(common_parrameters)):
    return commons
```

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
