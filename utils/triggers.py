"""This modules implements automatic triggering of tasks."""

from maintenancemanagement.models import Field, FieldGroup, FieldValue, Task

# Il faut qu'on récupère :
# On récupère les taches à null
# on vérifie les condition. Si l'une passe à True, l'état de la tache passe à false.
# # À faire à l'envers

# Récupération des taches à Null
# Déclenchement manuel : date et float : on vérifie avec Scheduler (date quotidiennement, float toutes les 5 minutes) si une est vraie on valide et on passe le statut à false

# Pour les déclenchements:
# Pour la date : on compare avec un today
# Pour le float : pour l'instant on moque pour les tests
