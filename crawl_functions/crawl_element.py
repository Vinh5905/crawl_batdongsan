import 

def get_data_safe_find(self, selector, multi_value = False, scope_element = None, return_text = False):
    try:
        scope = scope_element if scope_element else self.driver

        if multi_value:
            elements = scope.find_elements(By.CSS_SELECTOR, value = selector)
            return elements
        else:
            element = scope.find_element(By.CSS_SELECTOR, value = selector)
            if return_text:
                return element.text
            return element
    except:
        return None