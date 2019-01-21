import time

class AttrNullState(object):
    """
    This is just a special "attribute value is invalid" placeholder.
    """
    pass

class DependentAttr(object):
    """
    This descriptor class takes care of directed, acyclic dependencies among the attributes
    of a class. The attribute dependencies cannot form any cycles; dependency must be directed and
    free of cycles.
    
    When used in a class definition like...
        class DataflowSuccess():
    
        # The following defines the directed acyclic computation graph for these attributes.
        a1 = DependentAttr(1, [], None, 'a1')
        a2 = DependentAttr(None, ['a1'], 'update_a2', 'a2')
        a3 = DependentAttr(None, ['a2'], 'update_a3', 'a3')
        a4 = DependentAttr(None, ['a1','a2'], 'update_a4', 'a4')
        a5 = DependentAttr(None, ['a1','a2','a3','a6'], 'update_a5', 'a5')
        a6 = DependentAttr(6, [], None, 'a6')
        a7 = DependentAttr(None, ['a4','a5'], 'update_a7', 'a7')

        # ...... define the update functions update_a2, update_a3 etc
        def update_a2():
            ....

    ...this descriptor class automatically updates dependencies as required, and only at the
    very last moment they need to be calculated (that is, when that attribute's value is requested).
    
    Thus, a user is free to change the parameters of those attributes without dependencies 
    (a1 and a6 in the above example are independent) without causing nor requiring potentially-
    costly value updates. Instead, changing an attribute to a new value causes a cascade, setting 
    its childrens' values (dependent attributes) to a special null value: AttrNullState.

    Importantly, updating dependent attributes does not occur until a value is requested (via calling 
    getattr, obj.attr, etc). If an attribute has been made invalid by the previous changing of a 
    dependency, it will recursively trigger the required updates when its __get__ method is called.
    """

    def __init__(self, init_value, dependencies: list, calc_func: str, name, verbose=False):
        """
        init_value: initial internal value to be yielded by __get__.
        dependencies: a list of attributes which this attribute requires to be calculated.
        calc_func: the class function which __set__'s the value of this variable.
        name: The name of this attribute.
        verbose: Prints things for helpful debugging / understanding.
        """
        # Check passed arguments for more flexible usages.
        if dependencies is None:
            dependencies = []
        if init_value is None and len(dependencies)>0:
            init_value = AttrNullState
        # Set descriptor attributs.
        self.value = init_value
        self.dependencies = dependencies
        self.calc_func = calc_func
        self.name = name
        # Children will be added as necessary during runtime.
        self.children = []
        self.verbose = verbose
        if self.verbose:
           print('%s INIT: \t init_value: %s \t dependencies: %s \t calc_func: %s' %
                 (self.name, self.value, self.dependencies, self.calc_func))

    def __get__(self, obj, objtype):
        # This defines the behavior when using type(parent_object).attr
        if obj is None:
            return self
        if self.verbose:
            print('%s GET: \t obj: %s \t objtype: %s' % (self.name, obj, objtype))
        # None indicates the value must be recalculated.
        if self.value is AttrNullState:
            # Trigger the calculation of any attributes this one depends upon.
            for dependency in self.dependencies:
                if not hasattr(obj, dependency):
                    raise ValueError('Attribute %s is a dependency of %s but is not an attribute of %s'
                                     % (dependency, self.name, obj))
                # Get the dependency's descriptor via the defined type(obj).attr
                parent = getattr(type(obj), dependency, None)
                # If this descriptor doesn't know this is a child, inform it.
                if parent is not None:
                    if isinstance(parent, DependentAttr):
                        if self.name not in parent.children:
                            parent.children.append(self.name)
                # Get the dependency's value in order to trigger it to update.
                attr_value = getattr(obj, dependency)
                # Throw an error if the update was not successful and it should have been.
                if attr_value is AttrNullState:
                    if isinstance(getattr(type(obj), dependency, None), DependentAttr):
                        raise ValueError('Attribute %s requires %s but value was None' 
                                         % (self.name, dependency))
            # Execute function that re-calculates the value now all dependencies are ready.
            if self.calc_func is not None:
                update_func = getattr(obj, self.calc_func, None)
                if update_func is not None: 
                    if self.verbose: print('\tAttribute %s calling %s' 
                                           % (self.name,self.calc_func))
                    update_func()
                else: raise ValueError('Attribute %s cannot find method %s in object %s' 
                                       % (self.name, self.calc_func, obj))
        # By now, __set__ should have been called and has set the value.
        if self.value is AttrNullState: 
            raise ValueError('Attribute %s calling %s did not result in an updated value.' 
                                                         % (self.name, self.calc_func))
        return self.value

    def __set__(self, obj, value):
        if self.verbose:
            print('%s SET: \t obj: %s \t value: %s' % (self.name, obj, value))
        if self.value is not value:
            self.value = value
            # Set all attributes that depend upon this attribute to null state.
            for child in self.children:
                # In turn, these attributes will set their children to null state, and so forth.
                setattr(obj, child, AttrNullState)

class IndependentAttr(DependentAttr):
    """
    IndependentAttr a subclass of DependentAttr with no dependencies and no update function.

    For example:

        class DataflowSuccess():
            a1 = DependentAttr(1, [], None, 'a1')

    is identical to:

        class DataflowSuccess():
            a1 = IndependentAttr(1, None, 'a1')
    """
    def __init__(self, init_value, name, verbose=False):
        return super(IndependentAttr, self).__init__(init_value=init_value, 
                                        dependencies=[], calc_func=None, 
                                        name=name, verbose=verbose)

class DeterminantAttr(DependentAttr):
    """
    DeterminantAttr a subclass of DependentAttr, and is an attribute that is completely determined
    and dependent upon other attributes. Its syntax explicitly shows this. Its initial
    value is always AttrNullState.

    For example:

        class DataflowSuccess():
            a2 = DependentAttr(None, ['a1'], 'update_a2', 'a2')

    is identical to:

        class DataflowSuccess():
            a2 = DependentAttr(['a1'], 'update_a2', 'a2')
    """
    def __init__(self, dependencies, calc_func, name, verbose=False):
        return super(DeterminantAttr, self).__init__(init_value=AttrNullState, 
                                        dependencies=dependencies, calc_func=calc_func, 
                                        name=name, verbose=verbose)

if __name__ == '__main__':
    # Example of functionality

    # Define a class with interdependent attributes and the functions that update them.
    class DataflowFail():
        
        # Independent attributes
        a1 = 1
        a6 = 6

        # Define the functions responsible for updating the dependent attributes

        def full_update(self):
            self.update_a2()
            self.update_a3()
            self.update_a4()
            self.update_a5()
            self.update_a7()

        def update_a2(self):
            time.sleep(0.25)
            self.a2 = '('+str(self.a1)+'+2'+')'
            print('a2 updated to '+ self.a2)

        def update_a3(self):
            time.sleep(0.25)
            self.a3 = '('+ self.a2 + '+3)'
            print('a3 updated to '+self.a3)

        def update_a4(self):
            time.sleep(0.25)
            self.a4 = '(' + str(self.a1) + '*' + self.a2 + '+4)'
            print('a4 updated to '+self.a4)

        def update_a5(self):
            time.sleep(0.25)
            self.a5 = '(' + str(self.a1) + '+' + self.a2 + '+' + self.a3 + '*' + str(self.a6) + '+5)'
            print('a5 updated to '+self.a5)

        def update_a7(self):
            time.sleep(0.25)
            self.a7 = '(' + self.a4 + '*' + self.a5 + '+7)'
            print('a7 updated to '+self.a7)
            answer = eval(self.a7)
            target = eval('((a1*(a1+2)+4)*(a1+(a1+2)+((a1+2)+3)*a6+5)+7)'.replace('a6',str(self.a6)).replace('a1',str(self.a1)))
            print('Expression equals '+str(answer)+' vs expected '+str(target))
            if answer == target: print('SUCCESS!')
            else: print('Failure.')

    # Now correct the dependency problems in the class by creating a new class.
    class DataflowSuccess(DataflowFail):
        # This class corrects the dependency problems in the DataflowFail class by using the following descriptors:
        # The following defines the directed acyclic computation graph for these attributes.
        a1 = IndependentAttr(1, 'a1')
        a2 = DeterminantAttr(['a1'], 'update_a2', 'a2')
        a3 = DeterminantAttr(['a2'], 'update_a3', 'a3')
        a4 = DeterminantAttr(['a1','a2'], 'update_a4', 'a4')
        a5 = DeterminantAttr(['a1','a2','a3','a6'], 'update_a5', 'a5')
        a6 = IndependentAttr(6, 'a6')
        a7 = DeterminantAttr(['a4','a5'], 'update_a7', 'a7')

        # Inherets the rest of DataflowFail, including its updating functions for the dependent attributes.


    # Execute the test.
    print('------------- Testing the bad way of updating dependent attributes ------------')
    # Demonstrate no handling of data flow.
    program_bad = DataflowFail()
    # A full update works, but is computationally expensive and not always necessary.
    program_bad.full_update()
    print('Attribute a7 is '+str(program_bad.a7))

    # a6 affects a5 and a7, yet setting a6 doesn't change them at all.
    print('\nChanging a6 to 4 affects a5 and therefore a7.')
    program_bad.a6 = 4
    print('However, after changing a6, attribute a7 is still '+str(program_bad.a7))

    # Updating a7 doesn't work because it doesn't update a5 first.
    print('\nUpdating the value of a7 doesn\'t work without updating at least a5 first:')
    program_bad.update_a7()
    print('Attribute a7 is '+str(program_bad.a7))

    print('\nOnly a costly full update guarantees in all scenarios the correct value of a7:')
    program_bad.full_update()
    print('Attribute a7 is '+str(program_bad.a7))

    print('\n\n--------------- Testing the good way using explicitly-dependent attributes -------------')
    # Demonstrate good handling of data flow.
    program_good = DataflowSuccess()
    # No explicit updating required. Getting the value (.a7) triggers all necessary updates.
    print('Attribute a7 is '+str(program_good.a7))

    # Setting a6 to a *new* value triggers a5 and a7 to be set to None.
    print('\nChanging a6 to 4 affects the value of a5 and therefore a7.')
    program_good.a6 = 4
    # Getting the value of a7 triggers a5, the only null dependency, to be recalculated.
    # Once a5 has been recalculated, a7 recalculates itself automatically.
    print('Getting the value of a7 auto-triggers updating the only affected dependency a5 first.')
    print('Attribute a7 is '+str(program_good.a7))

    # Setting a1 works too.
    print('\nNow changing a1 to 9, which affects a2, a3, a4, a5, and a7.')
    program_good.a1 = 9
    print('Getting the value of a4 auto-triggers updating only a4\'s required dependencies.')
    print('Attribute a4 is '+str(program_good.a4))
    print('Getting the value of a7 auto-triggers only the remaining dependencies.')
    print('Attribute a7 is '+str(program_good.a7))


