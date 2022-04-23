#!/usr/bin/python3
# vim:set shiftwidth=4 expandtab:


'''
Intro goes here
===============

Use this as a template for your python  3.6+  programs.
Edit the various fields to customize it to your needs.

Tip - this is also a great place to put the program's user manual for the help page.

'''

# Standard library imports:
import getpass
import logging
import logging.handlers
import os
import sys
import textwrap
import time


# Beginning of logging setup section:

# Variables that control logging:
LogLevel = logging.DEBUG
    # ^ Initial log level of this program.
    #       Edit this if you want to change the initial log level.
    #       Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL .
MaxLogLineLength = 700
    # ^ Wrap log lines longer than this many chars.
    #   Keep a sensible and usable limit.
SysLogProgName = 'myprog'
    # ^ This is how our program is identified in syslog.
    #       Use:  journalctl -f -t 'myprog'  to watch its logs.
Indent = 8
    # ^ Wrapped lines are indented by n spaces to make
    #       logging easier to read.
    #   This field is optional.
IndentChar = '.'
    # ^ What sub character to use for indenting.
    #   This field is optional.
EnhancedLogging = True
    # ^ Use the fancy log line splitting (set to True).
    #   This includes forced splitting the supplied text at
    #       any \n newline marks.
    #   Send log line as-is to syslog (set to False) -
    #       you are responsible for line length constraints.
SecureLogging = False
    # ^ LogWrite supports safe logging if called in a particular way.
    #       This allows you to code two versions of your log line and
    #       depending upon this variable - one of the two will be logged.
    #       For example - the 'unsafe' version is used during debugging and
    #       the 'safe' version is used during production.
    #   To use this feature - call LogWrite with a dict:
    #       LogWrite.info( { 'safe': 'This message is CENSORED',
    #           'unsafe': 'Sensitive information here' } )
    #   If SecureLogging == True - the 'safe' value is logged.
    #   If SecureLogging == False - the 'unsafe' value is logged.
    #
    #   If you want simple logging - call LogWrite with a string:
    #       LogWrite.info('This will be logged as is')
    #
    #   You can also supply the dict:  'tee': "text to print"
    #       which saves you writing two lines (one for print and one for logging)
    #       per how you supply the dict (see the examples in the code later on):
    #   LogWrite.info( { 'tee': 'The same line\ngets printed to display\nand logged.'} )
    #   LogWrite.info( { 'tee': 'User line to display', 'safe': 'CENSORED line gets logged' } )


# Program identification strings:
__version__     = '1.0.4'
VersionDate     = '2022-04-24'
ProgramName     = 'MyProgram'
AuthorName      = 'Kenneth Aaron'
AuthorEmail     = 'mymail@example.com'
License         = 'GPLv3'


# This block handles logging to syslog:
class CustomHandler(logging.handlers.SysLogHandler):
    ''' Subclass for our custom log handler '''

    def __init__(self):
        super(CustomHandler, self).__init__(address = '/dev/log')
            # ^ Very important to send the address bit to SysLogHandler
            #   else you won't get logging in syslog!


    def emit(self, record):
        ''' Method for returning log lines to SysLogHandler.
            Here is where we split long lines into smaller slices and
            each slice gets logged with the appropriate syslog formatting,
            as well as the identifiers we add that clearly state where
            wrapping occurred.
        '''

        # This block deals with safe/unsafe/ignore LogWrite calls:
        if isinstance(record.msg, str):
            # ^ LogWrite was called with a basic string - ignore the SecureLogging setting
            #       and log the line as is.
            pass

        elif isinstance(record.msg, dict):
            # ^ LogWrite was called with a dict - log either safe/unsafe
            #       per SecureLogging setting.

            if 'tee' in record.msg:
                # ^ Dict key == tee means print the message to screen, and later choose
                #       which version gets logged.
                print(record.msg['tee'])

            if SecureLogging:
                if 'safe' in record.msg:
                    record.msg = record.msg['safe']
                else:
                    record.msg = record.msg['tee']

            if not SecureLogging:
                if 'tee' in record.msg:
                    record.msg = record.msg['tee']
                else:
                    record.msg = record.msg['safe']

        if EnhancedLogging:
            # ^ We will split the supplied log line (record.msg) into multiple lines.
            #   First - split the message at whatver \n newline chars were supplied
            #   by the caller (even before our own fancy splitting is done):

            RecordMsgSplitNL = record.msg.splitlines()
                # ^ If the log message supplied contains new lines we will split
                #   it at the newline mark - each split logged as a separate line.
                #   The splitlines() method creates RecordMsgSplitNL as a list,
                #   even if there was only one line in the original log message.
                #   Note - lines split because of \n will not get the !!LINEWRAPPED!!
                #   text prepended/appended at the split points.

            SplitLinesMessage = []
                # ^ Final version of line splitting

            for LineLooper in RecordMsgSplitNL:
                if len(LineLooper) < MaxLogLineLength:
                    # ^ Normal line length detected
                    SplitLinesMessage.append(LineLooper)

                else:
                    # ^ Long line detected, need to split
                    TempTextWrapLines = (textwrap.wrap(
                        LineLooper,
                        width=(MaxLogLineLength - 15),
                        subsequent_indent='!!LINEWRAPPED!!',
                        drop_whitespace=False))
                        # ^ If line to log is longer than MaxLogLineLength -
                        #   split it into multiple lines and prepend !!LINEWRAPPED!!
                        #   to the subsequent lines created by the split.

                        # ^ Note - We subtract 15 because we're adding !!LINEWRAPPED!!
                        #   at the end of lines, and we don't want the total length
                        #   of the log line to exceed MaxLogLineLength .

                        # ^ Note - textwrap.wrap doesn't know how to append text
                        #   to wrapped lines, so we must do it manually later.

                        # ^ Note - textwrap.wrap returns a list.

                    #   If we needed to wrap long lines let's append the !!LINEWRAPPED!!
                    #   text to the end of all lines except the last one:
                    if len(TempTextWrapLines) > 1:
                        for Looper in range(len(TempTextWrapLines)-1):
                            TempTextWrapLines[Looper] = ( TempTextWrapLines[Looper] +
                                '!!LINEWRAPPED!!' )

                    SplitLinesMessage.extend(TempTextWrapLines)

            # Finally, return the lines to the class,
            # adding the indent to lines #2 and above if required:
            for Counter, Looper in enumerate(SplitLinesMessage):
                if Counter > 0:
                    Looper = ( ((Indent - 4) * ' ') +
                        (IndentChar * 4) +
                        Looper )
                        # ^ This adds the indent and .... to all subsequent lines
                        #   after the first line - and applies to ALL LINES from
                        #   the second onwards, both for lines split on newline
                        #   and lines split on length!
                        #   Don't be confused if some lines don't have the
                        #   !!LINEWRAPPED!! text in them - there could be \n in
                        #   the string passed, and we made new lines from that.
                record.msg = Looper
                super(CustomHandler, self).emit(record)

        else:
            super(CustomHandler, self).emit(record)
                # ^ Pass it through as-is


#logging.disable(level=logging.CRITICAL)
    # ^ Uncomment this if you want to completely disable logging regardless of any
    #   logging settings made anywhere else.

LogWrite = logging.getLogger(SysLogProgName)
LogWrite.setLevel(LogLevel)
    # ^ Set this to logging.DEBUG or logging.WARNING for your INITIAL desired log level.

LogWrite.propagate = False
    # ^ Prevents duplicate logging by ancestor loggers (if any)

LogHandler = CustomHandler()
LogWrite.addHandler(LogHandler)

#LogWriteFormatter = logging.Formatter(
#    '{}[%(process)d]: <%(levelname)s> '
#    '(%(asctime)s , PN: %(processName)s , MN: %(module)s , '
#    'FN: %(funcName)s , '
#    'LI: %(lineno)d , TN: %(threadName)s):    '
#    '%(message)s'
#        .format(SysLogProgName))
    # ^ Works but uses comma milliseconds and I prefer dot milliseconds.

LogWriteFormatter = logging.Formatter(
    fmt = '{}[%(process)d]: <%(levelname)s> '
        '(%(asctime)s.%(msecs)03d , PN: %(processName)s , MN: %(module)s , '
        'FN: %(funcName)s , '
        'LI: %(lineno)d , TN: %(threadName)s):    '
        '%(message)s'.format(SysLogProgName),
    datefmt = '%Y-%m-%d %H:%M:%S' )
    # ^ Select the attributes to include in the log lines
    #   Documented here: https://docs.python.org/3/library/logging.html
    #     (LogRecord attributes)
    #
    #   Note: On Python 3.6+ we can get millisecond date using:
    #       datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
    #
    #   Note: Any variables passed in the:  format(...)  section are fixed for the
    #       duration of the run - don't use it to pass in a timestamp because it will
    #       not change - ever.
    #   This version gives dot milliseconds rather than the default comma as in
    #       the builtin python function.
    #       See here: https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format

    # Fields explained:
    #   PN: Process Name
    #   MN: Module Name (Also the file name of the first py file that is run
    #       or the name of the symlink that ran it)
    #   FN: Function Name
    #   LI: LIne number
    #   TN: Thread Name
    #
    #       LN: Logger Name (This is the contents of variable: SysLogProgName)
    #           I'm not using it because it's already used in the first {} of:
    #               {}[%(process)d]:

    # Example:
    #   Dec 29 14:35:29 asus303 nccm[31470]: <DEBUG> (2020-12-29 14:35:29.048 ,
    #   PN: MainProcess , MN: cm , FN: SetupWindows , LI: 1268 , TN: MainThread):
    #   ConnectionsList window built

LogHandler.setFormatter(LogWriteFormatter)

# ^ End of logging setup section


# Beginning of your global variables section:


# ^ End of global variables section


# Put your code below this:

def InitialLogging():
    ''' Called at program run time to log useful information prior
        to the actual program running.
    '''

    IntroLine = ('{} v{} , {} , by: {} ( {} )'
        .format(ProgramName, __version__, VersionDate, AuthorName, AuthorEmail))

    LogWrite.info(IntroLine)

    LogWrite.info( {
        'unsafe': 'Invoked commandline: {CmdLine} , from directory: {Dir} , '
            'by user: {User} , UID: {UID} , PPID: {PPID} , log level: {LogLevel}'
                .format(
                    CmdLine = sys.argv,
                    Dir = os.getcwd(),
                    User = getpass.getuser(),
                    UID = os.getuid(),
                    PPID = os.getppid(),
                    LogLevel = LogLevel ),
        'safe':   'Invoked commandline: CENSORED , from directory: CENSORED , '
        'by user: CENSORED , UID: CENSORED , PPID: CENSORED , log level: {LogLevel}'
            .format(LogLevel = LogLevel) } )


    LogWrite.info('Fields explained: PN: Process Name , MN: Module Name , '
        'FN: Function Name , LI: LIne number , '
        'TN: Thread Name')

    if not SecureLogging:
        LogWrite.warning('Attention:  SecureLogging == False  -->  '
            'sensitive information will be logged to syslog/journal !')


def main(*args):

    LogWrite.debug('Function main started')

    LogWrite.info( {
        'safe' :    'This message is CENSORED',
        'unsafe' :  'This message includes sensitive information' } )
        # ^ Uses the:  SecureLogging  setting.

    LogWrite.warning('This is a warning message')
    LogWrite.error('This is an error message')
    LogWrite.critical('This is a critical message')

    LogWrite.info( { 'tee': 'This same line\ngets printed to display\nand logged.'} )
        # ^ Only:  'tee'  supplied - the same line gets printed and logged - regardless
        #       the state of:  SecureLogging  .

    LogWrite.info( { 'tee': 'User line to display', 'safe': 'CENSORED line gets logged' } )
        # ^ 'tee'  line always gets printed.
        #   If:  SecureLogging = False  ->  'tee' line gets logged.
        #   If:  SecureLogging = True   ->  'safe' line gets logged.


# Program starter:
if __name__ == '__main__':
    ScriptStartTime = time.time()
    InitialLogging()
    main()

    LogWrite.info('{} exiting. Program run time: {:.3f} seconds'
        .format(ProgramName, time.time() - ScriptStartTime))

