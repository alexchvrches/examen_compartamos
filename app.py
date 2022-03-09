from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import psycopg2
from dateutil import tz
import datetime


app = Flask(__name__)
CORS(app, support_credentials=True)


# API para crear dispositivo
@app.route('/createDevice', methods=["POST"])
@cross_origin(supports_credentials=True)
def createDevice():
    print('createDevice')
    output = {}
    output["response"] = False

    if request.json is None:
        output["error"] = "No se envio body en la solicitud"
        return jsonify(output), 400
    else:
        content = request.json

    # ----------------------- Validaciones de informacion recibida
    print("Verificando JSON recibido")

    # Nombre del dispositivo
    if "nombre" in content:
        nombre = content["nombre"]
    else:
        output["nombre"] = "Este campo es obligatorio"
        return jsonify(output), 400

    # Tipo de dispositivo
    if "tipo_dispositivo" in content:
        tipo_dispositivo = content["tipo_dispositivo"]
    else:
        output["tipo_dispositivo"] = "Este campo es obligatorio"
        return jsonify(output), 400

    con = connectAidicare()
    if not con:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()

    try:
        print('Se registra el dispositivo en la BD')
        query = f"insert into dispositivo values (default, '{nombre}', {tipo_dispositivo}, '{nowWithTz()}', null, null, 1, false) returning id"
        print(query)
        cur.execute(query)
        idDispositivo = cur.fetchone()[0]
        print(f'Se registro el dispositivo con ID: {idDispositivo}')

        output['message'] = 'Se registro correctamente el dispositivo'
        output['response'] = True

    except Exception as e:
        print(e)
        print('Ocurrio un error al registrar la informacion del dispositivo')
        output["message"] = "Ocurrio un error al registrar la informacion del dispositivo"
        return jsonify(output), 500

    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


# API para obtener todos los dispositivos o filtrarlos por tipo
@app.route("/getDevices", methods=['GET'])
@cross_origin(supports_credentials=True)
def getDevices():
    print('getDevices')
    request_args = request.args
    output = {'response': False}

    con = connectAidicare()
    if not con:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()
    dispositivosArray = []

    try:
        if request_args and 'idtype' in request_args:
            idtype = request_args['idtype']
            query = f"select * from dispositivo where tipo_dispositivo = {idtype} order by nombre asc"
            print(query)
            cur.execute(query)
            dispositivos = cur.fetchall()
            if dispositivos is None or dispositivos == []:
                print('No se encontraron dispositivos con ese ID')
                con.commit()
                cur.close()
                con.close()
                output['devices'] = dispositivosArray
                output['message'] = 'No se encontraron dispositivos con ese ID'
                return jsonify(output), 202
    
            else:
                for disp in dispositivos:
                    idDispositivo = disp[0]
                    nombre = disp[1]
                    tipoId = disp[2]
                    query = f"select * from tipo_dispositivo where id = {tipoId}"
                    print(query)
                    cur.execute(query)
                    typeDevice = cur.fetchone()
                    if typeDevice is None:
                        tipoNombre = None
                    else:
                        tipoNombre = typeDevice[1]
                    fechaRegistro = disp[3].strftime('%Y-%m-%d %H:%M')
                    if disp[4] is not None:
                        fechaActualizacion = disp[4].strftime('%Y-%m-%d %H:%M')
                    else:
                        fechaActualizacion = None
                    potencialActual = disp[5]
                    statusId = disp[6]
                    if statusId is not None:
                        query = f"select * from status_dispositivo where id = {statusId}"
                        print(query)
                        cur.execute(query)
                        statusDevice = cur.fetchone()
                        if statusDevice is None:
                            statusNombre = None
                        else:
                            statusNombre = statusDevice[1]
                    else:
                        statusNombre = None
                    enconflicto = disp[7]
    
                    dispositivoJson = {
                        'id': idDispositivo,
                        'nombre': nombre,
                        'tipo_id': tipoId,
                        'tipo_nombre': tipoNombre,
                        'fecha_registro': fechaRegistro,
                        'fecha_actualizacion': fechaActualizacion,
                        'potencial_actual': potencialActual,
                        'status_id': statusId,
                        'status_ nombre': statusNombre,
                        'en_conflicto': enconflicto
                    }
                    dispositivosArray.append(dispositivoJson)
                else:
                    output['devices'] = dispositivosArray
                    output['response'] = True
                    output['message'] = f'Se obtuvieron los dispositivos del tipo {idtype}'
    
        else:
            query = f"select * from dispositivo order by nombre asc"
            print(query)
            cur.execute(query)
            dispositivos = cur.fetchall()
            if dispositivos is None or dispositivos == []:
                print('No se encontraron dispositivos registrados')
                con.commit()
                cur.close()
                con.close()
                output['devices'] = dispositivosArray
                output['message'] = 'No se encontraron dispositivos registrados'
                return jsonify(output), 202
    
            else:
                for disp in dispositivos:
                    idDispositivo = disp[0]
                    nombre = disp[1]
                    tipoId = disp[2]
                    query = f"select * from tipo_dispositivo where id = {tipoId}"
                    print(query)
                    cur.execute(query)
                    typeDevice = cur.fetchone()
                    if typeDevice is None:
                        tipoNombre = None
                    else:
                        tipoNombre = typeDevice[1]
                    fechaRegistro = disp[3].strftime('%Y-%m-%d %H:%M')
                    if disp[4] is not None:
                        fechaActualizacion = disp[4].strftime('%Y-%m-%d %H:%M')
                    else:
                        fechaActualizacion = None
                    potencialActual = disp[5]
                    statusId = disp[6]
                    if statusId is not None:
                        query = f"select * from status_dispositivo where id = {statusId}"
                        print(query)
                        cur.execute(query)
                        statusDevice = cur.fetchone()
                        if statusDevice is None:
                            statusNombre = None
                        else:
                            statusNombre = statusDevice[1]
                    else:
                        statusNombre = None
                    enconflicto = disp[7]
    
                    dispositivoJson = {
                        'id': idDispositivo,
                        'nombre': nombre,
                        'tipo_id': tipoId,
                        'tipo_nombre': tipoNombre,
                        'fecha_registro': fechaRegistro,
                        'fecha_actualizacion': fechaActualizacion,
                        'potencial_actual': potencialActual,
                        'status_id': statusId,
                        'status_ nombre': statusNombre,
                        'en_conflicto': enconflicto
                    }
                    dispositivosArray.append(dispositivoJson)
                else:
                    output['devices'] = dispositivosArray
                    output['response'] = True
                    output['message'] = f'Se obtuvieron todos los dispositivos'

    except Exception as e:
        print(e)
        print('Ocurrio un error al obtener la informacion de los dispositivos')
        output["message"] = "Ocurrio un error al obtener la informacion de los dispositivos"
        return jsonify(output), 500

    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


# Obtener informacion de UN SOLO dispositivo a partir del ID del dispositivo
@app.route("/getDevice/<idDevice>", methods=['GET'])
@cross_origin(supports_credentials=True)
def getDevice(idDevice):
    print('getDevice')
    output = {'response': False}

    con = connectAidicare()
    if not con:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()

    try:
        query = f"select * from dispositivo where id = {idDevice}"
        print(query)
        cur.execute(query)
        dispositivo = cur.fetchone()
        if dispositivo is None or dispositivo == []:
            print('No se encontro el dispositivo especificado')
            con.commit()
            cur.close()
            con.close()
            output['device'] = dict()
            output['message'] = 'No se encontro el dispositivo especificado'
            return jsonify(output), 202
    
        else:
            idDispositivo = dispositivo[0]
            nombre = dispositivo[1]
            tipoId = dispositivo[2]
            query = f"select * from tipo_dispositivo where id = {tipoId}"
            print(query)
            cur.execute(query)
            typeDevice = cur.fetchone()
            if typeDevice is None:
                tipoNombre = None
            else:
                tipoNombre = typeDevice[1]
            fechaRegistro = dispositivo[3].strftime('%Y-%m-%d %H:%M')
            if dispositivo[4] is not None:
                fechaActualizacion = dispositivo[4].strftime('%Y-%m-%d %H:%M')
            else:
                fechaActualizacion = None
            potencialActual = dispositivo[5]
            statusId = dispositivo[6]
            if statusId is not None:
                query = f"select * from status_dispositivo where id = {statusId}"
                print(query)
                cur.execute(query)
                statusDevice = cur.fetchone()
                if statusDevice is None:
                    statusNombre = None
                else:
                    statusNombre = statusDevice[1]
            else:
                statusNombre = None
            enconflicto = dispositivo[7]
    
            dispositivoJson = {
                'id': idDispositivo,
                'nombre': nombre,
                'tipo_id': tipoId,
                'tipo_nombre': tipoNombre,
                'fecha_registro': fechaRegistro,
                'fecha_actualizacion': fechaActualizacion,
                'potencial_actual': potencialActual,
                'status_id': statusId,
                'status_ nombre': statusNombre,
                'en_conflicto': enconflicto
            }
            output['device'] = dispositivoJson
            output['response'] = True
            output['message'] = f'Se obtuvo la informacion del dispositivo'

    except Exception as e:
        print(e)
        print('Ocurrio un error al obtener la informacion del dispositivo')
        output["message"] = "Ocurrio un error al obtener la informacion del dispositivo"
        return jsonify(output), 500

    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


@app.route('/createReading', methods=["POST"])
@cross_origin(supports_credentials=True)
def createReading():
    print('createReading')
    output = {}
    output["response"] = False

    if request.json is None:
        output["error"] = "No se envio body en la solicitud"
        return jsonify(output), 400
    else:
        content = request.json

    # ----------------------- Validaciones de informacion recibida
    print("Verificando JSON recibido")

    # ID del dispositivo
    if "iddispositivo" in content:
        iddispositivo = content["iddispositivo"]
    else:
        output["iddispositivo"] = "Este campo es obligatorio"
        return jsonify(output), 400

    # Potencia actual del dispositivo
    if "potencia" in content:
        potencia = content["potencia"]
    else:
        output["potencia"] = "Este campo es obligatorio"
        return jsonify(output), 400

    con = connectAidicare()
    if not con:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()

    try:
        print('Se verifica que el dispositivo proporcionado exista y este operativo')
        query = f"select * from dispositivo where id = {iddispositivo}"
        print(query)
        cur.execute(query)
        dispositivo = cur.fetchone()
        if dispositivo is None:
            output["message"] = "El dispositivo proporcionado no existe"
            return jsonify(output), 202
        else:
            tipo_dispositivo = dispositivo[2]
            statusId = dispositivo[6]
            if statusId == 1:
                print('El dispositivo esta en operacion')
            else:
                print('El dispositivo proporcionado esta en mantenimiento, registrar intento')
                print('Se verifica que no se haya alcanzado el numero maximo de intentos de lectura')
                query = f"select * from conteo_intentos_lectura where iddispositivo = {iddispositivo}"
                print(query)
                cur.execute(query)
                intentos = cur.fetchone()
                if intentos is None:
                    print('El dispositivo nunca ha tenido intentos fallidos de lectura, registrar el primer intento')
                    query = f"insert into conteo_intentos_lectura values ({iddispositivo}, 1)"
                    print(query)
                    cur.execute(query)

                else:
                    numIntentos = intentos[1]
                    print(f'El dispositivo ha tenido {numIntentos} intentos fallidos de lectura')
                    if numIntentos >= 5:
                        print('El dispositivo han llegado al numero maximo de intentos, marcar en conflicto')
                        query = f"update dispositivo set enconflicto = true where id = {iddispositivo}"
                        print(query)
                        cur.execute(query)
                        con.commit()
                        cur.close()
                        con.close()
                        output["message"] = "El dispositivo proporcionado esta en mantenimiento, se ha marcado como En conflicto"
                        return jsonify(output), 202
                    else:
                        print('Aun no se alcanza el numero maximo de intentos, sumar uno mas')
                        query = f"update conteo_intentos_lectura set total = (total + 1) where iddispositivo = {iddispositivo}"
                        print(query)
                        cur.execute(query)

                con.commit()
                cur.close()
                con.close()
                output["message"] = "El dispositivo proporcionado esta en mantenimiento"
                return jsonify(output), 202

    except Exception as e:
        print(e)
        print('Ocurrio un error al validar el dispositivo')
        output["message"] = "Ocurrio un error al validar el dispositivo"
        return jsonify(output), 500

    try:
        print('Se registra la lectura en la BD')
        query = f"insert into lectura values (default, {iddispositivo}, {tipo_dispositivo}, {potencia}, '{nowWithTz()}') returning id"
        print(query)
        cur.execute(query)
        idLectura = cur.fetchone()[0]
        print(f'Se registro la lectura con ID: {idLectura}')

        print('Se actualiza la potencia actual de la tabla Dispositivo')
        query = f"update dispositivo set potencia_actual = {potencia}, fecha_actualizacion = '{nowWithTz()}' where id = {iddispositivo}"
        print(query)
        cur.execute(query)

        output['message'] = 'Se registro correctamente la lectura'
        output['response'] = True

    except Exception as e:
        print(e)
        print('Ocurrio un error al registrar la lectura del dispositivo')
        output["message"] = "Ocurrio un error al registrar la lectura del dispositivo"
        return jsonify(output), 500

    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


# API para obtener todas las lecturas registradas o filtrarlos por ID o tipo de dispositivo
@app.route("/getReadings", methods=['GET'])
@cross_origin(supports_credentials=True)
def getReadings():
    print('getReadings')
    request_args = request.args
    output = {'response': False}

    con = connectAidicare()
    if not con:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()
    lecturasArray = []

    try:
        if request_args and 'idtype' in request_args:
            idtype = request_args['idtype']
            query = f"select * from lectura where idtipodispositivo = {idtype} order by fecha_registro desc"
            print(query)
            cur.execute(query)
            lecturas = cur.fetchall()
            if lecturas is None or lecturas == []:
                print('No se encontraron lecturas registradas del tipo de dispositivo proporcionado')
                con.commit()
                cur.close()
                con.close()
                output['readings'] = lecturasArray
                output['message'] = 'No se encontraron lecturas registradas del tipo de dispositivo proporcionado'
                return jsonify(output), 202

            else:
                for disp in lecturas:
                    idLectura = disp[0]
                    iddispositivo = disp[1]
                    query = f"select * from dispositivo where id = {iddispositivo}"
                    print(query)
                    cur.execute(query)
                    infoDevice = cur.fetchone()
                    if infoDevice is None:
                        dispNombre = None
                    else:
                        dispNombre = infoDevice[1]
                    tipoId = disp[2]
                    potencialActual = disp[3]
                    fechaRegistro = disp[4].strftime('%Y-%m-%d %H:%M')
                    query = f"select * from tipo_dispositivo where id = {tipoId}"
                    print(query)
                    cur.execute(query)
                    typeDevice = cur.fetchone()
                    if typeDevice is None:
                        tipoNombre = None
                    else:
                        tipoNombre = typeDevice[1]

                    lecturaJson = {
                        'id': idLectura,
                        'iddispositivo': iddispositivo,
                        'nombre_dispositivo': dispNombre,
                        'tipo_id': tipoId,
                        'tipo_nombre': tipoNombre,
                        'potencia': potencialActual,
                        'fecha_registro': fechaRegistro
                    }
                    lecturasArray.append(lecturaJson)
                else:
                    output['readings'] = lecturasArray
                    output['response'] = True
                    output['message'] = f'Se obtuvieron las lecturas del tipo de dispositivo proporcionado'

        elif request_args and 'iddevice' in request_args:
            iddevice = request_args['iddevice']
            query = f"select * from lectura where iddispositivo = {iddevice} order by fecha_registro desc"
            print(query)
            cur.execute(query)
            lecturas = cur.fetchall()
            if lecturas is None or lecturas == []:
                print('No se encontraron lecturas registradas del dispositivo proporcionado')
                con.commit()
                cur.close()
                con.close()
                output['readings'] = lecturasArray
                output['message'] = 'No se encontraron lecturas registradas del dispositivo proporcionado'
                return jsonify(output), 202

            else:
                for disp in lecturas:
                    idLectura = disp[0]
                    iddispositivo = disp[1]
                    query = f"select * from dispositivo where id = {iddispositivo}"
                    print(query)
                    cur.execute(query)
                    infoDevice = cur.fetchone()
                    if infoDevice is None:
                        dispNombre = None
                    else:
                        dispNombre = infoDevice[1]
                    tipoId = disp[2]
                    potencialActual = disp[3]
                    fechaRegistro = disp[4].strftime('%Y-%m-%d %H:%M')
                    query = f"select * from tipo_dispositivo where id = {tipoId}"
                    print(query)
                    cur.execute(query)
                    typeDevice = cur.fetchone()
                    if typeDevice is None:
                        tipoNombre = None
                    else:
                        tipoNombre = typeDevice[1]

                    lecturaJson = {
                        'id': idLectura,
                        'iddispositivo': iddispositivo,
                        'nombre_dispositivo': dispNombre,
                        'tipo_id': tipoId,
                        'tipo_nombre': tipoNombre,
                        'potencia': potencialActual,
                        'fecha_registro': fechaRegistro
                    }
                    lecturasArray.append(lecturaJson)
                else:
                    output['readings'] = lecturasArray
                    output['response'] = True
                    output['message'] = f'Se obtuvieron las lecturas del dispositivo'

        else:
            query = f"select * from lectura order by fecha_registro desc"
            print(query)
            cur.execute(query)
            lecturas = cur.fetchall()
            if lecturas is None or lecturas == []:
                print('No se encontraron lecturas registradas')
                con.commit()
                cur.close()
                con.close()
                output['readings'] = lecturasArray
                output['message'] = 'No se encontraron lecturas registradas'
                return jsonify(output), 202

            else:
                for disp in lecturas:
                    idLectura = disp[0]
                    iddispositivo = disp[1]
                    query = f"select * from dispositivo where id = {iddispositivo}"
                    print(query)
                    cur.execute(query)
                    infoDevice = cur.fetchone()
                    if infoDevice is None:
                        dispNombre = None
                    else:
                        dispNombre = infoDevice[1]
                    tipoId = disp[2]
                    potencialActual = disp[3]
                    fechaRegistro = disp[4].strftime('%Y-%m-%d %H:%M')
                    query = f"select * from tipo_dispositivo where id = {tipoId}"
                    print(query)
                    cur.execute(query)
                    typeDevice = cur.fetchone()
                    if typeDevice is None:
                        tipoNombre = None
                    else:
                        tipoNombre = typeDevice[1]

                    lecturaJson = {
                        'id': idLectura,
                        'iddispositivo': iddispositivo,
                        'nombre_dispositivo': dispNombre,
                        'tipo_id': tipoId,
                        'tipo_nombre': tipoNombre,
                        'potencia': potencialActual,
                        'fecha_registro': fechaRegistro
                    }
                    lecturasArray.append(lecturaJson)
                else:
                    output['readings'] = lecturasArray
                    output['response'] = True
                    output['message'] = f'Se obtuvieron todas las lecturas'

    except Exception as e:
        print(e)
        print('Ocurrio un error al obtener la informacion de las lecturas')
        output["message"] = "Ocurrio un error al obtener la informacion de las lecturas"
        return jsonify(output), 500

    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


# API para obtener la energia total de un dispositivo
@app.route("/getTotal/<iddevice>", methods=['GET'])
@cross_origin(supports_credentials=True)
def getTotal(iddevice):
    print('getTotal')
    request_args = request.args
    output = {'response': False}

    con = connectAidicare()
    if not con:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()

    try:
        print('Se obtienen las lecturas del dispositivo proporcionado')
        query = f"select * from lectura where iddispositivo = {iddevice} order by fecha_registro asc"
        print(query)
        cur.execute(query)
        lecturas = cur.fetchall()
        if lecturas is None or lecturas == []:
            print('No se encontraron lecturas del dispositivo registradas')
            con.commit()
            cur.close()
            con.close()
            output['message'] = 'No se encontraron lecturas del dispositivo registradas'
            return jsonify(output), 202

        else:
            total = 0
            for disp in lecturas:
                potencialActual = disp[3]
                total += potencialActual
            else:
                if len(lecturas) > 1:
                    primerRegistro = lecturas[0][4].strftime('%Y-%m-%d %H:%M')
                    ultimoRegistro = lecturas[-1][4].strftime('%Y-%m-%d %H:%M')
                else:
                    primerRegistro = lecturas[0][4].strftime('%Y-%m-%d %H:%M')
                    ultimoRegistro = lecturas[0][4].strftime('%Y-%m-%d %H:%M')

                output['primer_lectura'] = primerRegistro
                output['ultima_lectura'] = ultimoRegistro
                output['total'] = f'{total} Kw/h'
                output['response'] = True
                output['message'] = f'Se obtuvo el total de las lecturas'

    except Exception as e:
        print(e)
        print('Ocurrio un error al obtener la informacion de las lecturas')
        output["message"] = "Ocurrio un error al obtener la informacion de las lecturas"
        return jsonify(output), 500

    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


def nowWithTz():
    utc_dt = datetime.datetime.now()
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Mexico_City')
    utc = utc_dt.replace(tzinfo=from_zone)
    mexTime = utc.astimezone(to_zone)
    return mexTime.strftime('%Y-%m-%d %H:%M')


def connectAidicare():
    user = 'postgres'
    password = 'Lauren10110love'
    dbname = 'compartamos'
    host = 'compartamos-dev.cpmaxwoqxvbu.us-east-1.rds.amazonaws.com'

    try:
        action = f"dbname='{dbname}' user='{user}'host='{host}' password='{password}'"
        conn = psycopg2.connect(action)
        return conn

    except Exception as e:
        print(str(e))
        exit()
        return None


if __name__ == '__main__':
    app.run()