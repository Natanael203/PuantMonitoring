#  Prérequis : 

Pour utiliser ce logiciel, il faut installer le logiciel : [Libre Hardware Monitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor?tab=readme-ov-file). 

Pour cela, suivre les étapes suivantes : 

1. Ouvrir une invite de commande windows (appuyer sur la touche windows, taper commande)*
2. Lancer la commande : 
```cmd
winget install LibreHardwareMonitor.LibreHardwareMonitor
```

3. Fermer le terminal,le logiciel est installé
# Installation  :  
Pour installer PuantMonitoring, il suffit de télecharger le fichier .zip [PuantMonitoring_X.X.X.zip](PuantMonitor_0.0.5.zip). 
Il faut ensuite unzip le fichier et lancer le .exe. 
# Utilisation 

Pour utiliser PuantMonitoring, il faut d'abord lancer le server web via LHM : 

1. Ouvrir un PowerShell en mode administrateur 
2. Taper la commande :
```
LibreHardwareMonitor.exe
```
3. Une fois le logiciel lancé, allez dans : Options > Remote Web Server. 
Verifiez que la case  "Run" est bien cochée
4. Le server est en route et publie les données sur l'adresse : [http://127.0.0.1:8085/](http://127.0.0.1:8085/)
5. Vous pouvez ensuite lancer PuantMonitoring
