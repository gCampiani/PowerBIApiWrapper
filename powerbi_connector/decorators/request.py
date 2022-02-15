import warnings


def get_all_info(func):
    def inner(*args, **kwargs):
        if 'top' in kwargs.keys() and kwargs['top'] > 5000:
            warnings.warn("The maximum registries one API call can retrieve is 5000")
            kwargs['top'] = 5000
        partial = func(*args, **kwargs)
        if isinstance(partial, dict) and partial['status_code'] == 200:
            results = partial['value']
            while len(results) < partial['@odata.count']:
                kwargs['skip'] = len(results)
                partial = func(*args, **kwargs)
                results += partial['value']
            return results
        return partial

    return inner
