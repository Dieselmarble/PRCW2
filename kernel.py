# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:38:17 2018

@author: zl6415
"""
import metric_learn
import numpy as np
import matplotlib
import matplotlib.image as mpimg # read images
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from knn_naive import kNN
from ranklist import Rank
import time
import sys
import json
from sklearn import decomposition
import metric_learn
from sklearn.decomposition import KernelPCA
from sklearn.kernel_approximation import RBFSampler

# 1467 identities in total
num_identies = 1467
num_validation = 100  
rnd = np.random.RandomState(100)
#
camId = loadmat('PR_data/cuhk03_new_protocol_config_labeled.mat')['camId'].flatten()
filelist = loadmat('PR_data/cuhk03_new_protocol_config_labeled.mat')['filelist'].flatten()
labels = loadmat('PR_data/cuhk03_new_protocol_config_labeled.mat')['labels'].flatten()
train_idx = loadmat('PR_data/cuhk03_new_protocol_config_labeled.mat')['train_idx'].flatten()
#only for testing the design
gallery_idx = loadmat('PR_data/cuhk03_new_protocol_config_labeled.mat')['gallery_idx'].flatten()
query_idx = loadmat('PR_data/cuhk03_new_protocol_config_labeled.mat')['query_idx'].flatten()
with open('PR_data/feature_data.json', 'r') as f:
    features = json.load(f)
features = np.asarray(features) 

def plotimg(filename):
    imgplot = mpimg.imread('PR_data/images_cuhk03/%s' %filename)
    #lena.shape #(512, 512, 3)
    plt.imshow(imgplot)
    
# find distinct identities in training set (should be 767 refer to the protocol)
train_label = labels[train_idx-1]
iden_train = np.unique(labels[train_idx-1])

# use 100 randomly selected identities from training set as validation set
valid_iden = rnd.choice(iden_train, num_validation,replace=False)
valid_index = []
for i in range (num_validation):
    valid_index.append(np.argwhere(train_label == valid_iden[i]))

valid_index = np.concatenate(valid_index, axis=0)
valid_idx = train_idx[valid_index].ravel()
valid_label = labels[valid_idx-1]
train_idx_new = np.delete(train_idx, valid_index)
train_label_new = labels[train_idx_new-1]
features_train = features[train_idx_new-1]
features_valid = features[valid_idx-1]
features_query = features[query_idx-1]
features_gallery = features[gallery_idx-1]
label_query = labels[query_idx-1]
label_gallery = labels[gallery_idx-1]
camId_train = camId[train_idx_new-1]
camId_valid = camId[valid_idx-1]
camId_query = camId[query_idx-1]
camId_gallery = camId[gallery_idx-1]
iden_query = np.unique(label_query)
iden_gallery = np.unique(label_gallery)

print('start!')
pca = decomposition.PCA(n_components=30)
pca.fit(features_train)
pca1 = decomposition.PCA(n_components=30)
pca1.fit(features_valid)
pca2 = decomposition.PCA(n_components=30)
pca2.fit(features_gallery)

features_train_pca = pca.transform(features_train)
features_valid_pca = pca1.transform(features_valid)
features_query_pca = pca2.transform(features_query)
features_gallery_pca = pca2.transform(features_gallery)

#transformer = KernelPCA(n_components=50, kernel='poly', degree = 2, max_iter=10)
#features_train_pca = transformer.fit_transform(features_train)
#features_valid_pca = transformer.fit_transform(features_valid)
#transformer.fit(features_gallery)
#features_query_pca = transformer.transform(features_query)
#features_gallery_pca = transformer.transform(features_gallery)



rbf_feature = RBFSampler(gamma=1, random_state=1, n_components =30)
rbf_feature.fit(features_train_pca)

features_train1 = rbf_feature.transform(features_train_pca)
features_valid1 = rbf_feature.transform(features_valid_pca)
features_query1 = rbf_feature.transform(features_query_pca)
features_gallery1 = rbf_feature.transform(features_gallery_pca)


# setting up LMN
lmnn = metric_learn.LMNN(k=5, learn_rate=1e-6,max_iter=1000, convergence_tol=0.1, 
                         regularization = 0.8, use_pca= False, verbose=True)

# fit the data!
lmnn.fit(features_train1, train_label_new)
# transform our input space
features_train2 = lmnn.transform(features_train1)
features_valid2 = lmnn.transform(features_valid1)
features_query2 = lmnn.transform(features_query1)
features_gallery2 =lmnn.transform(features_gallery1)

n_neighbors = 20
#knn classifier with metric defined
clf = kNN(n_neighbors,'euclidean')
rk = Rank(n_neighbors)
#pred_train, errors_train = clf.fit(features_train2, features_train2)
#arr_label_train = rk.generate(train_idx_new, pred_train, train_label_new, train_label_new, camId_train, camId_train)
#rank1 train accuracy
#score_train = accuracy_score(arr_label_train[:,0], train_label_new)
#
#valid_query_idx = []
#count1 = 0
#count2 = 0
#num = 1
#for i in range(1, len(valid_idx)):
#    if(valid_label[i] == valid_label[i-1]):
#        if(camId_valid[i] == 1) and (count1 <num):
#            valid_query_idx.append(i)
#            count1 +=1
#    if(valid_label[i] == valid_label[i-1]) and (count2 <num):
#        if(camId_valid[i] == 2):
#            valid_query_idx.append(i)
#            count2 +=1
#    if(valid_label[i] != valid_label[i-1]):
#        count1 = 0
#        count2 = 0
#valid_query_idx = np.asarray(valid_query_idx)
#
#valid_query = features_valid2[valid_query_idx,:]
#valid_gallery = np.delete(features_valid2, valid_query_idx,0)
#valid_label_q = valid_label[valid_query_idx]
#valid_label_g = np.delete(valid_label, valid_query_idx)
#cam_valid_q = camId_valid[valid_query_idx]
#cam_valid_g = np.delete(camId_valid, valid_query_idx)
#
#pred_valid, errors_valid = clf.fit(valid_query, valid_gallery)
#arr_label_valid = rk.generate(valid_query_idx, pred_valid, valid_label_g, valid_label_q, cam_valid_q, cam_valid_g)
##rank1 valid accuracy
#score_valid = accuracy_score(arr_label_valid[:,0], valid_label_q)

pred_query, errors = clf.fit(features_query2, features_gallery2)
arr_label_query = rk.generate(query_idx, pred_query, label_gallery, label_query, camId_query, camId_gallery)
#rank1 test accuracy
score_test = accuracy_score(arr_label_query[:,0], label_query)


# rankk test accuracy
#rankk=5
#arr_label_rankk=np.zeros((1400,1))
#for i in range(query_idx.shape[0]):
#    for j in range(rankk):
#        if (arr_label[i,j]==label_query[i]):
#            arr_label_rankk[i]=arr_label[i,j]
#            break
#score_rankk = accuracy_score(arr_label_rankk, label_query)

#plotimg(filelist[14065][0])
