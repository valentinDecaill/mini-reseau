#! /usr/bin/python
# -*- coding:utf-8 -*-
import pymysql.cursors
from flask import Flask, render_template, g, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

######################CONNECTION################################

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host="localhost",  # à modifier
            user="valou",  # à modifier
            password="1301",  # à modifier
            database="social",  # à modifier
            charset='utf8mb4',
            port=3307,
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

###########################################################

@app.route('/')
def show_layout():
    return render_template('layout.html')


###########################################################
##################inscription##############################
@app.route('/inscription', methods=['GET'])
def show_inscription():
    return render_template('inscription.html')


@app.route('/inscription/valider', methods=['POST'])
def valid_inscription():
    pseudo = request.form.get('pseudo')
    email = request.form.get('email')
    password = request.form.get('password')

    if not pseudo or not email or not password:
        flash('Tous les champs sont obligatoires.', 'danger')
        return redirect('/inscription')

    # Hachage
    mdp_hash = generate_password_hash(password)

    # curseur insertion BDD
    db = get_db()
    cursor = db.cursor()

    # On cherche s'il existe déja le pseudo ou l'email dans la BDD
    sql_verif = "SELECT * FROM utilisateur WHERE pseudo = %s OR email = %s"
    cursor.execute(sql_verif, (pseudo, email))
    utilisateur_existant = cursor.fetchone()

    if utilisateur_existant:
        flash('Ce pseudo ou cet email est déjà utilisé !', 'danger')
        return redirect('/inscription')

    # insertion BDD
    sql_insert = "INSERT INTO utilisateur (pseudo, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(sql_insert, (pseudo, email, mdp_hash))

    db.commit()

    flash('Inscription réussie ! Vous pouvez vous connecter.', 'success')
    return redirect('/connexion')


###########################################################
##################connexion################################
@app.route('/connexion', methods=['GET'])
def show_connexion():
    return render_template('connexion.html')

@app.route('/connexion/valider', methods=['POST'])
def valid_connexion():
    email = request.form.get('email')
    password = request.form.get('password')

    db = get_db()
    with db.cursor() as cursor:
        sql = "SELECT * FROM utilisateur WHERE email = %s"
        cursor.execute(sql, (email,))
        user = cursor.fetchone()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['pseudo'] = user['pseudo']
        session['email'] = user['email']
        flash('Connexion réussie !', 'success')
        return redirect('/')  # Redirection vers l'accueil
    else:
        flash('Identifiants incorrects.', 'danger')
        return redirect('/connexion')  # On renvoie vers le formulaire



#########################################################
##################deconnexion############################
@app.route('/logout')
def logout():
    session.pop('user_id', None) # Supprime l'id utilisateur de la session
    session.pop('pseudo', None)  # Supprime le pseudo de la session
    session.pop('email', None) # Supprime l'email de la session
    flash('Vous êtes déconnecté.', 'success')
    return redirect('/')

#########################################################
##################message################################




#########################################################
##################profil modification####################

@app.route('/profile', methods=['GET'])
def show_profil():
    return render_template('modifProfile/profile.html')

#########################################################
@app.route('/modif_pseudo', methods=['GET'])
def show_modif_pseudo():
    id_user = session['user_id']
    cursor = get_db().cursor()
    cursor.execute("SELECT pseudo FROM utilisateur WHERE id = %s", (id_user,))
    user = cursor.fetchone()
    pseudo = user['pseudo']
    cursor.close()
    return render_template('modifProfile/modif_pseudo.html', pseudo=pseudo)

@app.route('/modif_pseudo/valider', methods=['POST'])
def valid_modif_pseudo():
    id_user = session['user_id']
    cursor = get_db().cursor()






#########################################################


@app.route('/modif_email', methods=['GET'])
def show_modif_email():
    id_user = session['user_id']
    cursor = get_db().cursor()
    cursor.execute("SELECT email FROM utilisateur WHERE id = %s", (id_user,))
    user = cursor.fetchone()
    email = user['email']
    cursor.close()
    return render_template('modifProfile/modif_mail.html', email=email)



@app.route('/modif_email/valider', methods=['POST'])
def valid_modif_email():
    id_user = session['user_id']
    cursor = get_db().cursor()





#########################################################

@app.route('/modif_mdp', methods=['GET'])
def show_modif_mdp():
    return render_template('modifProfile/modif_mdp.html')


#########################################################

if __name__ == '__main__':
    app.run(debug=True)