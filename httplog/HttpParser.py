import re
import logging
from datetime import datetime

from httplog.Metrics import Data
from httplog.Stage import Stage


class HttpParser(Stage[str, Data]):
    """
    Parser for http log

    Receives: String
    Publishes: Data
    """
    # Regex with with 7 matching groups for string with this format
    # "<remote-host>","-","<remote-user>",<timestamp>,"<Verb Path HTTP Version>",<status>,<length>
    _regex = re.compile(r'^\"(\S+)\",\"(-)\",\"(\S+)\",(\d+),\"(.*)\",(\d+),(\d+)$')

    def receive(self, data: str):
        if m := self._regex.match(data):
            try:
                host, rfc, user, date, http_str, status, length = m.groups()
                date = datetime.fromtimestamp(int(date))

                verb, path, _ = http_str.split(" ")
                data = Data(
                    host=host,
                    rfc981=rfc,
                    user=user,
                    date=date,
                    verb=verb,
                    path=path,
                    length=length,
                    status=int(status)
                )
                self.publish(data)

            except ValueError as e:
                logging.error(f"Error: {e}")
        else:
            logging.debug("Received non matching string")
