import motor


async def get_channels(db: motor.MotorDatabase, collection: str):
    channels = []
    async for channel in db[collection].find({}):
        channels.append(channel)

    return channels


async def get_messages(db: motor.MotorDatabase, collection: str, channel):
    messages = []
    async for channel in db[collection].find({'channel': channel}):
        messages.append(channel)

    return messages
