import argparse, re, smtplib, pickle, pprint
from email.mime.text import MIMEText

import settings
from utils import DB, DNS

class Email(object):
    """ Base object for e-mail messages """
    def __init__(self, message, subject, sender = None, recipient = None):
        self._messageText = message
        se.f.msg = None
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
    def send(self, sender = None, recipient = None, subject = None):
        self.msg['Subject'] = subject or self.subject
        self.msg['From'] = sender or self.sender
        self.msg['To'] = recipient or self.recipient

        receivingServer = DNS.getPrimaryMXFromEmail(self.msg['To'])
        receivingServer = str(receivingServer).rstrip('.')
        s = smtplib.SMTP(receivingServer)
        s.sendmail(self.msg['From'], [self.msg['To'], ], self.msg.as_string())
        s.quit()

class LogNotify(Email):
    """ Message template for sending logs out """
    def __init__(self):
        self._messageText = ''

        self.log_id = -1

    def setMessage(self, messageExtra = ''):
        self._messageText = """This is a log test notification from pyqual.  You're receiving this because you are set as the owner of at least one test.
%s
Test ID | Test                      | Result
--------+---------------------------+---------
%s                                  

Result Data
===============================================
%s
""" % (messageExtra, self._testResultText, self._resultDataText)
        self.msg = MIMEText(self._messageText)
    def getMessage(self):
        return self._messageText
    message = property(setMessage, getMessage)

    def setTestResults(self, testResultList):
        if type([]) != type(testResultList):
            raise AttributeError('test_results must be a list of triples.')

        self._testResultText = ''
        for r in testResultList:
            name = r[1][:22] + (r[1][72:] and '...')
            self._testResultText += '%s | %s | %s\n' % (
                str(r[0]).ljust(7, ' '),
                name.ljust(25, ' '),
                r[2].ljust(8, ' ')
            )
    def getTestResults(self):
        return self._testResultText
    test_results = property(getTestResults, setTestResults)

    def setResultData(self, resultDataList):
        self._resultDataText = ''
        for d in resultDataList:
            self._resultDataText += 'Test ID: %s\n%s\n' % (
                d[0],
                repr(d[1])
            )
    def getTestResults(self):
        return _resultDataText
    result_data = property(getTestResults, setResultData)

""" Send out log messages
"""
if __name__ == '__main__':
    """ Handle cli arguments """
    parser = argparse.ArgumentParser(description='Run pyqual tests logging results to the DB.')
    parser.add_argument(
        '-d', '--debug', 
        action='store_true',
        default=False,
        help='Output debug statements to stdout'
    )
    args = parser.parse_args()

    db = DB()
    cur = db.connect(settings.DSN)

    cur.execute("""SELECT log_id, message, t.test_id, t.name, t.lastrun, u.email, result_data FROM pq_log l JOIN pq_test t USING (test_id) JOIN pq_user u USING (user_id) WHERE notify = false ORDER BY u.email, l.stamp DESC, t.lastrun DESC, test_id;""")

    currentEmail = ''
    logs = ()
    pp = pprint.PrettyPrinter(indent=2)
    if cur.rowcount > 0:
        for l in cur.fetchall():
            logs += (l['log_id'], )
            if l['email'] != currentEmail:
                if currentEmail != '':
                    msg.test_results = testResults
                    msg.result_data = resultData
                    msg.send(settings.EMAIL_SENDER, l['email'], 'Pyqual Test Results')
                msg = LogNotify()
                currentEmail = l['email']
                testResults = []
                resultData = []

            if re.search('passed', l['message'], re.IGNORECASE):
                result = 'Success'
            elif re.search('fail', l['message'], re.IGNORECASE):
                result = 'Failure'
            else:
                result = 'Unknown'
            testResults.append((l['test_id'], l['name'], result))

            if l.get('result_data'):
                if args.debug:
                    print 'Debug: Found data'
                data = pickle.loads(l.get('result_data'))
                strData = pp.pformat(data)
                if strData:
                    if args.debug:
                        print 'Debug: storing data'
                    resultData.append( (l['test_id'], strData) )

        msg.test_results = testResults
        msg.result_data = resultData
        msg.setMessage()
        msg.send(settings.EMAIL_SENDER, l['email'], 'Pyqual Test Results')
    else:
        if args.debug:
            print "Debug: Nothing to send."

    if len(logs) > 0:
        cur.execute("UPDATE pq_log SET notify = true WHERE log_id IN %s", (logs, ))
        db.commit()

    db.disconnect()