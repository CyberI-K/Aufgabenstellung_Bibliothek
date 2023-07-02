from flask import Flask,request,render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_bibliothek'

mysql = MySQL(app)
############################### INDEX #############################
@app.route('/')
def index():
    return render_template('index.html')

##################################### USER #############################
@app.route('/user')
def user():
    cursor = mysql.connection.cursor()

    query = '''
             SELECT *
        FROM tbl_nutzer
        ORDER by tbl_nutzer.ID_Nutzer ASC


            '''

    cursor.execute(query)
    user = cursor.fetchall()


#### suche nach den aktuell ausgeborgten bücher
    sucheausleihbuch = '''
                    SELECT tbl_nutzer.ID_Nutzer,
	    tbl_nutzer.Vorname,
	    tbl_ausleihliste.*,
        tbl_buch.*
        FROM tbl_ausleihliste
        LEFT JOIN tbl_nutzer on tbl_nutzer.ID_Nutzer = tbl_ausleihliste.FID_Nutzer
        Left JOIN tbl_buch on tbl_buch.ID_Buch = tbl_ausleihliste.FID_Buch

        WHERE tbl_ausleihliste.bis IS NULL OR tbl_ausleihliste.bis = '0000-00-00'
        ORDER by tbl_nutzer.ID_Nutzer ASC
    
    '''

    cursor.execute(sucheausleihbuch)
    buecher = cursor.fetchall()

    for i in buecher:
        print(i)

## suche nach den schon zurück gebrachen bücher
    sqlsearch = '''
                    SELECT tbl_nutzer.ID_Nutzer,
	    tbl_nutzer.Vorname,
	    tbl_ausleihliste.*,
        tbl_buch.*
        FROM tbl_ausleihliste
        LEFT JOIN tbl_nutzer on tbl_nutzer.ID_Nutzer = tbl_ausleihliste.FID_Nutzer
        Left JOIN tbl_buch on tbl_buch.ID_Buch = tbl_ausleihliste.FID_Buch

		WHERE tbl_ausleihliste.bis IS NOT NULL AND tbl_ausleihliste.bis <> 0000-00-00
        
        ORDER BY `tbl_ausleihliste`.`bis` ASC
    
    '''

    cursor.execute(sqlsearch)
    retouren = cursor.fetchall()
    return render_template('user.html',user=user,buecher=buecher,retouren=retouren)

#################################### VERLEIH #################################################
@app.route('/verliehen',methods=['GET','POST'])
def verleih():
    cursor = mysql.connection.cursor()

    query = '''
                         SELECT tbl_nutzer.*,
	    tbl_ausleihliste.*,
        tbl_buch.*
        FROM tbl_ausleihliste
        LEFT JOIN tbl_nutzer on tbl_nutzer.ID_Nutzer = tbl_ausleihliste.FID_Nutzer
        Left JOIN tbl_buch on tbl_buch.ID_Buch = tbl_ausleihliste.FID_Buch

          

    
    
    '''
    if request.method == 'POST':
        if request.form['von'] and request.form['bis']:
            searchquery = request.form['von'],request.form['bis']
            query += f'''
                WHERE tbl_ausleihliste.von >=  '{searchquery[0]}' AND tbl_ausleihliste.bis <='{searchquery[1]}'
            '''
        elif request.form['von']:
            searchquery = request.form['von']
            query += f'''
                    WHERE tbl_ausleihliste.von >=  '{searchquery}'
            '''
        elif request.form['bis']:
            searchquery = request.form['bis']
            query += f'''
                WHERE tbl_ausleihliste.bis <=  '{searchquery}'
            '''



    cursor.execute(query)
    verliehen = cursor.fetchall()

    print(query)

    return render_template('verliehen.html', verliehen=verliehen)


############################## Alle Bücher ###########################
@app.route('/buecher', methods=['GET','POST'])
def buecher():
    cursor = mysql.connection.cursor()

    query = '''
                Select tbl_buch.*,
    		tbl_autoren.*,
            tbl_autorbuecher.*,
            tbl_verlag.Name

            FROM tbl_autorbuecher

            INNER JOIN tbl_buch on tbl_buch.ID_Buch = tbl_autorbuecher.FID_Buch
            INNER JOIN tbl_autoren on tbl_autoren.ID_Autoren = tbl_autorbuecher.FID_Autor
            LEFT JOIN tbl_verlag on tbl_verlag.ID_Verlag = tbl_buch.FID_Verlag


        '''
    if request.method == 'POST':
        if request.form['BT'] and request.form['ED']:
            search_query = request.form['BT'],request.form['ED']
            query += f'''
                 WHERE tbl_buch.Titel LIKE '%{search_query[0]}%' AND tbl_buch.Erscheinungsdatum LIKE '%{search_query[1]}%'
            ORDER BY tbl_buch.Titel ASC
            '''
        elif request.form['BT']:
            search_query = request.form['BT']
            query += f'''
                 WHERE tbl_buch.Titel LIKE '%{search_query}%' 
                ORDER BY tbl_buch.Titel ASC
                    '''
        elif request.form['ED']:
            search_query = request.form['ED']
            query += f'''
                             WHERE tbl_buch.Erscheinungsdatum LIKE '%{search_query}%' 
                            ORDER BY tbl_buch.Titel ASC
                                '''
        else:
            query += '''
            Order BY tbl_buch.ID_Buch ASC;
            '''
    print(query)

    cursor.execute(query)
    buchtiteln = cursor.fetchall()


    for i in buchtiteln:
        print(i)

    return render_template('buecher.html',buchtiteln=buchtiteln)




if __name__ == '__main__':
    app.run(debug=True)