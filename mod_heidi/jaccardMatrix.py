import numpy as np
import pandas as pd

def getJaccardMatrix(patterns_df):
    
    mat=np.zeros((patterns_df.shape[0],patterns_df.shape[0]))

    for i in range(0, patterns_df.shape[0]):
        for j in range(0, patterns_df.shape[0]):
            similarity_score,_,_,_ = jaccard(set(patterns_df.iloc[i,2] + patterns_df.iloc[i,3]),set(patterns_df.iloc[j,2] + patterns_df.iloc[j,3]))     
            if similarity_score >= 0.5:
                mat[i,j] =similarity_score

    mat=pd.DataFrame(mat,columns=list(patterns_df.loc[:,'subspace']),index=list(patterns_df.loc[:,'subspace']))
    return mat

def getJaccardMatrix2(patterns_df):
    
    mat=np.zeros((patterns_df.shape[0],patterns_df.shape[0]))
    for i in range(0, patterns_df.shape[0]):
        for j in range(0, patterns_df.shape[0]):
            similarity_score,_,_,_ = jaccard(set(patterns_df.iloc[i,4]),set(patterns_df.iloc[j,4]))     
            if similarity_score >= 0.3:
                mat[i,j] =similarity_score

    mat=pd.DataFrame(mat,columns=list(patterns_df.loc[:,'subspace']),index=list(patterns_df.loc[:,'subspace']))
    return mat

def jaccard(a, b):
    c = a.intersection(b)
    A=a
    B=b
    A_minus_B = list(A.difference(B))#A-B
    B_minus_A = list(B.difference(A))#B-A
    A_int_B = list(A.intersection(B))#A intersection B
    return float(len(c)) / (len(a) + len(b) - len(c)),A_minus_B,B_minus_A,A_int_B