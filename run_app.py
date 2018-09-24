import os

import tornado.ioloop
import tornado.web
import motor


from handlers import MainHandler, ChannelsHandler, LeaveChannelHandler, ChannelHandler, \
    WebSocketHandler, LoginHandler, SignUpHandler, LogoutHandler
import settings


class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            (r'/', MainHandler),
            (r'/channels', ChannelsHandler),
            (r'/leave_channel', LeaveChannelHandler),
            (r"/channels/(?P<channel>\w+)", ChannelHandler),
            (r'/ws/(.*)', WebSocketHandler),
            (r'/login', LoginHandler),
            (r'/sign_up', SignUpHandler),
            (r'/logout', LogoutHandler),
        ]

        app_settings = dict(
            cookie_secret='12345678',
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            login_url='/login',
            xsrf_cookies=True,
            debug=True,
        )
        super().__init__(handlers, **app_settings)
        self.con = None
        self.db = None

    def connect(self):
        self.con = motor.MotorClient(settings.MONGO_URI)
        self.db = self.con[settings.MONGO_DB]


def run():
    # parse_command_line()
    app = Application()
    app.connect()
    app.listen(settings.PORT)
    print('STARTED LISTEN ON 8888')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run()
