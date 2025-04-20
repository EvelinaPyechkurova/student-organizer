def set_dafault_if_none(instance, field_name, default_callable_or_value):
    '''
    Sets a default value or calls a function 
    to set value dynamically if field is None.
    '''
    if getattr(instance, field_name) is None:
        if callable(default_callable_or_value):
            value = default_callable_or_value()
        else:
            value = default_callable_or_value
        setattr(instance, field_name, value)