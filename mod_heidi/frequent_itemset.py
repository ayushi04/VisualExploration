import pandas as  pd
import pyfpgrowth
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from collections import Counter


class Frequent_itemset:

    def __init__(self):
        self.classDistribution = [] #order of class Label is same as the one in Heidi image
        self.subspaceHeidi_map = {}
        columns = []#['rp','cp']
        columns.append(list(subspaceHeidi_map.keys()))
        self.dataset=pd.DataFrame(columns=columns)
        self.transactions=[]
        '''
        e.g., transactions = [['a', 'b', 'c', 'd'],
              ['b', 'c', 'e', 'f'],
              ['a', 'd', 'e', 'f'],
              ['a', 'e', 'f'],
              ['b', 'd', 'f']
           ]
        '''
        self.setDiagonalBlocks_zero()
        self.set_dataset()

    def setDiagonalBlocks_zero(self):
        #TODO: write code here to set diagonal blocks to zero
        for subspace in self.subspaceHeidi_map:
            prev=0
            for curr in self.classDistribution:
                for i in range(prev,curr):
                    for j in range(prev,curr):
                        self.subspaceHeidi_map[subspace][i][j]=0
            prev=curr

    def set_dataset(self):
        default_val = [0 for i in list(subspaceHeidi_map.keys())]
        for subspace in self.subspaceHeidi_map:
            mat = subspaceHeidi_map[subspace]
            for i in range(0,mat.shape[0]):
                for j in range(0,mat.shape[1]):
                    if(mat[i][j]==1):
                        self.dataset.loc[(i,j),subspace]=1        
        return

    def get_dataset(self):
        return self.dataset

    def get_freq_itemsets(self):
        df = self.dataset.values.tolist()
        #te = TransactionEncoder()
        #te_ary = te.fit(transactions).transform(transactions)
        #df = pd.DataFrame(te_ary, columns=te.columns_)
        #print (df)

        #print(apriori(df, min_support = 0.0))

        frequent_itemsets = apriori(df, min_support=0.6, use_colnames=True)
        frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
        print ("frequent itemset at min support = 0.6")
        print(frequent_itemsets)