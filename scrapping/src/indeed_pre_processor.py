import os
from orderedset import OrderedSet
from bs4 import BeautifulSoup
from indeed_mongodb_dao import IndeedMongodbDao
#from pymongo import MongoClient 
from pymongo import errors 
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import pandas as pd
from key_words_provider import KeyWordsProvider
import re
import traceback
import os
import numpy as np
#import normalize
class IndeedPreProcessor:
    def __init__(self):
        self.dao = IndeedMongodbDao() 
        self.pages_path = r'C:\Users\Junior\Documents\Projects_Simplon\Projet_ML_gr3-master\scrapping\pages'
        
        self.pre_processing_file_name = "indeed.pre_processing.csv"
        self.delete_file()#delete pre_processing file befor re-create it
        
        self.mongo_df = pd.read_csv("indeed_mongo.csv") 
        self.processing_df = pd.DataFrame()
        self.salary_pattern = "[[S|s]alaire?[\s+]?:?[\s+]?(.*)e?[\s+]?\/(an|mois)|((.*)?[\s+]?par?[\s+]?(an|ans|mois|jour|heure))"
        self.keyWordsProvider = KeyWordsProvider()
    
    def process(self):
        self.set_salary_man()
        print("salaire moyen enregistré")
        self.parse_education_level()
        print("niveau d'éducation enregistré")
        self.set_type_de_cursus()
        print("type de cursus enregistré")
        self.set_type_de_contrat()
        print("type de contrat enregistré")
        self.set_grande_categorie()
        print("grande catégorie enregistré")
        self.parse_langage()
        print("langage de programmation enregistré")
        self.parse_tools()
        print("outils enregistré")
    
    def _get_salary(self,select_result):
        salary = ""
        for item in select_result:
            if "€" in item.text:
                outer_salary = re.compile(self.salary_pattern)
                m_salary = outer_salary.search(item.text)
                if m_salary is not None:
                    salary = m_salary.group(0)
                    break
        return salary
    
    def delete_file(self):
        if os.path.exists(self.pre_processing_file_name):
            os.remove(self.pre_processing_file_name)

    def save_file(self):
        self.processing_df = pd.concat([self.mongo_df,self.processing_df], axis=1)
        self.processing_df.drop(self.processing_df.columns[0], axis=1,inplace=True)
        self.processing_df.to_csv(self.pre_processing_file_name,index=False)
        print("fichier sauvegardé")
    
    def _get_binnary_list_data(self, input_list):
        data = []
        for i in range(len(self.mongo_df)):
            inside_data = []
            for ele in input_list:
                try:
                    pattern = re.compile(r"[\s/\(\),]"+ele+r"[\s/\(\),]")
                    value = pattern.search(self.mongo_df['description'][i].lower().replace('\n',' ').replace('\r',' '))
                    if value:
                        inside_data.append(1)
                    else:
                        inside_data.append(0)
                except Exception as e:
                    print("*****pattern value :",ele)
                    print(traceback.format_exc())
                
                    
            data.append(inside_data)
        
        return data
    
    def _set_quantitative_features(self, pattern, col_indice,label_col,func_callback = None):
        result = []
        for index, row in self.mongo_df.iterrows():
            re_pattern = re.compile(pattern)
            value = re_pattern.search(row['description'].lower().replace('\n',' ').replace('\r',' '))
            if value:
                if func_callback is not None:
                    result.append(func_callback(value.group(0)))
                else:
                    result.append(value.group(0))
            else:
                result.append(None)
        
        if (label_col not in self.processing_df.columns):
            self.processing_df.insert(col_indice, label_col,result,True)
        else:
            self.processing_df[label_col] = pd.DataFrame(result)
        dummies = self.processing_df[label_col].str.get_dummies() 
        self._fusion_with_dataset(dummies)
        
    
    def parse_education_level(self):
        reg_pattern = "([(b|B)\w+]ac\s*\+\s*[1-8])|ingénieur|master\s*(1|2)|(D|d)iplôme\s*supérieur"
        self._set_quantitative_features(reg_pattern,1,"niveau_etude", self._education_level_callback)
    
    def _education_level_callback(self, value):
        bac_pattern = "bac\s*\+\s*[1-8]"
        result = re.compile(bac_pattern).search(value)
        response = ""
        if result:
            response = re.findall('(\d+)',value)
            if response is not None:
                return "bac + " + response[0] 
        
        master_pattern = "master\s*(1|2)"
        result = re.compile(master_pattern).search(value)
        if result:
            response = re.findall('(\d+)',value)
            if response is not None:
                return "master " + response[0] 
            
        return value
    
    def set_type_de_cursus(self):
        #j'ai desactivé le pattern "|([(m|M)\w+]aster?\s?\w{3,25})" master car ça renvoie "master dans" ou "master data"
        reg_pattern = '([(é|E)\w+]cole [(i|I)\w+]ngénieur?)|([(a|A)\w+]utodidacte?)|([(g|G)\w+]rande[s]? [(é|E)\w+]cole[s]?)|([(é|E)\w+]cole[s]? de [(c|C)\w+]ommerce[s]?)|([(i|I)\w+]ngénieur [(i|I)\w+]nformatique?)'
        self._set_quantitative_features(reg_pattern,2,"type_de_cursus", self._type_cursus_callback)
    
    def _type_cursus_callback(self, value):
        ge_pattern = "grandes?\s*(é|e)coles?"
        result = re.compile(ge_pattern).search(value)
        if result:
            return "grande école"
        
        ec_pattern = "([(é|E)\w+]cole[s]? de [(c|C)\w+]ommerce[s]?)"
        result = re.compile(ec_pattern).search(value)
        if result:
            return "école de commerce"
        
        return value
        
    def set_type_de_contrat(self):
        #j'ai desactivé le pattern "[(c|C)\w+]ontrat?:?\s\w{3,25}|"  car ça renovie "contrat logue", "contrat avec", etc
        reg_pattern = '(cdi|cdd|stage|alternance|alternant|cdic|freelance)|3\s*mois\s*renouvelable\s*'
        self._set_quantitative_features(reg_pattern,3,"type_de_contrat", self._type_de_contrat_callback)
    
    def _type_de_contrat_callback(self,value):
        bac_pattern = "alternance|alternant"
        result = re.compile(bac_pattern).search(value)
        if result:
            return "alternance"
        return value
    
    def set_grande_categorie(self):
        reg_pattern = 'développeur?\s*(web|mobile|data|front\s*end|back\s*end|desktop|full stack\s*(developer))'
        self._set_quantitative_features(reg_pattern,4,"grande_categorie",self._grande_categorie_callback)
        
    def _grande_categorie_callback(self, value):
        bac_pattern = "front\s*end|back\s*end"
        result = re.compile(bac_pattern).search(value)
        if result:
            if 'front' in value:
                return "front-end"
            else:
                return "back-end"
            
        return value
    
    def _fusion_with_dataset(self, df):
        diff_cols = list(OrderedSet(self.processing_df.columns) - OrderedSet(df.columns))
        self.processing_df = self.processing_df[diff_cols]
        self.processing_df = pd.concat([self.processing_df,df], axis=1)
    
    def parse_langage(self):
        languages = self.keyWordsProvider.get_langages()
        
        data = self._get_binnary_list_data(languages)
        
        language_dict = pd.DataFrame(data, columns=languages)
        self.language_df = pd.DataFrame.from_dict(language_dict)

        self._fusion_with_dataset(self.language_df)
    
    def parse_tools(self):
        tools = self.keyWordsProvider.get_tools()
        
        data = self._get_binnary_list_data(tools)
        tools_dict = pd.DataFrame(data, columns=tools)
        self.tools_df = pd.DataFrame.from_dict(tools_dict)
        self._fusion_with_dataset(self.tools_df)
    
    def set_salary_man(self):
        salaire_moyen = []
        for i in range(len(self.mongo_df)):
            try:
                #salaire_liste = re.findall('(\d+),?',normalize('NFKD',df['salaire'][i]).replace(' ',''))
                salaire_liste = []
                if (self.mongo_df['salaire'][i] != np.nan):
                    salaire_liste = re.findall('(\d+),?',self.mongo_df['salaire'][i].replace(' ',''))
                mois = re.search('mois',self.mongo_df['salaire'][i])
                if mois:
                    if len(salaire_liste) > 1:
                        moy = 12 * (int(salaire_liste[0]) + int(salaire_liste[1])) / 2
                        salaire_moyen.append(moy)
                    else:
                        salaire_moyen.append(int(salaire_liste[0]) * 12)
                else:
                    if len(salaire_liste) > 1:
                        moy = (int(salaire_liste[0]) + int(salaire_liste[1])) / 2
                        if moy < 100:
                            moy *= 1000
                        salaire_moyen.append(moy)
                    else:
                        if int(salaire_liste[0]) < 100:
                            salaire_moyen.append(int(salaire_liste[0]) * 1000)
                        else:
                            salaire_moyen.append(int(salaire_liste[0]))

            except Exception as e:
                salaire_moyen.append(None)
                continue
        
        label_col = "salaire_moyen"
        
        if (label_col not in self.processing_df.columns):
            self.processing_df.insert(0, label_col,salaire_moyen,True)
        else:
            self.processing_df[label_col] = pd.DataFrame(salaire_moyen)
            self.processing_df[label_col]
    
    