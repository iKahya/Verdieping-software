import asyncio
import discord

class MyClient(discord.Client):

    def __init__(self, target_id=None, active_bots=None, token=None, log_messages=None, **kwargs):
        super().__init__(**kwargs)
        self.target_id = int(target_id)
        self.active_bots = active_bots
        self.token_key = token
        self.log_messages = log_messages if log_messages is not None else []

    def log(self, msg):
        print(msg)
        self.log_messages.append(msg)

    async def on_ready(self):
        self.log(f"Logged in as: {self.user}")

        try:
            user = await self.fetch_user(self.target_id)
            channel = await user.create_dm()
            self.log(f"DM channel is ready: {user}")

            last_id = None

            while True:
                try:
                    if last_id:
                        last_message = await channel.fetch_message(last_id)
                        messages = [
                            msg async for msg in channel.history(limit=100, before=last_message)
                        ]
                    else:
                        messages = [
                            msg async for msg in channel.history(limit=100)
                        ]

                    if not messages:
                        self.log("Successfully cleared!")
                        break

                    last_id = messages[-1].id

                    for msg in messages:
                        if msg.author.id == self.user.id:
                            try:
                                await msg.delete()
                                preview = msg.content[:40] if msg.content else "[media]"
                                self.log(f"Deleted: {preview}")
                                await asyncio.sleep(0.8)
                            except Exception as e:
                                self.log(f"Delete error: {e}")
                                await asyncio.sleep(2)

                except Exception as error:
                    self.log(f"History error: {error}")
                    break

        except Exception as e:
            self.log(f"DM ERROR: {e}")

        finally:
            if self.active_bots and self.token_key in self.active_bots:
                del self.active_bots[self.token_key]
            await self.close()


def run_bot(token, target_id, active_bots, log_messages):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = MyClient(
        target_id=target_id,
        active_bots=active_bots,
        token=token,
        log_messages=log_messages
    )

    active_bots[token] = client

    try:
        loop.run_until_complete(client.start(token))
    except Exception as e:
        log_messages.append(f" BOT ERROR: {e}")
        print(f"=== BOT ERROR: {e} ===")
    finally:
        if token in active_bots:
            del active_bots[token]
        loop.close()