package Server;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Scanner;

/**
 * Client interactif qui va se connecter à la Gateway Documentaire (Spring Boot).
 * Basé sur l'architecture de référence ClientMeteo.
 */
public class ClientDocumentaire {
    
    private int port = 8080; // Port par défaut de la gateway document-api
    private HttpClient httpClient;

    public ClientDocumentaire(int p) {
        this.setPort(p);
        // Initialisation du client HTTP (remplace la gestion brute des Sockets)
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .build();
    }

    // Methode pour envoyer une requête HTTP au serveur
    public String envoyerRequete(String ip, String endpoint, String jsonBody) throws IOException, InterruptedException {
        String url = "http://" + ip + ":" + this.getPort() + endpoint;
        HttpRequest request;

        if (jsonBody != null) {
            request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                    .build();
        } else {
            request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .POST(HttpRequest.BodyPublishers.noBody())
                    .build();
        }

        HttpResponse<String> response = this.httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return "Statut HTTP : " + response.statusCode() + "\n" + response.body();
    }

    // Methode pour afficher sur la console le message recu du serveur
    public void afficherResultat(String msg) {
        System.out.println("============== Réponse du serveur ===============\n");
        System.out.println(msg); 
        System.out.println("=================================================\n");
    }

    // Methode pour demander à l'utilisateur de saisir l'adresse IP
    public String demanderSaisieIP(Scanner clavier) {
        System.out.print("Saisir l'adresse IP du serveur documentaire (ex: localhost) : ");
        return clavier.next();
    }

    // Methode pour afficher le menu et récupérer le choix
    public String demanderSaisieCommande(Scanner clavier) {
        System.out.println("\n--- MENU DES SCRIPTS CLIENT ---");
        System.out.println("1 - ingest_sample.sh");
        System.out.println("2 - fit_classification.sh");
        System.out.println("3 - evaluate_ocr.sh");
        System.out.println("4 - evaluate_classification.sh");
        System.out.println("5 - estimate_environment.sh");
        System.out.println("0 - Quitter");
        System.out.print("Votre choix : ");
        return clavier.next();
    }

    public static void main(String[] args) {
        // On cree un client qui va se connecter au serveur
        ClientDocumentaire client = new ClientDocumentaire(8080);
        Scanner clavier = new Scanner(System.in);
        
        String adresseDuServeur = client.demanderSaisieIP(clavier);
        
        boolean continuer = true;
        while (continuer) {
            String choix = client.demanderSaisieCommande(clavier);
            try {
                String resultat = "";
                switch (choix) {
                    case "1":
                        System.out.print("Chemin du fichier (ex: data/raw/doc1.pdf) : ");
                        String path = clavier.next();
                        resultat = client.envoyerRequete(adresseDuServeur, "/parse", "{\"file\": \"" + path + "\"}");
                        break;
                    case "2":
                        resultat = client.envoyerRequete(adresseDuServeur, "/fit", null);
                        break;
                    case "3":
                        resultat = client.envoyerRequete(adresseDuServeur, "/metrics/ocr", null);
                        break;
                    case "4":
                        resultat = client.envoyerRequete(adresseDuServeur, "/metrics/classification", null);
                        break;
                    case "5":
                        resultat = client.envoyerRequete(adresseDuServeur, "/metrics/environment", null);
                        break;
                    case "0":
                        continuer = false;
                        System.out.println("Fermeture du client.");
                        break;
                    default:
                        System.out.println("Choix invalide, veuillez réessayer.\n");
                }
                
                if (continuer && !resultat.isEmpty()) {
                    client.afficherResultat(resultat);
                }
            } catch (Exception e) {
                System.err.println("Erreur de communication avec le serveur : " + e.getMessage());
            }
        }
        
        clavier.close();
        System.exit(0);
    }

    public int getPort() {
        return port;
    }

    // Encapsulation avec vérification comme dans la référence
    public void setPort(int port) {
        if (port >= 8000 && port <= 9000) { // Intervalle de valeur autorisee pour le port
            this.port = port;
        } else {
            System.out.println("Valeur non autorisee: le port par défaut n'a pas ete modifie.\n");
        }
    }
}