import { useState } from "react";
import "./App.css";
import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { CirclesWithBar } from "react-loader-spinner";
const queryClient = new QueryClient();

function App() {
  return (
    <div className="App">
      <QueryClientProvider client={queryClient}>
        <div>

          <CommentsChecker />
        </div>
      </QueryClientProvider>

    </div>
  );
}
interface Review { probability: number; label: "negative" | "positive" }
export function CommentsChecker() {
  const [comments, setComments] = useState<string[]>(["This is an amazing movie"]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [modelType, setModelType] = useState<"GRU-TWO-LAYERS" | "LSTM-TWO-LAYERS">("GRU-TWO-LAYERS");
  const mutation = useMutation({
    mutationFn: async() => {
      const response = await fetch(`https://nlp-comments-analyser.onrender.com/predict/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comments, model: modelType }),
      });
      if (!response.ok) {
        throw new Error("Failed to fetch prediction results");
      }
      const data = await response.json() as {results: Review[]};
      return data.results;
    },
    onSuccess: (data) => {
      setReviews(data);
    },
    onError: (error) => {
      alert('Failed to fetch prediction results, Sorry! This is a free server...');
    }
  });
  return (
    <div id="root">
      <h1>Comments Sentiment Checker</h1>
      <div style={{ display: "flex", justifyContent: "center", gap: "1rem", marginBottom: "1.5rem" }}>
        <label>
          <input
            type="radio"
            value="GRU-TWO-LAYERS"
            checked={modelType === "GRU-TWO-LAYERS"}
            onChange={() => setModelType("GRU-TWO-LAYERS")}
          />
          GRU-TWO-LAYERS
        </label>
        <label>
          <input
            type="radio"
            value="LSTM-TWO-LAYERS"
            checked={modelType === "LSTM-TWO-LAYERS"}
            onChange={() => setModelType("LSTM-TWO-LAYERS")}
          />
          LSTM-TWO-LAYERS
        </label>
      </div>
      <button
        style={{ marginBottom: "1.5rem" }}
        onClick={() => {
          const randomReviews = [
            // "The plot was very predictable.",
            // "Amazing cinematography and visuals!",
            // "I would not recommend this movie.",
            // "The acting was phenomenal.",
            // "The story felt a bit rushed.",
            // "Incredible soundtrack and music!",
            // "Not as good as the trailer suggested.",
            // "The characters were very relatable.",
            // "A complete waste of time.",
            // "A masterpiece in every sense.",
            // "The dialogues were very cheesy.",
            // "An emotional rollercoaster.",
            // "Not worth the hype.",
            // "Brilliantly directed and executed.",
            // "Too long and boring.",
            `I have personally seen many Disney movies in my lifetime, though absolutely none of them match up in any way to Bedknobs and Broomsticks. Although I personally wouldn't have crossed live-action with animation, it was an improvement on trying to dress people up as animation characters. The movie pits three evacuees from world war two who are sent to stay with a silent and socially awkward woman in the country. I would have to say that the casting was brilliant. Angela Landsbury made a perfect Miss Price, while David Thomilson made a great desperate entertainer love interest. Endings always surprise me and this was no exception. It was neither happy nor sad, though I do not know if this was intentional. The dialog wasn't great, but considering it was designed to be a kid's movie, that is alright. Overall, I would give the performance nine out of ten, the dialog six out of ten, the casting nine out of ten and the costumes eight out of ten.`,
            `This movie has always been my favorit Disney movie. Then on 11/21/01 I saw the 30th aniversy of this movie DVD. WOW I remembered why I loved this movie. The DVD is So great, It has an extra 30 min that the original did not have. I did not know this when I first started watching. The movie made ever so much more since. The music they cut out should have been left in. You have not seen this movie until you have seen the Full 131 min version. A lot of people say that the music is forgettable. I remember every song in this movie by heart, every song has it's own Charm by it's self, and comes together as a hole. I remember when i was younger I had the "Eglantine" song stuck in my head for days at a time. As well as "Briny Sea" (that song was meant for marry poppens but was cut out of the film) Please Watch the new uncut 30th aniversy movie and re-vote for this movie. the 10 that it really is.`,
            `"Such a Long Journey" is a well crafted film, a good shoot, and a showcase for some good performances. However, the story is such a jumble of subplots and peculiar characters that it becomes a sort of Jack of all plots and master of none. Also, Western audiences will likely find the esoterics of the rather obscure Parsee culture a little much to get their arms around in 1.7 hours. Recommended for those with an interest in India.`,
            `They probably could have skipped some of the beginning - I'm not sure why this starts out in the Asian part of Turkey. If it was because starting in the Mediterranean, they could have gotten closer starting in modern day Lebanon.<br /><br />One the cameras and crews get to the Bakhtyari tribe, it's the beginning of an amazing 48 day journey. 50,000 people with about 250,000 goats, camels, cattle, and horses make this amazing trek across what seems to be a very fast moving Karun River. They use rafts that are kept afloat by inflating goat skins - you can see where the head and legs were removed. The other "bank" of the river was very steep - I'm guessing about a 60 degree rise.<br /><br />Just watching that was incredible, but there was much more to come. To get to the pastures, they also had to cross a major mountain that had about 4 feet of snow, if not more. Being able to climb this mountain was pretty amazing in and of itself, but they (and all of the animals) climbed this mountain barefoot! Yes, barefoot.<br /><br />The one drawback to this documentary were some of the inter-titles with poor attempts at humor.<br /><br />If you want to see a documentary from the silent era, or the incredible challenges that this tribe not only face, but conquer. This is just an incredible document of a little known group of people facing all kinds of challenges.`,
            `Although I really enjoyed Jim Carrey's latest "serious" performances ("The Truman Show", "Man on the Moon"), I've always thought his real genious lies in physical comedy. This is not to say he is a fantastic, talented actor: those bozos at the Academy Awards seem to dislike him so much, he has never had a (truly deserved) nomination or award. Well, any "institution" that nominates for 11 Oscars a bore such as "Titanic" shouldn't be taken seriously.<br /><br />On with the review. "The Grinch" is the sweetest, best looking, best acted, more enjoyable seasons film since "The Nightmare before Christmas". Both movies seem very similar, too, with their highly stylized sets and the premise of someone stealing Christmas. Both make their principal actors seem like the villains (one in a higher degree than the other), both pack a strong moral lesson, and both are truly enjoyable.<br /><br />That is, until you realize that Jack Skellington is a doll, and The Grinch is a human being. But a human being that is so incredibly expressive, so fluid in his movements, so cartoon-like, so unreal, that never gets in the way of the movie. He can be hilarious, he can be a sad soul, he can be angry. He lives in a 3-dimensional world, where 3-dimensional people live. He jokes, he laughs, he cries, and ultimately he saves the Christmas. I loved this film to bits, and cannot wait for it to come out on DVD. This is one of those films you will really enjoy 10, 20 years from now. As timeless as they come.`,
            `If the movies are to be believed, Chinese ghosts are much prettier and more mischievous than their Western counterparts. The storylines of the three 'Chinese Ghost' films are largely identical, but the direction is excellent and the detail and colour is such that it's not a huge problem. As always, humour is an integral part of the film, accompanied, of course, by a great deal of mugging. For those who haven't encountered the 'Chinese GhostStory' trilogy yet, this film offers an interesting departure from the Western horror/ghost genre; for those who have, another enjoyable romp in the Chinese ghost world.`,
            `My baby sitter was a fan so I saw many of the older episodes while growing up. I'm not a fan of Scooby Doo so I'm not sure why I left the TV on when this show premiered. To my surprise I found it enjoyable. To me Shaggy and Scooby were the only interesting characters *dodges tomatoes from fans of the others* so I like that they only focus on those two. However, this may cause fans of the original shows to hate it. I like the voice acting, especially Dr. Phinius Phibes. I liked listening to him even before I knew he was Jeff Bennett. And Jim Meskimen as Robi sounds to me like he's really enjoying his job as an actor. I also get a kick out of the techies with their slightly autistic personalities and their desires to play Dungeons and Dragons or act out scenes from Star Wars (not called by those names in the show, of course).`,
            `Ironically for a play unavailable on film or video for so long, ARMS AND THE MAN has remained fairly constantly available on stage over the years since its debut in 1894 - in no small part because it has aged so well as a solid satire on the nature of heroism and the business of war. Whenever the world sinks into strife, ARMS AND THE MAN seems to soar as ever more timely and relevant.<br /><br />This is the play which Oscar Strauss converted (leaving out most of Shaw's best ideas) into the successful operetta, THE CHOCOLATE SOLDIER (when Hollywood got to *that,* they left out the last vestiges of Shaw rather than pay him for the rights - he was, by then, an Oscar winner in his own right). While the best of Shaw has always been his ideas and his dialogue rather than his bare plots, in ARMS AND THE MAN, the plot sparkles as well and the master manages happy endings for all concerned. <br /><br />Young Raina (Helena Bonham Carter), daughter of an officer and the wealthiest man in her town, is betrothed to a dashing officer in the Bulgarian cavalry and all seems well until a bedraggled Swiss mercenary (Pip Torrens) from the other side climbs up her drainpipe fleeing from the battle where his army has been routed. As usual in a Shaw satire, nothing is as it first appears and societal conventions are stood on their head in the light of simple - and not so simple reason. There are no "good guys" or "bad guys," just people of a variety of classes getting by on the best of their wits - just like life only better - and naturally with Shaw, the wit is finely honed from all concerned.<br /><br />The early (1932) motion picture version (from Shaw's own screenplay) of this most traditional and traditionally funny of Shaw's stage satires, and one of his first to make a real hit on this side of the Atlantic, has long been among the missing. Shaw didn't sell the screen-rights to his plays - only licensed them for 5 year periods, and it appeared that with rapidly evolving sound technology making 1932 films look primitive only a few years later, Shaw did not renew the license to show it. Consequently, we're immensely in the BBC's debt for finally putting out their 1987 broadcast version in a DVD box with nine other sparkling plays. (Somewhat sadly, PYGMALION, that many view as Shaw's best, comes off least well on this set in a production with Lynn Redgrave and James Villiers.)<br /><br />Even paired, as it is on its DVD, with the less impressive one act, A MAN OF DESTINY, ARMS AND THE MAN makes for a real treasure.<br /><br />Helena Bonham Carter went on, after cutting her teeth on televised roles like this, to a major film career that will bring many viewers to this early role. They should not be disappointed, for Ms. Carter gives a performance in line with the layered innocence audiences have come to expect from her, but under James Cellan Jones' somewhat pedestrian direction (and despite the BBC's uniformly beautiful and well observed physical production), the role's mischievous fire (and her outrage at being underestimated in the last act) is banked at only about 80% of it's potential. <br /><br />Much the same can be said of the real star of the piece, Pip Torrens, as Bluntschli the "Switzer." It's a fine, appealing performance, but doesn't go for the physical comedy implicit in the early scene where the young soldier can barely stay awake despite his mortal peril.<br /><br />These reservations notwithstanding, this is a solid production of a wonderful play transferred to the small screen with aplomb. It deserves to be seen widely and, ideally, prompt an even livelier big screen remake with the style and zest of the recent remake of Wilde's AN IDEAL HUSBAND. Virtually *any* ARMS AND THE MAN is to be cherished, and with a lot of luck perhaps we'll even eventually get to see the original 1932 version. 'Till one or the other surfaces, this production will please anyone who loves good Shaw.`,
            `OK. There are people who should not see this movie.<br /><br />1) Don't see it if you don't like satire or black humour. 2) Don't like it if you got offended by _The Watchmen_. 3) Don't see it if you want a serious superhero movie.<br /><br />The rest of you, run, don't walk, to see _Mystery Men_. It's funny, it's quirky, it's a delightful sendup of every bad superhero cliche known to man. Occasional forays into junior-high humour don't ruin the tongue-in-cheek low-key fun of Jeanane Garafalo, Ben Stiller, and Hank Azaria, as well as a couple of amusing smaller parts by Geoffrey Rush and Greg Kinnear. (Good to see Louise Lasser getting work, too.) I laughed all the way through. Utterly unserious, somewhat weird, but -good-.`,
            `Where the Sidewalk Ends (1950)<br /><br />Where One Ends, Another Begins<br /><br />This is a prototypical film noir, and as such, pretty flawless, from both style and content points of view. The photography and night settings are first rate (cinematographer Joseph LaShelle lets the drama ooze in scene after scene), and the close-ups on faces pure expressionism. I can watch this kind of film for the visuals alone, even when the actors struggle and the plot stinks. <br /><br />But the acting is first rate here, and the plot features what I consider the core of most noir films, the alienated male lead (representing the many men returning home to a changed United States after the war and feeling lost themselves). In fact, not only is Dana Andrews really convincing as the troubled, loner detective, he has a small but important counterpart in the film, the lead female's (first) husband, an decorated ex-GI fallen onto hard times and booze. The fact the one man kills the other might be of monumental significance, overall-- the regular guy struggling through his inner problems to success while the medal-wearing soldier slips into an accidental death with a silver plate in his head. The woman transitions from one to the other--we assume they marry and have children as suggested earlier in the movie. Even if this is pushing an interpretation onto it after the fact, we can still see the path of one man with some psychological baggage careening through a crisis to the highest kind of moral order--turning himself in for a small crime just at the point he has actually gotten away with it.<br /><br />This movie belongs to Andrews. He plays a far more restrained and moving type than Kirk Douglas plays in a similar role in William Wyler's Detective Story made just one year later, and Andrews certainly is less theatrical. You could easily see both movies side by side for a textbook compare and contrast session. The fact that Andrews as Detective Dixon is morally struggling through it all, and Douglas as Detective McLeod is not, might explain why one man gets his girl and the other doesn't. Gene Tierney pulls off a hugely sympathetic, demurring, and ultimately conventional and "pretty" type of woman--not just a cardboard desirable, but someone you want Dixon to actually marry. <br /><br />The criminal plot is really secondary to the main drama, but is effective enough in its play with types and clichés. The bit parts are kept snappy, the small details (like the portable craps table) nice touches, far from the character actors or the glamour of gambling in Casablanca. But then, Curtiz's great movie is iconic even in the details--it makes no effort to be subtle and real and penetrating, but instead is sweeping and memorable and inspiring. They come at opposite ends of the war, and represent opposite possibilities for their leading men. Bogart is beginning his active duty, Dixon, and the man Dixon has killed, are all through. Through, thoroughly, but not washed up.<br /><br />It's no accident that many, possibly most, film noirs have what you would call "happy" endings. The man overcomes his adversaries and transforms his inner self, and the moviegoer, then and now, understands just how beautiful that must feel.`,
            `Many reviews here explain the story and characters of 'Opening Night' in some detail so I won't do that. I just want to add my comment that I believe the film is a wonderful affirmation of life.<br /><br />At the beginning Myrtle Gordon is remembering how 'easy' it was to act when she was 17, when she had youth and energy and felt she knew the truth. Experience has left her emotionally fragile, wondering what her life has been for and, indeed, if she can even continue living. A tragic accident triggers a personal crisis that almost overwhelms her.<br /><br />Almost - but not quite. At the eleventh hour she rediscovers the power of her art and reasserts herself ("I'm going to bury that bastard," she says of fellow actor Maurice as she goes on stage). It seems almost sadistic when Myrtle's director prevents people from helping her when she arrives hopelessly drunk for her first performance. He knows, however, that she has to have the guts to make it herself if she is to make it at all.<br /><br />Some critics wonder if this triumph is just a temporary pause on Myrtle's downward path. I believe this is truly her 'opening night' - she opens like a flower to new possibilities of life and action, she sees a way forward. It is tremendously moving.<br /><br />Gena Rowlands is superb. The film is superb. Thank you, Mr Cassavetes, wherever you are.`,
            `Winchester 73 gets credit from many critics for bringing back the western after WWII. Director Anthony Mann must get a lot of credit for his excellent direction. Jimmy Stewart does an excellent job, but I think Stephen McNalley and John McIntire steal the movie with their portrayal of two bad guys involved in a high stakes poker game with the treasured Winchester 73 going to the winner. This is a good script with several stories going on at the same time. Look for the first appearance of Rock Hudson as Young Bull. Thank God, with in a few years, we would begin to let Indians play themselves in western films. The film is in black and white and was shot in Tucson Arizona. I would not put Winchester 73 in the category of Stagecoach, High Noon or Shane, but it gets an above average recommendation from me.<br /><br />.`,
            `I have seen this movie and I must say that it is one of the best movies I have ever seen. `,
            `24 has got to be the best spy/adventure series TV had ever aired. The whole idea of telling a story in a 24 hour real time period is dazzling. The style of filming and pacing is what hooks us to watch it. And Jack Bauer is one of the greatest protagonists in a TV series in a long time. I rate this, along with The Simpsons and The X-Files, my three most favorite TV series.<br /><br />This first episode begins with the conspiracy to assassinate US Senator David Palmer who is also running for president. Bauer is called to his office in order to discover who is behind all this and, at the same time, figure his daughter's path to the unkwown after fleeing from her bedroom. Thus, begins an adventure on the best political style and, what's best of it, is that it always takes place in real time, which makes this TV series a real work of originality in a time where almost every program on TV seems to be showing us the same things over and over and over.`,
            `A great addition to anyone's collection.<br /><br />12 monkeys is a movie you don't see every day. It has excellent actors to go with a excellent story. This is not a normal role for Bruce Willis but he holds the role like he holds John McClane.<br /><br />The virus-kills everyone on earth and leaves a few hundred survivors story is not a new one but the story takes a fresh new direction on it.<br /><br />A man(Bruce)is sent back in time to get information on a virus which has wiped out most of man kind.<br /><br />The actors in this were awesome. I must give a mention to Brad Pitt who was hilarious as the mental patient James Cole(Bruce) meets in a mental hospital.<br /><br />The director did an amazing job on bringing us a disturbing picture of a future devastated by a man-made virus.<br /><br />The animals seen in the virus world made it feel like they run the world when humans are driven into underground facilities.<br /><br />This movie was excellent and must see and also its a must own.<br /><br />I very much highly recommend it.<br /><br />10/10`,
            `I saw this film at its premier at Sundance 09.<br /><br />Since American Beauty is a movie that had something to say, I had hopes for Towelhead. Unfortunately, it was a disappointment. In fact, of countless movies I've seen in almost a dozen Sundance festivals, Towelhead is the only Sundance movie I've ever wanted to walk out early from.<br /><br />The worst problem with Towelhead is that it so obviously originates with a collection of "provocative" concepts concerning cultural stereotypes, rather than with an organic human drama. The screenplay derives from the novel of the same name by Alicia Erian. The famous Edith Wharton quote comes to mind: I have never known a novel that was good enough to be good in spite of its being adapted to the author's political views. That observation is especially devastating for Towelhead because its political views are so stale and simplistic. If there ever was a time when Towelhead's white male villains, condescending portrayals of blacks, ironic treatments of foreign cultures, etc., were fresh, it's long past.<br /><br />For a more detailed review, please look up any of the many professional reviews available online. Almost all rate this movie poorly and expose the shallow and manipulative tissue it is based on.<br /><br />On the other hand, the amateur reviewers seem more easily bamboozled. As you read through the reviews in this and similar sites, you'll frequently come across superlatives: "stunning," "breathtaking," "profound," "shocking," ... It embarrasses me to read them, but it does not surprise me. Indeed, I've encountered many people who seem to regard any book or movie dealing with racial, cultural, gender, or sexual issues as deeply moving, thought provoking, full of profound insight. If you are such a person, by all means, rent Towelhead and be moved by it. On the other hand, if you set your standards higher, you can safely pass on this one.`,
            `Well, at least my theater group did, lol. So of course I remember watching Grease since I was a little girl, while it was never my favorite musical or story, it does still hold a little special place in my heart since it's still a lot of fun to watch. I heard horrible things about Grease 2 and that's why I decided to never watch it, but my boyfriend said that it really wasn't all that bad and my friend agreed, so I decided to give it a shot, but I called them up and just laughed. First off the plot is totally stolen from the first one and it wasn't really clever, not to mention they just used the same characters, but with different names and actors. Tell me, how did the Pink Ladies and T-Birds continue years on after the former gangs left? Not to mention the creator face motor cycle enemy, gee, what a striking resemblance to the guys in the first film as well as these T-Birds were just stupid and ridiculous.<br /><br />Another year at Rydell and the music and dancing hasn't stopped. But when a new student who is Sandy's cousin comes into the scene, he is love struck by a pink lady, Stephanie. But she must stick to the code where only Pink Ladies must stick with the T-Birds, so the new student, decides to train as a T-Bird to win her heart. So he dresses up as a rebel motor cycle bandit who can ride well and defeat the evil bikers from easily kicking the T-Bird's butts. But will he tell Stephanie who he really is or will she find out on her own? Well, find out for yourself.<br /><br />Grease 2 is like a silly TV show of some sort that didn't work. The gang didn't click as well as the first Grease did, not to mention Frenchy coming back was a bit silly and unbelievable, because I thought that she graduated from Rydell, but apparently she didn't. The songs were not really that catchy; I'm glad that Michelle was able to bounce back so fast, but that's probably because she was the only one with talent in this silly little sequel, I wouldn't really recommend this film, other than if you are curious, but I warned you, this is just a pathetic attempt at more money from the famous musical.<br /><br />2/10`,
            `Once again Canadian TV outdoes itself and creates another show that will go unwatched after its premiere episode. <br /><br />Last time I remember sitcoms were supposed to induce a reaction we in the business call laughter. How funny is it to beat the stereotype of all white people thinking that all Muslims are terrorists? OK maybe one joke just to stick it to the masses. But not 30 minutes. It's called beating a dead horse. Even SNL would know to give up after a commercial break.<br /><br />Also, let's have a little conflict in these scripts. Will she or won't she be able to serve cucumber sandwiches to break the fast on Ramadan? When will Ramadan start? Ohhhhh this is Emmy winning stuff here. <br /><br />And the characters! What characters?! They are all cardboard cut-outs without anything interesting to make us want to follow them from one situation to the next. That's the point of the situation comedy. We need to have strong, interesting, dynamic characters so that we are constantly drawn to the TV set each week. We have to care about these characters to worry about what trouble they're going to get into next week. If I never see these characters it'll be too soon. Thankfully I can't remember any of their names (note to CBC - that's not a good sign).<br /><br />And the acting is so bland. It's more so a problem in casting than in the actors. None of these people actually embody the characters they play. They just seem to act their part as though they were working on a movie of the week. Sitcoms require actors who live and breathe that character - make us fall in love with them - where they become inseparable from the character the portray. Watch any American sitcom and you'll see how easily identifiable characters are. Part of the problem is that the actors seem to treat this project as though it might be a platform to bigger and better things instead of being their one big character of a lifetime for whom they will spend the next 8 years portraying. That level of disinterest in the characters and the project shows. But to be honest, considering the lame concept and the horrible writing, there's not much for the actors to do but say their lines and try not to bump into any furniture. As another commenter mentions, this seems like a TV movie and not a sitcom.<br /><br />And the directing or lack there of! What can I say, Canada has so much talent, look at what the Comedy Channel is doing with Puppets Who Kill and Punched Up. Look at the Trailer Park Boys (not the movie cause it bit the big helium dog). Look at any American show to see the potentials our talent as that's where many of our stars go to find decent work.<br /><br />Give credit to the CBC, they really know how to build publicity for a non-event. Remember "The One"? No - well don't even try to learn any characters names in this show, as it's sure to go the way of the dodo.<br /><br />Let's all hope for a full blown ACTRA strike so that nothing like this emerges from the Ceeb for a good long while.`,
            `The idea had potential, but the movie was poorly scripted, poorly acted, poorly shot and poorly edited. There are lots of production flaws ... for example, Dr. Lane's daughter who never ages despite the passing years. Wait for video, but don't expect much.`,
            `Well, here we have yet another role reversal movie. There were many worth watching, despite the tired plot of gender reversal. However, this one is not. In previous reviews, I think I've made my point about the general decline of enjoyment for Haim movies that followed the late 80s. This is one of them.<br /><br />'Just One of the Girls' is about a high school kid (Corey Haim) who tries to avoid his bullies by dressing up as a girl and attending another school. He joins the cheerleading squad and makes friends with fellow cheerleader, Marie (Nicole Eggert). Obviously, he can't keep up the charade for too much longer.<br /><br />I thought this movie was utter crap, and it wasn't even funny. But, judging by a majority of reviews, it looks like fans of Alanis Morrisette or teen sex queen, Nicole Eggert, are the only ones who'd want to watch this. If you're looking for a good Haim feature (or role switching comedy), look no further than 1989. This is about the point that Haim's career tanked.`,
            `Why did I waste my money on this on the last day of Sundance? I want a refund... Can I have my $16 back? While I was watching this film I kept waiting for something to happen, nothing did happen. The only way I even knew what it was supposed to be about was by reading the plot, which was not really like the film. why did the director zoom in with their handy cam and then zoom out? It was not very artistic. Why did the director show Lulu filing her nails for fifteen minutes? Why is it when the actors tried to speak they sounded like they were reading? Or was that the point? I felt like Phantom Love had no story at all, and to be honest I felt like my friends vacation videos had a much higher entertainment value than this film.`,
            `I can't tell you how angry I was after seing this movie. The characters are not the slightest bit interesting, and the plot is non-existant. So after waiting to see how the lives of these characters affected each other, hoping that the past 2 and a half hours were leading up to some significant finish, what do we get??? A storm of frogs. Now yes, I understand the references to the bible (Exodus) and the underlying theme, but first of all, it was presented with absolutely no resolution, and second of all it would be lost to anyone who has not read the bible (a significant portion of the population) or Charles Fort (a still larger portion). As a somewhat well read person, I thought this movie was a self indulgent poor imitation of a seinfeld episode.<br /><br />Don't waste your time. It would be better spent reading...<br /><br />...well anything to be honest`
          ];
          const randomIndex = Math.floor(Math.random() * randomReviews.length);
          setComments([...comments, randomReviews[randomIndex]]);
          // setComments([...comments, "Movie is amazing"])
        }}
      >
        Add Comment
      </button>
      {mutation.isPending ? <div style={{ display: "grid" , placeItems: "center", height: "100px" }}>
        <CirclesWithBar
        height="100"
        width="100"
        color="#4fa94d"
        outerCircleColor="#4fa94d"
        innerCircleColor="#4fa94d"
        barColor="#4fa94d"
        ariaLabel="circles-with-bar-loading"
        wrapperStyle={{}}
        wrapperClass=""
        visible={true}
  />
      </div> : comments.map((comment, i) => (
    <div key={i} style={{ display: "flex", justifyContent: "center", gap: "1rem", marginBottom: "1rem" }}>
      <input
        style={{
          flex: 1,
          padding: "0.5rem",
          borderRadius: "4px",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          backgroundColor: "#1a1a1a",
          color: "inherit",
        }}
        type="text"
        value={comment}
        onChange={(e) => {
          const newComments = comments.slice();
          newComments[i] = e.target.value;
          setComments(newComments);
        }}
      />
      <button
        style={{
          backgroundColor: "#f44336",
          color: "#fff",
        }}
        onClick={() => {
          const newComments = comments.slice();
          newComments.splice(i, 1);
          setComments(newComments);
          setReviews(reviews.filter((_, index) => index !== i));
        }}
      >
        Delete
      </button>
      {reviews?.at(i) && <div style={{ alignSelf: "center" , padding: '1rem', borderRadius: '2rem' ,backgroundColor: (reviews?.at(i)?.probability ?? 0) > 0.5 ? 'green' : 'red' }}>
        <b>{reviews?.at(i)?.label}</b> {reviews?.at(i)?.probability?.toFixed(2)}
      </div>}
      
    </div>
  ))}
      
    
      <button
        onClick={async () => {
          // const response = await fetch(`https://nlp-comments-analyser.onrender.com/predict/`, {
          //   method: "POST",
          //   headers: { "Content-Type": "application/json" },
          //   body: JSON.stringify({ comments, model: modelType }),
          // });
          // const data = await response.json();
          // setReviews(data.results);
          mutation.mutate();
        }}
      >
        Send to Check
      </button>
    </div>
  );
}

export default App;
