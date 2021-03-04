''' Split artwork from an RFC XML file and feed them to a command.
'''
import os
import sys
import logging
import argparse
import subprocess
import lxml.etree as etree

LOGGER = logging.getLogger()


def main():
    ''' Main entry for the tool. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='info',
                        help='The minimum logging severity displayed.')
    parser.add_argument('infile', help='The file to read from.')
    parser.add_argument('xpath', help='The XPath expression to match.')
    parser.add_argument('command', nargs=argparse.REMAINDER,
                        help='The command and its arguments to run and pass to stdin.')

    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level.upper(),
        stream=sys.stdout
    )
    logging.root.debug('command args: %s', args)

    with open(args.infile, 'rb') as infile:
        xml_parser = etree.XMLParser()
        doc = etree.parse(infile, xml_parser)
    
    exitcodes = []
    for elem in doc.xpath(args.xpath):
        text = elem.text.strip()
        LOGGER.info('Processing element text:\n%s', text)
        proc = subprocess.Popen(args.command, stdin=subprocess.PIPE)
        proc.communicate(text.encode('utf8'))
        proc.stdin.close()
        exitcodes.append(proc.wait())
    
    return max(exitcodes) if exitcodes else 0


if __name__ == '__main__':
    sys.exit(main())
