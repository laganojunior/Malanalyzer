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
            
    def calcRMSE(self, knownValues):
        """
        Calculates the Root mean of the squared errors of the model from a 
        matrix of known values
        """
        error = 0
        num = 0
        for u in knownValues.keys():
            for v in knownValues[u].keys():
                dif = knownValues[u][v] - self.predict(u, v)
                error += dif * dif
                num += 1
            
        return numpy.sqrt(float(error) / num)  
    
    def calcRegularizedError(self, knownValues, beta):
        error = 0
        for u in knownValues.keys():
            for v in knownValues[u].keys():
                dif = knownValues[u][v] - self.predict(u, v)
                error += dif * dif

        vec = numpy.array(list(self.uVecs.values()) + list(self.vVecs.values())).flatten()

        norm = numpy.dot(vec, vec)

        return error + beta * norm
            
    def initModel(self, knownValues, stopThreshold = .01, verbose = False, beta = .0001):
        """
        Assigns vectors to minimize the regularized error from known values.

        The regularized error is sqrt(sum((known - predict) ^ 2)) + beta * norm(uVecs, vVecs) ^ 2
        
        Arguments:
        knownValues - a multi-dimensional dictionary mapping i and j, where i is 
                      in u and j is in v, to the known values of the model. Note
                      that not all possible such values need to be provided.
        stopThreshold - the minimum amount the regularized error must decrease for 
                        minimization to continue
        verbose  - if set to true, prints progress to standard output
        beta     - the regularization parameter
                      
        Return Value:
        The total error of the generated model
        """
        
        # Do minimization by alternating minimizing while fixing the u or v vecs.
        # I personally do not know the performance guarantees if any for this
        # algorithm.

        uLength = len(self.uIds)
        vLength = len(self.vIds)

        # Create maps to easily get the index of an element in the uid array
        uIndex = {}
        for index, u in enumerate(self.uIds):
            uIndex[u] = index

        vIndex = {}
        for index, v in enumerate(self.vIds):
            vIndex[v] = index
        
        # Create maps to easily get the known rating vectors for a particular
        # elements of u or v
        uToV = {}
        vToU = {}
        
        for u in self.uIds:
            uToV[u] = [v for v in self.vIds if u in knownValues and v in knownValues[u]]
        
        for v in self.vIds:
            vToU[v] = [u for u in self.uIds if u in knownValues and v in knownValues[u]]

        # Create the y vectors. These are constant.
        uYVecs = [numpy.zeros(len(uToV[u]) + self.numFactors) for u in self.uIds]
            
        for index, u in enumerate(self.uIds):
            # These are the values for errors from known values, everything
            # else is left at 0
            for index2, v in enumerate(uToV[u]):
                uYVecs[index][index2] = knownValues[u][v] - self.uBias[u] - self.vBias[v] - self.globalBias

        vYVecs = [numpy.zeros(len(vToU[v]) + self.numFactors) for v in self.vIds]

        for index, v in enumerate(self.vIds):
            # These are the values for errors from known values
            for index2, u in enumerate(vToU[v]):
                vYVecs[index][index2] = knownValues[u][v] - self.uBias[u] - self.vBias[v] - self.globalBias

        # Create the set of x vectors. These consist of the vectors
        # that represent known interactions (I.e. the u or v vectors), and some
        # scale vectors to minimize the norm of the linear regression result
        uXVecs = numpy.zeros((vLength + self.numFactors, self.numFactors))

        for index, v in enumerate(self.vIds):
            uXVecs[index][:] = self.vVecs[v][:]

        for index in range(self.numFactors):
            uXVecs[vLength + index][index] = numpy.sqrt(beta)

        vXVecs = numpy.zeros((uLength + self.numFactors, self.numFactors))

        for index, u in enumerate(self.uIds):
            vXVecs[index][:] = self.uVecs[u][:]

        for index in range(self.numFactors):
            vXVecs[uLength + index][index] = numpy.sqrt(beta)
        
        # Create the x masks. The x vecs aren't constant, but references to
        # the ones needed are constant. Here are masks that are true only for
        # the needed vectors.
        uXMasks = numpy.repeat(False, uLength * (vLength + self.numFactors)).reshape(uLength, vLength + self.numFactors) 
            
        for index, u in enumerate(self.uIds):
            for v in uToV[u]:
                uXMasks[index][vIndex[v]] = True
            
            for i in range(self.numFactors):
                uXMasks[index][vLength + i] = True

        vXMasks = numpy.repeat(False, vLength * (uLength + self.numFactors)).reshape(vLength, uLength + self.numFactors) 
            
        for index, v in enumerate(self.vIds):
            for u in vToU[v]:
                vXMasks[index][uIndex[u]] = True
            
            for i in range(self.numFactors):
                vXMasks[index][uLength + i] = True
        

        # Enter a loop that is only exited if the threshold is met
        error = 1.0 * 10 ** 20
        while True:
            # Fix the v set and minimize the vectors for u using linear regression 
            newError = 0          
            for i in range(uLength):
                result = lstsq(uXVecs[uXMasks[i]], uYVecs[i])
                vXVecs[i] = result[0]
                if result[1].shape != (0,):
                    newError += result[1][0]
                
            # Similarly fix the u set and minimize for v
            for i in range(vLength):
                result = lstsq(vXVecs[vXMasks[i]], vYVecs[i])
                uXVecs[i] = result[0]
                if result[1].shape != (0,):
                    newError += result[1][0]

            if verbose:
                print newError

            if error - newError < stopThreshold:
                error = newError
                break
                
            error = newError

        # Reassign the u and v vecs back to the dictionary
        for i in range(uLength):
            self.uVecs[self.uIds[i]] = vXVecs[i]

        for i in range(vLength):
            self.vVecs[self.vIds[i]] = uXVecs[i]

            
        return error
        
    def getUVecs(self):
        return self.uVecs
        
    def getVVecs(self):
        return self.vVecs

    def getUIds(self):
        return self.uIds
    
    def getVIds(self):
        return self.vIds

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
            
        
        
    
        
    
    
    
