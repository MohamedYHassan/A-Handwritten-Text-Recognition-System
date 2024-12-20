from collections import namedtuple
import os
import sys
from typing import List, Tuple
import numpy as np
import tensorflow as tf
from collections import defaultdict



Batch = namedtuple('Batch', 'imgs, gt_texts, batch_size')
# Disable eager mode
tf.compat.v1.disable_eager_execution()


class DecoderType:

    BestPath = 0
    BeamSearch = 1

class HTRModel:

    def __init__(self,
                 char_list: List[str],
                 decoder_type: int = DecoderType.BestPath,
                 must_restore: bool = False,
                 dump: bool = False) -> None:
        
        self.dump = dump
        self.char_list = char_list
        self.decoder_type = decoder_type
        self.must_restore = must_restore
        self.snap_ID = 0



        self.is_train = tf.compat.v1.placeholder(tf.bool, name='is_train')

        self.input_imgs = tf.compat.v1.placeholder(tf.float32, shape=(None, None, None))

        # Setup CNN-RNN-CTC
        self.setup_cnn()
        self.setup_rnn()
        self.setup_ctc()

        # Setup Adam optimizer
        self.batches_trained = 0
        self.update_ops = tf.compat.v1.get_collection(tf.compat.v1.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(self.update_ops):
            self.optimizer = tf.compat.v1.train.AdamOptimizer().minimize(self.loss)

        # Initialize TensorFlow session and saver
        self.sess, self.saver = self.setup_tf()

    def setup_cnn(self) -> None:

        cnn_in4d = tf.expand_dims(input=self.input_imgs, axis=3)

        # List of parameters
        kernel_vals = [5, 5, 3, 3, 3]
        feature_vals = [1, 32, 64, 128, 128, 256]
        stride_vals = pool_vals = [(2, 2), (2, 2), (1, 2), (1, 2), (1, 2)]
        num_layers = len(stride_vals)

        # Creating the layers
        pool = cnn_in4d  # Input to the first CNN layer
        for i in range(num_layers):
            kernel = tf.Variable(
                tf.random.truncated_normal([kernel_vals[i], kernel_vals[i], feature_vals[i], feature_vals[i + 1]],
                                           stddev=0.1))
            conv = tf.nn.conv2d(input=pool, filters=kernel, padding='SAME', strides=(1, 1, 1, 1))
            conv_norm = tf.compat.v1.layers.batch_normalization(conv, training=self.is_train)
            relu = tf.nn.relu(conv_norm)
            pool = tf.nn.max_pool2d(input=relu, ksize=(1, pool_vals[i][0], pool_vals[i][1], 1),
                                    strides=(1, stride_vals[i][0], stride_vals[i][1], 1), padding='VALID')

        self.cnn_out_4d = pool

    def setup_rnn(self) -> None:

        rnn_in3d = tf.squeeze(self.cnn_out_4d, axis=[2])

        # LSTM cells used to build multiRNN
        num_hidden = 256
        cells = [tf.compat.v1.nn.rnn_cell.LSTMCell(num_units=num_hidden, state_is_tuple=True) for _ in
                 range(2)]  # 2 layers

        # Stack LSTM cells
        stacked = tf.compat.v1.nn.rnn_cell.MultiRNNCell(cells, state_is_tuple=True)

        # Bidirectional RNN
        # BxTxF -> BxTx2H
        (fw, bw), _ = tf.compat.v1.nn.bidirectional_dynamic_rnn(cell_fw=stacked, cell_bw=stacked, inputs=rnn_in3d,
                                                                dtype=rnn_in3d.dtype)

        # BxTxH + BxTxH -> BxTx2H -> BxTx1x2H
        concat = tf.expand_dims(tf.concat([fw, bw], 2), 2)

        # Project output to chars (including blank token): BxTx1x2H -> BxTx1xC -> BxTxC
        kernel = tf.Variable(tf.random.truncated_normal([1, 1, num_hidden * 2, len(self.char_list) + 1], stddev=0.1))
        self.rnn_out_3d = tf.squeeze(tf.nn.atrous_conv2d(value=concat, filters=kernel, rate=1, padding='SAME'),
                                     axis=[2])

    def setup_ctc(self) -> None:

        # BxTxC -> TxBxC
        self.ctc_in_3d_tbc = tf.transpose(a=self.rnn_out_3d, perm=[1, 0, 2])
        # Ground truth text as sparse tensor
        self.gt_texts = tf.SparseTensor(tf.compat.v1.placeholder(tf.int64, shape=[None, 2]),
                                        tf.compat.v1.placeholder(tf.int32, [None]),
                                        tf.compat.v1.placeholder(tf.int64, [2]))

        # Calculate loss for batch
        self.seq_len = tf.compat.v1.placeholder(tf.int32, [None])
        self.loss = tf.reduce_mean(
            input_tensor=tf.compat.v1.nn.ctc_loss(labels=self.gt_texts, inputs=self.ctc_in_3d_tbc,
                                                  sequence_length=self.seq_len,
                                                  ctc_merge_repeated=True))

        # Calculate loss for each element to compute label probability
        self.saved_ctc_input = tf.compat.v1.placeholder(tf.float32,
                                                        shape=[None, None, len(self.char_list) + 1])
        self.loss_per_element = tf.compat.v1.nn.ctc_loss(labels=self.gt_texts, inputs=self.saved_ctc_input,
                                                         sequence_length=self.seq_len, ctc_merge_repeated=True)

        # Best path decoding or beam search decoding
        if self.decoder_type == DecoderType.BestPath:
            self.decoder = tf.nn.ctc_greedy_decoder(inputs=self.ctc_in_3d_tbc, sequence_length=self.seq_len)
        elif self.decoder_type == DecoderType.BeamSearch:
            self.decoder = tf.nn.ctc_beam_search_decoder(inputs=self.ctc_in_3d_tbc, sequence_length=self.seq_len,
                                                         beam_width=50)
            
       
    def setup_tf(self) -> Tuple[tf.compat.v1.Session, tf.compat.v1.train.Saver]:

        print('Python: ' + sys.version)
        print('TensorFlow: ' + tf.__version__)

        sess = tf.compat.v1.Session()  # TensorFlow session

        saver = tf.compat.v1.train.Saver(max_to_keep=1) 
        model_dir = '/Users/fofejo/Documents/GitHub/GP/backend/flask/model/checkpoint'
        latest_snapshot = tf.train.latest_checkpoint(model_dir)  # Check for a saved model

        if self.must_restore and not latest_snapshot:
            raise Exception('No saved model found in: ' + model_dir)

        # Load the saved model if available
        if latest_snapshot:
            print('Init with stored values from ' + latest_snapshot)
            saver.restore(sess, latest_snapshot)
        else:
            print('Init with new values')
            sess.run(tf.compat.v1.global_variables_initializer())

        return sess, saver

    def to_sparse(self, texts: List[str]) -> Tuple[List[List[int]], List[int], List[int]]:

        indices = []
        values = []
        shape = [len(texts), 0] 

        # Iterate over all texts
        for batch_element, text in enumerate(texts):
            # Convert to string of label (i.e., class-ids)
            label_str = [self.char_list.index(c) for c in text]
            # Sparse tensor must have a size of max. label-string
            if len(label_str) > shape[1]:
                shape[1] = len(label_str)
            # Put each label into sparse tensor
            for i, label in enumerate(label_str):
                indices.append([batch_element, i])
                values.append(label)

        return indices, values, shape

    def decoder_output_to_text(self, ctc_output: tuple, batch_size: int) -> List[str]:

        # CTC returns a tuple, the first element is SparseTensor
        decoded = ctc_output[0][0]

        # Contains a string of labels for each batch element
        label_strs = [[] for _ in range(batch_size)]

        # Go over all indices and save mapping: batch -> values
        for (idx, idx2d) in enumerate(decoded.indices):
            label = decoded.values[idx]
            batch_element = idx2d[0]  # Index according to [b,t]
            label_strs[batch_element].append(label)

        # Map labels to chars for all batch elements
        return [''.join([self.char_list[c] for c in labelStr]) for labelStr in label_strs]

    def train_batch(self, batch: Batch) -> float:

        num_batch_elements = len(batch.imgs)
        max_text_len = batch.imgs[0].shape[0] // 4
        sparse = self.to_sparse(batch.gt_texts)
        eval_list = [self.optimizer, self.loss]
        feed_dict = {self.input_imgs: batch.imgs, self.gt_texts: sparse,
                     self.seq_len: [max_text_len] * num_batch_elements, self.is_train: True}
        _, loss_val = self.sess.run(eval_list, feed_dict)
        self.batches_trained += 1
        return loss_val

    @staticmethod
    def dump_nn_output(rnn_output: np.ndarray) -> None:

        dump_dir = '../dump/'
        if not os.path.isdir(dump_dir):
            os.mkdir(dump_dir)

        # Iterate over all batch elements and create a CSV file for each one
        max_t, max_b, max_c = rnn_output.shape
        for b in range(max_b):
            csv = ''
            for t in range(max_t):
                csv += ';'.join([str(rnn_output[t, b, c]) for c in range(max_c)]) + ';\n'
            fn = dump_dir + 'rnnOutput_' + str(b) + '.csv'
            print('Write dump of NN to file: ' + fn)
            with open(fn, 'w') as f:
                f.write(csv)



    def infer_batch(self, batch: Batch, calc_probability: bool = False, probability_of_gt: bool = False):

        num_batch_elements = len(batch.imgs)

        # Put tensors to be evaluated into a list
        eval_list = []

        eval_list.append(self.decoder)

        if self.dump or calc_probability:
            eval_list.append(self.ctc_in_3d_tbc)

        # Sequence length depends on input image size (model downsizes width by 4)
        max_text_len = batch.imgs[0].shape[0] // 4

        # Dictionary containing all tensors fed into the model
        feed_dict = {self.input_imgs: batch.imgs, self.seq_len: [max_text_len] * num_batch_elements,
                    self.is_train: False}

        # Evaluate model
        eval_res = self.sess.run(eval_list, feed_dict)

        decoded = eval_res[0]

        # Map labels (numbers) to character string
        texts = self.decoder_output_to_text(decoded, num_batch_elements)


        # feed RNN output and recognized text into CTC loss to compute labeling probability
        probs = None
        if calc_probability:
            sparse = self.to_sparse(batch.gt_texts) if probability_of_gt else self.to_sparse(texts)
            ctc_input = eval_res[1]
            eval_list = self.loss_per_element
            feed_dict = {self.saved_ctc_input: ctc_input, self.gt_texts: sparse,
                        self.seq_len: [max_text_len] * num_batch_elements, self.is_train: False}
            loss_vals = self.sess.run(eval_list, feed_dict)
            probs = np.exp(-loss_vals)


        if self.dump:
            self.dump_nn_output(eval_res[1])

        # Return results
        return texts, probs

    def save(self) -> None:
        
        self.snap_ID += 1
        self.saver.save(self.sess, '../model/snapshot', global_step=self.snap_ID)
