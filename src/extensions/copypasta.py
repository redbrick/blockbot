import arc
import hikari

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="copypasta")

text = [
    """
 -🤖We've got a couple of people who want to say something. Yeah, that's Gerry, Gerry Hannan. Now you kind of are involved in an ongoing battle with uh Frank McCou-

-🌀It must be one sided I don't know anything about it

-☺️Yes you do, you know everything about it Frank. You have been peddling lies about Limerick for the last two and a half years. In every television station, in every newspaper. You have told lies....about Limerick, about your mother, about Theresa Carmody, about Willie Harold. You have done nothing but lied. You. Are. A liar. You are a self confessed liar. Theresa Carmody was three days away from her death, when you wrote in your book that you had sexual intercourse with her. You never mentioned anywhere in your book, that it was with her consent. Was it with her consent Frank? Was it with he-

-🌀There was no Teresa Carmody, it's a made up name!

-☺️It's not a made up name, you named her mother. You're going to tell more lies now are ya?

-🌀There was no proo-

-☺️Okay that's number one-

-🌀THERESA CARMODY. Just a minute we're not finished, THERESA CARMODY, THERESA CARMODY, THERESA CARMODY is a made up name

-☺️It is not a made up name

-🌀The young lady, you will never know her name

-☺️You are a liar! You are a liar! Number two Frank McCourt

-🌀Why are you so obsessed with me?

-☺️BECAUSE, FRANK. JESUS CHRIST UP IN HEAVEN

-🌀How old are you by the way? How old are you?

-☺️You ham... Irrelevant ☝️ You hammered your mother, you, you depicted her as a lazy, loose-moraled, good for nothing hoor, that's what you depicted your mother as. You owe your mother an apology, Theresa Carmody's parents... Theresa Carmody's family at least are looking into this program tonight, you owe her an apology.

-🤖Sorry Gerry, Gerry can I just explain something to you?

-☺️And number...sorry, I drove from limerick tonight to make three points and I want to make them

-🤖OK, make the third

-☺️You've censored me before pat you're not censoring me again

-🤖When did I censor you by the way?

-☺️Number three!...You censored me, you interviewed me, you gave me a twenty minute interview and without explanation you chopped it on your radio program

-🤖We often chop

-☺️Ah that's crap!

-🤖Absolutely. It's not crap it's customary practice

-☺️Number tree, number free, number three Frank. Why? If this miserable childhood that you had in limerick, this so-called miserable childhood, that you, you've, you've, peddled your LIES all over the world. Right, miserable lanes of Limerick, miserable childhood, miserable people of Limerick, misery, misery, misery the whole flippin' way. If that's the case, why did you not discuss your well paid employment with Jackie Brosnan? Why did you not discuss your years with St. Joseph's boy scout movement? You never discussed it
""",
    """
-🌀For the same reason that I didn't discuss various schools that I- you've had enough time now!

-🤖Gerry, Gerry, can I just ask-

-☺️YOU. ARE. A. LIAR

-🤖Gerry, can I just ask you one question? And I think the reason Frank was asking how old you are, is because he's writing of a time before you were born!

-☺️Frank, or, or Pat, you're a journalist, you've heard of research. I have interviewed over 70 people that are contemporaries of Frank McCourt. I interviewed Maire Gallagher. She describes Angela McCourt as the ANGEL OF THE LANES! Angela McCourt-

-🤖Can I also suggest to you that the late Jim Kemmy thought that Frank's book was an accurate description of the way things were in the Limerick of their mutual youth.

-☺️Jim Kemmy. Jim Kemmy with all due respect to him was a very close friend of Frank McCour-

-🌀No he wasn't. I didn't meet him til just before he died-

-☺️Yes he was, he was, Frank he was-

-🌀I met him just before he died...

-☺️I cant believe a word out of your mouth you're a liar!

-🌀...so you're a liar. I didn't know- I met him just before he died. Jim Kemmy! Jim Kemmy!

-☺️You're a liar

👏👏👏👏👏👏👏

-🤖I'm not sure who the audience are applauding there by the way but I must let Frank get back in from the charges, to respond to the charges you've made

-☺️There was...the name Theresa Carmody was one I made up because I was not going the name the-

-☺️Did you also make up the name of the girl in Bavaria?

-🌀...actual person.

-☺️You seem to have a morbid fascination for necrophilia-

-🌀I DO, I LOVE WOMEN

-☺️for necrophilia-

-🌀IF YOU DON'T MIND I LIKE WOMEN

-☺️necrophilia

-🌀I LOVE WOMEN. I'M MAD ABOUT WOMEN. I'VE BEEN MARRIED THREE TIMES, AND THIS, THE ONE I'M MARRIED TO NOW IS GOING LAST FOREVER BECAUSE...

-☺️Women?

-🌀I'M INFATUATED WITH WOMEN
""",
    """

-☺️Women? Women who are three days away from their death

-🌀TO PROTECT MY WIFE I MADE UP A FALSE NAME. I DON'T KNOW WHY YOU'RE SO OBSESSED WITH ME. DON'T YOU HAVE A LIFE? GO AHEAD AND LIVE! DO SOMETHING!

-☺️Women?

-🌀GO AHEAD, FIND A CAUSE, there are, there are, there are, THERE ARE POOR PEOPLE IN LIMERICK. GO AND HELP THE POOR OF LIMERICK, DON'T OBSESS WITH ME ALL THE TIME! You're there, you're in a city in Ireland, south of Ireland and you're obsessed with me

-☺️The two women you-

-🌀And I'm sure there are a few people that, when they cast sent out casting calls, for the movie in limerick, HUNDREDS OF PEOPLE SHOWED UP, then they brought their children to be in Angela's Ashes

-☺️Why did you lie about Willie Harold?

-🌀And if they hated, if they hated the book and the movie, WHY WERE THEY AUDITIONING FOR THIS TERRIBLE MOVIE

-☺️WHY DID YOU LIE ABOUT WILLIE HAROLD? You said Willie Harold, you said Willie Harold. You said. This man said, this man said

-🤖Gerry, Gerry, Gerry, hang on, I want to go down here, I want to go down here because, there's one thing I wanna ask you

-☺️This man said, this man said-

-🤖And hang on its the question, its the question,hang on SHHH. Most people watching this...

-☺️He castigated-

-🤖...have no idea what you're talking about-

-☺️Okay-

-🤖...because its fine detail about Limerick. You've made your point that you think it's very inaccurate

-☺️It's not, it's not inaccurate it's lies

-🤖But what I'd really like to know is why, why you are so obsessed? I mean, the latest book is called Tis, you're bringing out a book called Tisn't

-☺️ It's called Tis in my Ass

-🤖Okay I wasn't given the full title, Okay, Tis in my Ass, I thought it was going to be called Tisn't. This current book is about America, its about his experience in America now what are y-

-☺️Yeah yeah he spends his time in America, reminiscing about these miserable days back in miserable Limerick

-🤖What do you know about his life in America that you're going to contradict everything?

-☺️Zero, zero.
""",
    """
-🤖So why are you writing another book?

-☺️But who says my book is contradicting Tis? it hasn't been published yet.

-🤖Well Ashes was, your last book Ashes was contradicting Angela's Ashes

-☺️Ashes, was another side to the story, it was about the people who were happy, who lived on the lanes of limerick, MY relatives

-🤖Okay, okay

-☺️...who had a happy childhood

-🤖Yes, and we have a...

-👩Pat? I'd like to make a comment. Gerry Hannan didn't even write the book "Ashes". It was written by a fella by the name of Frank Hamilton

-🤖Is that so Gerry?

-☺️That is a total and absolute lie

-👩Gerry

-☺️THAT IS A LIE

-👩I'd like to see you try and disprove that

-☺️THAT IS A LIE

-👩and Frank Hamilton is in prison at the moment

-☺️THAT IS A LIE

-👩for sex crimes.

-☺️THAT IS A LIE

-👩So that is how-

-☺️THAT IS A LIE-

-👩...credible Gerry Hannan is!

-☺️That is a lie. Is that is that the best you can come up with?

-🤖Alright

-☺️Is that the best you can come up with?
""",
    """
-🤖Okay

-👩you're pathetic Gerry,

-☺️...is that the best you can come up with?-

-👩pathetic!

-🤖Very much a Limerick row

-🌀It's a squabble, It's a squabble

-🤖and we're going to-

-🌀and nobody's interested

-🤖...move on because we have to meet other people
""",
]


@plugin.include
@arc.slash_command("copypasta", "So tell me Frank!")
async def gerry_command(
    ctx: BlockbotContext,
) -> None:
    """Send a gerry!"""

    for part in text:
        embed = hikari.Embed(
            description=part,
            colour=Colour.GERRY_YELLOW,
        )

        await ctx.respond(embed)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
