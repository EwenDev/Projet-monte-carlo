import numpy as np
import matplotlib.pyplot as plt
import subprocess
import statistics

DATA_REDUDENCY = 5
colors = ["blue", "red", "green", "orange", "purple", "brown", "pink", "black", "cyan", "magenta", "yellow"]

def generate_data_scal_forte(iterations, proc, classname, filename):
    """Exécute le programme Java plusieurs fois pour assurer des résultats cohérents (scalabilité forte)."""
    for p in range(1, proc+1):
        for _ in range(DATA_REDUDENCY):
            args = ["java", "-cp", "./", classname, str(int(iterations)), str(p), filename]
            print(args)
            subprocess.run(args)

def generate_data_scal_faible(iterations, proc, classname, filename):
    """Exécute le programme Java plusieurs fois pour assurer des résultats cohérents (scalabilité faible)."""
    for p in range(1, proc+1):
        for _ in range(DATA_REDUDENCY):
            args = ["java", "-cp", "./", classname, str(int(iterations * p)), str(p), filename]
            print(args)
            subprocess.run(args)

def lire_donnees(fichier):
    """
    Lit un fichier contenant les données d'exécution pour la scalabilité
    et calcule le speedup en se basant sur le temps d'exécution.
    Format attendu par ligne : totalPoints, error, numCores, time
    """
    data = []
    temps_premiere = 0
    time_buff = []

    with open(fichier, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith("#"):  # Ignorer lignes vides/commentaires
                parts = line.split(',')
                nb_processeurs = int(parts[2].strip())
                temps_execution = int(parts[3].strip())

                if len(time_buff) >= DATA_REDUDENCY:
                    if len(data) == 0:
                        # La première série de DATA_REDUDENCY mesures sert de référence (speedup = 1)
                        data.append([nb_processeurs, 1])
                        temps_premiere = statistics.median(time_buff)
                    else:
                        speedup = temps_premiere / statistics.median(time_buff)
                        data.append([nb_processeurs, speedup])
                    time_buff = []  # Réinitialisation du tampon
                else:
                    time_buff.append(temps_execution)

    return np.array(data)

def tracer_scalabilite(data_forte, data_faible):
    """Trace deux graphiques comparant la scalabilité forte et faible."""
    plt.figure(figsize=(12, 5))

    # ============ Graphique : Scalabilité Forte ============
    plt.subplot(1, 2, 1)
    x_expected = np.linspace(1, 16, 100)
    y_expected = x_expected  # Croissance linéaire idéale
    plt.plot(x_expected, y_expected, label="Speedup attendu", linestyle="-", color="gray")

    # Tracé de la scalabilité forte
    for i, (k, datafort) in enumerate(data_forte.items()):
        x_forte = datafort[:, 0]  # Nombre de cœurs
        y_forte = datafort[:, 1]  # Speedup
        plt.plot(x_forte, y_forte, label=f"{k} itérations", linestyle="-", marker='o', color=colors[0])

    plt.xlabel("Nombre de Processus")
    plt.ylabel("Speedup")
    plt.title("Scalabilité Forte")
    plt.legend()
    plt.grid()

    # ============ Graphique : Scalabilité Faible ============
    plt.subplot(1, 2, 2)
    x_expected_faible = np.linspace(1, 16, 100)
    y_expected_faible = np.ones_like(x_expected_faible)
    plt.plot(x_expected_faible, y_expected_faible, label="Speedup attendu", linestyle="-", color="gray")

    # Tracé de la scalabilité faible
    for i, (k, datafaible) in enumerate(data_faible.items()):
        x_faible = datafaible[:, 0]
        y_faible = datafaible[:, 1]
        plt.plot(x_faible, y_faible, label=f"{k} itérations", linestyle="-", marker='o', color=colors[1])

    plt.xlabel("Nombre de Processus")
    plt.ylabel("Speedup")
    plt.title("Scalabilité Faible")
    plt.legend()
    plt.grid()

    plt.show()

def lire_donnees_erreur(fichier):
    """
    Lit un fichier contenant les données (totalPoints, error, numCores, time).
    Retourne deux listes (ou tableaux) : nbPoints_list, error_list
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

def tracer_erreur(fichier, titre="Erreur en fonction du nombre de points"):
    """
    Lit les données depuis 'fichier', trace un nuage de points (points vs. erreur)
    et une ligne horizontale correspondant à la médiane de l'erreur.
    """
    nbPoints, erreur = lire_donnees_erreur(fichier)

    # Création de la figure
    plt.figure(figsize=(7, 5))
    plt.scatter(nbPoints, erreur, color='blue', label=f"Erreur pour {fichier}")

    # Calcul et affichage de la médiane
    median_err = np.median(erreur)
    plt.axhline(median_err, color='red', linestyle='--',
                label=f"Médiane de l'erreur: {median_err:.2e}")

    plt.title(titre)
    plt.xlabel("Nombre de points")
    plt.ylabel("Erreur")
    plt.grid(True)
    plt.legend()
    plt.show()

# Exécution du programme
#generate_data_scal_forte(100000, 16, "Pi", "out_pi_fort100000.txt")
#generate_data_scal_faible(100000, 16, "Pi", "out_pi_faible100000.txt")
#generate_data_scal_forte(12000000, 16, "Pi", "out_pi_fort12000000.txt")
#generate_data_scal_faible(12000000, 16, "Pi", "out_pi_faible12000000.txt")

#generate_data_scal_forte(100000, 16, "Assignment102", "out_ass_fort100000.txt")
#generate_data_scal_faible(100000, 16, "Assignment102", "out_ass_faible100000.txt")
#generate_data_scal_forte(12000000, 16, "Assignment102", "out_ass_fort12000000.txt")
#generate_data_scal_faible(12000000, 16, "Assignment102", "out_ass_faible12000000.txt")


#pifodata1 = lire_donnees("./out_pi_fort100000.txt")
pifodata2 = lire_donnees("./out_pi_fort12000000.txt")
pi_scale_forte = {
#    100000: pifodata1,
    12000000: pifodata2
}

#pifadata1 = lire_donnees("./out_pi_faible100000.txt")
pifadata2 = lire_donnees("./out_pi_faible12000000.txt")
pi_scale_faible = {
#    100000: pifadata1,
    12000000: pifadata2
}

#assfodata1 = lire_donnees("./out_ass_fort100000.txt")
assfodata2 = lire_donnees("./out_ass_fort12000000.txt")
ass_scale_forte = {
#    100000: assfodata1,
    12000000: assfodata2
}

#assfadata1 = lire_donnees("./out_ass_faible100000.txt")
assfadata2 = lire_donnees("./out_ass_faible12000000.txt")
ass_scale_faible = {
#    100000: assfadata1,
    12000000: assfadata2
}

tracer_scalabilite(pi_scale_forte, pi_scale_faible)
tracer_scalabilite(ass_scale_forte, ass_scale_faible)

tracer_erreur("out_pi_faible12000000.txt", titre="Erreur sur Pi.java")
tracer_erreur("out_ass_faible12000000.txt", titre="Erreur sur Assignment102")
