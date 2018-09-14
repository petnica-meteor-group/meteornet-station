try:
    import urllib3
except ImportError:
    try:
        from pip._internal import main
    except ImportError:
        from pip import main
    main(['install', 'urllib3'])
    import urllib3

try:
    import requests
except ImportError:
    try:
        from pip._internal import main
    except ImportError:
        from pip import main
    main(['install', 'requests'])
    import requests
