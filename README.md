# DataflowAttributes
This is minimalistic, pure-python module for efficiently handling "acyclic dependencies" in your Python class attributes.

In other words, this module takes care of automatically and efficiently updating attributes that depend on other attributes, no matter how complicated the dependency graph. 

One typical use-case (but not the only one!) is optimization: A class could represent a system you are trying to optimize, and its independent attributes (controls, or hyperparameters) are things you control about the system. Dependent (determinant) attributes are then affected by these controls. The goal is to find the "best" controls/hyperparameters by changing them and seeing how they affect the dependent attributes. Changing one control might cause every dependent attribute of the system to change, while another control might only effect a few dependent attributes. Thus it is possible to avoid unncessary calculation if you know which attributes affect which other attributes.

This module does exactly that by modifying the way python class attributes work by using python's [descriptor protocol](https://docs.python.org/3/howto/descriptor.html). Here, class attributes know which attributes they depend on, which attributes they affect, and how to update their own value. Setting/modifying the value of an attribute results in a cascade of messages informing dependent attributes they need to be recalculated in the future. This recalculation occurs only when actually using/getting the value of an attribute that needs to be recalculated "just in time".

For instance, consider a class that has attributes a1 through a7, with a dependency structure shown below:

![Graph of Example](acyclic_dependency_example_pic.png)

Changing attribute 1 (`a1`) will affect every attribute value except `a6`, and so all the values should be updated before they are used. Changing attribute 6 (`a6`) will affect only attribute 5 and 7, so we don't need to update all attribute values, just `a5` and `a7`. And when are these values actually recalculated and updated? At the last possible moment.

The module is very simple to use. When you are defining your class attributes, simply define their dependency structure using the module's descriptor classes. 
 
 ```python
     class DataflowSuccess():
    
        # The following defines the directed acyclic computation graph for these attributes.
        a1 = IndependentAttr(init_value = 1, name = 'a1')
        a2 = DeterminantAttr(dependencies = ['a1'], calc_func = 'update_a2', name = 'a2')
        a3 = DeterminantAttr(dependencies = ['a2'], calc_func = 'update_a3', name = 'a3')
        a4 = DeterminantAttr(dependencies = ['a1','a2'], calc_func = 'update_a4', name = 'a4')
        a5 = DeterminantAttr(dependencies = ['a1','a2','a3','a6'], calc_func = 'update_a5', name = 'a5')
        a6 = IndependentAttr(init_value = 6, name = 'a6')
        a7 = DeterminantAttr(dependencies = ['a4','a5'], calc_func = 'update_a7', name = 'a7')
        
        # Now define the functions to update the attribute values.
        def update_a2(self, ....):
            ....
        # etc.
 ```
The module takes care of the rest (setting values, getting values, and updating values).

Example code is provided based on the above dependency graph. Attributes 1, 2, etc. in the diagram correspond to `a1`, `a2`, etc. in the example code. Give it a try!

# Installation
The entire module is a single `.py` file. Just download the file and put it somewhere in the python search path, such as in the same directory as your current project. Then just import [dataflowAttributes](/dataflowAttributes.py).
