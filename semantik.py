#%% import googletrans as gt
import textblob as tb
import nltk
nltk.download('punkt')
nltk.download('movie_reviews')

from textblob import Blobber

from textblob.sentiments import NaiveBayesAnalyzer
blobber = Blobber(analyzer=NaiveBayesAnalyzer())


class Text_analyzer:

    def __init__(self, text, lang="en"):
        """Constructor"""
        self.text = text
        self.text_blob = tb.TextBlob(text)
        self.words_list = self.text_blob.words
        self.lang = lang

    def print_self(self):
        return self.text_blob

    def words_with_errors(self):
        error_words_list = []
        for word in self.words_list:
            word_check = word.spellcheck()
            if word != word_check[0][0]:
                error_words_list.append(word)
        return (error_words_list)

    def get_sentiment(self):
        sentiment = blobber(self.text).sentiment
        # sentiment = self.text_blob.correct().sentiment
        return (sentiment)

    def get_lang(self):
        return (self.text_blob.correct().detect_language())

    def get_translate(self):
        try:
            # return(gt.translator.translate(self.text_blob.correct(), dest='ru'))
            return (self.text_blob.correct().translate(to=self.lang))
        except:
            return (self.print_self())

#%%

chat_text = "Thank you, Mickael"

sentense = Text_analyzer(chat_text)

sentiment = sentense.get_sentiment()

sentiment

# print(sentense.words_with_errors)
# print(sentense.get_sentiment())
