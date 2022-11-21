import time
from django.shortcuts import render, get_object_or_404, redirect
from .models import Animal, Equipement
from .forms import MoveForm
from django.contrib import messages


def animalerie_list(request):
    animaux = Animal.objects.all()
    equipements = Equipement.objects.all()
    # a_la_roue = Animal.objects.filter(lieu =="roue")
    return render(request, 'animalerie/animalerie_list.html', {'animaux':animaux, 'equipements':equipements})



def animal_detail(request, id_animal):
    animal = get_object_or_404(Animal, id_animal=id_animal)
    lieu = animal.lieu #lieu actuel de l'animal
    etat = animal.etat #état actuel de l'animal
    message = '' #message d'alerte
    form=MoveForm()
    if request.method == "POST":
        form = MoveForm(request.POST, instance=animal)
        if form.is_valid():
            form.save(commit = False)
            nouveau_lieu = get_object_or_404(Equipement, id_equip=animal.lieu.id_equip)
            if nouveau_lieu.disponibilite == "libre" or nouveau_lieu.id_equip == "litière":
                if etat == "repus" and nouveau_lieu.id_equip == "roue":
                    possible = True #booléen qui est True si le déplacement respecte les contraintes, False sinon
                    nouvel_etat = "fatigué"
                elif etat == "fatigué" and nouveau_lieu.id_equip == "nid":
                    possible = True
                    nouvel_etat = "endormi"
                elif etat == "affamé" and nouveau_lieu.id_equip == "mangeoire":
                    possible = True
                    nouvel_etat = "repus"
                elif etat == "endormi" and nouveau_lieu.id_equip == "litière":
                    possible = True
                    nouvel_etat = "affamé"
                else :
                    possible = False  #si l'état de l'animal n'est pas en accord avec son déplacement
                    message = animal.id_animal + " est " + animal.etat + " il n'a pas envie d'aller dans le/la " + nouveau_lieu.id_equip           
            else:
                possible = False  #si le nouveau lieu est déjà occupé 
                message = "Le lieu choisi est déjà occupé !"
            if possible :
                lieu.disponibilite = "libre"   #correspond à l'ancien lieu
                animal.etat = nouvel_etat
                animal.save()
                lieu.save()
                form.save()
                if nouveau_lieu.id_equip == "litière":
                    nouveau_lieu.disponibilite = "libre"
                else:
                    nouveau_lieu.disponibilite = "occupée"
                nouveau_lieu.save()
                #renvoie le message d'alerte vide => rien ne sera affiché
                message = animal.id_animal + " s'est déplacé(e). Nouveau lieu occupé : " + nouveau_lieu.id_equip
                messages.success(request, message)
                return redirect('animalerie_list')
            else:
                #afficher un message d'alerte !
                messages.error(request, message)
                return render(request,
                    'animalerie/animal_detail.html',
                    {'animal': animal, 'lieu': lieu, 'form': form})
            
    else:
        form = MoveForm()
        return render(request,
                    'animalerie/animal_detail.html',
                    {'animal': animal, 'lieu': lieu, 'form': form})
