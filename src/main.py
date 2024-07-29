import argparse
from logger import CustomFormatter
import logging


def setup_argparse(): 
    parser = argparse.ArgumentParser()
    parser.add_argument('--datafolder', help='folder where data is available', default='./data/')
    parser.add_argument('--outputfolder', help='folder to store output', default='./output/')
    parser.add_argument('--datafile', help='csv file', default='Texas7k_Gas.json')
    parser.add_argument('--debug', action='store_true', help='debug flag')
    parser.add_argument('--error', action='store_true', help='error flag')
    parser.add_argument('--warn', action='store_true', help='warn flag')
    return parser

if __name__ == '__main__':
    # create logger with 'texas-gas-grid' application
    log = logging.getLogger("texas-gas-grid")
    log.setLevel(logging.INFO)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    
    log.addHandler(ch)

    args = setup_argparse().parse_args()
    if (args.debug == True):
        log.setLevel(logging.DEBUG)
    if (args.error == True): 
        log.setLevel(logging.ERROR)
    if (args.warn == True):
        log.setLevel(logging.WARNING)
    log.info(f"CLI-args: {args}")