

# условие появления всех элементов на страничке
class waitForAllElements(object):
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, driver):
        try:
            for method in self.methods:
                if not method(driver):
                    return False
            return True
        except:
            return False