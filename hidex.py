from os import makedirs

import os
import shutil
#import itertools
import tempfile
import subprocess

HIDEX_CONFIG_DICT = {
    ## dbname: Name of the database to be worked on.
    ## This setting allows one to work with multiple databases in the same
    ## directory.
    'dbname': 'combined',

    ## dbpath: [Optional!] An absolute path for the working directory
    ## If not set, HiDEx will use the CurrentWorkingDirectory.
    'dbpath': '/var/opt/ENV/lib/hidex/work/',

    ## dictFilename: Name of the Lexicon file, assumed to be in the Working Directory
    'dictFilename': 'lexicon.txt',

    ## maxWindowBehind: Maximum size of word window behind target word
    'maxWindowBehind': 10,

    ## maxWindowAhead: Maximum size of word window ahead of target word
    'maxWindowAhead' :10,

    ## corpusFilename: The filename of the corpus. Assumed to be in the Working Directory.
    'corpusFilename':'corpus.txt',

    ## stepsize: The number of vectors to collect per pass through the corpus. If
    ## you run out of memory during an "update", reduce this value. If you find
    ## that you have more RAM to spare when running update, increase this value.
    'stepsize': 8000,

    ## eod: End of Document marker. Used when processing the corpus.
    'eod': '---END.OF.DOCUMENT---',

    ## outputpath: [Optional] An absolute path for program output. Defaults to
    ## Current Working Directory.
    'outputpath': '/var/opt/ENV/lib/hidex/work/',

    ## normalization: Choose your method for vector normalization here. Default is
    ## co-occurence divided by target word frequency. Other possibilities are PPMI
    ## (Positive Pointwise Mutual Information) and Correlation.
    'normalization': 'PPMI',

    ## weightingScheme: Code number to choose a weighting scheme. The names are
    ## fairly self explanatory! The original HAL model used #1, Ramped Linear
    #  FLAT = 0
    #  RAMPED LINEAR = 1
    #  RAMPED EXPONENTIAL = 2
    #  FORWARD RAMP = 3
    #  BACKWARD RAMP = 4
    #  INVERSE RAMP = 5
    #  INVERSE EXPONENTIAL = 6
    #  SECOND WORD = 7
    #  THIRD WORD = 8
    #  FOURTH WORD = 9
    'weightingScheme': 1,
    ## contextSize: The number of dimensions to use in the co-occurrence
    ## vector. Only the N most frequent word's vectors are included.
    'contextSize': 100,
    ## saveGCM: if it is 0, the Global Co-occurrence Matrix will not be saved
    ## after it is created. If it is 1, a new GCM will be saved to disk every time one is
    ## created in memory. Saving the GCM can save a lot of processing time if the
    ## same parameters are used repeatedly.
    'saveGCM': 0,
    ## metric: Choose your similarity metric here. If it is blank, HiDEx will
    ## default to using (inverse) Euclidean distance. Other possible values are
    ## Cosine and Correlation
    'metric': 'Cosine',
    ## windowLenBehind: Size of the window behind the target word. Can be any number from
    ## 1 to MaxWindowLenBehind.
    'windowLenBehind': 8,

    ## windowLenAhead: Size of the window behind the target word. Can be any number from
    ## 1 to MaxWindowLenAhead.
    'windowLenAhead': 8,

    ## useThreshold: Setting to turn on z-score based neighborhood membership
    ## thresholds (words more that 1 standard deviation similar than the average
    ## similarity. 1 means it is ON, 0 means it is OFF.
    'useThreshold': 1,

    ## neighbourhoodSize: When not using neighborhood thresholds, the number of
    ## neighbors to find. Any number greater than 1
    'neighbourhoodSize': 2,

    ## separate: Enables seperate forward and backward vectors when set to 1. When
    ## set to 0, Forward and Backward vectors are combined, halving the context size.
    'separate': 1,

    ## percenttosample: When using thresholds, the percent of pairs to sample
    ## during the calculation of the z-scores. 0.1 means 10%.
    'percenttosample': 0.1,

    ## wordlistfilename: List of words to analyze (can be a list of words, one per
    ##line, or a list of pairs, two words per line, separated by tabs.
    'wordlistfilename': 'words.txt',

    ## wordlistsize: If this number is smaller than the number of words in the
    ## wordlist, HiDEx will pick a random subset of the words in the wordlistfile
    ## to use. If this number is larger than the number of words in the
    ## wordlistfile, HiDEx will use all the words in the file.
    'wordlistsize': 1000,

    ## normCase: Apply case normalization globally. This option will take
    ## any Unicode character than can have a lower-case glyph, and replace
    ## it with that glyph. The default mode is 1 (true). To stop case
    ## normalization, set this to 0 (false). There is one more important
    ## factor to correct case normalization: your shell's environment
    ## variable settings for the LANG variable. HiDEx will check this
    ## setting and appy the correct normalization only if this is set to
    ## the correct language. For example, if you are processing German,
    ## your LANG setting should be set to de_DE.UTF-8
    'normCase': 1,

    ## englishContractions: In English, the string "'s" is a contraction
    ## that can make it difficult for the model to recognize words that
    ## are possessives.  This defaults to 1 (true), which means that words
    ## like "ball's" will be split into two words, "ball" and "'s" and
    ## "can't" will become "can" and "'nt".
    'englishContractions': 1}


class HidexCorpus(object):

    def __init__(self, corpus_list, hidex_path, username, lexicon_path):
        self.HIDEX_PATH = hidex_path
        self.corpus = []
        #corpus_list contains a list of text content from the various texts you want to be part of your corpus.
        self.corpus_list = corpus_list

        self.username = username
        self.config_dict = HIDEX_CONFIG_DICT
        self.work = self.HIDEX_PATH + '/' + self.username + '/' + 'work'
        self.lexicon_path = lexicon_path

    def create_corpus_file(self):
         #creates the corpus.txt file you are about to process.
         #takes a list of txt content that you want to combine into the corpus.txt file.
        if os.path.exists(self.work) == False:
            makedirs(self.work)

        with open(os.path.join(self.work, 'corpus.txt'), 'wb') as file:
            for item in self.corpus_list:

                file.write(item.encode('UTF-8') + '\n')
                file.write('---END.OF.DOCUMENT---' + ' \n')
            file.close()

    def create_config_file(self, option_changes):
        #takes a python dictinonary name option changes containing the option names and the
        #corresponding option values that you want to change.
        for key, value in option_changes.iteritems():
            self.config_dict[key] = value

        with open(os.path.join(self.work, 'config.txt'), 'wb') as file:
            for key, value in self.config_dict.iteritems():
                file.write(str(key)+'='+str(value)+'\n')
            file.close()

    def create_lexicon(self):
        #copies the lexicon into your working directory so that hidex can use it.
        #the lexicon file must be named lexicon.txt
        shutil.copy2(self.lexicon_path, self.work + '/lexicon.txt')

    def create_words_file(self, list_of_words):
        self.list_of_words = list_of_words
        with open(os.path.join(self.work, 'words.txt'), 'wb') as file:
            for word in list_of_words:
                file.write(word + '\n')
            file.close()

    def create_empty_datastore(self):
        #create a new empty data store
        shell_command = self.HIDEX_PATH  + '/hidex -f ' + os.path.join(self.work, 'config.txt') + ' -m create'
        process = subprocess.Popen([shell_command], shell=True, stdin=tempfile.TemporaryFile(), stdout=tempfile.TemporaryFile(), stderr=tempfile.TemporaryFile())
        process.wait()
        process.communicate()
        return shell_command

    def update(self):
        #create a new empty data store
        shell_command = self.HIDEX_PATH + '/hidex -f ' + os.path.join(self.work, 'config.txt') + ' -m update'
        process = subprocess.Popen([shell_command], shell=True, stdin=tempfile.TemporaryFile(), stdout=tempfile.TemporaryFile(), stderr=tempfile.TemporaryFile())
        process.wait()
        process.communicate()
        return shell_command

    def get_vectors(self):
        shell_command = self.HIDEX_PATH + '/hidex -f ' + os.path.join(self.work, 'config.txt') + ' -m getvectors'
        process = subprocess.Popen([shell_command], shell=True, stdin=tempfile.TemporaryFile(), stdout=tempfile.TemporaryFile(), stderr=tempfile.TemporaryFile())
        process.wait()
        process.communicate()
        return shell_command

    def get_similarity(self):
        shell_command = self.HIDEX_PATH + '/hidex -f ' + os.path.join(self.work, 'config.txt') + ' -m getsimilarity'
        process = subprocess.Popen([shell_command], shell=True, stdin=tempfile.TemporaryFile(), stdout=tempfile.TemporaryFile(), stderr=tempfile.TemporaryFile())
        process.wait()
        process.communicate()
        return shell_command

    def get_neighbors(self):
        shell_command = self.HIDEX_PATH + '/hidex -f ' + os.path.join(self.work, 'config.txt') + ' -m getneighbors'
        process = subprocess.Popen([shell_command], shell=True, stdin=tempfile.TemporaryFile(), stdout=tempfile.TemporaryFile(), stderr=tempfile.TemporaryFile())
        process.wait()
        process.communicate()

        return shell_command

    def parse_return_data(self, return_data):
        words = return_data.split()
        data = []
        list_size = len(words)
        iterations = (list_size - 4) / 4
        count = 0

        while count < iterations:


            data.append([words[0] + ': ' + words[(4 + (4*count))], words[1] + ': ' + words[(5 + (4*count))], words[2] + ': ' + words[(6 + (4*count))],
                        words[3] + ': ' + words[(7 + (4*count))]])

            count = count + 1
        return data

    def get_neighbor_data(self):
        #Grabs the output from file and returns it as a list of word data values
        data_dict = []
        for item in self.list_of_words:
            filename = self.work + '/output./wordneighborhoods/' + item + '.nbr.txt'
            try:
                file = open(filename.lower(), 'r')
                info = file.read()
                data_dict.append(self.parse_return_data(info))
                file.close()
            except IOError:
                data_dict.append(item +": This word does not seem to appear in your text.")

        return data_dict

    def clean_up(self):
        shutil.rmtree(self.HIDEX_PATH + '/' + self.username)












