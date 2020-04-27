# PicSlalomBack

#Tutoriel pour les développeurs back :

## Se créer un environnement de dev :

!Attention : le créer en dehors du git!


virtualenv env -p python3

. env/bin/activate

pip install django

pip install djangorestframework

!Attention bis : Pour dev il faudra activer l'environnement!

## Développer une feature :

Créer sa branche de developpement :

git checkout dev

git pull #uniquement si git vous indique que vous avez du retard


git checkout -b feature/#id dev

Vous vous retrouvez alors dans votre nouvelle branche. Ici vous pouvez faire les modifications de code nécessaires ainsi que les push/commit que vous souhaitez. A chaque push une pipeline est lancée donc pensez à aller vérifier sa sortie.
Lors de votre premier push vous aurez un message d'avertissement, vous demandant de rentrer la commande suivante :

git push --set-upstream origin feature/#id

Lancez cette commande, vous pourrez lancer un push normalement juste après.


Une fois que vous avez fini de développer votre fonctionnalité il faut aller sur gitea et faire une demande de pull request de votre branche feature/<id> into dev

