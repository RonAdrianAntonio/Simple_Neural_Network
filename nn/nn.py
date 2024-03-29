# -*- coding: utf-8 -*-
"""nn.ipynb

Automatically generated by Colaboratory.

Auto-generated the backward pass from the network definition (Please see all classes that implemented the "module" abstract class)

"""
### IMPORT

# Hello! Welcome to the start of my code!
# Here I'm just importing ABC and abstractmethod.
# These will be used to create an abstract class called "module"
# This will be explained later
from abc import ABC, abstractmethod
from tqdm import tqdm

# other important import statements
import os.path
import urllib.request
import gzip
import math
import numpy             as np
import matplotlib.pyplot as plt

"""START OF MY TRAIN/TEST CODE"""


# This class is just for calculating the Cross-Entropy loss. This compares
# a one-hot vector that represents the true label (y) and our predicted label (y_pred)
class CrossEntropyLoss:
  def calc_loss(self, y_pred:np.ndarray, y:np.ndarray):
    return -1. * np.sum( y * np.log(y_pred))

# So this is an abstract called "module"
# this is an abstract that lists the functions that need to be 
# defined for each and every module that you make.
# a "module" can either be an activation function (ReLU, softmax) or 
# an actual neural network layer (Fully Connected, etc.)
# This is just the basis for all of those.
# These will be our building blocks for our model
class module(ABC):
  def __init__(self):
    pass

  # The forward function will first run the input to the previous module,
  # then run the result of that through whatever it needs to do in its own
  # layer. If this module were a FullyConnected, the input would be given to
  # the previous layers first, then multiplied by the weight matrix. If this were
  # a activation function layer, like the ReLU or softmax, we would just take the softmax/ReLU
  # of the output of the previous layers
  def forward(self):
    pass

  # This defines how the layer weights would be updated. Specifically, the FullyConnected
  # layers.
  # PLEASE NOTE:
  # to properly implement this function, you need to return self at the very end. I had problems
  # updating the weights without that "return self" at the end, so please use that when
  # implementing a module.
  def backward(self):
    pass

  # This makes it so that we just need to do model(x) where x is our input. This will
  # call the forward function for us.
  def __call__(self, input):
    return self.forward(input)

  # This is like the toString() method for Python.
  def __str__(self):
    pass
  
  # This method makes it so that our weights are closer to zero, by dividing all
  # weights by 100
  def close_to_zero(self, matrix: np.ndarray):
    return (matrix) / 100.0

  # This generates all of the weights for this module's weight
  # matrix. This is the number of trainable parameters, so this 
  # should also include the bias values. They are instantiated the
  # same way, all from a Uniform distribution with the range [0, 0.01]. We
  # obtain this by using np.random.random, which obtains values from [0, 1]
  # then I just divide all results by 100
  def generate_random_weights(self, in_num, out_num):
    return self.close_to_zero(
        np.random.random(in_num * out_num).reshape(in_num, out_num)
      ).astype(np.float)

# This layer is just dividing the input image by a given number.
# in the actual use case, we would use 255
class Divide(module):
  def __init__(self, div_val):
    self.div_val = div_val

  # The forward is just dividing the input by the given value and returning that.
  # Specifically, the given numpy array input's values will be divided by our div_val
  def forward(self, input):

    return input / self.div_val

  # The backwards pass is just returning itself
  def backward(self):
    
    return self

  def __str__(self):
    return "Divide by " + str(self.div_val) + "\n"

# This layer is used to transform the weights into a row_size * column size vector.
class Vectorize(module):
  def __init__(self, prev_module, in_row_size, in_col_size, learn_rate):
    self.prev_module = prev_module
    self.fc = np.zeros((1, in_row_size * in_col_size))
    self.learn_rate = learn_rate

  # The forward pass returns the vectorized input, after pushing it through the previous
  # layer. For this project's implementation, that previous layer should be a Divide layer
  def forward(self, input):
    #print(input.shape)
    return self.prev_module(input).reshape(( input.shape[1] * input.shape[2] ,))

  # The backward pass just sets the previous module to the version of that module after
  # it's own backwards pass. Afterwards, this returns itself
  def backward(self, error):
    self.prev_module = self.prev_module.backward()
    return self

  def __str__(self):
    return self.prev_module.__str__() + "Vectorize\n"

# This represents the layer that Softmaxes the end output.
class Softmax(module):
  def __init__(self, prev_module):
    self.prev_module = prev_module
    self.fc = prev_module.fc
    self.learn_rate = prev_module.learn_rate

  # This forward method calculates the softmaxed version of the input vector.
  # The calculation is self-explanatory
  def forward(self, input):
    self.prev_result = np.copy(self.prev_module( input ))

    x_exp = np.exp( self.prev_result )

    return x_exp / np.sum( np.copy(x_exp))

  # For the backwards pass, I used the calculation that we got in the homework
  # We just need to pass back the subtraction between the predicted pmf vector, and the
  # actual label -- denoted as a one-hot
  def backward(self, y_pred, y):
    #print("Y predicted shape: ", y_pred.shape)
    self.prev_module = self.prev_module.backward( y_pred - y )

    self.fc = self.prev_module.fc
    return self

  def __str__(self):
    return "Learning Rate: {}\n\n".format(self.learn_rate) + self.prev_module.__str__() + "Softmax\n"

# This module is for adding a ReLU layer
class ReLU(module):
  def __init__(self, prev_module):
     self.prev_module = prev_module
     self.fc = prev_module.fc
     self.learn_rate = prev_module.learn_rate
  
  # This ReLUs the entire input
  def forward(self, input):
  
    self.prev_result = self.prev_module( input )
    return self.relu( self.prev_result )

  # The backwards pass checks all values in error if they are greater than or equal to
  # zero. If they are, then they get multiplied by 1. Else, they get multiplied by zero
  def backward(self, error):
    #print("Shape of ReLU previous result: ", self.prev_result.shape)
    relu_result_biased = self.relu_dx( np.append( np.array([1]), self.prev_result)) * error
    relu_result = np.delete(relu_result_biased, 0)
    #return self.prev_module.backward(
    self.prev_module = self.prev_module.backward( relu_result )

    self.fc = self.prev_module.fc
    return self
    
  
  def relu(self, x):
    return (x >= 0) * x

  def relu_dx(self, x):
    return (x >= 0) * 1.

  def __str__(self):
    return self.prev_module.__str__() + "ReLU\n"

# This is our FullyConnected layer
class FullyConnected(module):
  def __init__(self, in_num=0, out_num = 0,  prev_module=None, learn_rate=0.002):
    if prev_module is not None:
      self.prev_module = prev_module

      self.fc = self.generate_random_weights(prev_module.fc.shape[1] + 1, out_num)
      self.learn_rate = self.prev_module.learn_rate
    else:
      self.prev_module = None
      
      self.fc = self.generate_random_weights(in_num + 1, out_num)
      self.learn_rate = learn_rate
  
  # The forward pass multiplies our input vector with this layer's weight matrix
  # First the input gets added with a bias value, 1 to account for the bias values in
  # the weight matrix. Then, it continues with normal vector-matrix multiplication
  def forward(self, input):
    #print("went forward")
    if self.prev_module is not None:
      self.prev_result = self.prev_module(input)
    else:
      self.prev_result = input
    
    prev_result_with_bias = np.append(np.array([1]), self.prev_result)
    
    return prev_result_with_bias @ self.fc

  # This is the backwards pass 
  # This was the hardest part to figure out in the project.
  # So the way to think about this is, I believe, a good example.
  # Let's say we're trying to update the weights in the layer with (100 + 1) x 10 trainable parameters
  # That means that there should be a vector of 10 (shape (1, 10)) that represents the loss from the previous layer
  # (And by previous layer in this context I mean the layer that is in front of the layer that we are updating.)
  # Now, we actually have 100 results from the layer before this layer. This is represented by a vector with shape (100, 1).
  # now with that vector we need to add an extra dimension with value 1 to take into account the bias. so now the shape
  # is (101, 1).
  # Now let's look at both layers:
  # (101, 1) x (1 , 10)
  # See the pattern? now we just do a simple matrix multiplication.
  # Now we have a gradient matrix of shape (101, 10) which can now be used to update our (101, 10) shaped weight matrix.
  # Of course, our update rule is w_t+1 <- w_t - learn_rate * gradient
  # This is what this backwards pass implementation does, but in general.
  def backward(self, error):
    
    all_gradients = np.expand_dims(np.append( np.array([1]), self.prev_result), axis=1) @ np.expand_dims( error, axis=1).T

    prev_fc = self.fc.copy()

    self.fc = prev_fc - (self.learn_rate * all_gradients)

    next_error = np.sum(all_gradients * prev_fc, axis = 1)

    #print("next error shape: ", next_error.shape)

    if self.prev_module is not None:
      self.prev_module = self.prev_module.backward(next_error)
      #self.prev_module.backward(next_error)

    return self



  def __str__(self):
    prev = ""
    if self.prev_module is not None:
      prev = self.prev_module.__str__()

    return prev + "Fully Connected: ({},{})".format(self.fc.shape[0]-1, self.fc.shape[1]) + "\n    Number of Trainable values: ({} + 1) * {} = {}".format(self.fc.shape[0]-1, self.fc.shape[1], self.fc.shape[0] * self.fc.shape[1]) + "\n    MACs: {}\n".format(self.fc.shape[0] * self.fc.shape[1])

# This just creates a one-hot version of our labels
def create_onehot(location, size):
  new_onehot = np.zeros(shape=(10,))
  new_onehot[location] = 1
  return new_onehot

# This is for pre-processing for training/testing. This just gives us an
# iterator of (data, one-hot label) tuples of the given in_data and in_labels
def pre_process(in_data, in_labels):
  #data = [d.reshape(784,) / 255.0 for d in in_data]
  data = [d for d in in_data]
  labels = [create_onehot(l ,10) for l in in_labels]

  return zip(data, labels)


