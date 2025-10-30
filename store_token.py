import argparse
import keyring

def main():
    parser = argparse.ArgumentParser(
        prog = 'store_token.py',
        description = 'This utility will store the token for accessing Canvas.'
    )
    parser.add_argument('token', help = 'The token to store')
    args = parser.parse_args()

    print('Storing Canvas token...')
    keyring.set_password('pyCanvas', 'token', args.token)
    print('...done')

if __name__ == '__main__':
    main()
