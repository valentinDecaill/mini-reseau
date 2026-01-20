#! /usr/bin/python
# -*- coding:utf-8 -*-
import pymysql.cursors
from flask import Flask, render_template, g, request, redirect, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

######################CONNECTION BDD################################

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

################################################################

@app.route('/', methods=['GET'])
def show_layout():
    # Connexion BDD
    db = get_db()
    cursor = db.cursor()

    # Requête SQL avec jointure pour récupérer le pseudo de l'auteur du message
    sql = """
          SELECT message.contenu, message.date_envoi, utilisateur.pseudo
          FROM message
                   JOIN utilisateur ON message.user_id = utilisateur.id
          ORDER BY message.date_envoi DESC \
          """
    cursor.execute(sql)
    messages_recuperes = cursor.fetchall()
    cursor.close()

    return render_template('layout.html', messages=messages_recuperes)


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
        session['permission'] = user['permission_id']
        session['password_hash'] = user['password_hash']
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
    session.pop('password_hash', None)  # Supprime le mdp hasher
    session.pop('permission', 1) # Supprime les perm
    flash('Vous êtes déconnecté.', 'success')
    return redirect('/connexion')

#########################################################
##################message################################

@app.route('/envoyer_message', methods=['POST'])
def envoyer_message():
    # Vérification si l'utilisateur est connecté
    if 'user_id' not in session:
        flash("Vous devez être connecté pour parler !", "danger")
        return redirect('/connexion')

    # Récupération des données
    contenu = request.form.get('message')
    id_user = session['user_id']

    # 3. Vérification si le message est vide
    if not contenu or contenu.strip() == "":
        return redirect('/')  # On ne fait rien si c'est vide

    # Insertion dans la BDD
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO message (user_id, contenu) VALUES (%s, %s)", (id_user, contenu))
    db.commit()
    cursor.close()

    return redirect('/')  # On recharge la page d'accueil

#########################################################

@app.route('/api/messages')
def api_messages():
    # curseur insertion BDD
    db = get_db()
    cursor = db.cursor()

    # On récupère les messages dans la BDD
    sql = """
          SELECT message.contenu, message.date_envoi, utilisateur.pseudo
          FROM message
                   JOIN utilisateur ON message.user_id = utilisateur.id
          ORDER BY message.date_envoi DESC \
          """
    cursor.execute(sql)
    messages = cursor.fetchall()
    cursor.close()

    # On doit les convertir en texte pour éviter une erreur avec JS.
    for msg in messages:
        msg['date_envoi'] = msg['date_envoi'].strftime('%Y-%m-%d %H:%M:%S')

    # On renvoie la liste en format JSON pour JS
    return jsonify(messages)


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
    # Récupérer l'ID et du pseudo de l'utilisateur connecté
    id_user = session['user_id']
    pseudo = session['pseudo']

    # Récupérer le nouveau pseudo depuis la page web
    nouveau_pseudo = request.form.get('pseudo')

    # Connexion à la base
    db = get_db()
    cursor = db.cursor()

    # Vérifier si le pseudo n'est pas vide
    if not nouveau_pseudo:
        flash('Le pseudo ne peut pas être vide', 'danger')
        return redirect('/modif_pseudo')

    # Vérification si le nouveau pseudo est différents de l'ancien → modifier ou non le pseudo
    if nouveau_pseudo != pseudo:
        cursor.execute("update utilisateur set pseudo = %s where id = %s", (nouveau_pseudo, id_user))
        db.commit()
        session['pseudo'] = nouveau_pseudo
        flash('pseudo modifier avec succès', 'success')
        return redirect('/profile')
    else:
        flash('le pseudo est le meme que celui actuel', 'danger' )
        return redirect('/modif_pseudo')



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
    # Récupérer l'ID et de l'email de l'utilisateur connecté
    id_user = session['user_id']
    email = session['email']

    # Récupérer le nouvel email depuis la page web
    nouvel_email = request.form.get('email')

    # Connexion à la base
    db = get_db()
    cursor = db.cursor()

    # Vérifier si l'email n'est pas vide
    if not nouvel_email:
        flash('L\'email ne peut pas être vide', 'danger')
        return redirect('/modif_email')

    # Vérification si le nouvel email est différents de l'ancien → modifier ou non l'email
    if nouvel_email != email:
        cursor.execute("update utilisateur set email = %s where id = %s", (nouvel_email, id_user))
        db.commit()
        session['email'] = nouvel_email
        flash('L\'email est modifier avec succès', 'success')
        return redirect('/profile')
    else:
        flash('L\'email est le meme que celui actuel', 'danger')
        return redirect('/modif_email')





#########################################################

@app.route('/modif_mdp', methods=['GET'])
def show_modif_mdp():
    return render_template('modifProfile/modif_mdp.html')


@app.route('/modif_mdp/valider', methods=['POST'])
def valid_mdp_email():
    # Récupérer l'ID de l'utilisateur connecté
    id_user = session['user_id']
    mdp_hash = session['password_hash']

    # Récupérer les deux mdp entrer mdp1 + mdp2
    mdp1 = request.form.get('mdp1')
    mdp2 = request.form.get('mdp2')

    # Connexion à la base
    db = get_db()
    cursor = db.cursor()

    # Vérifier si le mdp n'est pas vide
    if not mdp1 or not mdp2:
        flash('Le mot de passe ne peut pas être vide', 'danger')
        return redirect('/modif_mdp')

    # Vérification si le nouveau mdp est différents de l'ancien → modifier ou non le mdp
    if mdp1 == mdp2:
        nouveau_mdp = generate_password_hash(mdp1)
        if nouveau_mdp != mdp_hash:
            cursor.execute("update utilisateur set password_hash = %s where id = %s", (nouveau_mdp, id_user))
            db.commit()
            session['password_hash'] = nouveau_mdp
            flash('Le mot de passe a été modifier avec succès ', 'success')
            return redirect('/profile')
        else:
            flash('Le mot de passe est le meme que celui actuel', 'danger')
            return redirect('/modif_mdp')
    else:
        flash('Les deux mots de passe sont différents', 'danger')
        return redirect('/modif_mdp')


#########################################################
################## Page Admin ############################

@app.route('/pageadmin', methods=['GET'])
def pageadmin():
    return render_template('pageadmin.html')


#########################################################

if __name__ == '__main__':
    app.run(debug=True)