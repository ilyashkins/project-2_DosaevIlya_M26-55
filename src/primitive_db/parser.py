def parse_condition(args, keyword):
    """Ищет keyword в списке args и вытаскивает условие после него."""
    if keyword not in args:
        return None
    
    idx = args.index(keyword)
    col = args[idx + 1]
    val_str = args[idx + 3] # пропускаем знак '='
    
    """делаем нужный тип"""
    if val_str.lower() == 'true':
        val = True
    elif val_str.lower() == 'false':
        val = False
    else:
        try:
            val = int(val_str)
        except ValueError:
            val = val_str
            
    return {col: val}