import random
from numpy.linalg import lstsq
import numpy
import cPickle

class FactorModel:
    """
    This class is a linear factor model that attempts to describe the 
    interaction between two sets of items labeled u and v. Internally, a
    vector is assigned to each element in u and v and their interaction is
    described by the dot product of the vectors. The predicted value between
    an element i in u and an element j in v is:
    
    vector_i dot vector_j + globalBias + uBias_i + vBias_j.
    
    where the biases are provided constants that vary on the elements i or j.
    
    The vectors are assigned to minimize the errors of the model on known
    interactions between some elements in u and v.
    """
    
    def __init__(self, uIds, vIds, numFactors, globalBias = 0, uBias = None,
                 vBias = None):
        """
        Initialize the linear factor model. This only sets a random model.
        
        uIds       - a list of ids for the u set
        vIds       - a list of ids for the v set
        numFactors - the number of linear factors to assume.
        globalBias - the value to add to all predicted values
        uBias      - a dictionary mapping elements of u to an intrinsic bias
        vBias      - a dictionary mapping elements of v to an intrinsic bias
        """
        
        self.uIds = uIds[:]
        self.vIds = vIds[:]
        self.numFactors = numFactors
        self.globalBias = globalBias
        
        if uBias != None:
            self.uBias = uBias.copy()
        else:
            self.uBias = {}
            
        # Fill in missing entries as 0
        for u in self.uIds:
            if u not in self.uBias:
                self.uBias[u] = 0
        
        if vBias != None:
            self.vBias = vBias.copy()
        else:
            self.vBias = {}
            
        # Fill in missing entries as 0
        for v in self.vIds:
            if v not in self.vBias:
                self.vBias[v] = 0
                
        self.randomize()
        
    def randomize(self):
        """
        Randomizes all internal parameters
        """
        
        self.uVecs = {}
        self.vVecs = {}
        
        for u in self.uIds:
            self.uVecs[u] = numpy.array([random.uniform(-1, 1) for _ in range(self.numFactors)])
        
        for v in self.vIds:
            self.vVecs[v] = numpy.array([random.uniform(-1, 1) for _ in range(self.numFactors)])
            
    def predict(self, u, v):
        """
        Gives the prediction for the value of the interaction between the item
        u in the u-set and v in the v-set. For the prediction to be somewhat
        meaningful, the model should have been initialized (i.e by
        calling initUseMatrix beforehand)
        """

        return numpy.dot(self.uVecs[u], self.vVecs[v]) + self.globalBias + self.uBias[u] + self.vBias[v]
            
    def calcError(self, knownValues):
        error = 0
        for (u,v) in knownValues.keys():
            dif = knownValues[(u,v)] - self.predict(u, v)
            error += dif * dif
            
        return error
        
    def initModel(self, knownValues, stopThreshold = .01, verbose = False):
        """
        Assigns vectors to minimize the error from known values.
        
        Arguments:
        knownValues - a dictionary mapping tuples (i,j), where i is in u and
                      j is in v, to the known values of the model. Note that not
                      all possible such tuples need to be provided.
        stopThreshold - the amount the sum of errors must change for minimization to
                        continue
        verbose  - if set to true, prints progress to standard output
                      
        Return Value:
        The total error of the generated model
        """
        
        # Do minimization by alternating minimizing while fixing the u or v vecs.
        # I personally do not know the performance guarantees if any for this
        # algorithm.
        
        # Calculate the initial error
        error = self.calcError(knownValues)
        
        if verbose:
            print error
        
        # Create maps to easily get the known rating vectors for a particular
        # elements of u or v
        uToV = {}
        vToU = {}
        
        for u in self.uIds:
            uToV[u] = [v for v in self.vIds if (u,v) in knownValues]
        
        for v in self.vIds:
            vToU[v] = [u for u in self.uIds if (u,v) in knownValues]
           
        
        # Enter a loop that is only exited if the threshold is met
        while True:
            # Fix the v set and minimize the vectors for u using linear regression
            for u in self.uIds:
                if len(uToV[u]) == 0:
                    continue
                    
                x = numpy.array([self.vVecs[v] for v in uToV[u]])
                y = numpy.array([knownValues[(u,v)] - self.globalBias - self.uBias[u] - self.vBias[v] for v in uToV[u]])
                
                self.uVecs[u] = lstsq(x,y)[0]
                
            # Similarly fix the u set and minimize for v
            for v in self.vIds:
                if len(vToU[v]) == 0:
                    continue
                    
                x = numpy.array([self.uVecs[u] for u in vToU[v]])
                y = numpy.array([knownValues[(u,v)] - self.globalBias - self.uBias[u] - self.vBias[v] for u in vToU[v]])
                
                self.vVecs[v] = lstsq(x,y)[0]
                
            # Recalculate error and see if loop should quit
            newError = self.calcError(knownValues)
            
            if verbose:
                print newError
            
            if error - newError < stopThreshold:
                error = newError
                break
                
            error = newError
            
        return error
        
    def getUVecs(self):
        return self.uVecs
        
    def getVVecs(self):
        return self.vVecs

    def save(self, fout):
        """
        Write a serialization of this object to a file-like object which
        supports write()
        """
        cPickle.dump(self, fout)


        

def loadFactorModel(fin):
    """
    Deserialize a FactorModel from a file-like object
    """
    return cPickle.load(fin)      
            
        
        
    
        
    
    
    
