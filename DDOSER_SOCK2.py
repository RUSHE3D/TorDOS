import concurrent.futures
import multiprocessing
import requests

def get_tor_session():
    session = requests.session()
    # Configures the proxy options for the session
    session.proxies = {
        'http':  'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150'
    }
    return session

def send_request(url, session, payload_size):
    try:
        payload = '0' * payload_size
        response = session.request('GET', url, data=payload)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f'Error connecting to site {url}: {e}')
        return False

def ping_onion_site(url, num_requests, max_workers, payload_size):
    session = get_tor_session()
    received = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = [executor.submit(send_request, url, session, payload_size) for i in range(num_requests)]
        for f in concurrent.futures.as_completed(results):
            if f.result():
                received += 1
    print(f'Of {num_requests} packets sent, {received} were received successfully')

if __name__ == '__main__':
    url = input('Enter the .onion site URL: ')
    num_requests = int(input('Enter the number of packets to send: '))
    max_workers = None
    while max_workers is None:
        try:
            max_workers = int(input('Enter the number of threads to use: '))
        except ValueError:
            max_workers = None
            print('Invalid number of threads. Please enter a valid number.')
    payload_size = None
    while payload_size is None:
        try:
            payload_size = int(input('Enter the payload size: '))
        except ValueError:
            payload_size = None
            print('Invalid payload size. Please enter a valid number.')

    # Get the number of available threads
    available_threads = multiprocessing.cpu_count()
    print(f'Number of available threads: {available_threads}')

    if max_workers <= 0 or max_workers > available_threads:
        max_workers = available_threads
        print(f'Using all available threads: {max_workers}')

    ping_onion_site(url, num_requests, max_workers, payload_size)