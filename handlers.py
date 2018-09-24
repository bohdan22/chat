import datetime
import hashlib
import json
import tornado.web
import tornado.websocket

from forms import ChannelNameForm
from utils import get_channels, get_messages


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        user = self.get_secure_cookie("username")
        if user:
            user = user.decode("utf-8")
        return user


class MainHandler(BaseHandler):

    async def get(self):
        if self.current_user:
            self.redirect('/channels')
        else:
            self.render('index.html')


class ChannelsHandler(BaseHandler):

    @tornado.web.authenticated
    async def get(self, *args, **kwargs):
        db = self.application.db
        channels = await get_channels(db, 'channels')
        self.render('channels.html', user=self.current_user, channels=channels, errors=None)

    async def post(self):
        form = ChannelNameForm(self.request.arguments)
        if form.validate():
            channel = str(form.data['name'])
            db = self.application.db
            channel_name_db = await db.channels.find_one({'channel': channel})
            if not channel_name_db:
                await db.channels.insert_one({'channel': channel})
                # self.set_cookie('channel', channel)
                self.redirect(f'/channels/{channel}')
            else:
                errors = "Please write another name"
                self.render('create_channel.html', errors=errors)
        else:
            errors = "Please write valid name"
            self.render('create_channel.html', errors=errors)


class ChannelHandler(BaseHandler):

    @tornado.web.authenticated
    async def get(self, *args, **kwargs):
        db = self.application.db
        channel = kwargs.get('channel', 'main')
        channel_exists = await db.channels.find_one({'channel': channel})
        if not channel_exists:
            self.redirect('/channels')

        messages = await get_messages(db, 'messages', channel)

        self.render('chat.html', user=self.current_user, messages=messages, channel=channel)


class WebSocketHandler(BaseHandler, tornado.websocket.WebSocketHandler):
    connections = {}

    def open(self, room):
        self.room = room
        try:
            self.connections[room]
        except KeyError:
            self.connections[room] = []
        self.connections[room].append(self)
        print(self.connections)

    def on_close(self):
        self.connections[self.room].remove(self)
        if len(self.connections[self.room]) < 1:
            self.connections.pop(self.room)
        print(self.connections)

    async def on_message(self, msg):
        db = self.application.db
        now_time = datetime.datetime.now()
        date = now_time.strftime("%d.%m.%Y %I:%M %p")
        data = json.loads(msg)
        await db.messages.insert_one({'user_name': self.current_user,
                                      'date': date,
                                      'channel': data['room'],
                                      'message': data['msg']})

        self.send_messages(data['msg'], date, data['room'])

    def send_messages(self, msg, date, room):
        for conn in self.connections[room]:
            conn.write_message(
                {'name': self.current_user, 'msg': msg, 'date': date})


class LoginHandler(BaseHandler):

    async def get(self):
        self.render('login.html', title='Authentication')

    async def post(self):
        password = self.get_argument('password')
        db = self.application.db
        user = await db.users.find_one({'user_name': self.get_argument('name')})

        if str(hashlib.md5(password.encode('utf-8')).hexdigest()) == str(user['password']):
            self.set_secure_cookie(
                'username', user['user_name'])
            self.redirect('/channels')
        else:
            self.render('login.html')


class SignUpHandler(BaseHandler):

    async def get(self):
        self.render('sign_up.html', title='Authentication')

    async def post(self):
        self.set_secure_cookie(
            'username', self.get_argument('name'))
        password = self.get_argument('password')
        user_name = self.get_argument('name')
        db = self.application.db
        await db.users.insert_one({'user_name': user_name,
                                   'password': hashlib.md5(password.encode('utf-8')).hexdigest(),
                                   'last_update': datetime.datetime.utcnow()})
        self.redirect('/login')


class LogoutHandler(BaseHandler):

    async def get(self):
        self.clear_all_cookies()
        self.redirect('/')
