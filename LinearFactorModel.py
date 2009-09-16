import random
from numpy.linalg import lstsq
import numpy

class FactorModel:
    
    def __init__(self, uIds, vIds, numFactors):
        """
        Initialize the linear factor model. The two sets are identified by
        the two lists uIds and vIds and the number of factors is set by
        numFactors
        """
        self.uIds = uIds[:]
        self.vIds = vIds[:]
        self.numFactors = numFactors
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
        
        return numpy.dot(self.uVecs[u], self.vVecs[v])
            
    def calcError(self, knownValues):
        error = 0
        for (u,v) in knownValues.keys():
            dif = knownValues[(u,v)] - self.predict(u, v)
            error += dif * dif
            
        return error
        
    def initUseMatrix(self, knownValues, stopThreshold = .01, verbose = False):
        """
        Assigns vectors a, b to each element i, j in u and v such that the error
        sum((actual - predicted) ^ 2) over known values is minimized. The predicted
        value for i and j is just the dot product a * b.
        
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
                y = numpy.array([knownValues[(u,v)] for v in uToV[u]])
                
                self.uVecs[u] = lstsq(x,y)[0]
                
            # Similarly fix the u set and minimize for v
            for v in self.vIds:
                if len(vToU[v]) == 0:
                    continue
                    
                x = numpy.array([self.uVecs[u] for u in vToU[v]])
                y = numpy.array([knownValues[(u,v)] for u in vToU[v]])
                
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
                    
            
        
        
    
        
    
    
    