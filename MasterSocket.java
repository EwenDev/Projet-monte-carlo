package assignments;

import java.io.*;
import java.net.*;

public class MasterSocket {
	static int maxServer = 16;
	static final int[] tab_port = {25545,25546,25547,25548,25549,25550,25551,25552,25553,25554,25555,25556,25557,25558,25559,25560};
	static BufferedReader[] reader = new BufferedReader[maxServer];
	static PrintWriter[] writer = new PrintWriter[maxServer];
	static Socket[] sockets = new Socket[maxServer];
	static final String ip = "127.0.0.1";

	public static void main(String[] args) throws Exception {
		if(args.length < 3){
			System.err.println("Usage: java assignments.MasterSocket <iterations> <numWorkers> <forte|faible>");
			return;
		}
		int iterations = Integer.parseInt(args[0]);
		int numWorkers = Integer.parseInt(args[1]);
		String scaling = args[2]; // "forte" ou "faible"

		int iterationsPerWorker;
		int totalIterations;
		if(scaling.equalsIgnoreCase("forte")){
			// En forte scalabilité, le total d’itérations reste constant.
			iterationsPerWorker = iterations / numWorkers;
			totalIterations = iterations;
		} else {
			// En faible scalabilité, chaque worker traite le même nombre d’itérations.
			iterationsPerWorker = iterations;
			totalIterations = iterations * numWorkers;
		}

		// Connexion aux workers
		for(int i = 0; i < numWorkers; i++) {
			sockets[i] = new Socket(ip, tab_port[i]);
			System.out.println("Connecté au worker sur le port " + tab_port[i]);
			reader[i] = new BufferedReader(new InputStreamReader(sockets[i].getInputStream()));
			writer[i] = new PrintWriter(new BufferedWriter(new OutputStreamWriter(sockets[i].getOutputStream())), true);
		}

		String message_to_send = String.valueOf(iterationsPerWorker);
		long startTime = System.currentTimeMillis();

		// Envoi de la demande à chaque worker
		for(int i = 0; i < numWorkers; i++){
			writer[i].println(message_to_send);
		}

		int totalInside = 0;
		// Récupération des résultats
		for(int i = 0; i < numWorkers; i++){
			String response = reader[i].readLine();
			System.out.println("Réponse du worker : " + response);
			totalInside += Integer.parseInt(response);
		}

		double pi = 4.0 * totalInside / totalIterations;
		long stopTime = System.currentTimeMillis();
		long duration = stopTime - startTime;
		double error = Math.abs(pi - Math.PI) / Math.PI;

		System.out.println("Valeur approchée de Pi : " + pi);
		System.out.println("Erreur relative : " + error);
		System.out.println("Itérations totales : " + totalIterations);
		System.out.println("Nombre de workers : " + numWorkers);
		System.out.println("Durée (ms) : " + duration);

		// Choix du fichier de sortie en fonction du mode
		String outFile;
		if(scaling.equalsIgnoreCase("forte")){
			outFile = "XP_socket_forte.txt";
		} else {
			outFile = "XP_socket_faible.txt";
		}

		// Écriture des résultats dans le fichier choisi
		FileWriter fw = new FileWriter(outFile, true);
		fw.write(totalIterations + ", " + error + ", " + numWorkers + ", " + duration + "\n");
		fw.close();

		// Fermeture des connexions et envoi du signal de fin aux workers
		for(int i = 0; i < numWorkers; i++){
			writer[i].println("END");
			reader[i].close();
			writer[i].close();
			sockets[i].close();
		}
	}
}
