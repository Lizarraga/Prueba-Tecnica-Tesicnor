"""
PRUEBA TÉCNICA DE PROGRAMACIÓN - Tesicnor

**Autor: Pablo Lizarraga Cia
**Fecha: 21/09/2021
"""

## Consideraciones previas:
# Es necesario tener instalado el paquete mysql-connector para interconectar Python y MySQL
# pip install mysql-connector

# Librerias.
import requests  # Modulo para realizar peticiones a la API
import mysql.connector  # Modulo para conectarnos con MySQL
import random


def main():
    # Parametros necesarios para la peticion a la API.
    apikey = "731e41f"  # Clave de acceso a la API
    titulo = "Harry+Potter"  # Titulo de la(s) pelicula(s) a buscar. (Los espacios se reemplazan por '+')

    parameters = {
        "apikey": apikey,
        "s": titulo
    }

    # Parametros necesarios para la conexion con la BD.
    host = "localhost"
    user = "root"
    passwd = ""
    n_database = "db1"  # Nombre de la BD

    """
    Para realizar la peticion GET usaremos el metodo request.get(), al cual hay que pasarle dos argumentos:
        - Url de la API
        - Parametros de la peticion
    Nos devuelve un objeto respuesta.
    """
    response = requests.get(url="http://www.omdbapi.com/?", params=parameters)

    """
    Si la peticion GET se ha realizado correctamente el 'status_code' de la respuesta sera un entero
    entre 200-299, normalmente 200. (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
    
    Por otro lado si la peticion es correcta pero no se encuentra(n) la(s) pelicula(s) solicitadas, o si por el contrario,
    la busqueda no puede devolver tantos resultados, el objeto respuesta tendra un campo llamado 'Error'. Sera necesario
    filtrarlo para continuar con la ejecucion. 
    """
    if (200 <= response.status_code <= 299) and ('Error' not in response.json()):

        # Creamos la conexion con la base de datos pasandole la ubicacion del servidor y las credenciales de acceso.
        try:
            conn = mysql.connector.connect(host=host, user=user, passwd=passwd, database=n_database)
            cursor = conn.cursor()
        except:
            print("Error al conectarse con la BD.")
            return

        """
        El metodo json() nos devuelve el JSON de la informacion solicitada. Python lo interprenta como un Diccionario.
        Este diccionario contiene tres claves, el contenido que nos interesa se encuentra en la seccion 'Search', por
        lo que descartamos las restantes y almacenamos la informacion en una variable.
        """
        info_peliculas = response.json()['Search']

        # Sentencia SQL para insertar la informacion necesaria de las peliculas en la BD.
        query = "INSERT INTO peliculas(ID_IMDB, TITULO, AÑO, VAL_PERSONAL) VALUES(%s,%s,%s,%s)"

        """
        Por cada pelicula recibida, filtramos los campos que nos interesan y descartamos el resto.
        """
        for i in range(len(info_peliculas)):
            # Para la valoracion personal, simplemente se genera un entero aleatorio entre el 1 y el 5 a modo de ejemplo.
            val_personal = random.randint(1, 5)

            # Los valores a insertar se estructuran a modo de Tupla.
            fila = (info_peliculas[i]['imdbID'], info_peliculas[i]['Title'], info_peliculas[i]['Year'], val_personal)

            """
            La configuración de la BD local impide que haya dos filas distintas con el mismo id_IMDB.
            El campo id_IMDB de la BD tiene clave unica. Por lo que saltare un error de integridad en el caso de volver
            a insertar la misma pelicula.
            De esta forma evitamos insertar datos duplicados.
            """
            try:
                # Ejecutamos la query con los datos de la pelicula i.
                cursor.execute(query, fila)
                conn.commit()
            except mysql.connector.errors.IntegrityError:
                # En caso de que la pelicula ya se encuentre en la BD, se indica y se continua con la ejecucion.
                print("La pelicula '" + info_peliculas[i]['Title'] + "' ya se encuentra en la BD.")
            except:
                print("Error al ejecutar la sentencia SQL.")
                break

        # Cerramos la conexion con el servidor de MySQL y el cursor
        conn.close()
        cursor.close()

    elif 'Error' in response.json():
        print("Error al recibir informacion desde la API: " + response.json()['Error'])
    else:
        print("Error al recibir la informacion desde la API.")


if __name__ == '__main__':
    main()
