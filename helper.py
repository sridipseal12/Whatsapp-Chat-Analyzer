import re
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter

extract = URLExtract()
def fetch_stats(selected_user, df):
    # Filter the DataFrame if a specific user is selected
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # total number of messages
    num_messages = df.shape[0]

    # number of words
    words = []
    for message in df['message']:
        if isinstance(message, str):
            words.extend(message.split())

    # number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round(df['user'].value_counts()/df.shape[0]*100, 2).reset_index().rename(columns={"index" : "name", "user" : "percent"})
    return x, df

def create_wordcloud(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)   # forms the sentence again

    wc = WordCloud(width=1500, height=900, min_font_size=10, background_color='white') # sets the resolution of the image(width, height). more resolution will take more time to print
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    # temp = temp[temp['message'] != ',']
    temp = temp[temp['message'] != 'This message was deleted\n']

    # Regular expression pattern to match emojis
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"  # other additional symbols
                               u"\U0001F970-\U0001F976"  # 🥲
                               u"\U0001FAE0-\U0001FAE8"  # 🫠
                               u"\u2620\ufe0f"           # ☠️
                               "]+", flags=re.UNICODE)

    tagged_user_pattern = re.compile(r'@\d+')
    # on removing 10, % is coming although I have removed symbols.

    words = []
    for message in temp['message']:
        message = emoji_pattern.sub(r'', message)
        message = tagged_user_pattern.sub(r'', message)
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    filtered_df = pd.DataFrame(Counter(words).most_common(20))
    return filtered_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    d_timeline = df.groupby('only_date').count()['message'].reset_index()
    return d_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
