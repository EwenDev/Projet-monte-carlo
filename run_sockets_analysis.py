import numpy as np
import matplotlib.pyplot as plt
import subprocess
import statistics
import time

DATA_REDUNDANCY = 5
colors = ["blue", "red", "green", "orange", "purple", "brown", "pink", "black", "cyan", "magenta", "yellow"]

# Liste des ports utilisés par les workers
WORKER_PORTS = [25545, 25546, 25547, 25548, 25549, 25550, 25551, 25552,
                25553, 25554, 25555, 25556, 25557, 25558, 25559, 25560]

def launch_workers_for(num_workers):
    """
    Lance num_workers instances de assignments.WorkerSocket.
    Chaque worker est lancé sur un port prédéfini.
    """
    workers = []
    for i in range(num_workers):
        port = WORKER_PORTS[i]
        cmd = ["java", "assignments.WorkerSocket", str(port)]
        print(f"Lancement du worker sur le port {port} : {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        workers.append(proc)
    time.sleep(1)
    return workers

def run_master_socket(iterations, p, mode):
    """
    Lance p workers, exécute assignments.MasterSocket avec les paramètres donnés,
    puis termine les workers.
    """
    workers = launch_workers_for(p)
    cmd = ["java", "assignments.MasterSocket", str(iterations), str(p), mode]
    print("Exécution :", cmd)
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for proc in workers:
        proc.kill()
    time.sleep(0.5)

def generate_data_scal_forte_socket(iterations, max_proc):
    """
    Scalabilité forte : le total d’itérations reste constant.
    Pour chaque valeur de p de 1 à max_proc, on exécute DATA_REDUNDANCY fois.
    """
    for p in range(1, max_proc+1):
        for _ in range(DATA_REDUNDANCY):
            run_master_socket(iterations, p, "forte")

def generate_data_scal_faible_socket(iterations, max_proc):
    """
    Scalabilité faible : chaque worker traite le même nombre d’itérations,
    le total augmente avec le nombre de workers.
    """
    for p in range(1, max_proc+1):
        for _ in range(DATA_REDUNDANCY):
            run_master_socket(iterations, p, "faible")

def lire_donnees(fichier):
    """
    Lit le fichier de sortie et extrait les données pour le calcul du speedup.
    Format par ligne : totalIterations, error, numWorkers, duration
    """
    data = []
    temps_premiere = None
    time_buff = []

    with open(fichier, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.split(',')
                nb_processeurs = int(parts[2].strip())
                temps_execution = int(parts[3].strip())

                time_buff.append(temps_execution)
                if len(time_buff) == DATA_REDUNDANCY:
                    if temps_premiere is None:
                        # Première série : référence pour le speedup
                        temps_premiere = statistics.median(time_buff)
                        data.append([nb_processeurs, 1])
                    else:
                        speedup = temps_premiere / statistics.median(time_buff)
                        data.append([nb_processeurs, speedup])
                    time_buff = []
        # Si on n'a pas un multiple exact de DATA_REDUNDANCY, gérer le reliquat
        if time_buff:
            if temps_premiere is None:
                temps_premiere = statistics.median(time_buff)
                data.append([nb_processeurs, 1])
            else:
                speedup = temps_premiere / statistics.median(time_buff)
                data.append([nb_processeurs, speedup])

    return np.array(data)

def tracer_scalabilite(data_forte, data_faible):
    """
    Affiche deux graphiques : scalabilité forte (à gauche) et faible (à droite).
    """
    plt.figure(figsize=(12, 5))

    # =================== Scalabilité Forte ===================
    plt.subplot(1, 2, 1)
    x_expected = np.linspace(1, 8, 100)
    y_expected = x_expected  # Speedup linéaire idéal
    plt.plot(x_expected, y_expected, label="Speedup attendu", linestyle="-", color="gray")

    data_forte = np.atleast_2d(data_forte)
    x_forte = data_forte[:, 0]
    y_forte = data_forte[:, 1]
    plt.plot(x_forte, y_forte, label="Scalabilité forte", linestyle="-", marker='o', color=colors[0])

    plt.xlabel("Nombre de workers")
    plt.ylabel("Speedup")
    plt.title("Scalabilité Forte")
    plt.legend()
    plt.grid()

    # =================== Scalabilité Faible ===================
    plt.subplot(1, 2, 2)
    x_expected_faible = np.linspace(1, 8, 100)
    y_expected_faible = np.ones_like(x_expected_faible)
    plt.plot(x_expected_faible, y_expected_faible, label="Speedup attendu", linestyle="-", color="gray")

    data_faible = np.atleast_2d(data_faible)
    x_faible = data_faible[:, 0]
    y_faible = data_faible[:, 1]
    plt.plot(x_faible, y_faible, label="Scalabilité faible", linestyle="-", marker='o', color=colors[1])

    plt.xlabel("Nombre de workers")
    plt.ylabel("Speedup")
    plt.title("Scalabilité Faible")
    plt.legend()
    plt.grid()

    plt.show()

def lire_donnees_erreur_socket(fichier):
    """
    Lit le fichier de sortie (XP_socket_forte.txt ou XP_socket_faible.txt)
    et renvoie deux tableaux : (nbPoints, erreur).
    Format attendu par ligne : totalIterations, error, numWorkers, duration
    """
    nbPoints_list = []
    error_list = []
    with open(fichier, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.split(',')
                total_points = int(parts[0].strip())
                erreur = float(parts[1].strip())
                nbPoints_list.append(total_points)
                error_list.append(erreur)
    return np.array(nbPoints_list), np.array(error_list)

def tracer_erreur_socket(fichier, titre="Erreur (Sockets) en fonction du nombre de points"):
    """
    Trace l'erreur en fonction du nombre total de points (colonne 0),
    avec une ligne horizontale pour la médiane de l'erreur.
    """
    nbPoints, erreur = lire_donnees_erreur_socket(fichier)

    plt.figure(figsize=(7, 5))
    plt.scatter(nbPoints, erreur, color='blue', label=f"Erreur pour {fichier}")

    # Calcul de la médiane
    median_err = np.median(erreur)
    plt.axhline(median_err, color='red', linestyle='--',
                label=f"Médiane de l'erreur: {median_err:.2e}")

    plt.title(titre)
    plt.xlabel("Nombre de points")
    plt.ylabel("Erreur")
    plt.grid(True)
    plt.legend()
    plt.show()

# --- Exécution des tests ---
iterations = 12_000_000
max_workers = 8

# Exécuter les tests pour la scalabilité forte et faible
#generate_data_scal_forte_socket(iterations, max_workers)
#generate_data_scal_faible_socket(iterations, max_workers)

# Lecture des résultats depuis les deux fichiers
data_forte = lire_donnees("XP_socket_forte.txt")
data_faible = lire_donnees("XP_socket_faible.txt")

tracer_scalabilite(data_forte, data_faible)
tracer_erreur_socket("XP_socket_faible.txt", titre="Erreur (Sockets)")
