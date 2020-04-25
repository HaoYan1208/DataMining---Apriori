#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math


# get csv file's header and values in list 
def getHeaderValues(f):
    f_header = (f.split('\n')[0]).split(',')
    f_lines = (f.split('\n')[1:])
    f_values = []
    for line in f_lines:
        f_values.append(list(line.split(",")))
    
    return f_header,f_values

# get min_sup or min_conf
def getMinSupConf(isSup=True):
    res = ""
    while True:
      try:
         if isSup:
             res = float(input("\nPlease enter a fraction value for min_sup:"))
         else:
             res = float(input("\nPlease enter a fraction value for min_conf:"))
         if res<=0 or res>=1:
            print("Not a fraction value!")
            continue
      except ValueError:
         print("Not a fraction value!")
         continue
      else:
         break 
    return res


# generating a Dictionary of Header and Values 
def generateHeaderValuesDict(f_header, f_values):
    res = dict()
    # adding header as key in order
    for header in f_header:
        res[header] = []
    # adding values as value (list)
    for values in f_values:
        for i, key in enumerate(res):
            if values[i] not in res[key]:
                res[key].append(values[i])
    return res


# output formart
def output(rules,min_sup_fraction, min_conf, fw, w=False):
    # construct obj1, obj
    def returnHeaderWithValue(l,header_value_dict):
        res = str()

        for val in l:
            # find header name
            header = str()
            for k,v in header_value_dict.items():
                if val in v:
                    header = k
                    break
            res+= header+'='+val+', '
        return res[:-2]
    
    # printRules(i, obj1, obj2, sup, conf):
    def printRules(i, obj1, obj2, sup, conf):
        # example
        #printRules(1,'Humidity','normal','PlayTennis','P',0.43,0.86)
        #printRules(2,'PlayTennis','P','Humidity','normal',0.43,0.67)
        if w:
            print('Rule#{}: {{{}}} => {{{}}}'.format(i,obj1, obj2),file=fw)
            print('(Support={:.2f}, Confidence={:.2f})\n'.format(sup,conf),file=fw)  
            
        print('Rule#{}: {{{}}} => {{{}}}'.format(i,obj1, obj2))
        print('(Support={:.2f}, Confidence={:.2f})\n'.format(sup,conf))   
        
    # output
    if w:
        print('1. User Input:',file=fw)
        print('Support = {:.2f}'.format(min_sup_fraction),file=fw)
        print('Confidence = {:.2f}'.format(min_conf),file=fw)
        print('\n2. Rules:\n',file=fw)
        
    print('1. User Input:')
    print('Support = {:.2f}'.format(min_sup_fraction))
    print('Confidence = {:.2f}'.format(min_conf))
    print('\n2. Rules:\n')
    for i,rule in enumerate(rules) :
        # rule[0] ==> obj1 list
        obj1 = returnHeaderWithValue(rule[0],header_value_dict)
        # rule[1] ==> obj2 list
        obj2 = returnHeaderWithValue(rule[1],header_value_dict)
        
        # rule[2] ==> sup
        # rule[3] ==> conf
        
        printRules(i+1, obj1, obj2, rule[2], rule[3])
        
    


# In[2]:


# read data from CSV file
csv_file = "Play_Tennis_Data_Set.csv"
f_obj = open(csv_file, encoding='utf-8-sig')

f = f_obj.read()

# data processing
f_header,f_values = getHeaderValues(f)
num_tuples = len(f_values)


# In[3]:


# get min_sup, min_conf
min_sup_fraction = getMinSupConf()
min_conf = getMinSupConf(isSup=False)
# calculate the min_sup
min_sup = math.ceil(min_sup_fraction*num_tuples) 


# In[4]:


# fuctions: important steps in Aprior Algorithm

# getCK actually generates a combination
def combination(lst,n):
    if n==0:
        return [[]]
    l=[]
    for i in range(0,len(lst)):
        m=lst[i]
        remLst=lst[i+1:]
        for p in combination(remLst,n-1):
            l.append([m]+p)
    return l
    
# reverse = False: frozenset to list
# reverse = True:  list to frozenset
def frozensetToList(l,reverse = False):
  if reverse:
    return list((map(frozenset, l)))
  res = []
  for val in l:
    res.append(list(val))
  res.sort()
  return res 
    
    
# C1 Creation 
def getC1(data):
    """
    Accroding to inputting dataset, create C1
    """
    temp = list()
    # search every item, which is not in C1 list 
    for trans in data:
        for item in trans:
            # find unique item
            if [item] not in temp:
                temp.append([item])
    # Since list can not be key in dictionary, 
    # using fromzenset here for building dictionary later
    return list(map(frozenset, temp))

# C_k Creation(k>1)
def getCK(L_k_1,k):
    """
    L_k_1: L(k-1)
    k: the number of itemsets
    e.g.: inputting: L1,2 ==> get C2
          inputting: L2,3 ==> get C3
    """
    
    # return unique item in a list from itemsets
    def getUnique(itemsets):
      res = []
      for itemset in itemsets:
        for item in itemset:
          if item not in res:
            res.append(item)
      res.sort()
      return res


    
    # get unique items for combination
    unique_item_list = getUnique(L_k_1)
    # get C_k without prune
    C_k_list = combination(unique_item_list,k)
    
    # return C_k without prune
    return frozensetToList(C_k_list,reverse=True)
    
    
# L_k Creation based on C_k
def getLK(data, C_k, min_sup):
    item_sup = dict()

    for trans in data:
        for itemset in C_k:
            if itemset not in item_sup:
                item_sup[itemset] = 0
            if set(list(itemset)).issubset(set(trans)):
                item_sup[itemset] += 1
    # delete item lsit           
    delete = [k for k,v in item_sup.items() if v < min_sup] 
  
    # delete the key 
    for k in delete: del item_sup[k] 

    freq_item = [k for k,v in item_sup.items()]
    
    item_relative_sup = {k:v/len(data) for k,v in item_sup.items()}

    return freq_item, item_sup, item_relative_sup


# In[5]:


# main function: Apriori Algorithm

# get C1
C1 = getC1(f_values)

# get L1, support count of all itemsets and the corresponding relative support 
L1,sup_count, relative_support = getLK(f_values, C1, min_sup)

# frequent_item initialization
frequent_item = [L1]

# 

# looping from k = 2
k = 2

while (len(frequent_item[k-2])>0):
    C_k = getCK(frequent_item[k-2],k)
    if len(C_k) == 0:
        break
    L_k, L_k_sup_count, L_k_relative_support = getLK(f_values, C_k, min_sup)
    sup_count.update(L_k_sup_count)
    relative_support.update(L_k_relative_support)
    frequent_item.append(L_k)
    k+=1

    

# get three important variables:
# 1. frequent_item: list of itemsets
# 2. sup_count: dictionary{itemsets: count}
# 3. relative_support: dictionary{itemsets: count/num_trans}
print('frequent_item:\n',)
for i in frequent_item:
    for j in i:
        print(j)
print('-----------------\n')
print('item_sup:\n')
for k,v in sup_count.items():
    print("{} : {}".format(k,v))
print('-----------------\n')
print('relative_sup:\n',)
for k,v in relative_support.items():
    print("{} : {}".format(k,v))


# In[6]:


# generating association rules Area

# construct a proper data structure for generating association rules
def transferFreqItemToListOfFrozenset(frequent_item):
    """
    parameter: frequent_item: (dict) get from main function: Apriori Algorithm
    return: itemset_frozenset: data structure for generating association rules
    """
    res = []
    # starting from itemsets, which its size is > 1
    # since there is no association rules if itemsets only have one element
    for i in range(1,len(frequent_item)):
        for j in frequent_item[i]:
            itemset_frozenset = []
            for item in j:
                itemset_frozenset.append(frozenset([item]))
            res.append(itemset_frozenset)
    return res

# construct a proper data structure for generating association rules
def frozensetToListAssociationRules(itemset_frozenset):
    """
    parameter: itemset_frozenset: (list[frozenset]) get transferFreqItemToListOfFrozenset(frequent_item)
    return: res: list with string not frozenset => ['a','b','c'...]
    """
    res = []
    for item in itemset_frozenset:
        res.append(list(item)[0])
    return res


# list x - list y
# operation of List x minus List y
def listMinusList(x,y):
  return [item for item in x if item not in y]


def getConf(obj_value1,l,relative_support):
    """
    parameters:
        list obj_value1, l(total)
        dict: relative_support
    return: confidence
    """
      # conf = support_count/relative[A U B]/ support_count/relative[A]
    return relative_support[frozenset(l)]/relative_support[frozenset(obj_value1)]


# generating association rules
def generatingAssociationRules(itemset_frozenset,min_conf,rules):
    """ 
    parameter: 
        itemset_frozenset ↓↓↓
        [frozenset({'a'}), frozenset({'b'}), frozenset({'c'}),.....]
        e.g.[frozenset({'normal'}), frozenset({'P'}), frozenset({'FALSE'})]
        
        min_conf: minimum confidence
        
    return list of [obj_val1, obj_val2, sup, conf (relevant sup and conf)]
    """
    

    # [a,b,c,d,....]
    l = frozensetToListAssociationRules(itemset_frozenset)
    sup = relative_support[frozenset(l)]
    print('\nSupport: ',sup,': For',l,)
    # find obj_val1, obj_val2
    # C(n,1), C(n,2), C(n,3) .....  C(n,n-1)
    for i in range(1,len(l)):
      # obj_val1 
      obj_val1_list = combination(l,i)
      # obj_val2: [l(total) - obj_val1]
      for obj_val1 in obj_val1_list:
        obj_val2 = listMinusList(l,obj_val1)
        conf = getConf(obj_val1,l,relative_support)
        if conf >=min_conf:
            print('Confidence: ',obj_val1,' ---> ',obj_val2,' : ',conf)
            rules.append([obj_val1,obj_val2,sup,conf])

            
# store rules         
rules = []

# generating a Dictionary of Header and Values 
header_value_dict = generateHeaderValuesDict(f_header, f_values)

# get itemsets
itemsets_frozenset = transferFreqItemToListOfFrozenset(frequent_item)

print('Support =',min_sup_fraction)
print('Confidence =',min_conf)
print('\nAssociation Rules:\n')
# generating association rules
for itemset_frozenset in itemsets_frozenset:
    generatingAssociationRules(itemset_frozenset,min_conf,rules)


# In[7]:


# print results
fw = open("Rules.txt", 'w+')

print('---- Final Results ----\n')
output(rules,min_sup_fraction, min_conf, fw, w=True)

fw.close()

print("Results are written in Rules.txt")


# ### Reference
# 
# 
# Piush.vaish. (2019, January 1). Apriori Algorithm (Python 3.0). Retrieved from https://adataanalyst.com/machine-learning/apriori-algorithm-python-3-0/
# 
# 
# Combinations without using "itertools.combinations". (1963, October 1). Retrieved from https://stackoverflow.com/questions/20764926/combinations-without-using-itertools-combinations
# 
# 
# Machine learning (10) Apriori algorithm for association analysis. (n.d.). Retrieved from https://blog.csdn.net/yangshaojun1992/article/details/105018781

# In[ ]:




