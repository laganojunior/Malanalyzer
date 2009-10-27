import numpy
import cPickle

class PredictionModel:
    """
    This class defines the interface to create a prediction model
    and some functions to make some measurements of the model's
    performance. Actual prediction classes should derive from
    this class and override the necessary functions, and if 
    other parameters are needed, this should be set in other 
    functions.
    """

    def train(self, trainingMatrix):
        """
        Train the model on some training set.
        
        Arguments:
        trainingMatrix - the training set presented as a pysparse matrix.
                         Only the non-zero entries should be treated as
                         known values.
        
        """
        pass

    def predict(self, u, v):
        """
        Return the prediction of the model of the agent u on the
        item v.
        """
        return random.uniform(0, 1) 

    def RMSE(self, ratingsMatrix):
        """
        Return the Root Mean Squared Error of predictions compared to the
        known (non-zero) values of the input matrix, which is a pysparse
        matrix.
        """
        
        diffs = numpy.array([(self.predict(u, v) - rating)\
                         for ((u, v), rating) in ratingsMatrixMatrix.items()]:

        return numpy.sqrt(diffs.dot(diffs) / diffs.size)

    def save(self, fout):
        cPickle.dump(self, fout)


def loadModel(fin):
    return cPickle.load(fin)             
