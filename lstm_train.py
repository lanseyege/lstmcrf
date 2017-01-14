from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
from data import get_vocab, load_train_data, data_iter
from model_lstm2 import LSTM

sen_len = 40
label_num = 5
sparse_len = 140
crf_num = 10720
learning_rate = 0.01
batch_size = 10
num_epoch = 20
dropout = True

print('read vocab ...')
vocab_size, embedding_size, embedding, vocab_w2i = get_vocab()
num_hidden = embedding_size

label_onehot = {}
label_hotone = {}
label_onehot['b-person'] = 1
label_onehot['i-person'] = 2
label_onehot['b-organization'] = 3
label_onehot['i-organization'] = 4
label_onehot['o'] = 0
label_hotone[1] = 'b-person'
label_hotone[2] = 'i-person'
label_hotone[3] = 'b-organization'
label_hotone[4] = 'i-organization'
label_hotone[0] = 'o'
label_m = np.array([[0, 0, 0, 0, 0], 
        [0, 0, 0, 0, 1], 
        [0, 0, 0, 1, 0], 
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0]])

files = []
dirs = '../OpenTargetedSentiment/data/pipe_en/'
for i in range(10):
    files.append('train'+str(i+1)+'.nn.ner')

files_t = []
for i in range(10):
    files_t.append('test'+str(i+1)+'.nn.ner')

for i in range(10):
    print('file ' + str(i+1))
    fw = open(dirs + files_t[i] + '.pipe.crf1', 'w')
    print('load train')
    doc, label, sparse = load_train_data(dirs+files[i], vocab_w2i, sen_len, sparse_len, crf_num, label_num, label_onehot)
    print('load test')
    doc_t, label_t, sparse_t = load_train_data(dirs+files_t[i], vocab_w2i, sen_len, sparse_len, crf_num, label_num, label_onehot)
    with tf.Graph().as_default():
        sess = tf.Session()
        with sess.as_default():
            lstm = LSTM(sen_len, num_hidden, label_num, vocab_size, embedding_size, embedding, learning_rate, label_m)
            sess.run(tf.initialize_all_variables())
            def train_step(input_, label_, d):
                feed_dict = {
                    lstm.input : input_,
                    lstm.label : label_,
				    lstm.dropout: d
                }
                _, lss = sess.run([lstm.trains, lstm.loss], feed_dict)
            def test_step(input_, label_, d, fw):
				totals_ = 0
				corrects_ = 0
				feed_dict = {lstm.input : input_, lstm.dropout:d}
				targets = sess.run([lstm.targets], feed_dict)
				lens = sess.run(lstm.sen_lens)
				print(targets)
				#corrects_ += cal
				#totals_ += lens
				for targets_, l_, lens_ in zip(targets, label_, lens):
					t = targets[:lens_]
					l = l_[:lens_]
					for k in range(lens_):
						fw.write(label_hotone[l[k]] + ' ' + label_hotone[t[k]] + '\n')
					fw.write('\n')
				return corrects_, totals_

			data = data_iter(doc, label, sparse, num_epoch, batch_size)
			for input_, label_ in data:
				train_step(input_, label_, True)
				corrects = 0
				totals = 0
			test_data = data_iter(doc_t, label_t, sparse_t, 1, 1)
			#trans = sess.run(lstm.trans)
			for input_, label_ in test_data:
				corrects_, totals_ = test_step(input_, label_, False, fw)
				corrects += corrects_
				totals += totals_
			print('accurry: ' + str(1.0 * corrects / totals))
			fw.close()

