import time
from random import random
from scholarly import scholarly, ProxyGenerator


def random_sleep(min_sec=5, max_sec=10):
    '''
    Random sleep for a period of time, in order to avoid being detected
    by web server as robot and thus banned from scratching data.

    [Args]
    min_sec : float, minimum sleep seconds
    max_sec : float, maximum sleep seconds
    '''
    sleep_sec = (max_sec-min_sec) * random() + min_sec
    time.sleep(sleep_sec)


def set_scholarly_proxy(select_proxy):
    '''
    Set up proxy generator for scholarly library.
    See https://github.com/scholarly/scholarly for detail instructions.
    
    [Args]
    select_proxy : str or None, can be [None, 'free_proxies', 'tor']
    '''
    if select_proxy is None:
        print("Skip proxy setup ...")
        return None
    else:
        pg = ProxyGenerator()
        if select_proxy == 'free_proxies':
            print("Use FreeProxies as scholarly proxy ...")
            pg.FreeProxies()
        elif select_proxy == 'tor':
            print("Use Tor as scholarly proxy ...")
            # Note that these parameters needs to be matched during
            # Tor set up. See https://github.com/scholarly-python-package/scholarly/blob/master/setup_tor.sh
            pg.Tor_External(tor_sock_port=9050,
                            tor_control_port=9051,
                            tor_password="scholarly_password")
        else:
            raise ValueError(f'Unknown proxy type {select_proxy}!')

        scholarly.use_proxy(pg)
        return pg


def str2list(s):
    '''
    Take a string of list in the form of "[a, b, c]",
    convert to a proper Python list.
    '''
    return [x.replace("'", "") for x in s[1:-1].split(", ")]
    
