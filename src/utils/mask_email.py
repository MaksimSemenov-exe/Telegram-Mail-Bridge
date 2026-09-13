def mask_email(email):

    name, domain = email.split('@')

    if len(name) <= 2:
        namee = name[0] + '*'
        return f'{namee}@{domain}'
    
    else:
        name = name[0] + '*' * (len(name) - 2) + name[-1]
        return f'{name}@{domain}'
