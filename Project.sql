CREATE DATABASE IF NOT EXISTS social;
USE social;

-- ==========================================
-- TABLE 1 : PERMISSIONS
-- ==========================================
CREATE TABLE permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_role VARCHAR(50) NOT NULL UNIQUE
);

-- Insertion des rôles de base par défaut
INSERT INTO permission (nom_role) VALUES ('user'), ('admin');


-- ==========================================
-- TABLE 2 : UTILISATEUR
-- ==========================================
CREATE TABLE utilisateur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pseudo VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    biographie TEXT,
    avatar_url VARCHAR(255) DEFAULT 'default_avatar.jpg',
    permission_id INT DEFAULT 1, -- Par défaut user
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Lien vers la table permission
    FOREIGN KEY (permission_id) REFERENCES permission(id)
);


-- ==========================================
-- TABLE 3 : MESSAGE
-- Stocke le texte. Les images/gifs sont liés à ce message.
-- ==========================================
CREATE TABLE message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    contenu TEXT,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Si l'utilisateur est supprimé, ses messages aussi
    FOREIGN KEY (user_id) REFERENCES utilisateur(id) ON DELETE CASCADE
);


-- ==========================================
-- TABLE 4 : PHOTO
-- Pour les fichiers images uploadés par l'utilisateur
-- ==========================================
CREATE TABLE photo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id INT NOT NULL,
    chemin_fichier VARCHAR(255) NOT NULL,
    taille_ko INT,

    -- Lié au message. Si le message est supprimé, la photo aussi.
    FOREIGN KEY (message_id) REFERENCES message(id) ON DELETE CASCADE
);


-- ==========================================
-- TABLE 5 : GIF (Liens externes)
-- ==========================================
CREATE TABLE gif (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id INT NOT NULL,
    url_externe VARCHAR(512) NOT NULL, -- Lien vers le GIF sur internet
    provenance VARCHAR(50),

    FOREIGN KEY (message_id) REFERENCES message(id) ON DELETE CASCADE
);


-- ==========================================
-- TABLE 6 : Ban
-- ==========================================
CREATE TABLE ban (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pseudo VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    date_ban TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);