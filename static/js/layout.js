
// JAVASCRIPT FAIT AVEC IA CAR PAS ENCORE MAITRISER
// Fonction qui charge les messages
function chargerMessages() {
    fetch('/api/messages') // On appelle la route Python pour récupéré les messages
        .then(response => response.json()) // On convertit la réponse en données
        .then(data => {
            const zone = document.getElementById('zone-messages');
            zone.innerHTML = ''; // On vide la zone actuelle

            // On boucle sur chaque message reçu
            data.forEach(msg => {
                // On crée le HTML pour chaque message
                const html = `
                    <div class="card mb-2">
                        <div class="card-header d-flex justify-content-between">
                            <strong>${msg.pseudo}</strong>
                            <small class="text-muted">${msg.date_envoi}</small>
                        </div>
                        <div class="card-body">
                            <p class="card-text">${msg.contenu}</p>
                        </div>
                    </div>
                `;
                // On l'ajoute à la page
                zone.innerHTML += html;
            });
        })
        .catch(error => console.error('Erreur:', error));
}

// Lancement automatique
document.addEventListener('DOMContentLoaded', () => {
    chargerMessages(); // On lance une fois au chargement
    setInterval(chargerMessages, 1000); // On relance toutes les 2 secondes
});