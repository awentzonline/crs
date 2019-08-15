import re

import click
from gensim.models.phrases import Phrases, Phraser

from rhymedict import RhymingDict


def load_corpus(path):
    re_ws = re.compile(r'\s+')
    re_sentence = re.compile(r'[!\?\.]')
    re_punct = re.compile(r"[\",=]+")
    with open(path, 'rb') as infile:
        lines = infile.readlines()
    corpus = b' '.join(lines)
    corpus = corpus.decode('latin1')
    corpus = re_punct.sub(' ', corpus).lower()
    corpus = re_ws.sub(' ', corpus).lower()
    sentences = re_sentence.split(corpus)
    split_sentences = [s.split() for s in sentences]
    return split_sentences


def get_phrases(corpus, threshold=0.6, min_count=2):
    phraser_model = Phrases(
        corpus,
        min_count=min_count,
        threshold=threshold,
        scoring='npmi',
        max_vocab_size=40000000,  # default
        delimiter=b'_',
        progress_per=10000
    )
    phraser = Phraser(phraser_model)
    return phraser, phraser_model


@click.command()
@click.argument('dict_path')
@click.argument('corpus_path')
def main(dict_path, corpus_path, min_word_length=3):
    """
    Steps:
     * Find popular bigrams in a corpus (B0,B1)
     * Find rhyme R1 with B1
     * cockney(R1) -> B0
    """
    print('Loading corpus...')
    corpus = load_corpus(corpus_path)
    print('Loading rhyming dict')
    rd = RhymingDict(dict_path)
    phraser, phraser_model = get_phrases(corpus)
    bigrams = set([gram for gram, _ in phraser_model.export_phrases(corpus)])
    for bigram in bigrams:
        bigram = bigram.decode()
        a, b = bigram.split()
        if len(b) < min_word_length or len(a) < min_word_length:
            continue
        try:
            best_rhymes = rd.best_rhymes(b, n=10)[0]
        except KeyError:
            print(f'unknown word: {b}')
            continue
        for rhyme in best_rhymes:
            rhyme = rhyme.lower()
            # ensure the matching words aren't sub-words of each other
            if rhyme in b or b in rhyme:
                continue
            if len(rhyme) < min_word_length:
                continue
        print(f'{a} -> {rhyme} because "{a} {b}"')


if __name__ == '__main__':
    main()
