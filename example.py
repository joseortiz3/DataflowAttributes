from dataflowAttributes import *

if __name__ == '__main__':
    # Testing

    class DataflowSuccess():
    
        # The following defines the directed acyclic computation graph for these attributes.
        a1 = IndependentAttr(1, 'a1')
        a2 = DeterminantAttr(['a1'], 'update_a2', 'a2')
        a3 = DeterminantAttr(['a2'], 'update_a3', 'a3')
        a4 = DeterminantAttr(['a1','a2'], 'update_a4', 'a4')
        a5 = DeterminantAttr(['a1','a2','a3','a6'], 'update_a5', 'a5')
        a6 = IndependentAttr(6, 'a6')
        a7 = DeterminantAttr(['a4','a5'], 'update_a7', 'a7')

        def __init__(self):
            pass

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
            target = eval('((1*(1+2)+4)*(1+(1+2)+((1+2)+3)*6+5)+7)'.replace('6',str(self.a6)).replace('1',str(self.a1)))
            print('Expression equals '+str(answer)+' vs expected '+str(target))
            if answer == target: print('SUCCESS!')
            else: print('Failure.')

    class DataflowFail():
    
        a1 = 1
        a6 = 6

        def __init__(self):
            pass

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
            target = eval('((1*(1+2)+4)*(1+(1+2)+((1+2)+3)*6+5)+7)'.replace('6',str(self.a6)).replace('1',str(self.a1)))
            print('Expression equals '+str(answer)+' vs expected '+str(target))
            if answer == target: print('SUCCESS!')
            else: print('Failure.')

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


