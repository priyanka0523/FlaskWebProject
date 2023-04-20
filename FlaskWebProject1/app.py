"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import pandas as pd
import pyodbc
from flask import Flask, redirect, url_for, render_template, flash, session, request
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
app.secret_key = "Data_Mining"

### DB Connections
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=LAPTOP-9B4F4L4E;'
                      'Database=DataMining_A1;'
                      'Trusted_Connection=yes;', autocommit = True)
cursor = conn.cursor()


### Home Page
@app.route('/')
def display_data():
    select_query = "select * from [DataMining_A1].[dbo].[MobileInfo];"
    out1 = cursor.execute(select_query)
    data_all = cursor.fetchall()
    out = pd.read_sql_query(select_query,conn)
    rank_in_df = int(out['Rank'].iloc[-1])
    session['rank_in_df'] = rank_in_df
    flash("Data Loaded Successfully")
    return render_template('data.html', out = data_all)

### New data entry Page
@app.route('/add')
def add():
    last_rank = session['rank_in_df']
    session['add_flag'] = "add"
    return render_template('add.html', last = last_rank)

### Adding / Updating / Deleting details Page
@app.route('/add_details', methods = ['GET','POST'])
def add_details():
    if request.method == 'POST':

        if session['add_flag'] == "delete":
            d_id = session['d_id']
            insert_query = "DELETE FROM [DataMining_A1].[dbo].[MobileInfo] WHERE Rank={0};".format(d_id)
            session.pop('add_flag', None)
            session.pop('d_id', None)
            #mes = "Deleted successfully"
        else:
            rank = request.form['rank']
            model = request.form['model']
            specs = request.form['specs']
            price = request.form['price']
            rating = request.form['rating']
            votes = request.form['votes']
        
            if session['add_flag'] == "add":
                insert_query = "insert into [DataMining_A1].[dbo].[MobileInfo] (Rank, Model, Specs, Price, Rating, Votes) values ({0},\'{1}\',\'{2}\',\'{3}\',\'{4}\',\'{5}\');".format(rank, model, specs, price, rating, votes)
                session.pop('add_flag', None)
            elif session['add_flag'] == "edit" :
                insert_query = "update [DataMining_A1].[dbo].[MobileInfo] set Model=\'{0}\', Specs=\'{1}\', Price=\'{2}\', Rating=\'{3}\', Votes=\'{4}\' where Rank={5};".format(model, specs, price, rating, votes, rank)
                session.pop('add_flag', None)
        
        cursor.execute(insert_query)
        return redirect(url_for('display_data'))

    else :
        return render_template('add.html')

### Update Selection Page
@app.route('/edit/<int:id>', methods = ['POST','GET'])
def edit_data(id):
    select_id = "select * from [DataMining_A1].[dbo].[MobileInfo] where Rank = '{0}';".format(id)
    e_out = pd.read_sql_query(select_id,conn)
    session['add_flag'] = "edit"
    return render_template('edit.html', out = [e_out.to_html(classes='data', header = True, index=False)], ran = id, mod=e_out.iloc[0]['Model'], spe=e_out.iloc[0]['Specs'], pri=e_out.iloc[0]['Price'], rat=e_out.iloc[0]['Rating'], vot=e_out.iloc[0]['Votes'])

### Delete Selection Page
@app.route('/delete/<int:id>', methods = ['POST','GET'])
def delete_data(id):
    del_id = "select * from [DataMining_A1].[dbo].[MobileInfo] where Rank = '{0}';".format(id)
    d_out = pd.read_sql_query(del_id,conn)
    session['add_flag'] = "delete"
    session['d_id'] = id
    return render_template('delete.html', out = [d_out.to_html(classes='data', header = True, index=False)])


if __name__ == '__main__':
    app.run(debug = True)
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
