import pandas as pd
from math import isnan
import time 
import numpy as np

df = pd.read_excel("PS_INFO.xlsx")

Form = df['Série diplôme']

def normalisation_bac(i,forme,epreuve):
    ns = []
    add = 0
    for e in range(len(df)):
        if Form[e] == forme:
            if isnan(df[epreuve][e]) == False:
                ns.append(df[epreuve][e])
    ecart_type = np.std(ns)
    moyenne = np.mean(ns)
    normalise = (df[epreuve][i]-moyenne)/ecart_type
    normaliser = (normalise*5)+10
    if normaliser > 20 :
        normaliser =20
    if normaliser < 0:
        normaliser = 0
    return normaliser
    print(normaliser)
    
matiere = ["Mathématiques","Langue vivante A","Langue vivante B","Français","Systemes d''information et numerique"]
trimestre = ["Trimestre 1","Trimestre 2","Trimestre 3"]

def normalisation_trimestre(df,i,matiere,trimestre):
    Moy=df["Moyenne classe en "+matiere+" "+trimestre][i]
    Min=df["Moyenne plus basse en "+matiere+" "+trimestre][i]
    Max=df["Moyenne plus haute en "+matiere+" "+trimestre][i]
    Can=df["Moyenne candidat en "+matiere+" "+trimestre][i]
    if(isnan(Can)) : 
        return None
    if(isnan(Moy) or isnan(Min) or isnan(Max)) :
        return None
    if(Max==Min) : 
        note = 0
    else : 
        note=(Can-Moy)/(Max-Min)
    return note
COEF_GENERO = pd.DataFrame(
    {
        'Mathématiques': [1,2,3,2,3,4,13,10], 
        'SCIENCES': [1,2,3,2,3,4,4,8], 
        "Systemes d''information et numerique": [1,1,1,2,2,2,6,9],  
        'Langue vivante A': [1,1,1,1,1,1,4,8], 
        'Langue vivante B': [1,1,1,1,1,1,4,8],
        'Français': [1,1,1,1,1,1,9,8]
    },
    index = ['P1', 'P2', 'P3', 'T1', 'T2', 'T3', 'COEF', 'PLANCHE']
)

def moyenne_mat(df,i,matiere):
    tri = ["Trimestre 1.1","Trimestre 2.1","Trimestre 3.1","Trimestre 1","Trimestre 2","Trimestre 3"]
    z = 0
    d = 0
    divis = 0
    for e in tri:
        mns = normalisation_trimestre(df,i,matiere,e)
        if mns != None:
            mnse = mns*COEF_GENERO[matiere][d]
            divis += COEF_GENERO[matiere][d]
            z += mnse
        d+=1
    if z != 0:
        res1 = z/divis
        return res1
    else:
        return 0
    
FR_Oral = df["Note à l'épreuve de Oral de Français (épreuve anticipée)"]
FR_Ecrit = df["Note à l'épreuve de Ecrit de Français (épreuve anticipée)"]

# Es-ce que le candidats à son Bac de Français ?
def BAC_FR(i):
    if (isnan(FR_Oral[i]) and isnan(FR_Ecrit[i])):
        return "NON"
    else :
        return "OUI"
def recupDBC(df,i):
    #Création de matière qui stock les notes du candidat
    matiere = pd.DataFrame()
    #Création d'une DataFrame pour le Candidats i
    DBC ={
        'Validation':0,
        'Num_Can':df['ID'][i],
        'SEXE':df['Sexe'][i], 
        'ANGLAIS':'?',
        'FILIERE':'?',
        'FORMATION':'?',
        'ANNE_BAC':'?',
        'Bourse': False, 
        'Nom_Eta' : df["Libellé établissement"][i], 
        'Com_Eta' : df["Commune établissement"][i], 
        'Depa_Eta' : df["Département établissement"][i]
    }
    
    
    #Récupération des informations:
    #Quelle est sa formations scolaire précédent sa candidatures
    Form = df['Série diplôme'][i]
    
    
    #Prise en compte des notes de BAC de Français
    FR_Oral = df["Note à l'épreuve de Oral de Français (épreuve anticipée)"][i]
    FR_Ecrit = df["Note à l'épreuve de Ecrit de Français (épreuve anticipée)"][i]   
    
    
    #Le Candidats est-il boursier ?
    if(df["Boursier"][i] in ["Boursier de l'enseignement supérieur", 'Boursier du secondaire']) : 
        DBC['Bourse'] = True # Mise à jour de sa situation de bourse
        
    #Es-ce que le candidats est en formation Générale ou Technologique ?
    if df["Groupe"][i] == 7415:
        DBC['FILIERE']='Générale'
    else : 
        DBC['FILIERE']='Technologique'
    #Année de Terminale/BAC
    DBC["ANNE_BAC"] = df["Année scolaire"][i]
        
    
    #On vas attrivuer des points:
    # -1 vaut une élémination
    #  0 sa candidatures sera prise en compte en manuel
    #  1 sa candidatures vas être 
    if(df['Candidature validée (O/N)'][i]=='NON') : 
        # Si non validé éléminé
        DBC['Validation']= -1    
        
    # On recherche les DAEU Mathématiques.
    # Dans un premier temps nous n'avons que les noms en DAEU
    elif Form == "DAEU" : 
        # On recherche plus précisemment les Daeu-b qui sont les DAEU MAthématiques
        if df["Spécialité diplôme bac Pro et anciens bacs"][i] == "Daeu-b" :
            # Dossier manuel
            DBC['Validation']=0
            DBC['Autre_Form']="Daeu-b"
            return DBC
        else:
            # Si DAEU-a, donc Littérature éléminé
            DBC['Validation']=-1
            
    # On recherche les anciens Bac ou Bac Internationale
    elif(Form in ["Bac général de plus de 15 ans","Baccalauréat International"]) : 
        #Bac en cours mais pas classique => dossier à étudier à la main
        DBC['Validation']=0
        DBC['Autre_Form']="AUTRES"
        return DBC
    
    # On cherche les Bac Scientifiques, qui ont validé leur Bac de français
    elif(BAC_FR(i)=="OUI" and Form=="Scientifique") : 
        DBC["Validation"]=1
        DBC['FORMATION'] = "Scientifique"
        #Mathématiques, les baccalauréat Scientifiques sont des "Anciens Baccalauréat", 
        #et ou on déjà passé leurs baccalauréat
        math = []
        math.append(normalisation_bac(i,"Scientifique","Note à l'épreuve de Mathématiques"))
        matiere['MATH']= math
        
        #Français
        fre = float(normalisation_bac(i,"Scientifique","Note à l'épreuve de Ecrit de Français (épreuve anticipée)"))
        fro = float(normalisation_bac(i,"Scientifique","Note à l'épreuve de Oral de Français (épreuve anticipée)"))
        frt = (fre+fro)/2
        matiere['FRANCAIS']= frt
        
        #Spécialité pour le baccalauréat Scientifique, les notes de Mathématiques Spé , sont incluse avec la note de Math
        # On ne vas rechercher que les notes d'ISN
        SPE=df["Note à l'épreuve de Informatique et Sciences du numérique"][i]
        nsi = normalisation_bac(i,"Scientifique","Note à l'épreuve de Informatique et Sciences du numérique")
        if isnan(SPE) == False  :
            matiere["NSI"]= nsi
            

        
        #Anglais
        LV1=df["LV1"][i]
        LV11=df["LV1.1"][i]
        LV12=df["LV1.2"][i]
        LV2=df["LV2"][i]
        LV21=df["LV2.1"][i]
        LV22=df["LV2.2"][i]
        Choix = ["Note à l'épreuve de Langue vivante 1","Note à l'épreuve de Langue vivante 2"]
        angl=None
        if((LV1=="Anglais" or LV11 =="Anglais") or LV12 =="Anglais"  ): 
            angl="Langue vivante 1"
            DBC["ANGLAIS"] = "LV1"
            agl = normalisation_bac(i,"Scientifique","Note à l'épreuve de Langue vivante 1")
            
        if((LV2=="Anglais" or LV21 =="Anglais") or LV22 =="Anglais"  ): 
            angl="Langue vivante 1"
            DBC["ANGLAIS"] = "LV2"
            agl = normalisation_bac(i,"Scientifique","Note à l'épreuve de Langue vivante 2")

        if(angl!=None) : 
            matiere['ANGLAIS']= agl 
            
    # Recherche des Bac ES
    elif(BAC_FR(i)=="OUI" and Form=="Economique et social" ): 
        DBC["Validation"]=1
        DBC['FORMATION'] = "Economique et social"
        #Mathématiques, les baccalauréat Scientifiques sont des "Anciens Baccalauréat", 
        #et ou on déjà passé leurs baccalauréat
        math = [] 
        math.append(normalisation_bac(i,"Economique et social","Note à l'épreuve de Mathématiques"))
        matiere['MATH']= math
        
        #Français
        fre = float(normalisation_bac(i,"Economique et social","Note à l'épreuve de Ecrit de Français (épreuve anticipée)"))
        fro = float(normalisation_bac(i,"Economique et social","Note à l'épreuve de Oral de Français (épreuve anticipée)"))
        frt = (fre+fro)/2
        matiere['FRANCAIS']= frt
        
        #SES
        ses = normalisation_bac(i,"Economique et social","Note à l'épreuve de Sciences économiques et sociales (SES)")
        matiere['SES']= ses
        
        #Spécialité pour le baccalauréat Scientifique, les notes de Mathématiques Spé , sont incluse avec la note de Math
        # On ne vas rechercher que les notes d'ISN
        SPE=df["Note à l'épreuve de Informatique et Sciences du numérique"][i]
        nsi = normalisation_bac(i,"Economique et social","Note à l'épreuve de Informatique et Sciences du numérique")
        if isnan(SPE) == False  :
            matiere["NSI"]= nsi
        
        #Anglais
        LV1=df["LV1"][i]
        LV11=df["LV1.1"][i]
        LV12=df["LV1.2"][i]
        LV2=df["LV2"][i]
        LV21=df["LV2.1"][i]
        LV22=df["LV2.2"][i]
        Choix = ["Note à l'épreuve de Langue vivante 1","Note à l'épreuve de Langue vivante 2"]
        angl=None
        if((LV1=="Anglais" or LV11 =="Anglais") or LV12 =="Anglais"  ): 
            angl="Langue vivante 1"
            DBC["ANGLAIS"] = "LV1"
            agl = normalisation_bac(i,"Economique et social","Note à l'épreuve de Langue vivante 1")
            
        if((LV2=="Anglais" or LV21 =="Anglais") or LV22 =="Anglais"  ): 
            angl="Langue vivante 2"
            DBC["ANGLAIS"] = "LV2"
            agl = normalisation_bac(i,"Economique et social","Note à l'épreuve de Langue vivante 2")

        if(angl!=None) : 
            matiere['ANGLAIS']= agl 
    # Recherche des candidats STI2D        
    elif(Form=="Sciences et Technologies de l'Industrie et du Développement Durable") : 
        
        DBC['Validation']=1
        DBC['FORMATION'] = "Sciences et Technologies de l'Industrie et du Développement Durable"
                
        #Math
        math = []
        math.append(moyenne_mat(df,i,"Mathématiques"))
        matiere['MATH']= math

        #Informatique
        nsi = moyenne_mat(df,i,"Systemes d''information et numerique")
        matiere['NSI']= nsi
        
        #Français
        fr = moyenne_mat(df,213,"Français")
        matiere['FRANCAIS']=  fr   

        #Anglais
        LV1=df["LV1"][i]
        LV2=df["LV2"][i]
        mat=None
        if(LV1=="Anglais") : 
            mat="Langue vivante A"
            DBC["ANGLAIS"] = "LV1"
        if(LV2=="Anglais") : 
            mat="Langue vivante B"
            DBC["ANGLAIS"] = "LV2"

        if(mat!=None) : 
            angl = moyenne_mat(df,i,mat)
            matiere['ANGLAIS']= angl
            
    #Recherche des candidats de Série Générale (nouveau bac)
    elif(Form=='Série Générale'): 
        
        DBC['Validation']=1
        DBC['FORMATION'] = "Série Générale"
        #Sciences
        if "Moyenne candidat en Enseignement scientifique Trimestre 1" in df.columns:
            matiere["NSI"] = moyenne_mat(df,i,"Enseignement scientifique")
        #Français
        fr = []
        fr.append(moyenne_mat(df,i,"Français"))
        matiere['FRANCAIS']= fr

        #Anglais
        LV1=df["LV1"][i]
        LV2=df["LV2"][i]
        mat=None
        if(LV1=="Anglais") : 
            mat="Langue vivante A"
            DBC["ANGLAIS"] = "LV1"
        if(LV2=="Anglais") : 
            mat="Langue vivante B"
            DBC["ANGLAIS"] = "LV2"

        if(mat!=None) : 
            angl = moyenne_mat(df,i,mat)
            matiere['ANGLAIS']= angl

        #Enseignements de spécialités
        mat1 = df["EDS BAC Terminale"][i]
        mat2 = df["EDS BAC Terminale.1"][i]
        if (mat1 == "Mathématiques Spécialité") or (mat2 == "Numérique et Sciences Informatiques"):
            if "Moyenne candidat en Mathématiques Spécialité Trimestre 1" in df.columns:
                matiere["MATH_SPE"] = moyenne_mat(df,i,"Mathématiques Spécialité")
            if "Moyenne candidat en Numérique et Sciences Informatiques Trimestre 1" in df.columns:
                matiere["NSI"] = moyenne_mat(df,i,"Numérique et Sciences Informatiques")
    #Si le candidats ne rentres dans aucune des conditions  
    else :
        DBC['Validation']=-1
        DBC['FORMATION'] = Form
        return [DBC , matiere]
    return [DBC , matiere]