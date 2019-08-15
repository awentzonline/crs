import os

import click
import numpy as np


class RhymingDict:
    """
    For use with file from http://www.speech.cs.cmu.edu/cgi-bin/cmudict
    """
    def __init__(self, path):
        self.load_pronunciations(path)

    def load_pronunciations(self, path):
        self.words, self.sounds = [], []
        with open(path, 'rb') as in_file:
            for line in in_file.readlines():
                line = line.decode('latin1')
                if line.startswith(';;;'):
                    continue
                parts = line.split()
                parts = list(map(lambda x: x.strip(), parts))
                word = parts.pop(0)
                self.words.append(word)
                self.sounds.append(parts)
        self.word_lookup = dict(zip(self.words, self.sounds))

    def best_rhymes(self, target_word, n=20):
        target_word = target_word.upper()
        target_sounds = self.word_lookup[target_word]
        words, scores = [], []
        for i, (word, sounds) in enumerate(zip(self.words, self.sounds)):
            if word == target_word:
                continue
            max_len = min(len(target_sounds), len(sounds))
            j = 1
            while j <= max_len:
                if sounds[-j] != target_sounds[-j]:
                    break
                j += 1
            if j > 0:
                words.append(word)
                scores.append(j)
        sorted_indexes = np.argsort(scores)[-n:][::-1]
        words = [words[i] for i in sorted_indexes]
        scores = [scores[i] for i in sorted_indexes]
        return words, scores

    def distance(self, word_a, word_b):
        """Length of common suffix between words."""
        word_a, word_b = word_a.upper(), word_b.upper()
        s_a = self.word_lookup[word_a]
        s_b = self.word_lookup[word_b]
        j = 1
        max_len = min(len(s_a), len(s_b))
        while j <= max_len:
            if s_a[-j] != s_b[-j]:
                break
            j += 1
        return j


@click.command()
@click.argument('dict_path')
def main(dict_path):
    rd = RhymingDict(dict_path)
    print(rd.best_rhymes('rhyme'))
    print(rd.distance('poop', 'hoop'))


if __name__ == '__main__':
    main()
