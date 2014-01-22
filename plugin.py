###
# Copyright (c) 2007, Benjamin Rubin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

#import supybot.utils as utils
from supybot.commands import *
#import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
#import supybot.conf as conf
#import supybot.log as log
import urlparse
import gdata.youtube
import gdata.youtube.service
from gdata.service import RequestError


class Supytube(callbacks.Plugin):
    """Add the help for "@plugin help Supytube" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Supytube, self)
        self.__parent.__init__(irc)
        self.service = gdata.youtube.service.YouTubeService()

    def getVideoid(self, msg):
        for word in msg.args[1].split(' '):
            if(word.find("youtube") != -1):
                ## get
                videoid = urlparse.parse_qs(urlparse.urlsplit(word).query)['v'][0]
                return videoid
            elif word.find('youtu.be') != -1:
                videoid = urlparse.urlsplit(word).path.strip('/')
                self.log.info(videoid)
                return videoid

    def convertRating(self, oldrating):
        if oldrating:
            return '{:.2%}'.format((float(oldrating) / 5))
        else:
            return 'n/a'

    def doPrivmsg(self, irc, msg):
        if(self.registryValue('enable', msg.args[0]) and
                (msg.args[1].find("youtube") != -1 or msg.args[1].find('youtu.be') != -1)):
            id = self.getVideoid(msg)
            if id:
                self.log.debug('videoid = {0}'.format(id))
                try:
                    entry = self.service.GetYouTubeVideoEntry(video_id=id)
                except RequestError, e:
                    self.log.error('Supytube.py: Error: {0}'.format(e))
                    return
                try:
                    rating = ircutils.bold(self.convertRating(entry.rating.average))
                except AttributeError, e:
                    rating = ircutils.bold('n/a')

                title = ircutils.bold(entry.media.title.text)
                views = ircutils.bold(entry.statistics.view_count)
                reply = 'Title: {0}, Views {1}, Rating: {2}'.format(title, views, rating)
                irc.queueMsg(ircmsgs.privmsg(msg.args[0], reply))
            else:
                irc.noReply()

Class = Supytube
