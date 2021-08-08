import argparse
import os
import string
import sys

from os import path
from wordcloud import WordCloud

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main(args):
	USER = args.username
	DIRPATH = os.path.join(os.getcwd(), USER)
	DATAPATH = os.path.join(os.getcwd(), USER, USER + ".csv")

	if not os.path.isdir(USER) or not os.path.exists(DATAPATH ):
		print("Could not find csv output of scrape.py at ", DATAPATH)
		exit()
	
	# Read data into dataframe
	data = pd.read_csv(DATAPATH)
	data.columns = ['post', 'post_type', 'caption', 'likes', 'views', 'date']

	# Save plot of likes over time
	likes_path = os.path.join(DIRPATH, "likes.png")
	plot(data, 'post', ['likes'], ['Likes'], save_path=likes_path, xlabel='Post', ylabel='Likes', title='@' + USER)

	# Generate wordcloud visualization
	data['caption_processed'] = data['caption'].map(lambda x: process_raw_caption(x))
	word_bag = ','.join(list(data['caption_processed'].values))
	wordcloud = WordCloud(background_color="white", max_words=1000, contour_width=3, contour_color='steelblue')
	wordcloud.generate(word_bag)
	WORD_CLOUD_PATH = os.path.join(USER, 'wordcloud.png')
	wordcloud.to_file(WORD_CLOUD_PATH)


def plot(df, x, y, labels, save_path=None, xlabel=None, ylabel=None, title=None):
	for i, label in zip(y, labels):
		plt.plot(df[x], df[i], label=label)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.legend()
	plt.title(title)
	if save_path is not None:
		plt.savefig(save_path)

def process_raw_caption(caption):
	stop_words = set(stopwords.words('english'))
	caption = caption.lower().strip()
	caption = re.compile('<.*?>').sub('', caption)
	caption = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', caption)
	caption = re.sub('\s+', ' ', caption)
	filtered_words  = [word for word in caption.split() if word not in stop_words]
	caption = ' '.join(filtered_words)
	return caption

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("username", help="Instagram username to process. Expects to find output of scrape.py (<username>.csv) at ./<username>")
	args = parser.parse_args()
	main(args)
