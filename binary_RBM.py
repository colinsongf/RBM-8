from __future__ import print_function
import numpy as np
from numba import jit


class binary_RBM(object):

    def __init__(self,n_visible=None,n_hidden=256,batchSize=256,lr=0.1,alpha=0,mu=.95,epoches=1):
        self.n_hidden=n_hidden
        self.n_visible=n_visible
        self.batchSize=batchSize
        self.alpha=alpha
        self.W=np.random.randn(n_visible,n_hidden)
        self.hbias=np.zeros(n_hidden)
        self.vbias=np.zeros(n_visible)
        self.epoches=epoches
        self.lr=lr
        self.mu=mu

    @jit    
    def fit(self,x):

        v_W=np.zeros(self.W.shape)
        v_h=np.zeros(self.hbias.shape)
        v_v=np.zeros(self.vbias.shape)        
    
        cost=self.get_pseudo_likelihood(x)
        print("Epoch %d Pseudo-likelihood cost:%f" % (0,cost))
    
        for t in range(0,self.epoches):
            N=x.shape[0]
            batches,num_batches=self._batchLists(N)
            num_batches=int(num_batches)
            for i in range(0,num_batches):
    
                idx=batches[i]
                data=np.squeeze(x[idx,:])
                B=data.shape[0]
        
                p_h=self._sigmoid(np.dot(data,self.W)+self.hbias)
                if t==0 and i==0:
                    h=p_h>np.random.rand(p_h.shape[0],p_h.shape[1])
                
                for k in range(0,15):
                    p_v=self._sigmoid(np.dot(h,self.W.T)+self.vbias)
                    v=p_v>np.random.rand(p_v.shape[0],p_v.shape[1])
        
                    q_h=self._sigmoid(np.dot(v,self.W)+self.hbias)
                    h=q_h>np.random.rand(q_h.shape[0],q_h.shape[1])
                
        
                g_W=np.dot(data.T,p_h)-np.dot(v.T,q_h)
                g_W/=B
                g_v=data.mean(axis=0)-v.mean(axis=0)
                g_h=p_h.mean(axis=0)-q_h.mean(axis=0)
        
        
                v_W=self.mu*v_W+self.lr*(g_W-self.alpha*self.W)
                v_h=self.mu*v_h+self.lr*g_h
                v_v=self.mu*v_v+self.lr*g_v
        
                self.W+=v_W
                self.hbias+=v_h
                self.vbias+=v_v
    
    
            self.lr/=(t+2)
            cost=self.get_pseudo_likelihood(x)
            print("Epoch %d Pseudo-likelihood cost:%f" % (t+1,cost))
        return None


    def _batchLists(self,N):
        num_batches=np.ceil(N/self.batchSize)
        batch_idx=np.tile(np.arange(0,num_batches)\
                ,self.batchSize)
        batch_idx=batch_idx[0:N]
        np.random.shuffle(batch_idx)
        batch_list=[]
    
        for i in range(0,int(num_batches)):
            idx=np.argwhere(batch_idx==i)
            batch_list.append(idx)
    
        return batch_list,num_batches
    
    @jit
    def _sigmoid(self,z):
        return 1/(1+np.exp(-z))

    @jit
    def get_pseudo_likelihood(self,x):
        v=x.copy()        
        idx = (np.arange(v.shape[0]),
                np.random.randint(0, v.shape[1], v.shape[0]))
        v[idx]=1-v[idx]
    
    
        N=self.vbias.shape[0]
        PL=N*np.log(self._sigmoid(self.free_energy(v)-self.free_energy(x)))
    
        return PL.mean()

    @jit
    def free_energy(self,x):
        F=-np.dot(x,self.vbias)-np.sum(np.logaddexp(0,np.dot(x,self.W)+self.hbias),axis=1)
        return F
if __name__=="__main__":
    import matplotlib.pyplot as plt
    
    x=np.load('trainIm.pkl')/255.0
    #x=x.reshape((60000,784))
    x=x.reshape((784,60000)).T
 
    
    rbm=binary_RBM(n_visible=784,alpha=1e-5,lr=.01,epoches=10)
    rbm.fit(x)
    
