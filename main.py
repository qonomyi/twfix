import discord
import re
import config

twitter_post_pattern = r"http(s)?:\/\/(mobile|www)?\.?(twitter|x).com\/\w+\/status\/\d+([\?|&]\w=[\w|\-]+)*"
url_query_pattern = r"(\?|&)(t|s)=(\w|\-)+"


def fix_tw_link(text: str) -> str:
    # TwitterのリンクをTwittpr(FixTweet)に置き換える
    # ついでにmobileとwwwとクエリも消します
    ft = text
    ft = re.sub(url_query_pattern, "", ft)
    ft = re.sub(r"(mobile|www)?\.?(twitter|x)\.com", "fxtwitter.com", ft)
    # ft = re.sub(r"(twitter|x)\.com", "twittpr.com", ft)
    return ft


intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.guild_reactions = True

client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    print("Ready")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    if message.content.startswith("!"):
        return
    if re.search(twitter_post_pattern, message.content) is not None:
        text = fix_tw_link(message.content)
        text = f"{message.author.mention} >\n{text}"
        try:
            msg = await message.channel.send(
                text, silent=True, allowed_mentions=discord.AllowedMentions.none()
            )
        except:
            await message.add_reaction("❌")
            return
        await msg.add_reaction("🗑")
        await message.delete()


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.emoji.name == "🗑":
        ch = await client.fetch_channel(payload.channel_id)
        msg = await ch.fetch_message(payload.message_id)
        user = re.search(r"\d+", msg.content).group()
        if int(user) == payload.user_id:
            await msg.delete()
        else:
            return


client.run(config.token)
